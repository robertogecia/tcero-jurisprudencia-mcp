"""Frente 1 (ii): 'recall total' do medir.py é @25 + parser contaminado."""
from _comum import *
import re as _re
async def main():
    instalar_mock()
    for i,(g,c) in enumerate(zip(GOLD, CONSULTAS),1):
        ess = {e["idDecisao"] for e in g["essencial"]}
        for chave, gr, o in [("a",None,"data"),("b",None,"relevancia"),("c",c["grupos"],"relevancia")]:
            s = await srv._buscar(c["texto_livre"],None,None,None,None,1,25,False,gr,o)
            parser_medir = [int(m) for m in _re.findall(r"\bid (\d+)\b", s)]
            itens = [int(x) for x in RE_ITEM.findall(s)]
            todos = await ids_todos(c["texto_livre"], gr, o)
            print(i,chave,"ids_parser_medir=",len(parser_medir),"itens_reais=",len(itens),
                  "extras=",sorted(set(parser_medir)-set(itens))[:5],
                  "| @25:",len(ess&set(itens)),"| total real:",len(ess&set(todos)),"de",len(todos),"devolvidos")
rodar(main())
