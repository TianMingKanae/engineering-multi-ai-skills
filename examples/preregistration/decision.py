"""Synthetic scalar-metric contract evaluator; thresholds come from a sealed contract."""
import argparse
from contextlib import closing
import json
import math
from pathlib import Path
import sqlite3


def read_metrics(path):
    path = Path(path)
    if path.suffix == ".sqlite":
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            rows = db.execute("SELECT name,value FROM metrics").fetchall()
        if len(rows) != len({name for name, _ in rows}):
            raise ValueError("Duplicate metrics")
        return dict(rows)
    if path.suffix in {".h5", ".hdf5"}:
        import h5py
        with h5py.File(path, "r") as f:
            return {name: f["metrics"][name][()].item() for name in f["metrics"]}
    if path.suffix == ".mat":
        from scipy.io import loadmat
        metrics = loadmat(path, simplify_cells=True)["metrics"]
        if not isinstance(metrics, dict):
            raise ValueError("MAT metrics must be a scalar named structure")
        return metrics
    if path.suffix == ".parquet":
        import pyarrow.parquet as pq
        rows = pq.read_table(path, columns=["name", "value"]).to_pylist()
        if len(rows) != len({r["name"] for r in rows}):
            raise ValueError("Duplicate metrics")
        return {r["name"]: r["value"] for r in rows}
    raise ValueError("Unsupported binary schema; write and register a tested adapter")


def decide(metrics, contract):
    rules = contract["minimums"]
    if not rules or set(metrics) != set(rules):
        raise ValueError("Metric schema mismatch")
    for values in (metrics, rules):
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in values.values()):
            raise ValueError("Metrics and thresholds must be finite numbers")
    return all(metrics[name] >= threshold for name, threshold in rules.items())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--result", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps({"passed": decide(read_metrics(args.result), json.loads(args.contract.read_text(encoding="utf-8")))}))
