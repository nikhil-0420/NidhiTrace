"""
Quick smoke test — hits every key endpoint once, prints pass/fail.
Run this while `uvicorn app.main:app --reload` is running in another terminal.
"""
import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def check(path, label):
    try:
        with urllib.request.urlopen(BASE + path, timeout=15) as r:
            data = json.loads(r.read())
            print(f"✅ {label}: {path}")
            print(f"   {json.dumps(data)[:200]}")
            return True
    except Exception as e:
        print(f"❌ {label}: {path}")
        print(f"   ERROR: {e}")
        return False

results = []
results.append(check("/health", "Health check"))
results.append(check("/api/anomalies/summary/breakdown", "Breakdown"))
results.append(check("/api/anomalies/?signal=high_severity&limit=3", "High severity list"))
results.append(check("/api/anomalies/?signal=delay&limit=3", "Delay list"))
results.append(check("/api/anomalies/?signal=amount&limit=3", "Amount list"))
results.append(check("/api/anomalies/?signal=mp_drift&limit=3", "MP-drift list"))
results.append(check("/api/works/?limit=3", "Works list"))

print(f"\n{sum(results)}/{len(results)} passed")