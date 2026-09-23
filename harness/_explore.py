"""Monta harness/gold.json (item 2) — 6 consultas típicas de advogado em matéria de contas,
cada uma com essencial/desejavel achados por REGEX CEGA sobre ementa+acordaoDescricao do
snapshot (harness/_snapshot/acervo.json), NUNCA usando _buscar/_filtrar_por_grupos do
servidor e NUNCA olhando informacoesAdicionais (texto de IA). Também grava _db_index.json
(idDecisao -> sigla/numero/orgão/relator/ementa[:300]), no padrão do harness do TJSE.

Isto é o gabarito CEGO à implementação: regex Python simples, direto sobre os dados. Mesmo
critério de normalização (fold de acento/caixa) do servidor foi reimplementado aqui à parte,
de propósito, para não herdar bug ou viés de `_fold`/`_termo_casa`."""
import json
import os
import re
import html

BASE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(BASE, "_snapshot", "acervo.json")


def _strip_html(t):
    t = t or ""
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t)


_ACENTOS = [("á", "a"), ("à", "a"), ("ã", "a"), ("â", "a"), ("é", "e"), ("ê", "e"),
            ("í", "i"), ("ó", "o"), ("õ", "o"), ("ô", "o"), ("ú", "u"), ("ç", "c")]


def _norm(t):
    t = (t or "").lower()
    for a, b in _ACENTOS:
        t = t.replace(a, b)
    return t


def _nucleo(s):
    return _norm(_strip_html(s.get("ementa") or "") + " " + _strip_html(s.get("acordaoDescricao") or ""))


def _casa_todos(nucleo, termos):
    return all(t in nucleo for t in termos)


def main():
    with open(SNAP, encoding="utf-8") as f:
        acervo = json.load(f)["result"]

    db_index = {}
    for item in acervo:
        s = item.get("source") or {}
        idd = s.get("idDecisao")
        if idd is None:
            continue
        db_index[str(idd)] = {
            "sigla": s.get("sigla"),
            "numero": s.get("numero"),
            "orgaoJulgador": s.get("orgaoJulgador"),
            "relator": s.get("relator"),
            "ementa_300": (s.get("ementa") or "")[:300],
        }
    with open(os.path.join(BASE, "_db_index.json"), "w", encoding="utf-8") as f:
        json.dump(db_index, f, ensure_ascii=False, indent=1)

    consultas = [
        {
            "pergunta": "Há precedente do TCE-RO sobre direcionamento/fraude em licitação?",
            "termos_advogado": ["direcionamento de licitação", "fraude à licitação"],
            "regex_essencial": ["licitacao", "direcionamento"],
        },
        {
            "pergunta": "Aposentadoria/ato de pessoal questionando tempo de contribuição — o "
                        "que o TCE-RO já decidiu?",
            "termos_advogado": ["aposentadoria", "tempo de contribuição", "registro de ato de pessoal"],
            "regex_essencial": ["aposentadoria", "tempo de contribuicao"],
        },
        {
            "pergunta": "Reincidência no descumprimento de determinação do Tribunal — como se "
                        "dosimetra a multa?",
            "termos_advogado": ["reincidência", "dosimetria da multa", "descumprimento de determinação"],
            "regex_essencial": ["reincidencia", "multa"],
        },
        {
            "pergunta": "Dano ao erário com imputação de débito solidário entre gestores — "
                        "precedentes?",
            "termos_advogado": ["dano ao erário", "débito solidário", "responsabilidade solidária"],
            "regex_essencial": ["debito", "solidari"],
        },
        {
            "pergunta": "Contratação temporária de servidor sem concurso público — o TCE-RO "
                        "já se pronunciou?",
            "termos_advogado": ["contratação temporária", "ausência de concurso público"],
            "regex_essencial": ["temporaria", "servidor"],
        },
        {
            "pergunta": "Obra pública paralisada/em atraso — há precedente de responsabilização?",
            "termos_advogado": ["obra paralisada", "atraso de obra pública"],
            "regex_essencial": ["obra", "atraso"],
        },
    ]

    gold = []
    for c in consultas:
        casos = []
        for item in acervo:
            s = item.get("source") or {}
            nucleo = _nucleo(s)
            if _casa_todos(nucleo, c["regex_essencial"]):
                casos.append(s)
        # ordena por data desc (mesmo critério do portal) e reparte em essencial (até 10,
        # mínimo 8 exigido pelo porte) e desejavel (próximos 10) — divisão arbitrária mas
        # DECLARADA: o corte é só "os N mais recentes que casam a regex", sem juízo de mérito
        # sobre qual É de fato mais relevante (isso pediria leitura humana, fora do escopo
        # deste gabarito automático).
        casos.sort(key=lambda s: s.get("data") or "", reverse=True)
        essencial = casos[:10] if len(casos) >= 8 else casos
        desejavel = casos[10:20]
        gold.append({
            "pergunta": c["pergunta"],
            "termos_advogado": c["termos_advogado"],
            "regex_usada_no_gabarito": c["regex_essencial"],
            "total_no_snapshot": len(casos),
            "essencial": [
                {
                    "idDecisao": s.get("idDecisao"),
                    "justificativa": f"núcleo (ementa+dispositivo) contém todos os termos "
                                      f"{c['regex_essencial']} (regex cega, sem acento/caixa)",
                }
                for s in essencial
            ],
            "desejavel": [
                {
                    "idDecisao": s.get("idDecisao"),
                    "justificativa": f"casa a mesma regex, mas fora do corte de recência do "
                                      f"essencial (posição {i + 11} entre {len(casos)})",
                }
                for i, s in enumerate(desejavel)
            ],
        })

    with open(os.path.join(BASE, "gold.json"), "w", encoding="utf-8") as f:
        json.dump(gold, f, ensure_ascii=False, indent=1)

    for c in gold:
        print(f"{c['pergunta'][:60]:60s} total={c['total_no_snapshot']:4d} "
              f"essencial={len(c['essencial'])} desejavel={len(c['desejavel'])}")


if __name__ == "__main__":
    main()
