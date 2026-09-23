import os,sys,re
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"]="1"
sys.path.insert(0,"/Users/robertogrecia/MCP/tcero-jurisprudencia"); import servidor_tcero as S
FX="/Users/robertogrecia/MCP/tcero-jurisprudencia/fixtures/pdf/"
for i in (77649,85572,96141,98114):
    r=S._extrair_texto_pdf(open(FX+f"{i}.pdf","rb").read()); t=r["texto"]
    ms=[re.sub(r"\s+"," ",m.group(1)) for m in S._RE_ORGAO_FECHO.finditer(t)]
    print(i,"fecho:",S._orgao_do_fecho(t),"| todas:",ms, "| 'transcreve acórdão':", len(re.findall(r"(?i)nos seguintes termos",t)))
emb=("Trata-se de embargos. O acórdão embargado assim dispôs: ACORDAM os Senhores Conselheiros da 1ª Câmara do Tribunal de Contas do Estado, por unanimidade... "
     "É o voto. ACORDAM os Senhores Conselheiros do Pleno do Tribunal de Contas do Estado de Rondônia, por unanimidade, em rejeitar os embargos.")
print("embargos sintetico:",S._orgao_do_fecho(emb))
