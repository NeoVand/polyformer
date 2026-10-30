// The canvas runtime for long multiplication (port of e4_mul.py). It holds no arithmetic and no loop knowledge: each
// tick it gathers a 3-cell view for the current op, asks the policy (the model, or the reference table in tests) for
// (glyph, glyph, next-op), stamps the glyphs, consumes the carry/product cells it read, and moves as the next-op says.

export const B = " ";
export const ROWS = ["a", "b", "cM", "p", "cA", "R"];

export function reference(op, v) {
  if (op === "MUL") {
    const [a, b, c] = v;
    if (a === B) return [c !== B ? c : "0", "0", "Z"];
    const s = +a * +b + (c !== B ? +c : 0);
    return [String(s % 10), String(Math.floor(s / 10)), "A"];
  }
  if (op === "ADD" || op === "ADZ" || op === "FLS") {
    const s = v.filter((g) => g !== B).reduce((x, g) => x + +g, 0);
    const nxt = { ADD: "M", ADZ: "F", FLS: "N" }[op];
    if (op === "FLS") return [s ? String(s) : B, "-", nxt];
    return [String(s % 10), String(Math.floor(s / 10)), nxt];
  }
  if (op === "NXT") return ["-", "-", v[0] === B ? "H" : "M"];
  throw new Error(op);
}

export class Canvas {
  constructor(a, b) {
    this.n = a.length; this.m = b.length; this.W = this.n + this.m + 2;
    this.rows = Object.fromEntries(ROWS.map((k) => [k, Array(this.W).fill(B)]));
    [...a].reverse().forEach((d, i) => (this.rows.a[i] = d));
    [...b].reverse().forEach((d, i) => (this.rows.b[i] = d));
    this.op = "MUL"; this.x = 0; this.j = 0; this.ticks = 0; this.done = false;
  }
  get(row, x) { return x >= 0 && x < this.W ? this.rows[row][x] : B; }
  view() {
    const { op, x, j } = this;
    if (op === "MUL") return [this.get("a", x - j), this.get("b", j), this.get("cM", x)];
    if (op === "NXT") return [this.get("b", j + 1), B, B];
    return [this.get("cA", x), this.get("p", x), this.get("R", x)];
  }
  // apply one policy output; returns false when halted
  apply([g1, g2, nxt]) {
    const r = this.rows, x = this.x;
    this.ticks++;
    if (this.op === "MUL") {
      r.cM[x] = B; r.p[x] = g1;
      if (x + 1 < this.W) r.cM[x + 1] = g2;
      this.op = nxt === "A" ? "ADD" : "ADZ";
    } else if (this.op === "ADD" || this.op === "ADZ") {
      r.cA[x] = B; r.p[x] = B; r.R[x] = g1;
      if (x + 1 < this.W) r.cA[x + 1] = g2 === "1" ? "1" : B;
      this.op = nxt === "M" ? "MUL" : "FLS"; this.x = x + 1;
    } else if (this.op === "FLS") {
      r.cA[x] = B; if (g1 !== B) r.R[x] = g1;
      this.op = "NXT";
    } else {
      if (nxt === "H") { this.done = true; return false; }
      this.j++; for (const k of ["cM", "p", "cA"]) r[k].fill(B);
      this.op = "MUL"; this.x = this.j;
    }
    return true;
  }
  result() { return r2s(this.rows.R); }
}
const r2s = (row) => [...row].reverse().join("").trim().replace(/^0+(?=\d)/, "") || "0";

export async function multiply(a, b, policy, onTick) {
  const cv = new Canvas(a, b);
  for (;;) {
    const out = await policy(cv.op, cv.view());
    if (onTick) await onTick(cv, out);
    if (!cv.apply(out)) break;
  }
  return cv;
}
