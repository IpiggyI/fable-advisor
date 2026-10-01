"""Mutation check for the `verification output log` case in tests/test_runner_contract.py.

Usage, from the repository root: python3 .scratch/verification-defaults/tools/mutation_output_log.py
Runs the case on the real runners (it must pass), then on a temporary copy of each runner
with its `log.write(chunk);` line removed (it must fail). If a runner change renames or
reformats that line, the count assertion fails; update the pattern.
"""
import shutil, sys, tempfile, traceback
from pathlib import Path
sys.path.insert(0, "tests")
import test_runner_contract as t

def run(label):
    try:
        t.case_verification_output_log()
        print(f"{label}: PASS")
        return True
    except AssertionError as error:
        frame = traceback.extract_tb(error.__traceback__)[-1]
        print(f"{label}: FAIL at line {frame.lineno}: {frame.line}")
        return False

real = t.REPO_ROOT
assert run("unmutated"), "case must pass on the real runners"
for name in ("run-codex.mjs", "run-grok.mjs"):
    with tempfile.TemporaryDirectory() as root:
        scripts = Path(root) / "plugin" / "scripts"
        scripts.mkdir(parents=True)
        for other in ("run-codex.mjs", "run-grok.mjs"):
            shutil.copy2(real / "plugin" / "scripts" / other, scripts / other)
        source = (scripts / name).read_text()
        assert source.count("    log.write(chunk);\n") == 1
        (scripts / name).write_text(source.replace("    log.write(chunk);\n", "", 1))
        t.REPO_ROOT = Path(root)
        try:
            assert not run(f"mutated {name} (log.write removed)"), f"case must fail with {name} mutated"
        finally:
            t.REPO_ROOT = real
print("mutation check complete")
