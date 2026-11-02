"""Lance le site NETO et les deux bots Discord en local."""
import os, sys, signal, subprocess, time
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
procs = []

def stop_all(*_):
    for p in procs:
        if p.poll() is None:
            p.terminate()
    for p in procs:
        try: p.wait(timeout=5)
        except Exception: p.kill()
    raise SystemExit(0)

signal.signal(signal.SIGINT, stop_all)
signal.signal(signal.SIGTERM, stop_all)

if not os.getenv("NETO_BOT_TOKEN") or not os.getenv("GESTION_BOT_TOKEN"):
    print("Configure d'abord les deux tokens dans le fichier .env.")
    raise SystemExit(1)
if not os.getenv("GESTION_CLIENT_ID"):
    print("Ajoute GESTION_CLIENT_ID dans le fichier .env.")
    raise SystemExit(1)

procs.append(subprocess.Popen([sys.executable, str(ROOT / "bots" / "index.py")], cwd=ROOT))
procs.append(subprocess.Popen(["node", str(ROOT / "bots" / "gestion.js")], cwd=ROOT))
try:
    from app import app
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False, use_reloader=False)
finally:
    stop_all()
