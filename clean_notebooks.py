import os
import json

folder = "notebook"

def remove_secrets(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if (
                    "gsk_" in v
                    or "AIza" in v
                    or "sk-" in v
                    or "hf_" in v
                ):
                    obj[k] = "[REMOVED]"
            else:
                remove_secrets(v)

    elif isinstance(obj, list):
        for item in obj:
            remove_secrets(item)


for root, dirs, files in os.walk(folder):
    for file in files:
        if file.endswith(".ipynb"):
            path = os.path.join(root, file)
            print(f"Cleaning: {path}")

            try:
                with open(path, "r", encoding="utf-8") as f:
                    nb = json.load(f)

                remove_secrets(nb)

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(nb, f, indent=2, ensure_ascii=False)

                print(f"✔ Cleaned secrets in: {file}")

            except Exception as e:
                print(f"Error reading {file}: {e}")
