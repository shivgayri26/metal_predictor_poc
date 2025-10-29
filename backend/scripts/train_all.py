# scripts/train_all.py — add project root to sys.path so "app" package can be imported
import sys
from pathlib import Path
# Add project root (parent of scripts) to sys.path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.predictor import train_model
import sqlite3

def get_metals():
    conn = sqlite3.connect("data/metal_prices.db")
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT metal FROM metal_prices")
    metals = [row[0] for row in cur.fetchall()]
    conn.close()
    return metals

if __name__ == "__main__":
    metals = get_metals()
    if not metals:
        print("No metals found in DB (check data/metal_prices.db)")
    for m in metals:
        print("Training", m)
        try:
            path = train_model(m)
            print("  -> trained saved to", path)
        except Exception as e:
            print("  -> skipped", m, ":", e)
