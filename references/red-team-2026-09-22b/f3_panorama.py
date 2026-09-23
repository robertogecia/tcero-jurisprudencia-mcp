"""Frente 3: panorama com campos estranhos, caixa de relator, pré/pós-grupos, página 2."""
from _comum import *
r = [{"source": {"orgaoJulgador": ["Pleno"], "data": "20x6-01-01", "sigla": "", "natureza": None, "relator": "JOSÉ EULER POTYGUARA PEREIRA DE MELLO"}},
     {"source": {"orgaoJulgador": "Pleno", "data": "2026", "relator": "José Euler Potyguara Pereira de Mello"}},
     {"source": {"orgaoJulgador": "Pleno", "data": None, "relator": " JOSÉ EULER POTYGUARA PEREIRA DE MELLO "}},
     {}]
try:
    print("\n".join(srv._bloco_panorama(r)))
except Exception as e:
    print("EXCEÇÃO:", type(e).__name__, e)
# relatores reais no snapshot com mais de uma grafia
from collections import defaultdict
g = defaultdict(set)
for it in ACERVO:
    rel = (it["source"].get("relator") or "")
    g[srv._fold(" ".join(rel.split()))].add(rel)
dup = {k: v for k, v in g.items() if len(v) > 1}
print("relatores com >1 grafia no snapshot:", len(dup), list(dup.values())[:3])
tipos = defaultdict(set)
for it in ACERVO:
    for c in ("orgaoJulgador","data","sigla","natureza","relator"):
        tipos[c].add(type(it["source"].get(c)).__name__)
print("tipos dos campos no snapshot:", dict(tipos))
# pré/pós grupos
async def m():
    instalar_mock()
    out = await srv._buscar(None, None, None, None, None, 1, 10, False, [["reincidência"], ["multa"]])
    cab = out.splitlines()[0]; pan = [l for l in out.splitlines() if "Panorama" in l]
    print("cabeçalho:", cab[:160]); print("panorama:", pan)
rodar(m())
