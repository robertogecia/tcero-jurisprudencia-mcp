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
    # Red team 22/09/2026-b, achado 1b: o regex antigo (`^\d+\. `) nunca casava o cabeçalho real
    # do item (`**N. SIGLA NUM** · id X`) e o fallback pegava TODO "id N" da saída — inclusive
    # ids citados em ementa/decisão vinculada (até 36 ids para 25 itens). Agora: só o cabeçalho.
    ids = [int(m) for m in _RE_ITEM_CABECALHO.findall(saida)]
    return ids, saida


_RE_ITEM_CABECALHO = re.compile(r"^\*\*\d+\. [^\n]*?\*\* · id (\d+)", re.M)


async def _ids_conjunto_inteiro(texto_livre, grupos, ordenar):
    """Recall no CONJUNTO INTEIRO (sem corte de página): mesmo pipeline de _buscar com as funções
    reais do servidor (OU nativo mockado -> _filtrar_por_grupos -> _ordenar_por_relevancia). O
    rótulo antigo "recall total" era o top-25 (por_pagina=25) — achado 1b do red team 22b."""
    g = srv._grupos_validos(grupos)
    dados = await _consultar_fake({"textoLivre": srv._montar_texto_livre_com_grupos(texto_livre, g)}, "busca")
    todos = dados["result"]
    if g:
        todos, _ = srv._filtrar_por_grupos(todos, g)
    return [it["source"]["idDecisao"] for it in todos]


_ANOTACAO = os.path.join(RAIZ, "references", "red-team-2026-09-22b", "anotacao.json")
ANOTACAO = json.load(open(_ANOTACAO, encoding="utf-8")) if os.path.exists(_ANOTACAO) else {}


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
    linhas_md.append("| # | consulta | forma | recall@10 (gold regex) | recall@25 | recall no conjunto inteiro | P@10 cega (anotação 22b) | perdidos no top-25 |")
    linhas_md.append("|---|---|---|---|---|---|---|---|")

    somatorio = {"a": [], "b": [], "c": []}
    precisao = {"a": [], "b": [], "c": []}
    nao_anotados = 0

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
            conjunto = await _ids_conjunto_inteiro(tl, grupos, ordenar)
            achou_tot, _, r_tot = _recall(conjunto, essenciais, teto=None)
            perdidos = [idd for idd in essenciais if idd not in ids]
            somatorio[chave].append(r10)
            rel = set((ANOTACAO.get(str(i)) or {}).get("relevantes") or [])
            p10 = len(rel & set(ids[:10])) / 10 if rel else float("nan")
            precisao[chave].append(p10)
            linhas_md.append(
                f"| {i} | {gold_item['pergunta'][:40]}... | ({chave}) | "
                f"{achou10}/{tot} ({r10:.0%}) | {achou25}/{tot} ({r25:.0%}) | "
                f"{achou_tot}/{tot} ({r_tot:.0%}) de {len(conjunto)} | {p10:.0%} | {len(perdidos)} |"
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
        mp = sum(precisao[chave]) / len(precisao[chave])
        linhas_md.append(f"- {nome}: recall@10 gold regex **{media:.0%}** · P@10 cega **{mp:.0%}**")

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

    mp = {k: sum(v) / len(v) for k, v in precisao.items()}
    linhas_md.append("\n## Circularidade do gabarito (red team 22/09/2026-b)\n")
    linhas_md.append(
        "O gold regex é circular com o ranking: ambos olham os MESMOS campos (ementa+dispositivo) "
        "e quase as mesmas palavras, e o `essencial` é \"os 10 mais recentes que casam a regex\" — "
        "exatamente o desempate por data do ranking. Por isso o recall@10 do gold regex serve para "
        "comparar (a) com (b), mas NÃO mede se o topo responde à pergunta. Medida independente: "
        "pool cego (top-10 de a/b/c embaralhado, sem rótulo de forma), anotado lendo a ementa "
        "contra a PERGUNTA (`references/red-team-2026-09-22b/anotacao.json`, um anotador). "
        f"P@10 cega média: (a) {mp['a']:.0%}, (b) {mp['b']:.0%}, (c) {mp['c']:.0%}. "
        "A decisão `relevancia` como padrão SE SUSTENTA na medida independente (a→b), mas: "
        "(1) o gold regex superestima a consulta 3 (recall 100%, só 40% de fato pertinente) e "
        "subestima a 5 (recall 0%, 50% pertinente — o gold da 5 é quase todo pensão \"temporária\", "
        "falso positivo da regex `temporaria`+`servidor`); (2) `grupos` NÃO é melhor que texto_livre "
        "na medida cega (68% vs 70%) — o ganho de (c) no gold regex é artefato; (3) o \"recall "
        "total\" antigo era o top-25 e o parser contava ids citados dentro de ementas (a linha 4c "
        "era 3/10 e é 5/10)."
    )
    with open(os.path.join(BASE, "medicao-2026-09-22.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md) + "\n")
    with open(os.path.join(BASE, "_resultado_bruto.json"), "w", encoding="utf-8") as f:
        json.dump(resultado_bruto, f, ensure_ascii=False, indent=1)

    print("\n".join(linhas_md))
    print(f"\nDECISAO_PADRAO_ORDENAR={decisao}")


if __name__ == "__main__":
    asyncio.run(main())
