#!/usr/bin/env python3
"""Baixa ~20 acórdãos do TCE-RO com inteiro teor (06/10/2026), um a um, 15 s entre pedidos, para medir às cegas as regras de
atribuição portadas do TJRO. Para em dois erros seguidos. Recibos em ~/.tcero-jurisprudencia-recibos (fora de git)."""
import asyncio, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import servidor_tcero as s
TEMAS = ["licitação dispensa", "multa gestor", "aposentadoria registro", "contas de governo", "irregularidade dano ao erário"]
async def main():
    ids = []
    for t in TEMAS:
        r = await s._buscar(t, None, None, None, None, 1, 6, False, None, "data")
        ids += [int(x) for x in re.findall(r"· id (\d{4,7})", r)][:4]
        print(t, "→", ids[-4:], flush=True); await asyncio.sleep(15)
    ids = list(dict.fromkeys(ids))[:20]
    falhas = 0
    for i, idd in enumerate(ids):
        r = await s._obter_acordao(idd, None, None, ler_inteiro_teor=True)
        ok = "inteiro teor" in r.lower() and "não" not in r[:200].lower()
        print(f"{i+1}/{len(ids)} id {idd}: {len(r)} chars", flush=True)
        falhas = 0 if len(r) > 3000 else falhas + 1
        if falhas >= 2: print("duas falhas seguidas — parando"); break
        await asyncio.sleep(15)
asyncio.run(main())
