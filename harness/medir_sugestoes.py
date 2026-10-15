"""Mede `sugerir_termos_tcero` (v1.6.0) contra o snapshot, sem rede. Reaproveita o mock de OU nativo de
`medir.py` e o gold/anotação já existentes. O gold é CIRCULAR (regex sobre os mesmos campos): o recall do
gold não consegue subir ao adicionar sinônimos em OU, só cair se algo der errado; por isso o número que
importa é o da anotação independente (references/red-team-2026-09-22b/anotacao.json, 1 anotador).

Para cada uma das 6 consultas de `medir.py`:
  1. sugestões calculadas sobre a consulta INGÊNUA (texto_livre), com o fundo montado SEM as decisões
     que casaram (para o fundo não conter as próprias casadas que geram a frequência);
  2. configurações de `grupos`: A (o que o pesquisador montou) · B3/B5 (A + top-3/top-5 sugestões como
     alternativas em OU no grupo mais estreito) · C3 (A + top-3 como grupo novo, E — estreita);
  3. métricas: tamanho do conjunto, recall total do gold, recall@10 do gold, P@10 contra o gold, relevantes
     ANOTADOS no top-10 e no conjunto.
Grava harness/_resultado_sugestoes.json e imprime o quadro.
"""
import asyncio
import json
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, RAIZ)
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"] = "1"
import servidor_tcero as srv  # noqa: E402
import medir  # noqa: E402  (mock do OU nativo e as consultas)

ACERVO = medir.ACERVO
GOLD = medir.GOLD
ANOT = json.load(open(os.path.join(RAIZ, "references", "red-team-2026-09-22b", "anotacao.json"), encoding="utf-8"))

srv._consultar_api = medir._consultar_fake  # type: ignore

# df por documento (uma vez) para montar fundos "sem" um conjunto
DOC_TOK = {}
DOC_PAR = {}
DF = Counter()
DF2 = Counter()
for it in ACERVO:
    s = it["source"]
    ws = srv._tokens_vocab(srv._texto_vocab_da_decisao(s))
    toks = set(ws)
    pars = {f"{a} {b}" for a, b in zip(ws, ws[1:]) if a != b}
    DOC_TOK[s["idDecisao"]] = toks
    DOC_PAR[s["idDecisao"]] = pars
    DF.update(toks)
    DF2.update(pars)


def fundo_sem(ids):
    df = Counter(DF)
    df2 = Counter(DF2)
    for i in ids:
        for w in DOC_TOK.get(i, ()):
            df[w] -= 1
        for p in DOC_PAR.get(i, ()):
            df2[p] -= 1
    return {"N": len(ACERVO) - len(set(ids)), "df": {w: c for w, c in df.items() if c >= 3},
            "df2": {p: c for p, c in df2.items() if c >= 5}}


def ids_gold(q):
    return [x["idDecisao"] for x in q["essencial"]], [x["idDecisao"] for x in q.get("desejavel", [])]


async def conjunto(grupos):
    r = await srv._consulta_filtrada(None, grupos, None, None, "medicao")
    termos = srv._termos_da_consulta(None, r["grupos_ok"])
    ordem = srv._ordenar_por_relevancia(r["todos"], termos)
    return [it["source"]["idDecisao"] for it in ordem]


def metricas(ids, ess, des, anot):
    top10 = ids[:10]
    gold = set(ess) | set(des)
    return {
        "n": len(ids),
        "recall_total_gold": round(len(gold & set(ids)) / len(gold), 3) if gold else None,
        "recall10_essencial": round(len(set(ess) & set(top10)) / len(ess), 3) if ess else None,
        "p10_gold": round(len(gold & set(top10)) / 10, 3),
        "anot_top10": len(set(anot) & set(top10)),
        "anot_total": len(set(anot) & set(ids)),
        "anot_n": len(anot),
    }


async def main():
    saida = []
    for qi, (q, cons) in enumerate(zip(GOLD, medir.CONSULTAS_BUSCA), start=1):
        ess, des = ids_gold(q)
        anot = ANOT[str(qi)]["relevantes"]
        # sugestões sobre a consulta ingênua, com fundo sem a resposta inteira dessa consulta
        r = await srv._consulta_filtrada(cons["texto_livre"], None, None, None, "medicao")
        todos_portal = r["brutos"]
        ids_resp = [it["source"]["idDecisao"] for it in todos_portal]
        unidades = srv._unidades_da_consulta(cons["texto_livre"], [])
        casadas, restante, k = srv._separar_casadas(todos_portal, unidades)
        termos_usuario = [t for u in unidades for t in u]
        nomes = set()
        for it in todos_portal:
            nomes.update(srv._RE_PALAVRA_VOCAB.findall(srv._fold(it["source"].get("relator") or "")))
        res = srv._sugerir_vocabulario(casadas, restante, termos_usuario, fundo_sem([it['source']['idDecisao'] for it in casadas]), nomes)
        res_sem_fundo = srv._sugerir_vocabulario(casadas, restante, termos_usuario, None, nomes)
        sug = [w for w, _ in res.get("termos", [])] + [p for p, _ in res.get("pares", [])]
        sug_uni = [w for w, _ in res.get("termos", [])]
        gA = cons["grupos"]
        # grupo mais estreito = o com menos decisões no núcleo
        tam = []
        for g in gA:
            rr = await srv._consulta_filtrada(None, [g], None, None, "medicao")
            tam.append(len(rr["todos"]))
        alvo = min(range(len(gA)), key=lambda i: tam[i])
        def com(extra):
            g2 = [list(g) for g in gA]
            g2[alvo] = g2[alvo] + extra
            return g2
        configs = {
            "A_base": gA,
            "B3_ou_top3": com(sug_uni[:3]),
            "B5_ou_top5": com(sug_uni[:5]),
            "C3_E_top3": gA + [sug_uni[:3]],
        }
        linha = {"consulta": qi, "pergunta": q["pergunta"], "casadas": len(casadas), "restante": len(restante), "k": k,
                 "sugestoes": sug, "sugestoes_sem_fundo": [w for w, _ in res_sem_fundo.get("termos", [])] + [p for p, _ in res_sem_fundo.get("pares", [])],
                 "grupo_alvo": alvo, "metricas": {}}
        for nome, g in configs.items():
            ids = await conjunto(g)
            linha["metricas"][nome] = metricas(ids, ess, des, anot)
            linha["metricas"][nome]["grupos"] = g
        saida.append(linha)
    json.dump(saida, open(os.path.join(BASE, "_resultado_sugestoes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for l in saida:
        print(f"\n#{l['consulta']} {l['pergunta']}\n  casadas={l['casadas']} restante={l['restante']} k={l['k']}  n_sugestões={len(l['sugestoes'])}")
        print("  sugestões:", "; ".join(l["sugestoes"]))
        for nome, m in l["metricas"].items():
            print(f"  {nome:11s} n={m['n']:5d} recall_gold={m['recall_total_gold']} r@10_ess={m['recall10_essencial']} p@10_gold={m['p10_gold']} anot_top10={m['anot_top10']}/{min(10,m['anot_n'])} anot_total={m['anot_total']}/{m['anot_n']}")

asyncio.run(main())
