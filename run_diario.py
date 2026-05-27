"""
Ciclo completo diario Hedgeye:
  scraper -> actualiza HTML -> git push -> Vercel actualizado

Correr desde Task Scheduler a las 13:00 en lugar de hedgeye_scraper.py directamente.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hedgeye_listener import handle_hedgeye_trigger

print("=== Hedgeye run diario ===")
handle_hedgeye_trigger()
print("=== Fin ===")
