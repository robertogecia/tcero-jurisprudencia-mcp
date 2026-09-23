"""Baixa o snapshot do acervo (item 1) — até 8 buscas amplas de UMA palavra em textoLivre,
dedupe por idDecisao, grava harness/_snapshot/acervo.json + contagem.md, e registra cada
requisição em harness/_log_rede.json. Roda uma vez, manual, fora do MCP (o disjuntor do
servidor não é usado aqui de propósito — este script tem seu próprio limitador simples de
>=2s entre requisições e um teto fixo de tentativas)."""
import json
import os
import sys
import time
import urllib.parse

import httpx
import truststore

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BASE)
SNAP_DIR = os.path.join(BASE, "_snapshot")
LOG = os.path.join(BASE, "_log_rede.json")
URL = "https://papyrus.tcero.tc.br/api/espelho/buscar"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) harness-tcero/1.0 (Roberto Grecia OAB/RO 7865-A)"

PALAVRAS = ["licitacao", "aposentadoria", "debito", "multa", "contrato", "pessoal", "prestacao", "obra"]
# sem acento de propósito: textoLivre já demonstrou (protocolo-papyrus.md) casar por termo OU;
# evita problema de encoding na querystring. Confirma-se pelo total retornado de cada uma.


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
    os.makedirs(SNAP_DIR, exist_ok=True)
    from_cache = "--from-cache" in sys.argv
    ctx = truststore.SSLContext() if not from_cache else None
    cliente = None if from_cache else httpx.Client(headers={"User-Agent": UA}, timeout=30.0, verify=ctx)

    acervo: dict[str, dict] = {}
    contagem_por_palavra = {}
    n_req = 0
    for palavra in PALAVRAS:
        if from_cache:
            caminho_raw = os.path.join(SNAP_DIR, f"_raw_{palavra}.json")
            if not os.path.exists(caminho_raw):
                print(f"[cache] {palavra}: sem raw salvo, pulando (não gasta rede em --from-cache)")
                contagem_por_palavra[palavra] = "sem cache"
                continue
            with open(caminho_raw, encoding="utf-8") as f:
                dados = json.load(f)
            resultados = dados.get("result") or []
            contagem_por_palavra[palavra] = len(resultados)
            for item in resultados:
                s = item.get("source") or {}
                idd = s.get("idDecisao")
                if idd is not None and idd not in acervo:
                    acervo[idd] = item
            print(f"[cache] {palavra}: {len(resultados)} resultados")
            continue
        params = {"textoLivre": palavra}
        t0 = time.time()
        try:
            resp = cliente.get(URL, params=params)
            status = resp.status_code
            corpo = resp.content
        except Exception as e:
            status = f"EXC:{type(e).__name__}:{e}"
            corpo = b""
        n_req += 1
        _log({
            "n": n_req,
            "url": f"{URL}?{urllib.parse.urlencode(params)}",
            "hora": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": status,
            "bytes": len(corpo),
        })
        print(f"[{n_req}] textoLivre={palavra!r} -> status={status} bytes={len(corpo)}")
        if status == 200:
            try:
                dados = json.loads(corpo)
            except Exception as e:
                print(f"  !! JSON inválido: {e}")
                dados = {"result": []}
            # cacheia a resposta crua em disco imediatamente — se algo adiante quebrar, a
            # requisição já feita não se perde e não precisa ser refeita.
            with open(os.path.join(SNAP_DIR, f"_raw_{palavra}.json"), "w", encoding="utf-8") as fraw:
                json.dump(dados, fraw, ensure_ascii=False)
            resultados = dados.get("result") or []
            contagem_por_palavra[palavra] = len(resultados)
            for item in resultados:
                s = item.get("source") or {}
                idd = s.get("idDecisao")
                if idd is not None and idd not in acervo:
                    acervo[idd] = item
        else:
            contagem_por_palavra[palavra] = f"FALHOU ({status})"
            if isinstance(status, int) and status >= 500:
                print("  erro 5xx — aguardando 60s e tentando 1 vez...")
                time.sleep(60)
                try:
                    resp2 = cliente.get(URL, params=params)
                    status2 = resp2.status_code
                    corpo2 = resp2.content
                except Exception as e:
                    status2 = f"EXC:{type(e).__name__}:{e}"
                    corpo2 = b""
                n_req += 1
                _log({
                    "n": n_req, "url": f"{URL}?{urllib.parse.urlencode(params)} (retry)",
                    "hora": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": status2, "bytes": len(corpo2),
                })
                if status2 == 200:
                    dados = json.loads(corpo2)
                    resultados = dados.get("result") or []
                    contagem_por_palavra[palavra] = len(resultados)
                    for item in resultados:
                        s = item.get("source") or {}
                        idd = s.get("idDecisao")
                        if idd is not None and idd not in acervo:
                            acervo[idd] = item
                else:
                    print("  retry também falhou — parando a frente de rede, seguindo com o que há.")
                    break
        # >= 2s entre requisições
        dt = time.time() - t0
        if dt < 2.0:
            time.sleep(2.0 - dt)

    # também incorpora fixtures existentes na raiz do projeto (reaproveitar, como pedido)
    fx_dir = os.path.join(RAIZ, "fixtures")
    reaproveitadas = 0
    for nome in os.listdir(fx_dir):
        if not nome.endswith(".json") or nome.startswith("exp_"):
            continue
        try:
            with open(os.path.join(fx_dir, nome), encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue  # 04_relatores.json e exp_log.json são listas, não respostas de busca
        for item in d.get("result") or []:
            s = item.get("source") or {}
            idd = s.get("idDecisao")
            if idd is not None and idd not in acervo:
                acervo[idd] = item
                reaproveitadas += 1

    with open(os.path.join(SNAP_DIR, "acervo.json"), "w", encoding="utf-8") as f:
        json.dump({"result": list(acervo.values())}, f, ensure_ascii=False)

    # contagem.md
    from collections import Counter
    orgaos = Counter()
    anos = Counter()
    siglas = Counter()
    for item in acervo.values():
        s = item.get("source") or {}
        orgaos[s.get("orgaoJulgador") or "sem informação"] += 1
        data = s.get("data") or ""
        anos[data[:4] if len(data) >= 4 else "sem informação"] += 1
        siglas[s.get("sigla") or "sem informação"] += 1

    with open(os.path.join(SNAP_DIR, "contagem.md"), "w", encoding="utf-8") as f:
        f.write("# Snapshot do acervo TCE-RO — 22/09/2026\n\n")
        f.write(f"Total de decisões únicas (por idDecisao): **{len(acervo)}**\n")
        f.write(f"({reaproveitadas} vieram só das fixtures já existentes, sem gastar requisição nova)\n\n")
        f.write("## Por palavra de busca (bruto, antes de deduplicar)\n\n")
        for p, c in contagem_por_palavra.items():
            f.write(f"- `{p}`: {c}\n")
        f.write("\n## Por órgão julgador\n\n")
        for k, v in orgaos.most_common():
            f.write(f"- {k}: {v}\n")
        f.write("\n## Por ano\n\n")
        for k, v in sorted(anos.items(), reverse=True):
            f.write(f"- {k}: {v}\n")
        f.write("\n## Por sigla\n\n")
        for k, v in siglas.most_common():
            f.write(f"- {k}: {v}\n")

    print(f"\nSnapshot: {len(acervo)} decisões únicas, {n_req} requisições gastas nesta corrida.")


if __name__ == "__main__":
    main()
