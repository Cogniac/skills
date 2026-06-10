# Field-tested API gotchas

Traps that cost real debugging time in agent sessions. Each entry: symptom →
cause → correct pattern. All verified against production (2026-06).

## 1. Subject media recency: use the raw endpoint, not `media_associations()`

**Symptom:** you need "newest media on subject X" (pipeline liveness, staleness
checks) or per-media `domain_unit`/`sequence_ix`, and the SDK results are missing
those fields.

**Cause:** `CogniacSubject.media_associations()` returns association records
whose media stanza carries only `media_id` — no `domain_unit`, no
`sequence_ix`, no timestamps you can rely on for recency.

**Pattern:** hit the endpoint directly and page via `paging.next`:

```python
url, params = cc.url_prefix + f'/1/subjects/{uid}/media', {'limit': 100, 'reverse': True}
while url:
    r = cc.session.get(url, params=params); r.raise_for_status()
    d = r.json()
    for rec in d['data']:
        m = rec.get('media', rec)          # media_id, domain_unit, sequence_ix,
                                           # media_timestamp, created_at ...
        sj = rec.get('subject', {})        # probability, app_data, ...
    url, params = d.get('paging', {}).get('next'), None   # cursor URL is complete
```

For a single recency probe, `{'limit': 1, 'reverse': True}` is one cheap call.

## 2. `app_data` may be a JSON *string*

The association record's `subject.app_data` (per-media application output) is
sometimes a serialized string, not a dict:

```python
ad = rec['subject']['app_data']
if isinstance(ad, str):
    ad = json.loads(ad)
```

Also guard empty frames — list-valued fields can contain zero-entry frames that
break `np.array(...).mean(0)`-style code.

## 3. `EdgeFlow.status()` is a non-terminating stream

**Symptom:** `list(ef.status())` or iterating it in a loop hangs forever.

**Cause:** it's a live status *stream* (generator), not a snapshot.

**Pattern:** consume a bounded number of records with a timeout, or use the REST
endpoints / read-only kubectl access (`references/edgeflow-kubectl-access.md`)
for point-in-time state. Never `list()` it.

## 4. Integration apps: frozen on-appliance workflows

Integration apps (`type: integration`) deploy via the `/1/builds` endpoint
(`name=<app_id>`, `src_code`, `base_image`, `requirements`,
`program_language`) and run on EdgeFlow as part of a **frozen deployment
workflow snapshot**. Consequences:

- **Cloud-side `active` toggles generally do NOT reach the running on-appliance
  process.** Toggling may be a no-op against the actual process — while risking
  a deployment re-sync of the whole appliance. Restarts are an appliance-side
  action by the EdgeFlow owners.
- **`input_queue_count` is always 0 for EdgeFlow apps** — processing is local;
  the cloud queue number carries no liveness information.
- **The only reliable liveness signal is media recency on the app's output
  subjects** (gotcha #1), compared against its input subjects: live input +
  dead output = that app's process is dead; an identically-configured sibling
  producing on the same appliance proves the appliance is healthy.

## 5. `CogniacMedia.download()` takes a file object

`m.download(filep=f)` — a `filep` file handle, not a filename:

```python
with open(path, 'wb') as f:
    m.download(filep=f)
```

## 6. Deletion ordering

Apps must be deactivated before deletion (`app.active = False`, save, then
`.delete()`), and subjects can only be deleted after the apps referencing them
are gone. Violating the order returns unhelpful 4xx errors.

## 7. Domain-unit hygiene

A low rate of media arrives with a unix-timestamp string as `domain_unit`
(e.g. `"1780365545.69"`) instead of the site's `<prefix>_<number>` convention.
When grouping by domain unit, filter to the expected pattern
(`du.startswith('3278_')`-style) or these strays corrupt per-unit aggregation.

## 8. Multi-line subject sweeps: cache per-subject lookups

Tenant-wide audits (hundreds of apps) reference the same subjects repeatedly.
Collect the unique subject set first and query each once — naive per-app loops
multiply API calls ~5×, and the public API rate-limits (429, no SDK retry).
