import json

with open('dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test/LogiTrack_Analytics_Compatibility_Test.Report/report.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

for s in r['sections']:
    print(f"\n=== Page: '{s['displayName']}' (name: {s['name']}) ===")
    for idx, vc in enumerate(s['visualContainers']):
        cfg = json.loads(vc['config'])
        sv = cfg.get('singleVisual', {})
        vtype = sv.get('visualType')
        proj = sv.get('projections')
        proto = sv.get('prototypeQuery')
        has_query = bool(vc.get('query'))
        has_dataTransforms = bool(vc.get('dataTransforms'))
        title = sv.get('objects', {}).get('general', [{}])[0].get('properties', {}).get('title', {}).get('expr', {}).get('Literal', {}).get('Value')
        print(f"  [{idx:02d}] {vtype:12s} | title={str(title):45s} | proj={bool(proj)} | proto={bool(proto)} | top_query={has_query} | dt={has_dataTransforms}")
