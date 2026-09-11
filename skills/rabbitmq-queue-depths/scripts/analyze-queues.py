#!/usr/bin/env python3
"""Summarize queue-depth samples: peaks, excursions, time backlogged, and the
queues that ran deep across several appliances.

usage: analyze-queues.py <gateway_id> [<gateway_id> ...] [--dir D] [--threshold N]

Reads depths-<gateway_id>.tsv written by sample-queues.sh. Prints a text report.

Why more than "peak": peak depth and time-spent-backlogged rank appliances
differently, and a single long excursion means something different from many
short ones. Reporting peak alone has produced misleading conclusions.
"""

import argparse
import time
from collections import defaultdict, Counter

# System queues, kept separate because their depth reflects link throughput or
# housekeeping rather than application work, and their scale can be very
# different from application queues.
SYSTEM_QUEUES = {"upload", "status", "http_stats_state"}


def load(gw, d):
    """Return (per_queue{name: {ts: depth}}, totals{ts: n}, nqueues{ts: n}, errors[ts])."""
    per_q = defaultdict(dict)
    totals, nqueues, errors = {}, {}, []
    hdr_at = set()
    with open(f"{d}/depths-{gw}.tsv") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            try:
                ts, name, val = int(parts[0]), parts[1], int(parts[2])
            except ValueError:
                # A leaked rabbitmqctl header row inflates that sample's count.
                if parts[1] == "name":
                    hdr_at.add(int(parts[0]))
                continue
            if name == "__total__":
                totals[ts] = val
            elif name == "__nqueues__":
                nqueues[ts] = val
            elif name == "__error__":
                errors.append(ts)
            elif not name.startswith("__"):
                per_q[name][ts] = val
    for ts in hdr_at:
        if ts in nqueues:
            nqueues[ts] -= 1
    return per_q, totals, nqueues, errors


def excursions(series, thresh, gap=180):
    """Contiguous runs above thresh, split where sampling shows a return to
    baseline for longer than `gap` seconds."""
    pts = sorted((t, v) for t, v in series.items() if v > thresh)
    out, cur = [], []
    for t, v in pts:
        if cur and t - cur[-1][0] > gap:
            out.append(cur)
            cur = []
        cur.append((t, v))
    if cur:
        out.append(cur)
    return out


def hm(t):
    return time.strftime("%H:%M", time.localtime(t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gateways", nargs="+")
    ap.add_argument("--dir", default=".", help="directory holding depths-*.tsv")
    ap.add_argument("--threshold", type=int, default=100,
                    help="depth above which an appliance counts as backlogged")
    a = ap.parse_args()

    loaded = []
    for gw in a.gateways:
        try:
            per_q, totals, nq, errs = load(gw, a.dir)
        except FileNotFoundError:
            print(f"{gw}: no depths-{gw}.tsv in {a.dir}")
            continue
        if not totals:
            print(f"{gw}: no samples")
            continue
        loaded.append((gw, per_q, totals, nq, errs))

    if not loaded:
        return

    print("=" * 72)
    print(f"{'gateway':12s} {'samples':>7s} {'peak':>7s} {'final':>6s} "
          f"{'queues':>7s} {'min>thr':>8s} {'exc':>4s} {'errs':>5s}")
    print("=" * 72)
    for gw, per_q, totals, nq, errs in loaded:
        st = sorted(totals)
        ex = excursions(totals, a.threshold)
        mins = sum(e[-1][0] - e[0][0] for e in ex) / 60
        print(f"{gw:12s} {len(st):7d} {max(totals.values()):7d} "
              f"{totals[st[-1]]:6d} {nq.get(st[-1], 0):7d} {mins:8.0f} "
              f"{len(ex):4d} {len(errs):5d}")

    for gw, per_q, totals, nq, errs in loaded:
        st = sorted(totals)
        ex = excursions(totals, a.threshold)
        print(f"\n--- {gw} "
              f"({hm(st[0])}-{hm(st[-1])}, {(st[-1]-st[0])/3600:.2f} h) ---")
        if not ex:
            print(f"  never exceeded {a.threshold}; peak {max(totals.values())}")
        for i, e in enumerate(ex, 1):
            print(f"  excursion {i}: {hm(e[0][0])}-{hm(e[-1][0])} "
                  f"peak={max(v for _, v in e)} "
                  f"dur={(e[-1][0]-e[0][0])/60:.0f}min")
        # a run ending near its peak has not drained - the strongest "still broken" signal
        peak, final = max(totals.values()), totals[st[-1]]
        if peak > a.threshold and final > 0.8 * peak:
            print(f"  ** ended at {final} against a peak of {peak}: NOT draining")

        deep = sorted(((max(d.values()), n) for n, d in per_q.items()), reverse=True)
        print("  deepest queues:")
        for pk, n in deep[:8]:
            tag = " (system)" if n in SYSTEM_QUEUES else ""
            print(f"    {n:24s} {pk:6d}{tag}")

    if len(loaded) > 1:
        print("\n" + "=" * 72)
        print("queues that held messages on EVERY appliance (application queues only)")
        print("=" * 72)
        qpeak = defaultdict(dict)
        for gw, per_q, _, _, _ in loaded:
            for q, d in per_q.items():
                if q not in SYSTEM_QUEUES:
                    qpeak[q][gw] = max(d.values())
        names = [gw for gw, *_ in loaded]
        common = [(q, pk) for q, pk in qpeak.items() if len(pk) == len(loaded)]
        common.sort(key=lambda kv: -max(kv[1].values()))
        if not common:
            print("  none")
        else:
            print(f"  {'queue':24s}" + "".join(f"{n:>11s}" for n in names))
            for q, pk in common[:15]:
                print(f"  {q:24s}" + "".join(f"{pk.get(n,0):11d}" for n in names))
            print(f"\n  {len(common)} of {len(qpeak)} application queues appeared on all "
                  f"{len(loaded)}.")
            spread = Counter(len(pk) for pk in qpeak.values())
            print("  spread: " + ", ".join(f"{spread[k]} on {k}"
                                           for k in sorted(spread, reverse=True)))
        print("\n  A queue deep on several appliances independently is a property of the")
        print("  application. Deep on one is a property of that appliance. Resolve ids to")
        print("  names with: cogniac --tenant <tenant> app get <app_id>")


if __name__ == "__main__":
    main()
