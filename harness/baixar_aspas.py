#!/usr/bin/env python3
"""Baixa até 24 acórdãos do TCE-RO com inteiro teor (06/10/2026) em temas que costumam TRANSCREVER texto entre aspas (parecer,
lei, decisão anterior), para medir às cegas o alerta ENTRE ASPAS, que ficou sem caso positivo na primeira amostra. Um pedido por
vez, 15 s entre pedidos; para em duas falhas seguidas. Recibos em ~/.tcero-jurisprudencia-recibos (fora de git)."""
import asyncio, glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import servidor_tcero as s
TEMAS = ["in verbis", "transcrevo", "nos seguintes termos", "pedido de reexame", "embargos de declaração omissão",
         "recurso de reconsideração", "tomada de contas especial"]
JA = {int(os.path.basename(f)[:-5]) for f in glob.glob(os.path.expanduser("~/.tcero-jurisprudencia-recibos/*.json"))}
async def main():
    ids = []
    for t in TEMAS:
        r = await s._buscar(t, None, None, None, None, 1, 8, False, None, "relevancia")
        novos = [int(x) for x in re.findall(r"· id (\d{4,7})", r) if int(x) not in JA][:4]
        ids += novos; print(t, "→", novos, flush=True); await asyncio.sleep(15)
    ids = list(dict.fromkeys(ids))[:24]
    falhas = 0
    for i, idd in enumerate(ids):
        r = await s._obter_acordao(idd, None, None, ler_inteiro_teor=True)
        print(f"{i+1}/{len(ids)} id {idd}: {len(r)} chars", flush=True)
        falhas = 0 if len(r) > 3000 else falhas + 1
        if falhas >= 2: print("duas falhas seguidas — parando"); break
        await asyncio.sleep(15)
asyncio.run(main())
