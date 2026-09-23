"""Item 6 — baixa até 16 PDFs adicionais (aqui: 14, para respeitar o orçamento total de 30
requisições da tarefa, já com 16 gastas no snapshot) para harness/_pdfs/, distribuídos entre
1ª Câmara, 2ª Câmara e Pleno e entre siglas normais e de embargos/recurso (AC1R-TC/AC2R-TC/
APLR-TC), a partir de harness/_pdfs_plano.json (montado offline sobre o snapshot). Loga cada
requisição em harness/_log_rede.json (mesmo arquivo do _fetch_snapshot.py)."""
import json
import os
import sys
import time

import httpx
import truststore

BASE = os.path.dirname(os.path.abspath(__file__))
PDFS_DIR = os.path.join(BASE, "_pdfs")
LOG = os.path.join(BASE, "_log_rede.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) harness-tcero/1.0 (Roberto Grecia OAB/RO 7865-A)"


def _corrigir_link_pdf(link: str) -> str:
    if not link:
        return ""
    if link.startswith("//tce.ro.gov.br/"):
        return "https://tcero.tc.br/" + link[len("//tce.ro.gov.br/"):]
    return link


def _log(entrada: dict) -> None:
    dados = []
    if os.path.exists(LOG):
        try:
            with open(LOG, encoding="utf-8") as f:
                dados = json.load(f)
        except Exception:
            dados = []
    dados.append(entrada)
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def main() -> None:
    os.makedirs(PDFS_DIR, exist_ok=True)
    with open(os.path.join(BASE, "_pdfs_plano.json"), encoding="utf-8") as f:
        plano = json.load(f)

    ctx = truststore.SSLContext()
    cliente = httpx.Client(headers={"User-Agent": UA}, timeout=60.0, verify=ctx, follow_redirects=True)

    with open(LOG, encoding="utf-8") as f:
        n_req = len(json.load(f))

    ok = 0
    for e in plano:
        destino = os.path.join(PDFS_DIR, f"{e['idDecisao']}.pdf")
        if os.path.exists(destino):
            print(f"{e['idDecisao']}: já baixado, pulando")
            continue
        url = _corrigir_link_pdf(e["linkArquivo"])
        t0 = time.time()
        try:
            resp = cliente.get(url)
            status = resp.status_code
            corpo = resp.content
        except Exception as ex:
            status = f"EXC:{type(ex).__name__}:{ex}"
            corpo = b""
        n_req += 1
        _log({
            "n": n_req, "url": url, "hora": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": status, "bytes": len(corpo), "idDecisao": e["idDecisao"],
        })
        print(f"[{n_req}] id {e['idDecisao']} ({e['sigla']}, {e['orgaoJulgador']}) -> status={status} bytes={len(corpo)}")
        if status == 200 and corpo[:4] == b"%PDF":
            with open(destino, "wb") as fpdf:
                fpdf.write(corpo)
            ok += 1
        else:
            print(f"  !! não é PDF válido ou falhou (status={status}); não salvo")
            if isinstance(status, int) and status >= 500:
                print("  erro 5xx — aguardando 60s e tentando 1 vez...")
                time.sleep(60)
                try:
                    resp2 = cliente.get(url)
                    status2 = resp2.status_code
                    corpo2 = resp2.content
                except Exception as ex:
                    status2 = f"EXC:{type(ex).__name__}:{ex}"
                    corpo2 = b""
                n_req += 1
                _log({
                    "n": n_req, "url": url + " (retry)", "hora": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "status": status2, "bytes": len(corpo2), "idDecisao": e["idDecisao"],
                })
                if status2 == 200 and corpo2[:4] == b"%PDF":
                    with open(destino, "wb") as fpdf:
                        fpdf.write(corpo2)
                    ok += 1
                else:
                    print("  retry também falhou — parando a frente de rede.")
                    break
        dt = time.time() - t0
        if dt < 2.0:
            time.sleep(2.0 - dt)

    print(f"\n{ok}/{len(plano)} PDFs novos baixados. Requisições totais no log: {n_req}.")


if __name__ == "__main__":
    main()
