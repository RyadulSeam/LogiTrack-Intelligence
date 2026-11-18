import json

with open('dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test/LogiTrack_Analytics_Compatibility_Test.SemanticModel/model.bim', 'r', encoding='utf-8') as f:
    d = json.load(f)

measures = []
for t in d['model']['tables']:
    for m in t.get('measures', []):
        measures.append((m['name'], m.get('displayFolder'), m.get('expression'), m.get('formatString')))

print(f"Total measures found: {len(measures)}")
for idx, (name, folder, expr, fmt) in enumerate(sorted(measures, key=lambda x: (x[1] or '', x[0]))):
    expr_single = " ".join(expr) if isinstance(expr, list) else str(expr)
    print(f"[{idx+1:02d}] [{folder}] {name:38s} | fmt={fmt} | expr={expr_single[:60]}...")
