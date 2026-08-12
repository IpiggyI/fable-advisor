# 03 — README Cursor 使用节 + 版本 3.9.0

**What to build:** 新用户按 README 即可在 Cursor 里跑通架构师模式（无 CLI 要求、车道映射、effort 档位差异一句话），插件版本递增使 `claude plugin update` 后两个 harness 同时吃到新版。

**Blocked by:** 01 — orchestration skill 双 harness 改写；02 — agents 文件双 harness 加固。

**Status:** ready-for-agent

- [x] `README.md` 新增 Cursor 使用小节（"Using it in Cursor"，位于 Use it 与 Commitment boundaries 之间）；经济学叙述不改写
- [x] `README.md` Upgrading 段追加 v3.9 一句并链接 ADR 0010
- [x] `.claude-plugin/plugin.json` 版本 3.8.0 → 3.9.0
- [x] 通读验证：README 的 Cursor 小节与 SKILL.md、ADR 0010 的表述一致，无平行真相源

## Comments

2026-08-12 — 已实现。范围外顺手修一处既有漂移并披露：`.claude-plugin/marketplace.json` 的版本停在 3.7.0（3.8.0 发布时未同步），本次一并对齐到 3.9.0——marketplace 版本驱动 `claude plugin marketplace update` 的更新发现，留旧值会让 Cursor/Claude Code 两侧都吃不到新版。
