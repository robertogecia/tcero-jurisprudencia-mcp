"""
Experimentos ONLINE controlados, 13/09/2026 — fecha os pontos que o red team de
references/red-team-2026-09-13.md deixou como [NÃO TESTADO] / hipótese.

Orçamento de rede: no máximo 10 requisições ao portal, espaçadas de >=4s, nunca em rajada,
sempre com o mesmo User-Agent que o servidor de produção usa (importado direto de
servidor_tcero, não duplicado). Cada resposta crua é salva em fixtures/exp_*.json ANTES de
qualquer análise, para nunca repetir uma requisição já feita.

Uso:
    .venv/bin/python scripts/experimentos-2026-09-13.py A     # Experimento A (5 requisições)
    .venv/bin/python scripts/experimentos-2026-09-13.py B     # Experimento B (0 ou 1 requisição)

Cada fase só roda depois que a anterior foi inspecionada manualmente (não roda tudo junto sem
supervisão) — mas nada aqui impede rodar as duas em sequência se já se sabe o que se quer.
"""
from __future__ import annotations

import json
import os
import sys
import time
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from servidor_tcero import HEADERS_BASE, SITE, ENDPOINT_BUSCAR  # noqa: E402

import httpx  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXDIR = os.path.join(BASE, "fixtures")
ESPACAMENTO_S = 5.0  # >= 4s exigido; 5s de margem

# Termos do Experimento A: dois termos técnicos específicos do vocabulário do TCE-RO,
# individualmente estreitos (não "licitação" sozinha) e que coocorrem pouco — uma decisão
# sobre REINCIDÊNCIA de um responsável já multado antes é um assunto diferente de uma decisão
# sobre DIRECIONAMENTO de edital (favorecimento de licitante). Escolhidos por leitura das
# ementas reais em fixtures/01_busca_numeroProcesso.json e 02_busca_numeroAcordao.json.
TERMO1 = "reincidência"
TERMO2 = "direcionamento"


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _pedir(url_completa: str, rotulo: str) -> dict:
    """Uma requisição, com o MESMO client/headers do servidor de produção. Salva a resposta
    crua em fixtures/exp_<rotulo>.json ANTES de devolver qualquer coisa analisada."""
    t0 = time.time()
    with httpx.Client(timeout=45.0, follow_redirects=True, headers=HEADERS_BASE) as cli:
        r = cli.get(url_completa)
    dt = time.time() - t0
    tamanho = len(r.content or b"")
    _log(f"{rotulo}: GET {url_completa}")
    _log(f"{rotulo}: HTTP {r.status_code} · {tamanho:,} bytes · {dt:.2f}s".replace(",", "."))
    destino = os.path.join(FIXDIR, f"exp_{rotulo}.json")
    corpo = r.text
    with open(destino, "w", encoding="utf-8") as f:
        f.write(corpo)
    meta = {
        "rotulo": rotulo,
        "url": url_completa,
        "status_code": r.status_code,
        "bytes": tamanho,
        "segundos": round(dt, 3),
    }
    if tamanho > 15 * 1024 * 1024:
        _log(f"{rotulo}: ⚠️ resposta > 15 MB — não repetir consultas desta amplitude.")
    return meta


def _registrar_meta(meta_lista: list[dict]) -> None:
    destino = os.path.join(FIXDIR, "exp_log.json")
    existente = []
    if os.path.exists(destino):
        try:
            existente = json.load(open(destino, encoding="utf-8"))
        except Exception:
            existente = []
    existente.extend(meta_lista)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(existente, f, ensure_ascii=False, indent=2)


def experimento_a() -> None:
    """5 requisições — mesmo par de termos, 5 sintaxes diferentes de textoLivre, para separar
    o que é AND, o que é OR, o que é frase exata, e se %2B é lido como operador."""
    t1 = quote(TERMO1, safe="")
    t2 = quote(TERMO2, safe="")
    consultas = [
        ("A1_espaco_pct20", f"{ENDPOINT_BUSCAR}?textoLivre={t1}%20{t2}"),
        ("A2_mais_pct2B", f"{ENDPOINT_BUSCAR}?textoLivre={t1}%2B{t2}"),
        ("A3_mais_CRU_controle", f"{ENDPOINT_BUSCAR}?textoLivre={t1}+{t2}"),  # + literal, não codificado
        ("A4_frase_exata", f"{ENDPOINT_BUSCAR}?textoLivre=%22{t1}%20{t2}%22"),
        ("A5_operador_e", f"{ENDPOINT_BUSCAR}?textoLivre={t1}%20e%20{t2}"),
    ]
    metas = []
    for i, (rotulo, url) in enumerate(consultas):
        if i > 0:
            time.sleep(ESPACAMENTO_S)
        metas.append(_pedir(url, rotulo))
    _registrar_meta(metas)
    _log("Experimento A concluído (5 requisições). Inspecione fixtures/exp_A*.json antes de A.")


def experimento_a6_isolar_e() -> None:
    """1 requisição extra (fora do plano original de 5): A5 (operador 'e') devolveu um
    SUPERCONJUNTO de A1/A2/A3 (156 -> 267), mas os 111 registros extras não contêm
    'reincidência' nem 'direcionamento' em NENHUM campo textual inspecionado (ementa,
    acordaoDescricao, objeto, assunto, natureza, informacoesAdicionais, veja) — nem têm
    highlight nenhum. Isola a variável: o que 'textoLivre=e' sozinho devolve?"""
    url = f"{ENDPOINT_BUSCAR}?textoLivre=e"
    meta = _pedir(url, "A6_isolar_e_sozinho")
    _registrar_meta([meta])
    _log("A6 concluído (1 requisição extra, fora do plano original de 5 do Experimento A).")


def experimento_b(forcar_termo_comum: str | None = None) -> None:
    """1 requisição ampla o bastante para trazer algumas centenas de decisões (termo comum de
    contas), só chamada quando nenhuma resposta do Experimento A já serve. Passe
    forcar_termo_comum=None para pular (reaproveitando resposta de A)."""
    if not forcar_termo_comum:
        _log("Experimento B: reaproveitando resposta do Experimento A — nenhuma requisição nova.")
        return
    url = f"{ENDPOINT_BUSCAR}?textoLivre={quote(forcar_termo_comum, safe='')}"
    meta = _pedir(url, "B1_termo_comum")
    _registrar_meta([meta])
    _log("Experimento B concluído (1 requisição).")


if __name__ == "__main__":
    fase = sys.argv[1] if len(sys.argv) > 1 else ""
    if fase == "A":
        experimento_a()
    elif fase == "A6":
        experimento_a6_isolar_e()
    elif fase == "B":
        termo = sys.argv[2] if len(sys.argv) > 2 else None
        experimento_b(termo)
    else:
        sys.exit("uso: experimentos-2026-09-13.py A | B [termo_comum_opcional]")
