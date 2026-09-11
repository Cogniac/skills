# Sizing the sampling window

Queue depth is only interpretable against the workload that caused it. An
appliance sampled between jobs looks perfectly healthy, and a short window will
tell you so with false confidence.

This is not hypothetical. In one investigation a 20-minute window put an
appliance's peak at 60. The same appliance reached 626 over a longer window -
the short sample simply landed between units of work. Any conclusion drawn from
the first window would have been wrong.

## Measure the cadence, don't guess it

Deployments that process discrete units of work usually post a status subsystem
tracking them. Where one exists, query it over the last 24 hours and measure:

- **arrival rate per appliance** - how often a unit of work starts
- **duration** - report the median and the p90, because these distributions are
  heavily skewed and the mean misleads
- **overlap** - whether units run concurrently, which decides whether "N units"
  means N intervals or fewer

Then size the window to cover several units *per appliance*, and say so in the
report. "Five hours, because each appliance sees about one unit an hour" is
auditable. "Five hours" is not.

Guessing costs real time in both directions. In one case the measured arrival
rate was 1.6 per hour per appliance where the estimate had been 1.0 - so a
window planned for five hours reached its coverage target in three and a half,
and running the full five would have wasted 90 minutes.

## Querying a workload subsystem

```
GET /1/gateways/<gw>/status/<subsystem>?reverse=true&limit=1000&start=<epoch>&end=<epoch>
```

Auth: `GET /1/token?tenant_id=<tenant>` with `Authorization: Key $COG_API_KEY`
returns an access token; use it as `Authorization: Bearer <token>`.

Behaviour worth knowing before you write the loop:

- Default sort is **ascending**; pass `reverse=true` for newest first.
- `limit` caps at 1000, but DynamoDB's 1 MB page ceiling usually binds first.
- `paging.next` is emitted **even on a short page**, so "follow next until
  absent" never terminates. Page by time instead: request the newest page in
  `[start, end]`, move `end` down to the oldest timestamp seen, repeat, and stop
  when a page yields nothing new. The boundary row repeats and is deduped.
- The subsystem filter is exact-match. A trailing `*` returns zero rows rather
  than an error.
- Payloads over 65536 bytes are replaced by the string `"<too large>"`.

## Interpreting coverage afterwards

Report units of work **per appliance**, not just a fleet total. Work is commonly
load-balanced, so a fleet total double-counts anything split across appliances.
Compute both and state the difference: "22 appliance-unit pairs, 21 distinct
units, 1 split across two appliances" tells a reader something that "22" does
not.

Also record which appliance handled how much. An appliance that queued nothing
while handling a full share of work is a more interesting finding than one that
queued nothing while idle, and only the workload figures distinguish them.

Note that event-driven subsystems stop posting once a unit goes inactive, so
units straddling the window edges are undercounted. Say so rather than
presenting the count as exact.
