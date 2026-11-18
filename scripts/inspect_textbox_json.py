import json

with open('dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test/LogiTrack_Analytics_Compatibility_Test.Report/report.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

t0 = r['sections'][0]['visualContainers'][0]
print("Textbox VC:", json.dumps(json.loads(t0['config']), indent=2))
