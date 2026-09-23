"""Base comum: mock do portal sobre o snapshot (cópia do mock de harness/medir.py) + coleta de
TODOS os ids devolvidos por _buscar, página a página, com parser correto do cabeçalho do item."""
import asyncio, json, os, re, sys
R = os.path.expanduser("~/MCP/tcero-jurisprudencia"); sys.path.insert(0, R)
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"] = "1"
import servidor_tcero as srv
ACERVO = json.load(open(f"{R}/harness/_snapshot/acervo.json", encoding="utf-8"))["result"]
GOLD = json.load(open(f"{R}/harness/gold.json", encoding="utf-8"))
POR_ID = {it["source"]["idDecisao"]: it["source"] for it in ACERVO}
sys.path.insert(0, f"{R}/harness")
import medir  # reaproveita CONSULTAS_BUSCA e o mock
CONSULTAS = medir.CONSULTAS_BUSCA
RE_ITEM = re.compile(r"^\*\*\d+\. [^\n]*?\*\* · id (\d+)", re.M)

def instalar_mock():
    srv._consultar_api = medir._consultar_fake

async def ids_todos(tl, grupos, ordenar, **kw):
    """Mesmo pipeline de _buscar (mock -> _filtrar_por_grupos -> _ordenar_por_relevancia), com
    as funções REAIS do servidor, sem paginar (paginar re-ordena o conjunto inteiro por página)."""
    dados = await medir._consultar_fake({"textoLivre": srv._montar_texto_livre_com_grupos(tl, srv._grupos_validos(grupos))}, "busca")
    todos = dados["result"]
    g = srv._grupos_validos(grupos)
    if g:
        todos, _ = srv._filtrar_por_grupos(todos, g)
    if ordenar == "relevancia":
        t = srv._termos_da_consulta(tl, g)
        if t: todos = srv._ordenar_por_relevancia(todos, t)
    return [it["source"]["idDecisao"] for it in todos]

def rodar(coro): return asyncio.run(coro)
