"""Score grader runs for the claim<->own-evidence axis against ground_truth.json.

The grading step is an LLM run and is not reproducible here. The scoring is, so it
lives in code: drop each grader's flagged-id list into runs/*.json and this prints
the numbers that go on the axis's calibration label.

    python3 tests/fixtures/claim_own_evidence/score.py

A run file is {"grader": "A", "model": "sonnet", "flagged": ["S06", ...]}.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def load():
    gt = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    items = gt["items"]
    truth = {k: v["label"] == "positive" for k, v in items.items()}
    hard = {k for k, v in items.items() if v["why"].startswith("HARD")}
    runs = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((HERE / "runs").glob("*.json"))]
    return items, truth, hard, runs


def confusion(truth, flagged):
    fl = set(flagged)
    unknown = fl - truth.keys()
    tp = sum(1 for k, t in truth.items() if t and k in fl)
    fn = sum(1 for k, t in truth.items() if t and k not in fl)
    fp = sum(1 for k, t in truth.items() if not t and k in fl)
    tn = sum(1 for k, t in truth.items() if not t and k not in fl)
    return tp, fn, fp, tn, unknown


def rate(n, d):
    return float("nan") if d == 0 else n / d


def main():
    items, truth, hard, runs = load()
    if not runs:
        print("no runs/*.json yet", file=sys.stderr)
        return 1

    print(f"{len(truth)} items: {sum(truth.values())} positive, "
          f"{len(truth) - sum(truth.values())} negative ({len(hard)} hard negatives)\n")
    print(f"{'grader':<10} {'recall':>8} {'FPR':>8} {'TP':>3} {'FN':>3} {'FP':>3} {'TN':>3}  misses / false alarms")
    for r in runs:
        tp, fn, fp, tn, unknown = confusion(truth, r["flagged"])
        assert not unknown, f"grader {r['grader']} reported unknown ids: {sorted(unknown)}"
        miss = sorted(k for k, t in truth.items() if t and k not in set(r["flagged"]))
        alarm = sorted(k for k, t in truth.items() if not t and k in set(r["flagged"]))
        print(f"{r['grader']:<10} {rate(tp, tp+fn):>8.3f} {rate(fp, fp+tn):>8.3f} "
              f"{tp:>3} {fn:>3} {fp:>3} {tn:>3}  {','.join(miss) or '-'} / {','.join(alarm) or '-'}")

    # majority vote: flagged by >half the graders
    votes = {k: sum(k in set(r["flagged"]) for r in runs) for k in truth}
    maj = [k for k, v in votes.items() if v > len(runs) / 2]
    tp, fn, fp, tn, _ = confusion(truth, maj)
    print(f"\n{'majority':<10} {rate(tp, tp+fn):>8.3f} {rate(fp, fp+tn):>8.3f} {tp:>3} {fn:>3} {fp:>3} {tn:>3}")

    split = [k for k, v in votes.items() if 0 < v < len(runs)]
    if split:
        print("\ndisagreed on: " + ", ".join(f"{k}({votes[k]}/{len(runs)})" for k in sorted(split)))
    print("\nhard negatives, times falsely flagged:")
    for k in sorted(hard):
        print(f"  {k}: {votes[k]}/{len(runs)}  {items[k]['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
