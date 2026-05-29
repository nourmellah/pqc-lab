#!/usr/bin/env python3
import csv
import sys
from pathlib import Path
from statistics import mean, median


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    k = (len(values) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


def summarize_request_file(path: Path):
    rows = []

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "http_code": row["http_code"],
                    "time_total": float(row["time_total"]),
                    "time_connect": float(row["time_connect"]),
                    "time_appconnect": float(row["time_appconnect"]),
                    "time_starttransfer": float(row["time_starttransfer"]),
                })
            except Exception:
                continue

    if not rows:
        return None

    appconnect = [r["time_appconnect"] for r in rows]
    total = [r["time_total"] for r in rows]
    connect = [r["time_connect"] for r in rows]
    starttransfer = [r["time_starttransfer"] for r in rows]
    success = [r for r in rows if str(r["http_code"]).startswith("2")]

    mode = "baseline" if path.name.startswith("baseline") else "hybrid" if path.name.startswith("hybrid") else "unknown"

    return {
        "type": "request",
        "mode": mode,
        "file": path.name,
        "count": len(rows),
        "success": len(success),
        "success_rate": len(success) / len(rows) * 100,
        "connect_avg": mean(connect),
        "appconnect_avg": mean(appconnect),
        "appconnect_median": median(appconnect),
        "appconnect_p95": percentile(appconnect, 95),
        "starttransfer_avg": mean(starttransfer),
        "total_avg": mean(total),
        "total_median": median(total),
        "total_p95": percentile(total, 95),
        "cpu_avg": "",
        "cpu_median": "",
        "cpu_p95": "",
        "mem_avg_mb": "",
        "mem_avg_percent": "",
        "load_avg": "",
    }


def summarize_resource_file(path: Path):
    rows = []

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "cpu_percent": float(row["cpu_percent"]),
                    "mem_used_mb": float(row["mem_used_mb"]),
                    "mem_percent": float(row["mem_percent"]),
                    "load_1m": float(row["load_1m"]),
                })
            except Exception:
                continue

    if not rows:
        return None

    cpu = [r["cpu_percent"] for r in rows]
    mem_mb = [r["mem_used_mb"] for r in rows]
    mem_pct = [r["mem_percent"] for r in rows]
    load = [r["load_1m"] for r in rows]

    mode = "baseline" if path.name.startswith("baseline") else "hybrid" if path.name.startswith("hybrid") else "unknown"

    return {
        "type": "resource",
        "mode": mode,
        "file": path.name,
        "count": len(rows),
        "success": "",
        "success_rate": "",
        "connect_avg": "",
        "appconnect_avg": "",
        "appconnect_median": "",
        "appconnect_p95": "",
        "starttransfer_avg": "",
        "total_avg": "",
        "total_median": "",
        "total_p95": "",
        "cpu_avg": mean(cpu),
        "cpu_median": median(cpu),
        "cpu_p95": percentile(cpu, 95),
        "mem_avg_mb": mean(mem_mb),
        "mem_avg_percent": mean(mem_pct),
        "load_avg": mean(load),
    }


def fmt(value):
    if value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def main():
    results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/vagrant/results")
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else results_dir / "summary.csv"

    request_files = sorted([
        p for p in results_dir.glob("*.csv")
        if "resources" not in p.name and "summary" not in p.name
    ])

    resource_files = sorted([
        p for p in results_dir.glob("*resources*.csv")
        if "summary" not in p.name
    ])

    summaries = []

    for path in request_files:
        summary = summarize_request_file(path)
        if summary:
            summaries.append(summary)

    for path in resource_files:
        summary = summarize_resource_file(path)
        if summary:
            summaries.append(summary)

    if not summaries:
        print(f"No usable CSV files found in {results_dir}")
        return 1

    columns = [
        "type",
        "mode",
        "file",
        "count",
        "success",
        "success_rate",
        "connect_avg",
        "appconnect_avg",
        "appconnect_median",
        "appconnect_p95",
        "starttransfer_avg",
        "total_avg",
        "total_median",
        "total_p95",
        "cpu_avg",
        "cpu_median",
        "cpu_p95",
        "mem_avg_mb",
        "mem_avg_percent",
        "load_avg",
    ]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in summaries:
            writer.writerow({col: fmt(row.get(col, "")) for col in columns})

    print(",".join(columns))
    for row in summaries:
        print(",".join(fmt(row.get(col, "")) for col in columns))

    print(f"\n[OK] Summary written to: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
