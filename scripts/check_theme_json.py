import json

with open(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Corporate_Theme.json", "r", encoding="utf-8") as f:
    theme = json.load(f)

print("Theme name:", theme.get("name"))
print("Data colors:", theme.get("dataColors"))
print("Background:", theme.get("background"))
print("Foreground:", theme.get("foreground"))
print("Good:", theme.get("good"))
print("Neutral:", theme.get("neutral"))
print("Bad:", theme.get("bad"))
print("VisualStyles keys:", list(theme.get("visualStyles", {}).keys()))
