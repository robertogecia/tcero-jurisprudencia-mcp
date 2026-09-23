"""Frente 1 (i-A): gabarito ALTERNATIVO por critério independente do ranking — decisões cujo
dispositivo ou informações adicionais contêm uma FRASE de `termos_advogado` (a pergunta do
advogado, não as palavras da regex do gold) mas cuja EMENTA não contém nenhuma delas.
Mede em que posição (a)/(b)/(c) colocam esses itens."""
from _comum import *
import statistics
def f(t): return srv._RE_ESPACO.sub(" ", srv._fold(t or ""))
def alt(g):
    frases = [f(t).replace(" a licitacao"," a licitacao") for t in g["termos_advogado"]]
    out=[]
    for it in ACERVO:
        s=it["source"]; em=f(s.get("ementa")); dp=f(srv._html_para_texto(s.get("acordaoDescricao") or "")); ia=f(srv._html_para_texto(s.get("informacoesAdicionais") or ""))
        if any(fr in dp or fr in ia for fr in frases) and not any(fr in em for fr in frases):
            out.append((s["idDecisao"], any(fr in dp for fr in frases), any(fr in ia for fr in frases)))
    return out
async def main():
    tot = {"a":[], "b":[], "c":[]}
    for i,(g,c) in enumerate(zip(GOLD,CONSULTAS),1):
        A = alt(g); ids_alt={x[0] for x in A}
        if not A: print(i,"gabarito alternativo vazio"); continue
        print(f"\n{i} {g['pergunta'][:60]} | alt={len(A)} (no dispositivo={sum(x[1] for x in A)}, só IA={sum(x[2] and not x[1] for x in A)})")
        for k,gr,o in [("a",None,"data"),("b",None,"relevancia"),("c",c["grupos"],"relevancia")]:
            ids = await ids_todos(c["texto_livre"], gr, o)
            pos=[ids.index(x)+1 for x in ids_alt if x in ids]
            n=min(10,len(A))
            r10=len(ids_alt&set(ids[:10]))/n
            tot[k].append(r10)
            print(f"   ({k}) no conjunto {len(pos)}/{len(A)} | recall@10 (sobre min(10,N)) {r10:.0%} | @25 {len(ids_alt&set(ids[:25]))} | mediana posição {statistics.median(pos) if pos else '-'} de {len(ids)}")
    for k in tot: print(k, "média recall@10 alt:", f"{sum(tot[k])/len(tot[k]):.0%}" if tot[k] else "-")
rodar(main())
