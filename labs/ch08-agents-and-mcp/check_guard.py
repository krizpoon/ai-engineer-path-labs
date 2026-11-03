# Generated from src/content/chapters (chapter 8) by `npm run labs`. Edit the chapter, not this file.
from tools import ToolDenied, safe_path

attempts = ["/etc/hosts", "../.ssh/config", "outside-link",
            ".env", "shop/pricing.py"]
for attempt in attempts:
    try:
        safe_path(attempt)
        print("allowed:", attempt)
    except ToolDenied as e:
        print("refused:", e)
