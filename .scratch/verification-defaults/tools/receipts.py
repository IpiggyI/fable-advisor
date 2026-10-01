"""列出一个仓库在某一时刻之后的 runner 回执，逐条给出回执里的检查。

用法：python3 receipts.py <仓库路径> <起始时刻，UTC，例如 2026-10-02T08:00> [全量命令的正则]
每张回执一行：开始与结束时刻、模式、模型、结论（error_class）、回执文件名前 10 位。
其下每条检查一行：退出码；`FULL` 表示命令匹配第三个参数；`log=null` 表示 output_log 为空，
即日志写入失败或被放弃，原因在 runner 的诊断里；6.1.0 之前的回执没有 output_log 字段，不标。
最后一行汇总回执数（其中实现回执数）、检查条数、全量条数和 output_log 为空的条数；
ADR 0029 的第一条复盘条件按实现派发计数，报告模式的回执不算。
"""
import glob
import json
import os
import re
import sys

root, since = sys.argv[1], sys.argv[2]
full = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
receipts = []
for path in glob.glob(os.path.join(root, ".fable-advisor", "receipts", "*.json")):
    with open(path, encoding="utf-8") as handle:
        receipt = json.load(handle)
    if (receipt.get("started_at") or "") >= since:
        receipts.append((receipt["started_at"], os.path.basename(path)[:10], receipt))
checks = fulls = nulls = 0
for started, name, receipt in sorted(receipts):
    print(f"{started[:19]} 至 {(receipt.get('finished_at') or '')[11:19]}  {receipt.get('mode')}  "
          f"{receipt.get('model_used') or receipt.get('model')}  {receipt.get('error_class')}  {name}")
    for entry in receipt.get("verification") or []:
        checks += 1
        is_full = bool(full and full.search(entry["command"]))
        is_null = "output_log" in entry and entry["output_log"] is None
        fulls += is_full
        nulls += is_null
        flags = " ".join(flag for flag, on in (("FULL", is_full), ("log=null", is_null)) if on)
        print(f"    exit {entry['exit_code']}  {flags:13s} {entry['command'][:100]}")
implements = sum(receipt.get("mode") == "implement" for _, _, receipt in receipts)
print(f"回执 {len(receipts)} 张（实现 {implements} 张），检查 {checks} 条，全量 {fulls} 条，output_log 为空 {nulls} 条")
