#!/usr/bin/env python3
"""Render queue-depth samples for one or more appliances as a single HTML page.

usage:
  report-queues.py <gw> [<gw> ...] [--dir D] [--out report.html]
                   [--name gw=LABEL]...      friendly label per gateway
                   [--workload gw=N]...      units of work handled, for context
                   [--apps apps.json]        {"dsp_xxx": "App name", ...}
                   [--title "..."] [--standalone]

--standalone emits a full <!DOCTYPE html> document (for a web host). Without it
the output is a fragment suitable for hosts that supply their own head/body.

Depth without workload is not interpretable, so pass --workload where you know
it. Peak and time-backlogged are both reported because they rank appliances
differently.
"""

import argparse
import html
import json
import time
from collections import defaultdict, Counter

SYSTEM_QUEUES = {"upload", "status", "http_stats_state"}

# Categorical slots validated for adjacent-pair colour-vision separation,
# light and dark. Assign in order; never cycle.
SERIES = [
    ("#2a78d6", "#3987e5"), ("#eb6834", "#d95926"), ("#1baf7a", "#199e70"),
    ("#eda100", "#c98500"), ("#e87ba4", "#d55181"), ("#008300", "#008300"),
    ("#4a3aa7", "#9085e9"), ("#e34948", "#e66767"),
]
TABLE_CAP = 18


def load(gw, d):
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


def severity(peak, thresh):
    if peak <= thresh / 5:
        return "quiet", "Draining"
    if peak <= thresh:
        return "elev", "Elevated"
    return "spike", "Spike"


def chart(series, t0, t1, width=880, height=300, pad_l=52, pad_b=38,
          pad_t=22, pad_r=20, fill=False, mark_peak=False):
    """Lines with an emphasized endpoint and an optional labelled peak. A dot on
    every sample reads as noise once there are hundreds of them."""
    span = max(t1 - t0, 1)
    vmax = max((max(d.values()) for _, d, _ in series if d), default=0)
    vmax = max(vmax, 1)
    step = max(1, -(-vmax // 4))
    ticks = list(range(0, vmax + step, step))
    top = ticks[-1]
    iw, ih = width - pad_l - pad_r, height - pad_t - pad_b
    x_of = lambda t: pad_l + (t - t0) / span * iw
    y_of = lambda v: pad_t + ih - (v / top) * ih

    o = [f'<svg viewBox="0 0 {width} {height}" class="chart" role="img" '
         f'preserveAspectRatio="xMidYMid meet">']
    for tk in ticks:
        y = y_of(tk)
        o.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width-pad_r}" y2="{y:.1f}" '
                 f'class="{"grid base" if tk == 0 else "grid"}"/>')
        o.append(f'<text x="{pad_l-10}" y="{y+4:.1f}" class="ylab">{tk}</text>')
    o.append(f'<text x="{pad_l-10}" y="{pad_t-9}" class="axname" text-anchor="end">msgs</text>')
    for i in range(5):
        t = t0 + span * i / 4
        o.append(f'<text x="{x_of(t):.1f}" y="{height-16}" class="xlab">'
                 f'{time.strftime("%H:%M", time.localtime(t))}</text>')
    o.append(f'<text x="{pad_l+iw/2:.1f}" y="{height-2}" class="axname">local time</text>')

    for _label, d, slot in series:
        if not d:
            continue
        pts = sorted(d.items())
        c = f"var(--s{slot})"
        line = " L".join(f"{x_of(t):.1f},{y_of(v):.1f}" for t, v in pts)
        if fill:
            o.append(f'<path d="M{line} L{x_of(pts[-1][0]):.1f},{y_of(0):.1f} '
                     f'L{x_of(pts[0][0]):.1f},{y_of(0):.1f} Z" fill="{c}" '
                     f'fill-opacity="0.10" stroke="none"/>')
        o.append(f'<path d="M{line}" fill="none" stroke="{c}" stroke-width="2" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
        et, ev = pts[-1]
        o.append(f'<circle cx="{x_of(et):.1f}" cy="{y_of(ev):.1f}" r="4" fill="{c}" '
                 f'stroke="var(--surface)" stroke-width="2"/>')
        if mark_peak:
            pt, pv = max(pts, key=lambda p: p[1])
            if pv > 0:
                px, py = x_of(pt), y_of(pv)
                o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{c}" '
                         f'stroke="var(--surface)" stroke-width="2"/>')
                anchor, lx = "middle", px
                if px < pad_l + 22:
                    anchor, lx = "start", pad_l
                elif px > width - pad_r - 22:
                    anchor, lx = "end", width - pad_r
                o.append(f'<text x="{lx:.1f}" y="{max(py-11, 12):.1f}" class="peaklab" '
                         f'text-anchor="{anchor}">{pv}</text>')
    o.append("</svg>")
    return "\n".join(o)


CSS = """
:root {
  color-scheme: light;
  --ground:#f4f6f9; --surface:#fdfdfe; --border:#dce1ea; --border-strong:#c3cbd8;
  --ink:#10141b; --ink-2:#4a5462; --muted:#767f8e; --grid:#e4e8ef;
  --good:#1baf7a; --warn:#b97d00; --crit:#cf3b3a;
  --seq1:#cde2fb; --seq2:#9ec5f4; --seq3:#3987e5; --seq4:#1c5cab;
__LIGHT__}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  color-scheme: dark;
  --ground:#0e1116; --surface:#161b22; --border:#2a313b; --border-strong:#3b4450;
  --ink:#f2f5f9; --ink-2:#b3bcc9; --muted:#818b99; --grid:#242b34;
  --good:#199e70; --warn:#c98500; --crit:#e66767;
  --seq1:#184f95; --seq2:#1c5cab; --seq3:#256abf; --seq4:#3987e5;
__DARK__} }
:root[data-theme="dark"] {
  color-scheme: dark;
  --ground:#0e1116; --surface:#161b22; --border:#2a313b; --border-strong:#3b4450;
  --ink:#f2f5f9; --ink-2:#b3bcc9; --muted:#818b99; --grid:#242b34;
  --good:#199e70; --warn:#c98500; --crit:#e66767;
  --seq1:#184f95; --seq2:#1c5cab; --seq3:#256abf; --seq4:#3987e5;
__DARK__}
*,*::before,*::after { box-sizing:border-box; }
body { margin:0; background:var(--ground); color:var(--ink);
  font:400 14px/1.55 "IBM Plex Sans",ui-sans-serif,-apple-system,"Segoe UI",sans-serif; }
.wrap { max-width:940px; margin:0 auto; padding:30px 20px 56px;
  display:flex; flex-direction:column; gap:22px; }
h1 { margin:0 0 4px; font-size:21px; font-weight:600; letter-spacing:-0.015em;
  text-wrap:balance; }
.meta { font:500 11.5px/1.5 "IBM Plex Mono",ui-monospace,Menlo,monospace;
  color:var(--muted); text-transform:uppercase; letter-spacing:0.07em; margin:0; }
.verdict { background:var(--surface); border:1px solid var(--border-strong);
  border-radius:3px; padding:15px 17px; font-size:13.5px; color:var(--ink-2); }
.verdict b { color:var(--ink); font-weight:600; }
.tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; }
.tile { background:var(--surface); border:1px solid var(--border);
  border-top:2px solid var(--border-strong); border-radius:2px; padding:13px 15px 11px; }
.tile.sev-elev { border-top-color:var(--warn); }
.tile.sev-spike { border-top-color:var(--crit); }
.tile-h { display:flex; align-items:center; gap:7px; flex-wrap:wrap; }
.cfname { font-weight:600; font-size:13px; }
.sw { width:9px; height:9px; border-radius:2px; flex:none; display:inline-block; }
.big { font:600 32px/1.1 "IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-variant-numeric:tabular-nums; letter-spacing:-0.02em; margin-top:7px; }
.klab { font-size:11px; color:var(--muted); }
.kv { display:grid; grid-template-columns:auto 1fr; gap:1px 10px; margin:11px 0 0;
  padding:9px 0 0; border-top:1px solid var(--border);
  font:400 11.5px/1.6 "IBM Plex Mono",ui-monospace,Menlo,monospace; }
.kv dt { color:var(--muted); }
.kv dd { margin:0; text-align:right; font-variant-numeric:tabular-nums; font-weight:500; }
.chip { font:500 10px/1 "IBM Plex Mono",ui-monospace,Menlo,monospace;
  text-transform:uppercase; letter-spacing:0.08em; padding:4px 6px; border-radius:2px;
  border:1px solid currentColor; white-space:nowrap; }
.chip-quiet { color:var(--good); } .chip-elev { color:var(--warn); }
.chip-spike { color:var(--crit); }
.panel, section.detail { background:var(--surface); border:1px solid var(--border);
  border-radius:2px; padding:16px 18px 10px; }
h2,h3 { margin:0 0 3px; font-size:13.5px; font-weight:600;
  display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.dim { color:var(--muted); font-weight:400;
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; font-size:11.5px; }
.note { color:var(--ink-2); font-size:12.5px; margin:0 0 12px; max-width:66ch; }
.note.tight { margin:9px 0 4px; font-size:11.5px; color:var(--muted); }
.note b { color:var(--ink); font-weight:600; }
.chart { width:100%; height:auto; display:block; min-width:520px; }
.chartwrap, .tablewrap { overflow-x:auto; }
.grid { stroke:var(--grid); stroke-width:1; }
.grid.base { stroke:var(--border-strong); }
.ylab,.xlab,.axname,.peaklab { font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; }
.ylab { fill:var(--muted); font-size:10.5px; text-anchor:end; }
.xlab { fill:var(--muted); font-size:10.5px; text-anchor:middle; }
.axname { fill:var(--muted); font-size:10px; text-anchor:middle;
  text-transform:uppercase; letter-spacing:0.08em; }
.peaklab { fill:var(--ink); font-size:11px; font-weight:600; }
.legend { display:flex; flex-wrap:wrap; gap:5px 13px; margin:2px 0 10px; }
.lg { display:inline-flex; align-items:center; gap:6px; font-size:11.5px;
  color:var(--ink-2); font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; }
.lg i { width:9px; height:9px; border-radius:2px; flex:none; }
table { border-collapse:collapse; width:100%; min-width:430px;
  font:400 12px/1.5 "IBM Plex Mono",ui-monospace,Menlo,monospace; }
th { text-align:left; font-weight:500; color:var(--muted); font-size:10px;
  text-transform:uppercase; letter-spacing:0.07em; padding:0 10px 6px 0;
  border-bottom:1px solid var(--border-strong); white-space:nowrap; }
td { padding:5px 10px 5px 0; border-bottom:1px solid var(--grid);
  font-variant-numeric:tabular-nums; }
td.muted { color:var(--muted); }
th:not(:first-child), td:not(:first-child) { text-align:right; width:74px; }
table.matrix td.app { color:var(--ink-2); font-family:"IBM Plex Sans",sans-serif;
  font-size:11.5px; text-align:left; width:auto; max-width:230px; }
table.matrix th:nth-child(-n+2) { text-align:left; }
.lv0 { color:var(--muted); }
.lv1 { background:var(--seq1); } .lv2 { background:var(--seq2); }
.lv3 { background:var(--seq3); color:#fff; } .lv4 { background:var(--seq4); color:#fff; }
footer { color:var(--muted); font-size:11.5px; line-height:1.75;
  border-top:1px solid var(--border); padding-top:14px; max-width:76ch; }
code { font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; font-size:0.94em;
  color:var(--ink-2); }
"""


def kvargs(pairs):
    out = {}
    for p in pairs or []:
        k, _, v = p.partition("=")
        out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gateways", nargs="+")
    ap.add_argument("--dir", default=".")
    ap.add_argument("--out", default="report.html")
    ap.add_argument("--name", action="append", help="gw=LABEL")
    ap.add_argument("--workload", action="append", help="gw=N units of work handled")
    ap.add_argument("--apps", help="JSON map of queue name -> application name")
    ap.add_argument("--title", default="RabbitMQ queue depths")
    ap.add_argument("--threshold", type=int, default=100)
    ap.add_argument("--standalone", action="store_true")
    a = ap.parse_args()

    labels, work = kvargs(a.name), kvargs(a.workload)
    apps = json.load(open(a.apps)) if a.apps else {}

    cfs = []
    for gw in a.gateways:
        try:
            per_q, totals, nq, errs = load(gw, a.dir)
        except FileNotFoundError:
            print(f"warning: no depths-{gw}.tsv in {a.dir}, skipping")
            continue
        if not totals:
            print(f"warning: no samples for {gw}, skipping")
            continue
        st = sorted(totals)
        peak = max(totals.values())
        sev, sev_label = severity(peak, a.threshold)
        ex = excursions(totals, a.threshold)
        cfs.append(dict(
            gw=gw, name=labels.get(gw, gw), slot=len(cfs) + 1, per_q=per_q,
            totals=totals, stamps=st, nq=nq.get(st[-1], 0), errors=errs,
            peak=peak, final=totals[st[-1]], sev=sev, sev_label=sev_label,
            dur=st[-1] - st[0], work=work.get(gw),
            peaks=sorted(((max(d.values()), n) for n, d in per_q.items()), reverse=True),
            ex=ex, mins=sum(e[-1][0] - e[0][0] for e in ex) / 60,
        ))
    if not cfs:
        print("no data")
        return

    t0 = min(c["stamps"][0] for c in cfs)
    t1 = max(c["stamps"][-1] for c in cfs)
    names = [c["name"] for c in cfs]

    by_peak = sorted(cfs, key=lambda c: -c["peak"])
    by_time = sorted(cfs, key=lambda c: -c["mins"])
    tallest, longest = by_peak[0], by_time[0]
    stuck = [c for c in cfs if c["final"] > max(a.threshold, c["peak"] * 0.8)]

    if tallest["peak"] <= a.threshold:
        verdict = (f"<b>Nothing is backing up.</b> The worst peak was "
                   f"{tallest['peak']} messages on {tallest['name']}, below the "
                   f"{a.threshold}-message threshold for this report.")
    elif stuck:
        verdict = (f"<b>{', '.join(c['name'] for c in stuck)} ended the window still "
                   f"backed up.</b> A depth that stops falling is the signal worth "
                   f"chasing; every other excursion here drained on its own.")
    else:
        verdict = (f"<b>Every queue drained. Nothing is stuck.</b> {tallest['name']} "
                   f"reached the highest depth ({tallest['peak']}), but "
                   f"{longest['name']} spent the most time backed up "
                   f"({longest['mins']:.0f} min over {a.threshold}, against "
                   f"{tallest['mins']:.0f} min). Peak height and time-backlogged rank "
                   f"these differently, so neither alone describes the fleet.")

    legend = "".join(f'<span class="lg"><i style="background:var(--s{c["slot"]})"></i>'
                     f'{html.escape(c["name"])}</span>' for c in cfs)
    tiles = "".join(f"""<div class="tile sev-{c['sev']}">
  <div class="tile-h"><i class="sw" style="background:var(--s{c['slot']})"></i>
  <span class="cfname">{html.escape(c['name'])}</span>
  <span class="chip chip-{c['sev']}">{c['sev_label']}</span></div>
  <div class="big">{c['peak']}</div><div class="klab">peak messages queued</div>
  <dl class="kv">
    {f"<dt>workload</dt><dd>{html.escape(str(c['work']))}</dd>" if c['work'] else ""}
    <dt>final</dt><dd>{c['final']}</dd>
    <dt>min&nbsp;over&nbsp;{a.threshold}</dt><dd>{c['mins']:.0f}</dd>
    <dt>queues</dt><dd>{c['nq']}</dd>
    <dt>ever&nbsp;used</dt><dd>{len(c['per_q'])}</dd>
    <dt>samples</dt><dd>{len(c['stamps'])}</dd>
  </dl></div>""" for c in cfs)

    # cross-appliance matrix of application queues present everywhere
    common_panel = ""
    if len(cfs) > 1:
        qpeak = defaultdict(dict)
        for c in cfs:
            for q, d in c["per_q"].items():
                if q not in SYSTEM_QUEUES:
                    qpeak[q][c["name"]] = max(d.values())
        common = sorted(((q, pk) for q, pk in qpeak.items() if len(pk) == len(cfs)),
                        key=lambda kv: -max(kv[1].values()))
        if common:
            gmax = max(max(pk.values()) for _, pk in common) or 1
            lvl = lambda v: "lv0" if v == 0 else "lv" + str(min(4, 1 + int(3 * v / gmax)))
            crows = "".join(
                f"<tr><td class='q'>{html.escape(q)}</td>"
                f"<td class='app'>{html.escape(apps.get(q, ''))}</td>"
                + "".join(f"<td class='{lvl(pk.get(n,0))}'>{pk.get(n,0)}</td>"
                          for n in names) + "</tr>"
                for q, pk in common[:14])
            spread = Counter(len(pk) for pk in qpeak.values())
            common_panel = f"""
<div class="panel">
  <h3>Application queues that ran deep on every appliance</h3>
  <p class="note">Peak depth per appliance for the {len(common)} application queues
  that held a message on all {len(cfs)}, deepest first. System queues
  ({', '.join(sorted(SYSTEM_QUEUES))}) are excluded: their depth reflects link
  throughput and housekeeping rather than application work, and their scale can bury
  everything charted beside them. Spread across the fleet:
  {', '.join(f'{spread[k]} on {k}' for k in sorted(spread, reverse=True))} appliance(s).
  A queue deep on several appliances independently is a property of the application;
  deep on one is a property of that appliance.</p>
  <div class="tablewrap"><table class="matrix"><thead><tr><th>Queue</th>
  <th>Application</th>{''.join(f'<th>{html.escape(n)}</th>' for n in names)}</tr></thead>
  <tbody>{crows}</tbody></table></div>
</div>"""

    details = []
    for c in cfs:
        top = c["peaks"][:8]
        tser = [(n, c["per_q"][n], i + 1) for i, (_, n) in enumerate(top)]
        qleg = "".join(f'<span class="lg"><i style="background:var(--s{i+1})"></i>'
                       f'{html.escape(n)}</span>' for i, (_, n) in enumerate(top))
        shown = c["peaks"][:TABLE_CAP]
        rows = "".join(
            f"<tr><td class='q'>{html.escape(n)}</td>"
            f"<td class='app'>{html.escape(apps.get(n,''))}</td><td>{pk}</td>"
            f"<td>{c['per_q'][n].get(c['stamps'][-1],0)}</td>"
            f"<td class='muted'>{len(c['per_q'][n])}</td></tr>" for pk, n in shown)
        more = len(c["peaks"]) - len(shown)
        table = (f"<table class='matrix'><thead><tr><th>Queue</th><th>Application</th>"
                 f"<th>Peak</th><th>Final</th><th>Seen</th></tr></thead>"
                 f"<tbody>{rows}</tbody></table>"
                 + (f"<p class='note tight'>and {more} more that held "
                    f"1&ndash;{shown[-1][0]}</p>" if more > 0 else "")
                 ) if c["peaks"] else "<p class='note'>Every queue stayed empty.</p>"
        exlist = "".join(
            f"<li>{time.strftime('%H:%M', time.localtime(e[0][0]))}"
            f"&ndash;{time.strftime('%H:%M', time.localtime(e[-1][0]))}, peak "
            f"{max(v for _,v in e)}, {(e[-1][0]-e[0][0])/60:.0f} min</li>"
            for e in c["ex"])
        details.append(f"""
<section class="detail">
  <h2><i class="sw" style="background:var(--s{c['slot']})"></i>
  {html.escape(c['name'])} <span class="dim">{html.escape(c['gw'])}</span>
  <span class="chip chip-{c['sev']}">{c['sev_label']}</span></h2>
  <p class="note">{c['nq']} queues on the broker; <b>{len(c['per_q'])}</b> carried a
  message during the {c['dur']//60}m{c['dur']%60:02d}s window. Peak {c['peak']},
  final {c['final']}.
  {f"<br>Excursions over {a.threshold}:<ul>{exlist}</ul>" if exlist else ""}</p>
  {('<div class="legend">'+qleg+'</div>'+chart(tser, c['stamps'][0], c['stamps'][-1],
      height=230, mark_peak=True)) if tser else ''}
  <div class="tablewrap">{table}</div>
</section>""")

    css = (CSS.replace("__LIGHT__", "".join(f"  --s{i+1}:{l};\n"
                                            for i, (l, _) in enumerate(SERIES)))
              .replace("__DARK__", "".join(f"  --s{i+1}:{d};\n"
                                           for i, (_, d) in enumerate(SERIES))))
    total_samples = sum(len(c["stamps"]) for c in cfs)
    total_errs = sum(len(c["errors"]) for c in cfs)
    head = f"""<title>{html.escape(a.title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{css}</style>"""
    body = f"""<div class="wrap">
<header>
  <h1>{html.escape(a.title)}</h1>
  <p class="meta">{time.strftime('%d %b %Y %H:%M', time.localtime(t0))}&ndash;{time.strftime('%H:%M', time.localtime(t1))} local
  &middot; {len(cfs)} appliance(s) &middot; {total_samples} samples
  &middot; {total_errs} failed</p>
</header>
<div class="verdict">{verdict}</div>
<div class="tiles">{tiles}</div>
<div class="panel">
  <h3>Total messages queued, per appliance</h3>
  <p class="note">Every queue on each broker, summed. Runs may start at different
  moments, so the axis is wall-clock: a line that stops is a run that ended, not a
  broker that emptied. Peak is labelled; the dot marks where sampling stopped.</p>
  <div class="legend">{legend}</div>
  <div class="chartwrap">{chart([(c['name'], c['totals'], c['slot']) for c in cfs],
      t0, t1, height=310, fill=True, mark_peak=True)}</div>
</div>
{common_panel}
{''.join(details)}
<footer>
Measured with <code>rabbitmqctl list_queues name messages</code> via
<code>kubectl exec</code> against each appliance's broker pod. Read-only throughout:
no <code>DELETE /api/reset</code> was issued, so the broker's stats database is intact.
&ldquo;Seen&rdquo; counts samples in which a queue held at least one message.
<br><br>
Sampling cannot resolve anything shorter than its interval: a queue that fills and
empties between two samples is invisible here. Consumer counts are deliberately not
reported &mdash; appliance services poll with <code>basic_get</code> rather than holding a
subscription, so a healthy draining queue shows zero consumers and the number means
nothing.
</footer>
</div>"""

    if a.standalone:
        doc = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
               + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    else:
        # host supplies the skeleton; emit head content followed by the page
        doc = head + "\n" + body
    with open(a.out, "w") as f:
        f.write(doc)
    print(f"wrote {a.out} ({len(doc)} bytes)")
    for c in cfs:
        print(f"  {c['name']:12s} {c['gw']:10s} samples={len(c['stamps']):4d} "
              f"peak={c['peak']:5d} final={c['final']:5d} min_over_"
              f"{a.threshold}={c['mins']:.0f} errs={len(c['errors'])}")


if __name__ == "__main__":
    main()
