import json

recs = {}
for line in open('ongoing_work/prismatic_sweep_log.jsonl'):
    r = json.loads(line)
    if r.get('slug') == 'duoprism_4_10':
        recs[r.get('rng')] = r

for rng in sorted(recs):
    r = recs[rng]
    us = r.get('unique_shapes')
    rh = r.get('raw_hits')
    ad = r.get('after_dir_dedup')
    sf = r.get('snap_failed', '?')
    print(f'--- rng={rng}: {us} emits, raw_hits={rh}, after_dir_dedup={ad}, snap_failed={sf} ---')
    for e in r.get('emitted', []):
        if e.get('status') == 'emitted':
            k = e.get('kernel')
            print(f'  {e.get("basename"):20s} kernel={k}')
