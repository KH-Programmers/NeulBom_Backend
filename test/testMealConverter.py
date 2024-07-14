import json
from utilities import mealJSONConverter

with open("C:\\goosebumps.json", "r", encoding="utf-8") as f:
    data = json.load(f)

JSON = mealJSONConverter.BatchConvertJSON(data)

with open("meal.json", "w", encoding="utf-8") as f:
    json.dump(JSON, f, ensure_ascii=False, indent="\t")
