import { multiply, reference } from "./canvas_runtime.js";
let rng = 1; const rand = () => (rng = (rng * 1103515245 + 12345) % 2147483648) / 2147483648;
const num = (n) => Array.from({ length: n }, (_, i) => (i === 0 ? 1 + Math.floor(rand() * 9) : Math.floor(rand() * 10))).join("");
let bad = 0, total = 0;
for (const [n, m, k] of [[1, 1, 100], [4, 4, 200], [6, 6, 100], [10, 10, 50], [7, 3, 50], [2, 9, 50], [30, 30, 5]]) {
  for (let i = 0; i < k; i++) {
    const a = num(n), b = num(m);
    const cv = await multiply(a, b, async (op, v) => reference(op, v));
    total++; if (cv.result() !== (BigInt(a) * BigInt(b)).toString()) { bad++; console.log("BAD", a, b, cv.result()); }
  }
}
for (const [a, b] of [["0", "5"], ["10", "10"], ["99", "99"], ["100", "1"], ["1", "1000"]]) {
  const cv = await multiply(a, b, async (op, v) => reference(op, v));
  if (cv.result() !== (BigInt(a) * BigInt(b)).toString()) { bad++; console.log("BAD edge", a, b, cv.result()); }
}
console.log(`JS runtime with reference tables: ${total - bad}/${total} random products exact + edge cases`);
