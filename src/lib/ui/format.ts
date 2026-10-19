export const pct = (v: number | undefined, digits = 1) =>
	v === undefined || Number.isNaN(v) ? '—' : `${(v * 100).toFixed(digits)}%`;

export function compact(n: number): string {
	if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
	if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
	if (n >= 1e3) return `${(n / 1e3).toFixed(1)}k`;
	return String(Math.round(n));
}

export function flops(n: number): string {
	if (n >= 1e15) return `${(n / 1e15).toFixed(2)} PFLOP`;
	if (n >= 1e12) return `${(n / 1e12).toFixed(2)} TFLOP`;
	if (n >= 1e9) return `${(n / 1e9).toFixed(2)} GFLOP`;
	return `${(n / 1e6).toFixed(1)} MFLOP`;
}

export function duration(ms: number): string {
	const s = Math.floor(ms / 1000);
	const m = Math.floor(s / 60);
	return m ? `${m}m ${String(s % 60).padStart(2, '0')}s` : `${s}s`;
}

export const ms = (v: number) => (v ? `${v.toFixed(1)} ms` : '—');
