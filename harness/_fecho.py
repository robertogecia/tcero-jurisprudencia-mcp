"""Item 6 — tabula fecho x cadastro sobre os 4 PDFs de fixtures/pdf/ + os até 16 novos de
harness/_pdfs/, usando _orgao_do_fecho real do servidor (com a correção de 22/09/2026: None
quando há fechos de órgãos diferentes no mesmo PDF). Grava harness/fecho-2026-09-22.md."""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, RAIZ)
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"] = "1"
import servidor_tcero as srv  # noqa: E402
import fitz  # noqa: E402

with open(os.path.join(BASE, "_snapshot", "acervo.json"), encoding="utf-8") as f:
    ACERVO = {it["source"]["idDecisao"]: it["source"] for it in json.load(f)["result"]}

# os 4 originais de fixtures/pdf/ não estão no snapshot (vieram de buscas específicas por
# numero_processo/numero_acordao) — cadastro conhecido do --selftest existente.
CADASTRO_FIXTURES = {77649: "Pleno", 85572: "Pleno", 96141: "1ª Câmara", 98114: "Pleno"}

linhas = []
divergencias = 0
total = 0

fontes = []
for idd, cadastro in CADASTRO_FIXTURES.items():
    fontes.append((idd, cadastro, os.path.join(RAIZ, "fixtures", "pdf", f"{idd}.pdf"), "fixtures/pdf/ (original)"))

with open(os.path.join(BASE, "_pdfs_plano.json"), encoding="utf-8") as f:
    plano = json.load(f)
for e in plano:
    idd = e["idDecisao"]
    caminho = os.path.join(BASE, "_pdfs", f"{idd}.pdf")
    if os.path.exists(caminho):
        fontes.append((idd, e["orgaoJulgador"], caminho, "harness/_pdfs/ (22/09/2026)"))

for idd, cadastro, caminho, origem in fontes:
    doc = fitz.open(caminho)
    txt = "".join(p.get_text() for p in doc)
    doc.close()
    fecho = srv._orgao_do_fecho(txt)
    total += 1
    if fecho is None:
        veredito = "CONFLITO (fechos de órgãos diferentes -> None)"
        divergencias += 1
    elif srv._fold(fecho) == srv._fold(cadastro):
        veredito = "bate"
    else:
        veredito = f"DIVERGE (fecho={fecho})"
        divergencias += 1
    linhas.append((idd, cadastro, fecho, veredito, origem))

md = []
md.append("# Fecho x cadastro — servidor_tcero.py, 22/09/2026\n")
md.append(f"Amostra: N={total} PDFs reais (4 originais de `fixtures/pdf/` + "
          f"{total - len(CADASTRO_FIXTURES)} novos em `harness/_pdfs/`, baixados nesta sessão, "
          "distribuídos entre 1ª Câmara/2ª Câmara/Pleno e siglas normais + embargos/recurso).\n")
md.append("| id | cadastro (`orgaoJulgador`) | fecho do PDF | veredito | origem |")
md.append("|---|---|---|---|---|")
for idd, cadastro, fecho, veredito, origem in linhas:
    md.append(f"| {idd} | {cadastro} | {fecho if fecho is not None else '(None — conflito)'} | {veredito} | {origem} |")

md.append(f"\n**{total - divergencias}/{total} batem**; {divergencias} divergência(s)/conflito(s) real(is) na amostra.\n")
if divergencias == 0:
    md.append(
        "0 divergências em N maior (18) — o aviso de divergência em "
        "`obter_acordao_tcero(..., ler_inteiro_teor=True)` **continua desligado**: não há base "
        "na amostra para acionar um aviso que ainda não tem nenhum caso real para apontar."
    )
else:
    md.append(
        f"{divergencias} divergência(s)/conflito(s) real(is) encontrada(s) na amostra — "
        "decisão sobre ligar o aviso em `obter_acordao_tcero(..., ler_inteiro_teor=True)` cabe "
        "à conversa principal à luz destes casos concretos (ver linhas acima)."
    )

with open(os.path.join(BASE, "fecho-2026-09-22.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")

print("\n".join(md))
print(f"\nDIVERGENCIAS={divergencias} TOTAL={total}")
