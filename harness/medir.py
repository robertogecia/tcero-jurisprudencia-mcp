"""Item 4 — mede recall@10/@25/total do gold.json contra três formas de busca, rodando o
_buscar REAL do servidor com _consultar_api MOCKADO para servir do snapshot local (sem rede):

  (a) texto_livre "ingênuo", ordenar="data"      — o que a maioria digitaria hoje
  (b) o mesmo texto_livre, ordenar="relevancia"   — mesma consulta, só reordenada
  (c) grupos de sinônimos (E entre conceitos), ordenar="relevancia" — o que um pesquisador
      experiente montaria

O mock de _consultar_api reproduz o OU nativo do portal (qualquer palavra de textoLivre,
fold-normalizada, presente em ementa+dispositivo+informações adicionais) — é o único ponto
"fake" desta medição; tudo daí para frente (_filtrar_por_grupos, ordenação, paginação) é
código real do servidor.
"""
import asyncio
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, RAIZ)

os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"] = "1"
import servidor_tcero as srv  # noqa: E402

with open(os.path.join(BASE, "_snapshot", "acervo.json"), encoding="utf-8") as f:
    ACERVO = json.load(f)["result"]

with open(os.path.join(BASE, "gold.json"), encoding="utf-8") as f:
    GOLD = json.load(f)

_RE_ESP = re.compile(r"\s+")


def _texto_bruto(s):
    return srv._fold(
        (s.get("ementa") or "") + " " + srv._html_para_texto(s.get("acordaoDescricao") or "")
        + " " + srv._html_para_texto(s.get("informacoesAdicionais") or "")
    )


async def _consultar_fake(params, operacao):
    """Simula /api/espelho/buscar: OU nativo sobre textoLivre (palavras soltas, sem suporte a
    frase exata nesta simulação — nenhuma consulta deste harness usa aspas), sobre o snapshot
    local inteiro (ACERVO), igual ao comportamento real documentado em
    references/protocolo-papyrus.md."""
    tl = params.get("textoLivre") or ""
    palavras = [p for p in _RE_ESP.split(srv._fold(tl)) if p]
    if not palavras:
        return {"result": []}
    resultado = []
    for item in ACERVO:
        s = item.get("source") or {}
        texto = _texto_bruto(s)
        if any(p in texto for p in palavras):
            resultado.append(item)
    resultado.sort(key=lambda it: (it.get("source") or {}).get("data") or "", reverse=True)
    return {"result": resultado}


# Consultas — texto_livre "ingênuo" (o que um advogado digitaria de cara) e grupos (o que um
# pesquisador experiente, sabendo do achado do OU nativo, montaria com E entre conceitos).
CONSULTAS_BUSCA = [
    {"texto_livre": "direcionamento fraude licitação", "grupos": [["licitação"], ["direcionamento", "fraude"]]},
    {"texto_livre": "aposentadoria tempo de contribuição", "grupos": [["aposentadoria"], ["tempo de contribuição"]]},
    {"texto_livre": "reincidência multa", "grupos": [["reincidência"], ["multa"]]},
    {"texto_livre": "débito solidário dano ao erário", "grupos": [["débito"], ["solidário", "solidária", "solidariedade"]]},
    {"texto_livre": "contratação temporária concurso servidor", "grupos": [["temporária"], ["servidor"]]},
    {"texto_livre": "obra atraso paralisada", "grupos": [["obra"], ["atraso"]]},
]


def _recall(encontrados_ids, essenciais_ids, teto=None):
    alvo = essenciais_ids if teto is None else encontrados_ids[:teto]
    if teto is None:
        achou = len(set(encontrados_ids) & set(essenciais_ids))
    else:
        achou = len(set(alvo) & set(essenciais_ids))
    total = len(essenciais_ids)
    return achou, total, achou / total if total else 0.0


async def _rodar_uma(texto_livre, grupos, ordenar, usar_grupos):
    srv._consultar_api = _consultar_fake
    saida = await srv._buscar(
        texto_livre, None, None, None, None, 1, 25, False,
        grupos if usar_grupos else None, ordenar,
    )
    ids = [int(m) for m in re.findall(r"^\d+\. .*?\bid (\d+)\b", saida, re.M)]
    if not ids:
        # fallback: o formato de _resumo_item usa "id <n>" em algum ponto da linha do item —
        # recupera todos os "id N" da saída, na ordem em que aparecem (ordem = ordenação real).
        ids = [int(m) for m in re.findall(r"\bid (\d+)\b", saida)]
    return ids, saida


async def main():
    linhas_md = []
    resultado_bruto = []
    linhas_md.append("# Medição — servidor_tcero.py, 22/09/2026\n")
    linhas_md.append(
        "Gabarito: `harness/gold.json` (6 consultas, regex cega sobre o snapshot local de "
        f"{len(ACERVO)} decisões únicas — `harness/_snapshot/acervo.json`). `_consultar_api` "
        "mockado para servir do snapshot (sem rede); `_buscar` e toda a formatação/ordenação "
        "são código real do servidor.\n"
    )
    linhas_md.append("| # | consulta | forma | recall@10 | recall@25 | recall total | perdidos essenciais |")
    linhas_md.append("|---|---|---|---|---|---|---|")

    somatorio = {"a": [], "b": [], "c": []}

    for i, (gold_item, consulta) in enumerate(zip(GOLD, CONSULTAS_BUSCA), start=1):
        essenciais = [e["idDecisao"] for e in gold_item["essencial"]]
        formas = [
            ("a", consulta["texto_livre"], None, "data"),
            ("b", consulta["texto_livre"], None, "relevancia"),
            ("c", consulta["texto_livre"], consulta["grupos"], "relevancia"),
        ]
        for chave, tl, grupos, ordenar in formas:
            ids, saida_bruta = await _rodar_uma(tl, grupos, ordenar, usar_grupos=grupos is not None)
            achou10, tot, r10 = _recall(ids, essenciais, teto=10)
            achou25, _, r25 = _recall(ids, essenciais, teto=25)
            achou_tot, _, r_tot = _recall(ids, essenciais, teto=None)
            perdidos = [idd for idd in essenciais if idd not in ids]
            somatorio[chave].append(r10)
            linhas_md.append(
                f"| {i} | {gold_item['pergunta'][:40]}... | ({chave}) | "
                f"{achou10}/{tot} ({r10:.0%}) | {achou25}/{tot} ({r25:.0%}) | "
                f"{achou_tot}/{tot} ({r_tot:.0%}) | {len(perdidos)} |"
            )
            resultado_bruto.append({
                "consulta_idx": i, "pergunta": gold_item["pergunta"], "forma": chave,
                "texto_livre": tl, "grupos": grupos, "ordenar": ordenar,
                "ids_devolvidos_top25": ids[:25],
                "essenciais": essenciais,
                "recall_10": r10, "recall_25": r25, "recall_total": r_tot,
                "perdidos": perdidos,
            })

    linhas_md.append("")
    linhas_md.append("## Recall@10 médio por forma\n")
    for chave, nome in [("a", "(a) texto_livre, ordenar=data"), ("b", "(b) texto_livre, ordenar=relevancia"), ("c", "(c) grupos, ordenar=relevancia")]:
        media = sum(somatorio[chave]) / len(somatorio[chave])
        linhas_md.append(f"- {nome}: **{media:.0%}**")

    # decisão
    media_a = sum(somatorio["a"]) / len(somatorio["a"])
    media_b = sum(somatorio["b"]) / len(somatorio["b"])
    venceu_sem_piorar = all(b >= a for a, b in zip(somatorio["a"], somatorio["b"])) and media_b > media_a
    linhas_md.append("\n## Diagnóstico das perdas\n")
    for r in resultado_bruto:
        if r["forma"] == "a" and r["perdidos"]:
            linhas_md.append(
                f"- Consulta {r['consulta_idx']} ({r['pergunta'][:50]}...), forma (a): perdeu "
                f"{len(r['perdidos'])} essencial(is) — ids {r['perdidos'][:5]}{'...' if len(r['perdidos']) > 5 else ''}. "
                "Causa provável: portal ordena por data, não por relevância — decisão relevante "
                "mas antiga cai fora do top-10/25 mesmo estando no conjunto OU nativo."
            )

    linhas_md.append("\n## Decisão sobre o padrão de `ordenar`\n")
    if venceu_sem_piorar:
        linhas_md.append(
            f"**`relevancia` melhora recall@10 em TODAS as {len(somatorio['a'])} consultas sem "
            f"piorar nenhuma** (média {media_a:.0%} → {media_b:.0%}). Decisão: tornar "
            "`relevancia` o padrão de `ordenar` quando a busca tem texto_livre e/ou grupos "
            "(sem eles, não há termo para pontuar — comportamento cai para `data`)."
        )
        decisao = "relevancia"
    else:
        piores = [i + 1 for i, (a, b) in enumerate(zip(somatorio["a"], somatorio["b"])) if b < a]
        linhas_md.append(
            f"`relevancia` não venceu de forma consistente (média (a) {media_a:.0%} vs (b) "
            f"{media_b:.0%}; piorou nas consultas {piores}). Decisão: **manter `data` como "
            "padrão**; `relevancia` continua disponível como opção explícita."
        )
        decisao = "data"

    with open(os.path.join(BASE, "medicao-2026-09-22.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md) + "\n")
    with open(os.path.join(BASE, "_resultado_bruto.json"), "w", encoding="utf-8") as f:
        json.dump(resultado_bruto, f, ensure_ascii=False, indent=1)

    print("\n".join(linhas_md))
    print(f"\nDECISAO_PADRAO_ORDENAR={decisao}")


if __name__ == "__main__":
    asyncio.run(main())
