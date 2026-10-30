import type { Calc } from './calc';
import { exponent, type Expr } from './parse';
export interface Rational {
	n: bigint;
	d: bigint;
	approximate?: boolean;
}
export type Environment = ReadonlyMap<string, Rational>;
export class CheckFailed extends Error {
	constructor(message: string) {
		super(message);
		this.name = 'CheckFailed';
	}
}
// Sign and decimal placement are layout. No arithmetic answer digits are computed here.
export const magnitude = (n: bigint): bigint => BigInt(n.toString().replace('-', ''));
export const flip = (n: bigint): bigint =>
	n === 0n ? 0n : BigInt(n < 0n ? n.toString().slice(1) : '-' + n.toString());
export const ten = (places: number): bigint => BigInt('1' + '0'.repeat(places));
export const integer = (n: bigint): Rational => ({ n, d: 1n });
export class Arithmetic {
	constructor(readonly calc: Calc) {}
	async gcd(a: bigint, b: bigint): Promise<bigint> {
		a = magnitude(a);
		b = magnitude(b);
		while (b !== 0n) {
			const { r } = await this.calc.divmod(a, b);
			if (r < 0n || r >= b) throw new CheckFailed('Invalid division remainder');
			a = b;
			b = r;
		}
		return a;
	}
	async exact(a: bigint, b: bigint): Promise<bigint> {
		if (b === 0n) throw new CheckFailed('Exact division by zero');
		const { q, r } = await this.calc.divmod(magnitude(a), magnitude(b));
		if (r !== 0n) throw new CheckFailed('Exact division left a remainder');
		return a < 0n !== b < 0n ? flip(q) : q;
	}
	async fraction(n: bigint, d: bigint, approximate = false): Promise<Rational> {
		if (d === 0n) throw new Error('Division by zero');
		if (d < 0n) {
			n = flip(n);
			d = flip(d);
		}
		if (d === 1n) return { n, d, approximate };
		const g = await this.gcd(n, d);
		return { n: await this.exact(n, g), d: await this.exact(d, g), approximate };
	}
	async add(a: Rational, b: Rational, subtract = false): Promise<Rational> {
		const op = subtract ? this.calc.sub.bind(this.calc) : this.calc.add.bind(this.calc);
		const approximate = !!(a.approximate || b.approximate);
		if (a.d === b.d) return this.fraction(await op(a.n, b.n), a.d, approximate);
		const n = await op(await this.calc.mul(a.n, b.d), await this.calc.mul(b.n, a.d));
		return this.fraction(n, await this.calc.mul(a.d, b.d), approximate);
	}
	async mul(a: Rational, b: Rational): Promise<Rational> {
		return this.fraction(
			await this.calc.mul(a.n, b.n),
			a.d === 1n && b.d === 1n ? 1n : await this.calc.mul(a.d, b.d),
			!!(a.approximate || b.approximate)
		);
	}
	async div(a: Rational, b: Rational): Promise<Rational> {
		return this.fraction(
			b.d === 1n ? a.n : await this.calc.mul(a.n, b.d),
			a.d === 1n ? b.n : await this.calc.mul(a.d, b.n),
			!!(a.approximate || b.approximate)
		);
	}
	async pow(a: Rational, e: number): Promise<Rational> {
		if (e === 0) return integer(1n);
		let out = a;
		for (let i = 1; i < Math.abs(e); i++) out = await this.mul(out, a);
		return e < 0 ? this.div(integer(1n), out) : out;
	}
	async quantize(a: Rational, places: number): Promise<Rational> {
		if (a.d === 1n) return a;
		const scale = ten(places);
		const { q, r } = await this.calc.divmod(await this.calc.mul(magnitude(a.n), scale), a.d);
		return this.fraction(a.n < 0n ? flip(q) : q, scale, !!a.approximate || r !== 0n);
	}
	async sqrt(a: Rational, places?: number, exact = false): Promise<Rational> {
		if (a.n < 0n) throw new Error('Square root has no real value');
		const nr = await this.calc.isqrt(a.n),
			dr = a.d === 1n ? { root: 1n, rem: 0n } : await this.calc.isqrt(a.d);
		if (nr.rem === 0n && dr.rem === 0n) {
			const root = await this.fraction(nr.root, dr.root, !!a.approximate);
			if (exact) return root;
			const cut = await this.quantize(root, places ?? 12);
			return places !== undefined || cut.approximate ? cut : root;
		}
		if (exact) throw new Error('Irrational value is not allowed in exact evaluation');
		const k = places ?? 12,
			scale = ten(k);
		const scaled = await this.calc.mul(a.n, ten(2 * k));
		const { q } = await this.calc.divmod(scaled, a.d);
		const { root } = await this.calc.isqrt(q);
		return this.fraction(root, scale, true);
	}
	async evaluate(
		expr: Expr,
		env: Environment = new Map(),
		options: { places?: number; exact?: boolean; positive?: boolean } = {}
	): Promise<Rational> {
		const visit = (e: Expr) => this.evaluate(e, env, options);
		switch (expr.kind) {
			case 'number': {
				const [whole, frac = ''] = expr.text.split('.');
				return this.fraction(BigInt((whole || '0') + frac), ten(frac.length));
			}
			case 'name': {
				const n = env.get(expr.name);
				if (!n) throw new Error(`Unknown name ${expr.name}`);
				return options.positive ? { ...n, n: magnitude(n.n) } : n;
			}
			case 'unary': {
				const v = await visit(expr.value);
				if (expr.op === 'sqrt') return this.sqrt(v, options.places, options.exact);
				return expr.op === '-' && !options.positive ? { ...v, n: flip(v.n) } : v;
			}
			case 'gcd': {
				const a = await visit(expr.left),
					b = await visit(expr.right);
				if (a.d !== 1n || b.d !== 1n) throw new Error('gcd needs integer arguments');
				return integer(await this.gcd(a.n, b.n));
			}
			case 'binary': {
				const a = await visit(expr.left);
				if (expr.op === '^') return this.pow(a, exponent(expr.right));
				const b = await visit(expr.right);
				if (expr.op === '+') return this.add(a, b);
				if (expr.op === '-') return this.add(a, b, !options.positive);
				if (expr.op === '*') return this.mul(a, b);
				const q = await this.div(a, b);
				if (options.exact) return q;
				if (options.places !== undefined) return this.quantize(q, options.places);
				// Default precision applies at every division, even inside a larger expression.
				const cut = await this.quantize(q, 12);
				return cut.approximate ? cut : q;
			}
		}
	}
	async equal(a: Rational, b: Rational): Promise<boolean> {
		return (await this.calc.mul(a.n, b.d)) === (await this.calc.mul(b.n, a.d));
	}
	async decimal(a: Rational, places = 12, fixed = false): Promise<string> {
		// An integer is already a sheet-produced digit row. Padding its decimal point is layout.
		if (a.d === 1n)
			return (
				a.n.toString() +
				(fixed && places ? '.' + '0'.repeat(places) : '') +
				(a.approximate ? '…' : '')
			);
		const { q, r } = await this.calc.divmod(await this.calc.mul(magnitude(a.n), ten(places)), a.d);
		const digits = q.toString().padStart(places + 1, '0');
		let result = places ? digits.slice(0, -places) + '.' + digits.slice(-places) : digits;
		if (!fixed && places) result = result.replace(/0+$/, '').replace(/\.$/, '');
		if (a.n < 0n && q !== 0n) result = '-' + result;
		return result + (r !== 0n || a.approximate ? '…' : '');
	}
	async rootText(a: Rational): Promise<string> {
		return a.d === 1n ? a.n.toString() : `${a.n}/${a.d} (≈ ${await this.decimal(a, 6, true)})`;
	}
}
