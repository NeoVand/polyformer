# Cursor agents: how to check and resume (written 28 Oct 2026, before the Claude app relaunch)

Running when written. All are reparented to PID 1, in their own process groups, with stdin /dev/null and stdout and
stderr going to a log file. Quitting the Claude app does not signal them.

| agent | pid | workspace | chat id | log (hard link; same inode as the scratchpad copy) |
|---|---|---|---|---|
| r4 | 65713 | /Users/neo/repos/polyformer-wt/r4 | 7fbcfaeb-e9ed-4939-bd52-2c49a998c558 | research/cursor_logs/cursor_r4.json |
| reasonexport (Loom) | 65715 | /Users/neo/repos/polyformer-wt/webexport | 1b233d2a-be69-468a-8d15-823027d1b547 | research/cursor_logs/cursor_reasonexport.json |
| picker | 65718 | /Users/neo/repos/polyformer-wt/site-reason | db940ba5-644f-47fc-b9c8-42a7ca47b45c | research/cursor_logs/cursor_picker.json |
| scan | 91729 | /Users/neo/repos/polyformer-wt/scan | f47555b2-5e40-4f75-8b59-96d5b63d660a | research/cursor_logs/cursor_scan.json |

- **Check:** `ps -p 65713,65715,65718,91729`. Each agent's log gets its final JSON only on exit; its real output is
  the commits in its worktree.
- **Resume an agent that died before finishing:** from its workspace, run
  `nohup ~/.local/bin/cursor-agent -p --output-format json --model grok-4.7-xhigh-fast --force --trust --workspace <ws> --resume <chat id> "Continue the brief from where you stopped; check what is already committed and what Modal jobs are running before launching anything." > <log> 2>&1 &`
- **Briefs** (in git):
  - r4: research/r4/R4_BRIEF.md
  - Loom export: research/webexport/REASON_EXPORT_BRIEF.md
  - picker: briefs/MODEL_PICKER_BRIEF.md
  - scan: research/scan/SCAN_BRIEF.md
- **Modal jobs** are launched with deploy + spawn and write to their own volumes, so they do not depend on any local
  process.
- **COMPILE** (a Claude agent) dies with the app. Its Modal curve jobs keep running. Collect them with its collector
  script (compile worktree, jobs/curve-sft300.json and curve-sft600.json).
| remember | 2747 | /Users/neo/repos/polyformer-wt/remember | (see ~/.cursor/chats/7594d603b25b206b862781ebab98f400) | research/cursor_logs/cursor_remember.json |
| predict-fix | 29635 | /Users/neo/repos/polyformer-wt/predict | 65ff6de4-a31c-4313-9bed-b581efad41aa | research/cursor_logs/cursor_predict_fix.json |
| scan-fix | 32678 | /Users/neo/repos/polyformer-wt/scan | f47555b2-5e40-4f75-8b59-96d5b63d660a | research/cursor_logs/cursor_scan-fix.json |
| remember-fix | 32680 | /Users/neo/repos/polyformer-wt/remember | 7b7127cf-779a-4aa7-a202-b1c3e3c7c85e | research/cursor_logs/cursor_remember-fix.json |
| headpin-fix | 32682 | /Users/neo/repos/polyformer-wt/headpin | 7b4d106a-ae9d-4c70-a169-f2f2912db8da | research/cursor_logs/cursor_headpin-fix.json |
| e3e4-fix | 32685 | /Users/neo/repos/polyformer-wt/theory | (fresh; see ~/.cursor/chats) | research/cursor_logs/cursor_e3e4-fix.json |
| lean-dec | 35090 | /Users/neo/repos/polyformer-wt/lean-p | (fresh) | research/cursor_logs/cursor_lean-dec.json |
| daudit | 35729 | /Users/neo/repos/polyformer-wt/r5audit | (fresh) | research/cursor_logs/cursor_daudit.json |
| webscan | 64581 | /Users/neo/repos/polyformer-wt/webexport | (fresh) | research/cursor_logs/cursor_webscan.json |
| stack | 73537 | /Users/neo/repos/polyformer-wt/stack | (fresh) | research/cursor_logs/cursor_stack.json |
| horizon | 73539 | /Users/neo/repos/polyformer-wt/horizon | (fresh) | research/cursor_logs/cursor_horizon.json |
| cert | 82468 | /Users/neo/repos/polyformer-wt/cert | (fresh) | research/cursor_logs/cursor_cert.json |
| askq | 82474 | /Users/neo/repos/polyformer-wt/askq | (fresh) | research/cursor_logs/cursor_askq.json |
| predict-collect | 83184 | /Users/neo/repos/polyformer-wt/predict | (fresh; old chat 65ff6de4 cannot resume: 'Unknown model ID grok-4.7') | research/cursor_logs/cursor_predict-collect.json |
| cert (Sol) | 85629 | /Users/neo/repos/polyformer-wt/cert | (fresh, gpt-5.6-sol-xhigh-fast) | research/cursor_logs/cursor_cert.json |

## 29 Oct: moved off Cursor (Neo). Agents now run on Antigravity (agy) and Codex.
Launchers: `run_agy_ws.sh <name> <ws> <model> <prompt>` (agy -p, --dangerously-skip-permissions) and
`run_codex_ws.sh <name> <ws> <prompt>` (codex exec, full access, high effort). Logs: agy_<name>.log,
codex_<name>.log / codex_<name>.md.

| agent | pid | engine | workspace |
|---|---|---|---|
| scan-fix | 89673 | Codex | polyformer-wt/scan |
| remember-fix | 89678 | agy Opus 5.5 high | polyformer-wt/remember |
| daudit | 89680 | agy Opus 5.5 high | polyformer-wt/r5audit |
| webscan | 89682 | agy Opus 5.5 high | polyformer-wt/webexport |
| stack | 89684 | agy Opus 5.5 high | polyformer-wt/stack |
| horizon | 89686 | Codex | polyformer-wt/horizon |
| askq | 89688 | agy Gemini 4 Argon high | polyformer-wt/askq |
| cert | 89693 | Codex | polyformer-wt/cert |
| predict-collect | 89695 | agy Gemini 4 Argon high | polyformer-wt/predict |
| r5-harness | 96221 | agy Opus 5.5 high | polyformer-wt/r5-harness (branch r5-harness from main 2c9a2882) |
