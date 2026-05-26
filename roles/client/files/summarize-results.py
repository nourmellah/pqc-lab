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


def summarize_file(path: Path):
    rows = []
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    'http_code': row['http_code'],
                    'time_total': float(row['time_total']),
                    'time_connect': float(row['time_connect']),
                    'time_appconnect': float(row['time_appconnect']),
                    'time_starttransfer': float(row['time_starttransfer']),
                })
            except Exception:
                continue
    if not rows:
        return None
    ok = [r for r in rows if r['http_code'].startswith('2')]
    app = [r['time_appconnect'] for r in rows]
    total = [r['time_total'] for r in rows]
    return {
        'file': path.name,
        'count': len(rows),
        'success': len(ok),
        'success_rate': len(ok) / len(rows) * 100,
        'appconnect_avg': mean(app),
        'appconnect_median': median(app),
        'appconnect_p95': percentile(app, 95),
        'total_avg': mean(total),
        'total_median': median(total),
        'total_p95': percentile(total, 95),
    }


def main():
    results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/opt/pqc-lab/results')
    files = sorted(results_dir.glob('*.csv'))
    if not files:
        print(f'No CSV files found in {results_dir}')
        return 1

    summaries = [summarize_file(p) for p in files]
    summaries = [s for s in summaries if s]

    print('file,count,success,success_rate,appconnect_avg,appconnect_median,appconnect_p95,total_avg,total_median,total_p95')
    for s in summaries:
        print(','.join([
            s['file'],
            str(s['count']),
            str(s['success']),
            f"{s['success_rate']:.2f}",
            f"{s['appconnect_avg']:.6f}",
            f"{s['appconnect_median']:.6f}",
            f"{s['appconnect_p95']:.6f}",
            f"{s['total_avg']:.6f}",
            f"{s['total_median']:.6f}",
            f"{s['total_p95']:.6f}",
        ]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
