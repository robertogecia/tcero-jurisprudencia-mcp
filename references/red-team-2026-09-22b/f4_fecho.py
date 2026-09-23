"""Frente 4: fecho x cadastro — todos os matches por PDF, cadastro conferido contra o snapshot."""
import json, os, sys, re
R = os.path.expanduser("~/MCP/tcero-jurisprudencia"); sys.path.insert(0, R)
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"] = "1"
import servidor_tcero as srv, fitz
ac = {it["source"]["idDecisao"]: it["source"] for it in json.load(open(f"{R}/harness/_snapshot/acervo.json"))["result"]}
plano = json.load(open(f"{R}/harness/_pdfs_plano.json"))
for e in plano:
    p = f"{R}/harness/_pdfs/{e['idDecisao']}.pdf"
    if not os.path.exists(p): continue
    t = "".join(pg.get_text() for pg in fitz.open(p))
    ms = [re.sub(r"\s+"," ",m.group(1)) for m in srv._RE_ORGAO_FECHO.finditer(t)]
    snap = ac.get(e["idDecisao"], {})
    print(e["idDecisao"], "plano:", e["orgaoJulgador"], "| snapshot:", snap.get("orgaoJulgador"), snap.get("sigla"), "| matches:", ms, "->", srv._orgao_do_fecho(t))
for idd in (77649,85572,96141,98114):
    t = "".join(pg.get_text() for pg in fitz.open(f"{R}/fixtures/pdf/{idd}.pdf"))
    print(idd, "fixture matches:", [re.sub(r"\s+"," ",m.group(1)) for m in srv._RE_ORGAO_FECHO.finditer(t)])
# sintéticos
P="ACORDAM os Senhores Conselheiros do Pleno do Tribunal de Contas do Estado de Rondônia"
TP="ACORDAM os Senhores Conselheiros do Tribunal Pleno do Tribunal de Contas do Estado de Rondônia"
C1="ACORDAM os Senhores Conselheiros da 1ª Câmara do Tribunal de Contas do Estado de Rondônia"
C1b="ACORDAM os Senhores Conselheiros da Primeira Câmara do Tribunal de Contas do Estado de Rondônia"
CE="ACORDAM os Senhores Conselheiros da Câmara Especial do Tribunal de Contas do Estado de Rondônia"
for nome, t in [("Pleno",P),("Tribunal Pleno",TP),("1ª Câmara",C1),("Primeira Câmara",C1b),("Câmara Especial",CE),
                ("transcrito C1 antes de P (embargos no Pleno)", "Acórdão embargado: '"+C1+"'. ... "+P),
                ("Pleno + Tribunal Pleno (mesmo órgão, grafias)", P+" ... "+TP),
                ("C1 + Primeira Câmara (mesmo órgão)", C1+" ... "+C1b)]:
    print(f"{nome!r:55} -> {srv._orgao_do_fecho(t)!r}")
