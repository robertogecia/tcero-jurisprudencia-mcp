"""Frente 1 (i-B): pool cego (estilo TREC) — top-10 de (a),(b),(c) por consulta, embaralhado
com semente fixa, sem rótulo de forma. Grava _pool.json (ids por forma) e imprime ementas para
anotação manual; a anotação vai em anotacao.json (id -> 0/1 por consulta)."""
from _comum import *
import random
async def main():
    pool = {}
    for i,(g,c) in enumerate(zip(GOLD,CONSULTAS),1):
        formas = {}
        for k,gr,o in [("a",None,"data"),("b",None,"relevancia"),("c",c["grupos"],"relevancia")]:
            formas[k] = (await ids_todos(c["texto_livre"], gr, o))[:10]
        u = sorted(set(sum(formas.values(), [])))
        random.Random(1000+i).shuffle(u)
        pool[i] = {"formas": formas, "ordem_anotacao": u}
        print(f"\n######## Q{i}: {g['pergunta']}")
        for idd in u:
            s = POR_ID[idd]
            em = srv._RE_ESPACO.sub(" ", s.get("ementa") or "")[:420]
            print(f"[{idd}] {em}")
    json.dump(pool, open("_pool.json","w"), indent=1)
rodar(main())
