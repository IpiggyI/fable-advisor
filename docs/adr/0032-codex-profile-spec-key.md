# 0032 — codex runner 的 `profile` spec 键

- **Status**: accepted（2026-10-14 椰椰的要求；同日随 6.4.0 发布，说明书 `docs/manuals/6.4.0.html`）
- **Date**: 2026-10-14
- **影响范围**:
  - `plugin/scripts/run-codex.mjs`：`SPEC_KEYS`、`normalizeSpec`、`executeCodex` 的参数组装、receipt 与 state。
  - `plugin/skills/orchestration/lanes-claude-code.md`：调参字段列表新增 `profile`。
  - `tests/test_runner_contract.py`：新增 `case_codex_profile`。
  - `docs/zh/` 下对应孪生、`README.md`。
  - 版本 6.4.0：`docs/manuals/6.4.0.html` 与两个版本字段。
- **关联**: 沿用 [ADR 0003](./0003-codex-lane-param-policy.md) 的取向：runner 不读本机配置，只在 spec 要求时注入参数，并在 receipt 记录提交值。

## 背景

椰椰 2026-10-14 要求 codex 调用能加 `--profile`，用来指定供应商，例如 Windows 侧的 `--profile official`；这个参数默认不带，需要用户显式要求。此前椰椰在 Windows 侧已安装的 6.3.0 缓存里打了临时补丁：读环境变量 `FABLE_CODEX_PROFILE`，把 `--profile <name>` 放在 `exec` 之后。

核验（2026-10-14，WSL 侧 `codex-cli 0.162.1`）：`codex exec --help` 列出 `-p, --profile <CONFIG_PROFILE_V2>`，说明为在基础配置之上叠加 `$CODEX_HOME/<name>.config.toml`；`codex exec resume --help` 没有列出该选项。

## 决策

1. **spec 键，不是环境变量。** 新增可选键 `profile`，非空字符串；空串或非字符串判 `spec_invalid`，不拉起 CLI。省略时不传 `--profile`。"用户显式要求"落在主代理：只在用户明确要求时写这个键。
2. **位置紧跟 `exec`。** 新会话为 `codex exec --profile <name> --json …`，续接为 `codex exec --profile <name> [--sandbox read-only] resume …`，因为 `resume` 子命令不接受 `--profile`。
3. **receipt 记录 `profile`。** 记提交值，省略时为 null，与 `service_tier` 一致。
4. **文档不进 JSON 示例。** `lanes-claude-code.md` 的字段列表写明默认省略、用户要求时才填；示例 JSON 不含这个键，避免照抄示例时默认开启。
5. **runner 不校验 profile 是否存在。** 名字写错由 CLI 报错，receipt 按已有错误类记录。

## 未采纳

- **沿用环境变量 `FABLE_CODEX_PROFILE`。** 它是一台机器的常设配置，与"默认不带、用户显式要求"不符，也违背 ADR 0003 的 runner 不读本机配置。
- **profile 白名单。** profile 名由各机器的 `$CODEX_HOME` 决定，插件无从得知。

## 已知能力上限

- 用户的要求只在当前会话有效；主代理在同一会话的多次派发里漏写 `profile` 时，runner 不补。
- 发布前只用假 CLI 测过参数位置，没有用真实 profile 跑过。

## 复盘条件

- 某台机器需要每次都用同一个 profile，且试用中出现漏写的记录：再考虑本机默认值（例如环境变量），届时修订本 ADR 与 ADR 0003。
- Codex CLI 的 `exec resume` 开始接受 `--profile`，或 `exec` 不再接受它：按新的帮助输出调整位置。
