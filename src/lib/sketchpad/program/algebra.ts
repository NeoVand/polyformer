import {
	Arithmetic,
	CheckFailed,
	flip,
	integer,
	magnitude,
	ten,
	type Environment,
	type Rational
} from './arithmetic';
import { degree, names, type Equation, type Expr } from './parse';
export interface GridRow {
	kind: 'evaluation' | 'confirmation' | 'coefficient';
	label: string;
	point?: Rational[];
	left?: Rational;
	right?: Rational;
	value?: Rational;
	cells: Rational[];
}
export interface CoefficientGrid {
	columns: string[];
	rows: GridRow[];
}
export interface RootCheck {
	kind: 'substitution' | 'bracket';
	passed: boolean;
	root?: Rational;
	lower?: Rational;
	upper?: Rational;
}
export interface AlgebraResult {
	text: string;
	coefficients?: Rational[];
	roots: Rational[];
	checks: RootCheck[];
	grids: CoefficientGrid[];
	remaining?: bigint[];
	factors?: { p: bigint; q: bigint }[];
	guesses?: { root: Rational; label: 'not certified'; accepted: boolean }[];
	complete: boolean;
}
const empty = (): AlgebraResult => ({ text: '', roots: [], checks: [], grids: [], complete: true });
function integerSyntax(e: Expr, env: Environment): boolean {
	if (e.kind === 'number') return !e.text.includes('.');
	if (e.kind === 'name') return e.name === 'x' || env.get(e.name)?.d === 1n;
	if (e.kind === 'unary') return e.op !== 'sqrt' && integerSyntax(e.value, env);
	return (
		e.kind === 'binary' && e.op !== '/' && integerSyntax(e.left, env) && integerSyntax(e.right, env)
	);
}
function assertIntegerPolynomial(e: Expr, env: Environment): void {
	if (!integerSyntax(e, env))
		throw new Error('expand and factor require integer coefficients, with no division');
	for (const name of names(e))
		if (name !== 'x' && !env.has(name)) throw new Error(`Unknown polynomial name ${name}`);
}
function pointEnv(env: Environment, point: readonly Rational[]): Map<string, Rational> {
	const map = new Map(env);
	point.forEach((v, i) => map.set(['x', 'y', 'z'][i], v));
	return map;
}
async function sides(a: Arithmetic, eq: Equation, env: Environment, point: readonly Rational[]) {
	const variables = pointEnv(env, point);
	const left = await a.evaluate(eq.left, variables, { exact: true });
	const right = await a.evaluate(eq.right, variables, { exact: true });
	if (left.approximate || right.approximate)
		throw new CheckFailed('Approximate named value in an exact equation');
	return { left, right, value: await a.add(left, right, true) };
}
export async function checkRoot(
	a: Arithmetic,
	eq: Equation,
	root: Rational,
	env: Environment = new Map()
): Promise<RootCheck> {
	const { left, right } = await sides(a, eq, env, [root]);
	if (!(await a.equal(left, right)))
		throw new CheckFailed('Root does not satisfy the typed equation');
	return { kind: 'substitution', passed: true, root };
}
async function horner(a: Arithmetic, coefficients: Rational[], x: Rational): Promise<Rational> {
	let y = coefficients.at(-1)!;
	for (let j = coefficients.length - 2; j >= 0; j--)
		y = await a.add(await a.mul(y, x), coefficients[j]);
	return y;
}
/** Values at -1,0,...,d-1 recover d+1 coefficients; d is a separate confirmation. */
export async function recover(
	a: Arithmetic,
	eq: Equation,
	env: Environment = new Map()
): Promise<{ coefficients: Rational[]; grid: CoefficientGrid }> {
	const d = Math.max(degree(eq.left), degree(eq.right));
	const grid: CoefficientGrid = {
		columns: Array.from({ length: d + 1 }, (_, i) => `x^${i}`),
		rows: []
	};
	const values: Rational[] = [];
	for (let i = 0; i < d + 2; i++) {
		const x = integer(BigInt(i - 1)),
			v = await sides(a, eq, env, [x]);
		values.push(v.value);
		const cells: Rational[] = [integer(1n)];
		for (let j = 1; j <= d; j++) cells.push(await a.mul(cells[j - 1], x));
		grid.rows.push({
			kind: i === d + 1 ? 'confirmation' : 'evaluation',
			label: `x = ${x.n}`,
			point: [x],
			...v,
			cells
		});
	}
	let differences = values.slice(0, d + 1),
		basis = [integer(1n)],
		factorial = 1n;
	const coefficients = Array.from({ length: d + 1 }, () => integer(0n));
	const integral = integerSyntax(eq.left, env) && integerSyntax(eq.right, env);
	for (let order = 0; order <= d; order++) {
		if (order > 0) factorial = await a.calc.mul(factorial, BigInt(order));
		const head = differences[0];
		const weight = integral
			? integer(await a.exact(head.n, factorial))
			: await a.div(head, integer(factorial));
		for (let j = 0; j < basis.length; j++)
			coefficients[j] = await a.add(coefficients[j], await a.mul(weight, basis[j]));
		if (order === d) break;
		const next: Rational[] = [];
		for (let i = 0; i < differences.length - 1; i++)
			next.push(await a.add(differences[i + 1], differences[i], true));
		differences = next;
		// Newton's basis is numerical layout derived from chosen points, never the typed expression tree.
		const updated = Array.from({ length: basis.length + 1 }, () => integer(0n));
		for (let j = 0; j < basis.length; j++) {
			updated[j] = await a.add(updated[j], await a.mul(basis[j], integer(BigInt(1 - order))));
			updated[j + 1] = await a.add(updated[j + 1], basis[j]);
		}
		basis = updated;
	}
	const prediction = await horner(a, coefficients, integer(BigInt(d)));
	if (!(await a.equal(prediction, values[d + 1])))
		throw new CheckFailed('Degree confirmation failed');
	for (let i = 0; i < coefficients.length; i++)
		grid.rows.push({
			kind: 'coefficient',
			label: `coefficient of x^${i}`,
			value: coefficients[i],
			cells: coefficients.map((c, j) => (i === j ? c : integer(0n)))
		});
	return { coefficients, grid };
}
async function clearDenominators(a: Arithmetic, cs: Rational[]): Promise<bigint[]> {
	if (cs.every((c) => c.d === 1n)) {
		const integers = cs.map((c) => c.n);
		while (integers.length > 1 && integers.at(-1) === 0n) integers.pop();
		return integers;
	}
	let common = 1n;
	for (const c of cs) {
		common = await a.calc.mul(await a.exact(common, await a.gcd(common, c.d)), c.d);
	}
	const result: bigint[] = [];
	for (const c of cs) result.push(await a.calc.mul(c.n, await a.exact(common, c.d)));
	while (result.length > 1 && result.at(-1) === 0n) result.pop();
	return result;
}
async function bracket(
	a: Arithmetic,
	eq: Equation,
	candidate: Rational,
	env: Environment
): Promise<RootCheck> {
	const scale = ten(6);
	const scaled = await a.calc.mul(magnitude(candidate.n), scale);
	const { q, r } = await a.calc.divmod(scaled, candidate.d);
	let floor = candidate.n < 0n ? flip(q) : q;
	if (candidate.n < 0n && r !== 0n) floor = await a.calc.sub(floor, 1n);
	for (const offset of [0n, -1n, 1n]) {
		const lo = await a.calc.add(floor, offset),
			hi = await a.calc.add(lo, 1n);
		const lower = await a.fraction(lo, scale),
			upper = await a.fraction(hi, scale);
		const f = await sides(a, eq, env, [lower]),
			g = await sides(a, eq, env, [upper]);
		if (f.value.n !== 0n && g.value.n !== 0n && f.value.n < 0n !== g.value.n < 0n)
			return { kind: 'bracket', passed: true, lower, upper };
	}
	throw new CheckFailed('No opposite-sign bracket at six decimal places');
}
async function lowDegree(
	a: Arithmetic,
	eq: Equation,
	c: bigint[],
	env: Environment
): Promise<AlgebraResult> {
	const result = empty();
	if (c.length === 1) {
		result.text = c[0] === 0n ? 'every x' : 'no solution';
		return result;
	}
	if (c.length === 2) {
		const root = await a.fraction(flip(c[0]), c[1]);
		result.checks.push(await checkRoot(a, eq, root, env));
		result.roots.push(root);
		result.text = `x = ${await a.rootText(root)}`;
		return result;
	}
	const [constant, b, leading] = c;
	const disc = await a.calc.sub(
		await a.calc.mul(b, b),
		await a.calc.mul(await a.calc.mul(4n, leading), constant)
	);
	if (disc < 0n) {
		result.text = 'no real roots';
		return result;
	}
	const sr = await a.calc.isqrt(disc),
		den = await a.calc.mul(2n, leading);
	if (sr.rem === 0n) {
		for (const sign of [-1, 1]) {
			const num =
				sign < 0 ? await a.calc.sub(flip(b), sr.root) : await a.calc.add(flip(b), sr.root);
			const root = await a.fraction(num, den);
			if (result.roots.some((r) => r.n === root.n && r.d === root.d)) continue;
			result.checks.push(await checkRoot(a, eq, root, env));
			result.roots.push(root);
		}
		const text: string[] = [];
		for (const root of result.roots) text.push(await a.rootText(root));
		result.text = `x = ${text.join(', ')}`;
	} else {
		// Extra square-root digits locate the six-place cell; the typed equation proves the cell.
		const places = 6 + magnitude(den).toString().length + 3,
			scale = ten(places);
		const large = await a.calc.isqrt(await a.calc.mul(disc, ten(2 * places)));
		const base = await a.calc.mul(flip(b), scale),
			divisor = await a.calc.mul(den, scale);
		const bounds: string[] = [];
		for (const sign of [-1, 1]) {
			const num =
				sign < 0 ? await a.calc.sub(base, large.root) : await a.calc.add(base, large.root);
			const check = await bracket(a, eq, await a.fraction(num, divisor), env);
			result.checks.push(check);
			bounds.push(
				`[${await a.decimal(check.lower!, 6, true)}, ${await a.decimal(check.upper!, 6, true)}]`
			);
		}
		result.text = `x = (${flip(b)} ± √${disc})/(${den}); six-place bounds ${bounds.join(', ')}`;
	}
	return result;
}
/** Float64 candidates only. Derivative roots split the real line into monotone intervals.
 * This is an uncertified search; no float-derived digit can pass into an accepted answer unchecked.
 */
function floatRoots(c: number[]): number[] {
	while (c.length > 1 && c.at(-1) === 0) c.pop();
	if (c.length < 2 || c.some((v) => !Number.isFinite(v))) return [];
	if (c.length === 2) return [-c[0] / c[1]];
	const evaluate = (x: number) => c.reduceRight((y, v) => y * x + v, 0);
	const bound = 1 + Math.max(...c.slice(0, -1).map((v) => Math.abs(v / c.at(-1)!)));
	const critical = floatRoots(c.slice(1).map((v, i) => v * (i + 1))).filter(
		(v) => Math.abs(v) < bound
	);
	const points = [-bound, ...critical.sort((a, b) => a - b), bound];
	const roots = critical.filter(
		(x) => Math.abs(evaluate(x)) < 1e-6 * Math.max(1, ...c.map(Math.abs))
	);
	for (let i = 0; i < points.length - 1; i++) {
		let lo = points[i],
			hi = points[i + 1],
			left = evaluate(lo);
		if (left < 0 === evaluate(hi) < 0) continue;
		for (let n = 0; n < 100; n++) {
			const mid = (lo + hi) / 2,
				value = evaluate(mid);
			if (left < 0 === value < 0) {
				lo = mid;
				left = value;
			} else hi = mid;
		}
		roots.push((lo + hi) / 2);
	}
	return roots;
}
function candidates(c: bigint[]): Rational[] {
	const found: Rational[] = [];
	const leading = Math.abs(Number(c.at(-1)!));
	const roots = floatRoots(c.map(Number));
	// A bounded search keeps hostile input finite. Exhaustiveness is deliberately never claimed.
	for (const root of roots)
		for (let q = 1; q <= Math.min(leading, 256); q++) {
			if (leading % q !== 0) continue;
			const near = Math.round(root * q);
			for (const p of [near, near - 1, near + 1]) {
				if (!Number.isSafeInteger(p) || !Number.isSafeInteger(q)) continue;
				const r = { n: BigInt(p), d: BigInt(q) };
				if (!found.some((v) => v.n === r.n && v.d === r.d)) found.push(r);
			}
		}
	return found;
}
/** Divide by (q*x-p) with exact divisions on the sheet. Null means an unproved guess. */
async function synthetic(a: Arithmetic, c: bigint[], root: Rational): Promise<bigint[] | null> {
	const out = Array<bigint>(c.length - 1);
	try {
		out[out.length - 1] = await a.exact(c.at(-1)!, root.d);
		for (let i = out.length - 1; i > 0; i--)
			out[i - 1] = await a.exact(await a.calc.add(c[i], await a.calc.mul(root.n, out[i])), root.d);
		const rem = await a.calc.add(c[0], await a.calc.mul(root.n, out[0]));
		return rem === 0n ? out : null;
	} catch (e) {
		if (e instanceof CheckFailed) return null;
		throw e;
	}
}
async function factorCoefficients(
	a: Arithmetic,
	eq: Equation,
	coefficients: bigint[],
	env: Environment
): Promise<AlgebraResult> {
	const result = empty();
	result.complete = false;
	result.guesses = [];
	result.factors = [];
	let remaining = coefficients;
	while (remaining.length > 1) {
		let proved = false;
		for (const guess of candidates(remaining)) {
			const quotient = await synthetic(a, remaining, guess);
			const item = { root: guess, label: 'not certified' as const, accepted: false };
			result.guesses.push(item);
			if (!quotient) continue;
			const root = await a.fraction(guess.n, guess.d);
			result.checks.push(await checkRoot(a, eq, root, env));
			result.roots.push(root);
			item.accepted = true;
			result.factors.push({ p: guess.n, q: guess.d });
			remaining = quotient;
			proved = true;
			break;
		}
		if (!proved) break;
	}
	result.remaining = remaining;
	const text: string[] = [];
	for (const root of result.roots) text.push(await a.rootText(root));
	const factors = result.factors.map(({ p, q }) => `(${polynomialText([flip(p), q])})`).join('');
	result.text = `proven roots: ${text.join(', ') || 'none'}; factors ${factors || 'none'}; remaining ${polynomialText(remaining)}. Guesses are not certified; checks prove these roots, not that no others exist.`;
	return result;
}
export function polynomialText(c: bigint[]): string {
	const terms: string[] = [];
	for (let i = c.length - 1; i >= 0; i--) {
		if (c[i] === 0n) continue;
		const abs = magnitude(c[i]);
		const variable = i === 0 ? '' : i === 1 ? 'x' : `x^${i}`;
		const body = (abs === 1n && i > 0 ? '' : abs.toString()) + variable;
		terms.push((terms.length ? (c[i] < 0n ? ' - ' : ' + ') : c[i] < 0n ? '-' : '') + body);
	}
	return terms.join('') || '0';
}
export async function solve(
	a: Arithmetic,
	eq: Equation,
	env: Environment = new Map()
): Promise<AlgebraResult> {
	const recovered = await recover(a, eq, env),
		c = await clearDenominators(a, recovered.coefficients);
	const result =
		c.length <= 3 ? await lowDegree(a, eq, c, env) : await factorCoefficients(a, eq, c, env);
	result.coefficients = recovered.coefficients;
	result.grids.push(recovered.grid);
	return result;
}
export async function factor(
	a: Arithmetic,
	value: Expr,
	env: Environment = new Map()
): Promise<AlgebraResult> {
	assertIntegerPolynomial(value, env);
	const eq: Equation = { left: value, right: { kind: 'number', text: '0' } };
	const recovered = await recover(a, eq, env),
		c = await clearDenominators(a, recovered.coefficients);
	const result = await factorCoefficients(a, eq, c, env);
	result.coefficients = recovered.coefficients;
	result.grids.push(recovered.grid);
	return result;
}
export async function expand(
	a: Arithmetic,
	value: Expr,
	env: Environment = new Map()
): Promise<AlgebraResult> {
	assertIntegerPolynomial(value, env);
	const d = degree(value),
		result = empty();
	const bound = await a.evaluate(value, pointEnv(env, [integer(1n)]), {
		positive: true,
		exact: true
	});
	const twice = await a.calc.mul(2n, bound.n);
	const base = ten(magnitude(twice).toString().length);
	const v = await a.evaluate(value, pointEnv(env, [integer(base)]), { exact: true });
	if (v.d !== 1n || v.approximate)
		throw new CheckFailed('Expansion needs exact integer coefficients');
	let packed = v.n;
	const coefficients: bigint[] = [];
	const half = await a.exact(base, 2n);
	for (let i = 0; i <= d; i++) {
		const qr = await a.calc.divmod(magnitude(packed), base);
		let quotient = packed < 0n ? flip(qr.q) : qr.q,
			remainder = packed < 0n ? flip(qr.r) : qr.r;
		if (remainder > half) {
			remainder = await a.calc.sub(remainder, base);
			quotient = await a.calc.add(quotient, 1n);
		}
		if (remainder < flip(half)) {
			remainder = await a.calc.add(remainder, base);
			quotient = await a.calc.sub(quotient, 1n);
		}
		coefficients.push(remainder);
		packed = quotient;
	}
	if (packed !== 0n) throw new CheckFailed('Expansion exceeds degree or coefficient bound');
	const eq = { left: value, right: { kind: 'number' as const, text: '0' } };
	const grid: CoefficientGrid = { columns: coefficients.map((_, i) => `x^${i}`), rows: [] };
	const cellsAt = async (x: bigint) => {
		const cells = [integer(1n)];
		for (let i = 1; i <= d; i++) cells.push(await a.mul(cells[i - 1], integer(x)));
		return cells;
	};
	grid.rows.push({
		kind: 'evaluation',
		label: 'positive-coefficient bound at x = 1',
		point: [integer(1n)],
		value: bound,
		cells: await cellsAt(1n)
	});
	grid.rows.push({
		kind: 'evaluation',
		label: `packed value at x = ${base}`,
		point: [integer(base)],
		value: v,
		cells: await cellsAt(base)
	});
	// Independent small-point checks detect pack/unpack errors without symbolic expansion.
	for (const x of [-1n, 0n, 1n, 2n]) {
		const sample = await sides(a, eq, env, [integer(x)]);
		if (!(await a.equal(sample.value, await horner(a, coefficients.map(integer), integer(x)))))
			throw new CheckFailed('Expansion confirmation failed');
		grid.rows.push({
			kind: 'confirmation',
			label: `x = ${x}`,
			point: [integer(x)],
			...sample,
			cells: await cellsAt(x)
		});
	}
	coefficients.forEach((c, i) =>
		grid.rows.push({
			kind: 'coefficient',
			label: `coefficient of x^${i}`,
			value: integer(c),
			cells: coefficients.map((v, j) => integer(i === j ? v : 0n))
		})
	);
	result.coefficients = coefficients.map(integer);
	result.grids.push(grid);
	result.text = polynomialText(coefficients);
	return result;
}
async function determinant2(a: Arithmetic, m: bigint[][]): Promise<bigint> {
	return a.calc.sub(await a.calc.mul(m[0][0], m[1][1]), await a.calc.mul(m[0][1], m[1][0]));
}
/** Bareiss elimination with row swaps, including the right-hand column. */
async function bareiss(a: Arithmetic, input: bigint[][]): Promise<bigint[][] | null> {
	const m = input.map((r) => [...r]),
		n = m.length;
	let previous = 1n;
	for (let k = 0; k < n - 1; k++) {
		if (m[k][k] === 0n) {
			const row = m.findIndex((r, i) => i > k && r[k] !== 0n);
			if (row < 0) return null;
			[m[k], m[row]] = [m[row], m[k]];
		}
		const pivot = m[k][k];
		for (let i = k + 1; i < n; i++) {
			for (let j = k + 1; j <= n; j++)
				m[i][j] = await a.exact(
					await a.calc.sub(await a.calc.mul(pivot, m[i][j]), await a.calc.mul(m[i][k], m[k][j])),
					previous
				);
			m[i][k] = 0n;
		}
		previous = pivot;
	}
	return m[n - 1][n - 1] === 0n ? null : m;
}
export async function system(
	a: Arithmetic,
	equations: Equation[],
	env: Environment = new Map()
): Promise<AlgebraResult> {
	const n = equations.length,
		result = empty(),
		matrix: bigint[][] = [];
	for (const eq of equations) {
		const points = [
			Array.from({ length: n }, () => integer(0n)),
			...Array.from({ length: n }, (_, i) =>
				Array.from({ length: n }, (_, j) => integer(i === j ? 1n : 0n))
			),
			Array.from({ length: n }, (_, i) => integer(BigInt(i + 2)))
		];
		const grid: CoefficientGrid = {
			columns: ['constant', ...['x', 'y', 'z'].slice(0, n)],
			rows: []
		};
		const samples: Rational[] = [];
		for (const [i, p] of points.entries()) {
			const s = await sides(a, eq, env, p);
			samples.push(s.value);
			grid.rows.push({
				kind: i === points.length - 1 ? 'confirmation' : 'evaluation',
				label: `(${p.map((v) => v.n).join(', ')})`,
				point: p,
				...s,
				cells: [integer(1n), ...p]
			});
		}
		const cs = [samples[0]];
		for (let i = 1; i <= n; i++) cs.push(await a.add(samples[i], samples[0], true));
		let check = cs[0];
		for (let i = 0; i < n; i++)
			check = await a.add(check, await a.mul(cs[i + 1], points.at(-1)![i]));
		if (!(await a.equal(check, samples.at(-1)!)))
			throw new CheckFailed('System linear-degree confirmation failed');
		cs.forEach((c, i) =>
			grid.rows.push({
				kind: 'coefficient',
				label: grid.columns[i],
				value: c,
				cells: cs.map((v, j) => (i === j ? v : integer(0n)))
			})
		);
		const cleared = await clearDenominators(a, cs);
		while (cleared.length <= n) cleared.push(0n);
		matrix.push([...cleared.slice(1), flip(cleared[0])]);
		result.grids.push(grid);
	}
	let roots: Rational[];
	if (n === 2) {
		const [[aa, b, e], [c, d, f]] = matrix,
			det = await determinant2(a, [
				[aa, b],
				[c, d]
			]);
		if (det === 0n) {
			result.text = 'zero determinant; no unique solution';
			result.complete = false;
			return result;
		}
		roots = [
			await a.fraction(
				await determinant2(a, [
					[e, b],
					[f, d]
				]),
				det
			),
			await a.fraction(
				await determinant2(a, [
					[aa, e],
					[c, f]
				]),
				det
			)
		];
	} else {
		const m = await bareiss(a, matrix);
		if (!m) {
			result.text = 'zero determinant; no unique solution';
			result.complete = false;
			return result;
		}
		roots = Array<Rational>(n);
		for (let i = n - 1; i >= 0; i--) {
			let rhs = integer(m[i][n]);
			for (let j = i + 1; j < n; j++)
				rhs = await a.add(rhs, await a.mul(integer(m[i][j]), roots[j]), true);
			roots[i] = await a.div(rhs, integer(m[i][i]));
		}
	}
	for (const eq of equations) {
		const s = await sides(a, eq, env, roots);
		if (!(await a.equal(s.left, s.right))) throw new CheckFailed('System substitution failed');
		result.checks.push({ kind: 'substitution', passed: true });
	}
	result.roots = roots;
	const formatted: string[] = [];
	for (let i = 0; i < n; i++)
		formatted.push(`${['x', 'y', 'z'][i]} = ${await a.rootText(roots[i])}`);
	result.text = formatted.join(', ');
	return result;
}
