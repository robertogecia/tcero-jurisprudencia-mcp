import os, sys, json, asyncio, tempfile, re, random, glob
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"]="1"
D=tempfile.mkdtemp(); os.environ["TCERO_MCP_DIR_RECIBOS"]=D
sys.path.insert(0,"/Users/robertogrecia/MCP/tcero-jurisprudencia")
sys.path.insert(0,os.path.expanduser("~/.claude/skills/peticao-rg/scripts"))
import servidor_tcero as S, lint_citacoes as L
S.DIR_RECIBOS=D
FX="/Users/robertogrecia/MCP/tcero-jurisprudencia/fixtures/"
src={}
for f in glob.glob(FX+"*.json"):
    d=json.load(open(f))
    for r in (d.get("result") or []) if isinstance(d,dict) else []:
        s=r.get("source") or {}
        if s.get("idDecisao") in (77649,85572,96141,98114): src[s["idDecisao"]]=s
cur={"id":None}
async def fake_api(params, op): return {"result":[{"source":src[cur["id"]]}]}
async def fake_pdf(url): return open(FX+f"pdf/{cur['id']}.pdf","rb").read()
S._consultar_api=fake_api; S._baixar_pdf=fake_pdf
random.seed(7)
tot={}
for i in sorted(src):
    cur["id"]=i; S._cache_pdf_limpar()
    asyncio.run(S._obter_acordao(str(i),None,None,ler_inteiro_teor=True))
    rec=json.load(open(os.path.join(D,f"{i}.json")))
    nt=L.norm_literal(rec["texto"]).split()
    rot={"TR":("texto_transcrito",),"DV":("texto_divergente",),"AL":("texto_alegacao_parte",),"PA":("texto_parecer_mpc",)}
    marc={k:L._blocos_do_recibo(rec,v) for k,v in rot.items()}
    amostra=[" ".join(nt[p:p+12]) for p in random.sample(range(len(nt)-12),60)]
    lint_rate={k:sum(L._toca_bloco(a,b) for a in amostra)/60 for k,b in marc.items()}
    alvo=S._normalizar_casamento(rec["texto"]); pal=[m.start() for m in re.finditer(r"(?<= )\w",alvo)]
    cont={}
    for p in random.sample(pal,60):
        for a in S._alertas_atribuicao(alvo,p,p+80): cont[a.split(":")[0]]=cont.get(a.split(":")[0],0)+1
    print(i,len(nt),"lint-avisos(12w):",{k:round(v,2) for k,v in lint_rate.items()},"srv-alertas/60:",cont, "ex/campo",{k:len(rec[v[0]]) for k,v in rot.items()})
print()
for i in sorted(src):
    rec=json.load(open(os.path.join(D,f"{i}.json")))
    for k in ("texto_parecer_mpc","texto_transcrito","texto_alegacao_parte"):
        print(i,k,[x[:45] for x in rec[k]])
    t=rec["texto"]
    print(i,"triggers PA total:",len(list(S._RE_PARECER_MPC_RAW.finditer(t))),"TR:",len(list(S._RE_TRANSCRICAO_RAW.finditer(t))),"AL:",len(list(S._RE_ALEGACAO_RAW.finditer(t))))
