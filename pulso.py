"""Pulso en vivo del Trading Floor. Corre en GitHub Actions cada 15 min (aunque la PC de Romano esté apagada).

Lee las posiciones de la demo (datos/estado.json, lo sube publicar.py cada mañana), busca precios actuales
y escribe vivo.json, que la página lee cada minuto. No compra ni vende nada.
"""
import json, datetime as dt
from zoneinfo import ZoneInfo
import requests, yfinance as yf

CAPITAL = 100_000.0
est = json.load(open("datos/estado.json", encoding="utf-8"))
precios = {}
for a in est["unidades"]:
    try:
        if a.endswith("USDT"):
            r = requests.get("https://data-api.binance.vision/api/v3/ticker/price", params={"symbol": a}, timeout=20)
            precios[a] = float(r.json()["price"])
        else:
            precios[a] = float(yf.Ticker(a).fast_info["last_price"])
    except Exception as ex:
        print("sin precio", a, ex)

if len(precios) == len(est["unidades"]):
    valor = est["efectivo"] + sum(u * precios[a] for a, u in est["unidades"].items())
    vivo = dict(hora=dt.datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="minutes"),
                valor=round(valor, 2), ganancia_pct=round((valor / CAPITAL - 1) * 100, 2),
                precios={a: round(p, 4) for a, p in precios.items()})
    json.dump(vivo, open("vivo.json", "w", encoding="utf-8"), indent=1)
    print("vivo:", vivo["hora"], vivo["valor"])
