"""Frente 5: recibo v1.1.0 x v1.2.0 byte a byte (mesmo source, mesmo relógio), verificar_citacao
e link de relato sem termo de busca. Offline; v1.1.0 extraída do git para /private/tmp."""
import importlib.util, json, os, sys, tempfile, time
R = os.path.expanduser("~/MCP/tcero-jurisprudencia"); sys.path.insert(0, R)
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"] = "1"
def carregar(nome, caminho, dirrec):
    os.environ["TCERO_MCP_DIR_RECIBOS"] = dirrec
    spec = importlib.util.spec_from_file_location(nome, caminho); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.DIR_RECIBOS = dirrec; return m
d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp()
v110 = carregar("v110", "/private/tmp/claude-501/rt22b/servidor_v110.py", d1)
v120 = carregar("v120", f"{R}/servidor_tcero.py", d2)
ac = json.load(open(f"{R}/harness/_snapshot/acervo.json"))["result"]
time.strftime = lambda *a, **k: "2026-09-22T00:00:00-0400"
iguais = 0; n = 0
for it in ac[:300]:
    s = it["source"]
    v110._gravar_recibo_tcero(s, None); v120._gravar_recibo_tcero(s, None)
    a = open(os.path.join(d1, f"{s['idDecisao']}.json"), "rb").read(); b = open(os.path.join(d2, f"{s['idDecisao']}.json"), "rb").read()
    n += 1; iguais += (a == b)
print(f"recibos byte-idênticos v1.1.0 x v1.2.0: {iguais}/{n}")
s = ac[0]["source"]
for trecho in [s["ementa"][:60], "multa", "trecho inexistente xyz"]:
    r1 = v110._verificar_trecho if hasattr(v110, "_verificar_trecho") else None
print("_verificar_trecho idêntico nas duas versões (código):", v110._verificar_trecho.__code__.co_code == v120._verificar_trecho.__code__.co_code)
link = v120._link_relato("timeout")
print("link de relato contém termo de busca?", any(t in link for t in ("reincid", "multa", "textoLivre")))
