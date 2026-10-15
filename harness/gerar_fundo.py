"""Gera `fundo_vocabulario.json` (ao lado de servidor_tcero.py): frequência de documento (df) de cada palavra
(4+ letras, sem acento, sem palavra de ligação) no núcleo (ementa + dispositivo) das decisões do snapshot
`harness/_snapshot/acervo.json` (5.052 decisões, 8 buscas amplas de 22/09/2026). É o "fundo" que
`sugerir_termos_tcero` usa para saber o que é comum a toda ementa do TCE-RO. A tokenização é a do próprio
servidor (`_tokens_vocab`), para fundo e consulta nunca divergirem. Palavras com df >= 3 (`df`) e pares de palavras adjacentes com df >= 5 (`df2`).
Uso: .venv/bin/python harness/gerar_fundo.py
"""
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
sys.path.insert(0, RAIZ)
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"] = "1"
import servidor_tcero as srv  # noqa: E402

with open(os.path.join(BASE, "_snapshot", "acervo.json"), encoding="utf-8") as f:
    acervo = json.load(f)["result"]

df: dict[str, int] = {}
df2: dict[str, int] = {}
for item in acervo:
    s = item.get("source") or {}
    ws = srv._tokens_vocab(srv._texto_vocab_da_decisao(s))
    for w in set(ws):
        df[w] = df.get(w, 0) + 1
    for p in {f"{a} {b}" for a, b in zip(ws, ws[1:]) if a != b}:
        df2[p] = df2.get(p, 0) + 1
df = {w: c for w, c in df.items() if c >= 3}
df2 = {p: c for p, c in df2.items() if c >= 5}
saida = {"versao": 2, "N": len(acervo), "gerado_em": time.strftime("%Y-%m-%d"),
         "fonte": "harness/_snapshot/acervo.json (ementa + acordaoDescricao; nunca informacoesAdicionais)",
         "df": dict(sorted(df.items())), "df2": dict(sorted(df2.items()))}
destino = os.path.join(RAIZ, "fundo_vocabulario.json")
with open(destino, "w", encoding="utf-8") as f:
    json.dump(saida, f, ensure_ascii=False, separators=(",", ":"))
print(f"{len(acervo)} decisões, {len(df)} palavras com df>=3 e {len(df2)} pares com df>=5 → {destino} ({os.path.getsize(destino)/1024:.0f} KB)")
