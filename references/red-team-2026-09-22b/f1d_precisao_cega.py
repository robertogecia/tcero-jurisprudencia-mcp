"""Frente 1 (i-B): precisão@10 de cada forma contra a anotação cega do pool, e recall@10 contra
o gold.json regex, lado a lado. Também: quantos relevantes anotados o gold regex NÃO contém."""
import json
from _comum import GOLD
pool = json.load(open("_pool.json")); an = json.load(open("anotacao.json"))
med = {"a":[], "b":[], "c":[]}; medg = {"a":[], "b":[], "c":[]}
for q in map(str, range(1,7)):
    rel = set(an[q]["relevantes"]); gold = {e["idDecisao"] for e in GOLD[int(q)-1]["essencial"]}
    linha = []
    for k in "abc":
        top = pool[q]["formas"][k]
        p = len(rel & set(top))/10; r = len(gold & set(top))/10
        med[k].append(p); medg[k].append(r); linha.append(f"({k}) P@10 cega {p:.0%} | R@10 gold {r:.0%}")
    print(f"Q{q}: " + " || ".join(linha) + f" || relevantes anotados fora do gold regex: {len(rel-gold)}/{len(rel)}")
for k in "abc": print(k, f"média P@10 cega {sum(med[k])/6:.0%} | média R@10 gold regex {sum(medg[k])/6:.0%}")
