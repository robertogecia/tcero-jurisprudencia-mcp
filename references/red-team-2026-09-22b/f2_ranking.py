"""Frente 2: casos em que o ranking por relevância erra ou rotula mal. Offline."""
from _comum import *
import copy
def item(i, data, ementa="", disp="", ia=""):
    return {"source": {"idDecisao": i, "data": data, "ementa": ementa, "acordaoDescricao": disp, "informacoesAdicionais": ia, "sigla": "APL-TC", "numero": f"{i}/26"}}
print("2.1 termos de texto_livre com aspas:", srv._termos_da_consulta('"fraude à licitação" direcionamento', None))
s = {"ementa": "FRAUDE À LICITAÇÃO. DIRECIONAMENTO.", "acordaoDescricao": "", "informacoesAdicionais": ""}
t = srv._termos_da_consulta('"fraude à licitação" direcionamento', None)
print("    pontuação de ementa que contém a frase exata:", srv._pontuar_relevancia(s, t), "de", 2*len(t), "possíveis")
print("2.2 stopwords viram termo:", srv._termos_da_consulta("tempo de contribuição", None), srv._termos_da_consulta("dano ao erário", None))
n_de = sum(1 for it in ACERVO if srv._termo_casa(srv._campos_casamento(it["source"])[0], "de"))
n_a = sum(1 for it in ACERVO if srv._termo_casa(srv._campos_casamento(it["source"])[0], "à"))
print(f"    'de' casa o núcleo de {n_de}/{len(ACERVO)} decisões; 'à' (-> \\ba) casa {n_a}/{len(ACERVO)}")
# 2.3 IA vence núcleo
A = item(1, "2026-05-01", ementa="MULTA.")  # 1 termo no núcleo
B = item(2, "2020-01-01", ia="multa reincidência dosimetria")  # 3 termos só em IA
t = srv._termos_da_consulta("multa reincidência dosimetria", None)
print("2.3 núcleo 1 termo vs IA 3 termos:", [x["source"]["idDecisao"] for x in srv._ordenar_por_relevancia([A, B], t)], "(2 = só IA na frente)")
# 2.4 termo duplicado frase+palavra infla
t = srv._termos_da_consulta("multa", [["multa diária"]])
print("2.4 termos com grupo 'multa diária' + texto 'multa':", t)
# 2.5 ordenar ignorado sem termos: rótulo
async def m():
    async def fake(params, op): return {"result": [item(1,"2024-01-01","x"), item(2,"2026-01-01","y"), item(3,"2025-01-01","z")]}
    srv._consultar_api = fake
    async def rel(nome, op): return nome, None
    srv._resolver_relator = rel
    out = await srv._buscar(None, None, None, "FULANO", None, 1, 10, False)
    print("2.5 só relator, cabeçalho:", out.splitlines()[0][-60:])
    # 2.6 mutação + paginação estável com empate total
    base = [item(i, "2026-01-01", "multa") for i in range(1, 31)]
    snap = copy.deepcopy(base); ref = list(base)
    async def fake2(params, op): return {"result": base}
    srv._consultar_api = fake2
    p1 = await srv._buscar("multa", None, None, None, None, 1, 10, False)
    p2 = await srv._buscar("multa", None, None, None, None, 2, 10, False)
    i1 = set(RE_ITEM.findall(p1)); i2 = set(RE_ITEM.findall(p2))
    print("2.6 empate total: p1∩p2 =", i1 & i2, "| array cacheado mutado?", base != snap or [id(x) for x in base] != [id(x) for x in ref])
    # 2.7 orçamento: detalhar com 50 itens grandes
    big = [item(i, "2026-01-01", "multa " + "x"*6000, "y"*6000) for i in range(1, 51)]
    async def fake3(params, op): return {"result": big}
    srv._consultar_api = fake3
    out = await srv._buscar("multa", None, None, None, None, 1, 50, True)
    print("2.7 len saída", len(out), "cortada?", "SAÍDA CORTADA" in out, "panorama presente?", "Panorama" in out)
rodar(m())
