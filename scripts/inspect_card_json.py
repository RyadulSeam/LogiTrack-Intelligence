import json

with open('dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test/LogiTrack_Analytics_Compatibility_Test.Report/report.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

c0 = r['sections'][0]['visualContainers'][1]
print("Card VC keys:", list(c0.keys()))
print("Card config parsed:", json.dumps(json.loads(c0['config']), indent=2))
