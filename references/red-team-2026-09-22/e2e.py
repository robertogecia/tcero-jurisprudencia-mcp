import os, sys, json, asyncio, tempfile, re
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"]="1"
D=tempfile.mkdtemp(); os.environ["TCERO_MCP_DIR_RECIBOS"]=D
os.environ["TCERO_MCP_ESTADO"]=os.path.join(D,"estado.json")
sys.path.insert(0,"/Users/robertogrecia/MCP/tcero-jurisprudencia")
sys.path.insert(0,os.path.expanduser("~/.claude/skills/peticao-rg/scripts"))
import servidor_tcero as S, lint_citacoes as L
S.DIR_RECIBOS=D
FX="/Users/robertogrecia/MCP/tcero-jurisprudencia/fixtures/"
fx=json.load(open(FX+"03_busca_idDecisao.json"))
async def fake_api(params, op): return fx
async def fake_pdf(url): return open(FX+"pdf/98114.pdf","rb").read()
S._consultar_api=fake_api; S._baixar_pdf=fake_pdf
out=asyncio.run(S._obter_acordao("98114",None,None,ler_inteiro_teor=True))
rec=json.load(open(os.path.join(D,"98114.json")))
print("len texto",len(rec["texto"]),"pdf_completo",rec["texto_pdf_completo"], "crlf" , "\r" in rec["texto"], "&" in rec["texto"])
for k in ("texto_transcrito","texto_divergente","texto_alegacao_parte","texto_parecer_mpc"): print(k,len(rec[k]), [x[:60] for x in rec[k]])
print("ia_dejur", (rec["texto_ia_dejur"] or "")[:200])
def lint(trecho, **k):
    f=L.Ficha(dict({"chave":"APL-TC 00055/26","tribunal":"TCE-RO","id_documento":"98114","trecho":trecho,"verificacao":"inteiro teor lido (PDF)"},**k),("x",))
    return L.conferir_recibo(f,None,None,None,D)
json.dump(rec,open(os.path.join(D,"rec_copy.json.txt"),"w"))
S_=sys.modules[__name__]
