# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.4.0,<2", "httpx>=0.27", "truststore>=0.9"]
# (mcp 2.x renomeou FastMCP para MCPServer e mudou APIs — mesma trava dos irmãos TJRO/TRF1;
#  manter <2 até migrar os três juntos)
# ///
"""
Servidor MCP — Jurisprudência do TCE-RO (Tribunal de Contas do Estado de Rondônia)
===================================================================================
Pesquisa pública no portal ePapyrus (https://papyrus.tcero.tc.br/), SEM login, SEM WAF,
SEM captcha — confirmado ao vivo com curl puro em 13/09/2026 (ver references/protocolo-papyrus.md
para o levantamento completo). Diferença importante em relação aos irmãos: aqui não há
sessão/ViewState (TRF1) nem desafio anti-robô (TJRO) para contornar — é uma API JSON simples.

Expõe quatro ferramentas ao Claude:
  • buscar_jurisprudencia_tcero — busca livre e/ou por campo, paginação NO CLIENTE (a API do
                                  portal devolve tudo de uma vez, sem paginar no servidor),
                                  resumo compacto por padrão
  • obter_acordao_tcero         — detalhe completo de uma decisão (ementa integral, dispositivo,
                                  informações adicionais geradas por IA pelo DEJUR, legislação,
                                  link do inteiro teor em PDF)
  • verificar_citacao_tcero     — confere se um trecho aparece literalmente na ementa/dispositivo
  • diagnostico_ritmo_tcero     — estado do disjuntor/limitador, sem rede

Problema estrutural a resolver, dito com todas as letras: a API `/api/espelho/buscar` NÃO
pagina no servidor — uma busca ampla já devolve múltiplos megabytes de JSON (confirmado ao
vivo: 4,03 MB para uma busca de dois termos; o usuário já havia visto 10,8 MB / 866 resultados
antes deste servidor existir). Nunca repassar esse array cru para quem chama: paginar aqui,
resumir por padrão, cachear a resposta crua por alguns minutos.

Gerado para Roberto Grécia Bessa — OAB/RO 7865-A.
"""
from __future__ import annotations

import asyncio
import contextlib
import html as _html
import json
import os
import re
import sys
import time
import unicodedata
from typing import Any

try:
    import fcntl  # POSIX (mac/Linux); ausente no Windows
except Exception:
    fcntl = None

# Usa o trust store do sistema operacional (macOS Keychain), assim como o curl — evita
# "self-signed certificate" quando há proxy TLS na rede.
try:
    import truststore

    truststore.inject_into_ssl()
except Exception:  # truststore é opcional; segue sem ele
    pass

try:
    import httpx
except Exception:  # permite importar o módulo para testes sem httpx instalado
    httpx = None  # type: ignore

# --------------------------------------------------------------------------- #
# Constantes do portal                                                         #
# --------------------------------------------------------------------------- #
SITE = "https://papyrus.tcero.tc.br"
ENDPOINT_BUSCAR = SITE + "/api/espelho/buscar"
ENDPOINT_RELATORES = SITE + "/api/busca/relatores"
# linkArquivo vem como //tce.ro.gov.br/AbrirPdfConvidado/<hash> — esse host redireciona (301)
# para tcero.tc.br, onde o PDF é servido de fato (confirmado ao vivo, 13/09/2026; ver
# references/protocolo-papyrus.md). O cliente HTTP precisa seguir redirect.
_RE_HOST_ANTIGO_PDF = re.compile(r"^(https?:)?//tce\.ro\.gov\.br", re.I)

## DECISÃO PESSOAL, NÃO REPLICAR EM PACOTE DISTRIBUÍDO ##
# User-Agent identificável, não de navegador: o portal não mostrou nenhum filtro de UA nas
# ~20 requisições de mapeamento (13/09/2026) — diferente do TRF1/TJRO, não há necessidade de
# se camuflar de navegador aqui. Mesmo assim, identificação clara é boa prática de acesso a
# API pública de terceiro.
HEADERS_BASE = {
    "User-Agent": "EscritorioRobertoGrecia-PesquisaJurisprudencia/1.0",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

# Órgãos julgadores: NÃO existe endpoint próprio de descoberta (procurado e não encontrado —
# ver references/protocolo-papyrus.md). Lista hardcoded extraída do bundle do frontend
# (app-busca.js, 13/09/2026); a API exige o valor EXATO, sem fuzzy match confirmado.
ORGAOS_JULGADORES_CONHECIDOS = ["1ª Câmara", "2ª Câmara", "Pleno"]

POR_PAGINA_PADRAO = 10
POR_PAGINA_MAX = 50
EMENTA_TRECHO = 600  # busca: ementa truncada no resumo compacto
ORCAMENTO_DETALHE = 40_000  # obter_acordao: teto de caracteres por decisão
TETO_DETALHAR_NA_BUSCA = 5  # quantos itens da página aceitam detalhar=true de uma vez

# Cache da resposta crua de uma consulta já feita (por processo, TTL curto): repetir a MESMA
# busca (ex.: só mudando a página) não deve rebaixar o mesmo payload de novo.
_CACHE_TTL_S = 5 * 60.0
_CACHE_MAX = 24
_cache_respostas: "dict[str, tuple[float, Any]]" = {}
# Cache separado (TTL mais longo) da lista de relatores — muda raramente.
_CACHE_RELATORES_TTL_S = 60 * 60.0
_cache_relatores: "tuple[float, list[dict]] | None" = None


def _cache_ler(chave: str):
    item = _cache_respostas.get(chave)
    if not item:
        return None
    quando, dados = item
    if time.time() - quando > _CACHE_TTL_S:
        _cache_respostas.pop(chave, None)
        return None
    return dados


def _cache_gravar(chave: str, dados) -> None:
    if len(_cache_respostas) >= _CACHE_MAX:
        _cache_respostas.pop(next(iter(_cache_respostas)), None)
    _cache_respostas[chave] = (time.time(), dados)


# --------------------------------------------------------------------------- #
# Funções puras (sem rede) — fáceis de testar                                  #
# --------------------------------------------------------------------------- #
def _fold(t: str) -> str:
    """Minúsculas sem acento: comparação sem caixa nem acento."""
    return "".join(
        c for c in unicodedata.normalize("NFD", (t or "").lower())
        if not unicodedata.category(c).startswith("M")
    )


def _so_digitos(nr: str) -> str:
    return re.sub(r"\D", "", nr or "")


def _html_para_texto(txt: str) -> str:
    """`informacoesAdicionais`, `veja` e `acordaoDescricao` vêm em HTML (o DEJUR gera com
    <p>/<ul>/<span> e entidades tipo &uacute;). Quebras de bloco viram '\n', tags somem,
    entidades são decodificadas."""
    if not txt:
        return ""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", txt)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", t)
    t = re.sub(r"(?i)<li[^>]*>", "- ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _html.unescape(t)
    t = re.sub(r"[ \t\r\xa0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def _truncar(t: str, limite: int) -> str:
    t = (t or "").strip()
    if limite and len(t) > limite:
        return t[:limite].rsplit(" ", 1)[0] + "…"
    return t


def _data_br(iso: str) -> str:
    """AAAA-MM-DDTHH:MM:SS... → DD/MM/AAAA ('' se vazio/não casar)."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", iso or "")
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}" if m else ""


def _corrigir_link_pdf(link: str) -> str:
    """//tce.ro.gov.br/... → https://tcero.tc.br/... (host antigo redireciona, mas ir direto
    ao host final evita depender do redirect ficar de pé para sempre — achado ao vivo,
    13/09/2026, ver references/protocolo-papyrus.md)."""
    if not link:
        return ""
    l = "https:" + link if link.startswith("//") else link
    return _RE_HOST_ANTIGO_PDF.sub("https://tcero.tc.br", l)


def _situacao_rotulo(situacao) -> str:
    """Só o valor 1 foi observado ao vivo (13/09/2026); qualquer outro é mostrado cru, sem
    inventar rótulo — 'não localizado' documentado em references/protocolo-papyrus.md."""
    if situacao == 1:
        return "1 (única situação observada em campo até 13/09/2026 — presumivelmente 'ativo/vigente', não confirmado pelo portal)"
    return f"{situacao!r} (valor não catalogado — ver references/protocolo-papyrus.md)"


def _citacao(s: dict) -> str:
    """Citação pronta para peça, padrão forense. Segmentos ausentes são omitidos.
    Ex.: (TCE-RO - APL-TC 00055/26, Rel. JOSÉ EULER..., Pleno, j. 29/06/2026, DOe 30/06/2026)"""
    rotulo = " ".join(x for x in (s.get("sigla"), s.get("numero")) if x) or f"decisão id {s.get('idDecisao')}"
    partes = [f"TCE-RO - {rotulo}"]
    if s.get("relator"):
        partes.append(f"Rel. {s['relator']}")
    if s.get("orgaoJulgador"):
        partes.append(s["orgaoJulgador"])
    dj = _data_br(s.get("dataSessao") or s.get("data") or "")
    if dj:
        partes.append(f"j. {dj}")
    ddoe = _data_br(s.get("dataDOE") or "")
    if ddoe:
        partes.append(f"DOe {ddoe}")
    return "(" + ", ".join(partes) + ")"


def _avisos_cancelamento_vinculo(s: dict) -> list[str]:
    """Campos nativos de cancelamento/vínculo do próprio portal — capacidade que TJRO e TRF1
    não têm pronta. Nenhuma das decisões amostradas ao vivo trouxe isso populado (ver
    references/protocolo-papyrus.md); a checagem fica pronta para quando aparecer um caso real."""
    avisos: list[str] = []
    if s.get("acordaoCanceladoId") or s.get("acordaoCancelado"):
        alvo = s.get("acordaoCanceladoId") or s.get("acordaoCancelado")
        avisos.append(f"⚠️ Este acórdão consta como CANCELADO no portal (acordaoCancelado{'Id' if s.get('acordaoCanceladoId') else ''}={alvo}) — não cite sem antes conferir o acórdão que o cancelou.")
    vinculos = s.get("vinculos") or []
    if isinstance(vinculos, list) and vinculos:
        avisos.append(f"⚠️ Há acórdão(s) vinculado(s) a esta decisão: {vinculos} — confira antes de citar isoladamente.")
    for campo, rotulo in (("acordaoVinculoPai", "acórdão-pai"), ("acordaoVinculoFilho", "acórdão-filho")):
        if s.get(campo):
            avisos.append(f"ℹ️ Vínculo de {rotulo}: id {s[campo]}.")
    mesmo_tema = s.get("mesmoTema") or []
    if isinstance(mesmo_tema, list) and mesmo_tema:
        avisos.append(f"ℹ️ O portal lista outro(s) acórdão(s) sobre o mesmo tema: {mesmo_tema} — considere conferir também.")
    return avisos


def _resumo_item(s: dict, indice: int) -> list[str]:
    linhas = [f"\n**{indice}. {s.get('sigla') or '?'} {s.get('numero') or '(sem número)'}** · id {s.get('idDecisao')}"]
    meta = []
    if s.get("processo"):
        meta.append(f"Processo: {s['processo']}")
    if s.get("relator"):
        meta.append(f"Relator: {s['relator']}")
    if s.get("orgaoJulgador"):
        meta.append(f"Órgão: {s['orgaoJulgador']}")
    dj = _data_br(s.get("dataSessao") or s.get("data") or "")
    if dj:
        meta.append(f"Sessão: {dj}")
    if s.get("resultado"):
        meta.append(f"Resultado: {s['resultado']}")
    if s.get("transitoEmJulgado"):
        meta.append("transitado em julgado" + (f" em {_data_br(s.get('dataTransitadoJulgado') or '')}" if s.get("dataTransitadoJulgado") else ""))
    linhas.append("  " + " · ".join(meta))
    linhas.append(f"  Citação: {_citacao(s)}")
    linhas.append(f"  Ementa (trecho): {_truncar(s.get('ementa') or '', EMENTA_TRECHO) or '—'}")
    for a in _avisos_cancelamento_vinculo(s):
        linhas.append(f"  {a}")
    return linhas


def _detalhe_item(s: dict) -> list[str]:
    linhas = [f"\n### {s.get('sigla') or '?'} {s.get('numero') or '(sem número)'} · id {s.get('idDecisao')}"]
    linhas.append(f"Citação: {_citacao(s)}")
    campos = []
    for chave, rotulo in (
        ("processo", "Processo"), ("natureza", "Natureza"), ("objeto", "Objeto"),
        ("assunto", "Assunto"), ("jurisdicionado", "Jurisdicionado"), ("votacao", "Votação"),
        ("resultado", "Resultado"), ("classificacao", "Classificação"),
    ):
        if s.get(chave):
            campos.append(f"{rotulo}: {s[chave]}")
    if campos:
        linhas.append("  " + " · ".join(campos))
    linhas.append(f"  Situação (campo `situacao`): {_situacao_rotulo(s.get('situacao'))}")
    if s.get("transitoEmJulgado"):
        linhas.append("  Trânsito em julgado: SIM" + (f" em {_data_br(s.get('dataTransitadoJulgado') or '')}" if s.get("dataTransitadoJulgado") else " (data não informada)"))
    else:
        linhas.append("  Trânsito em julgado: não informado como transitado")
    for a in _avisos_cancelamento_vinculo(s):
        linhas.append(a)
    ementa = (s.get("ementa") or "—").strip()
    if len(ementa) > ORCAMENTO_DETALHE:
        ementa = ementa[:ORCAMENTO_DETALHE].rsplit(" ", 1)[0] + "… [CORTADO pelo orçamento de caracteres]"
    linhas.append(f"\n**Ementa (integral, literal do portal):**\n{ementa}")
    disp = _html_para_texto(s.get("acordaoDescricao") or "")
    if disp:
        linhas.append(f"\n**Dispositivo (campo `acordaoDescricao`, literal):**\n{_truncar(disp, ORCAMENTO_DETALHE)}")
    else:
        linhas.append("\nDispositivo (`acordaoDescricao`): não informado pelo portal para esta decisão — use o `resultado` acima como rótulo curto, ou o inteiro teor em PDF.")
    info = _html_para_texto(s.get("informacoesAdicionais") or "")
    if info:
        linhas.append(
            "\n**Informações adicionais (⚠️ GERADO COM APOIO DE IA pelo DEJUR do TCE-RO, "
            "com revisão da equipe técnica do tribunal — NUNCA usar como fonte primária "
            "sozinha; confira sempre contra a ementa/dispositivo e, se possível, o inteiro "
            "teor):**\n" + _truncar(info, ORCAMENTO_DETALHE)
        )
    veja = _html_para_texto(s.get("veja") or "")
    if veja:
        linhas.append(f"\n**Legislação aplicada / veja também (campo `veja`, literal):**\n{_truncar(veja, ORCAMENTO_DETALHE)}")
    link = _corrigir_link_pdf(s.get("linkArquivo") or "")
    if link:
        linhas.append(f"\nInteiro teor (PDF): {link} — confirmado baixável sem login (13/09/2026).")
    else:
        linhas.append("\nInteiro teor: link não informado pelo portal para esta decisão.")
    linhas.append(
        "\n---\nPara a ficha de precedente: `tribunal: \"TCE-RO\"`, `id_documento` = id acima, "
        "`julgamento` em ISO, `ementa`/`dispositivo` literais (cortes com [...]). O dispositivo "
        "real é `acordaoDescricao` quando presente — `resultado` é só um rótulo curto. As "
        "\"informações adicionais\" são conteúdo de IA do próprio tribunal: nunca citar como se "
        "fossem o texto do acórdão; \"inteiro teor lido\" só depois de abrir o PDF."
    )
    return linhas


def _verificar_trecho(textos: dict[str, str], trecho: str) -> dict:
    """Mesmo padrão dos irmãos: `[...]` separa fragmentos que devem aparecer em ordem;
    tolerante a caixa/acento/pontuação/espaço, intolerante a palavra trocada ou omitida."""
    def _normalizar(t: str) -> str:
        t = _fold(t or "")
        t = re.sub(r"[^\w\s]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    fragmentos = [f for f in (x.strip() for x in re.split(r"\[\s*\.\.\.\s*\]|\[…\]|…", trecho or "")) if f]
    if not fragmentos:
        return {"valido": False, "onde": None, "faltando": [], "motivo": "trecho vazio"}
    faltando_por_texto: dict[str, list[str]] = {}
    for nome, texto in textos.items():
        alvo = _normalizar(texto)
        if not alvo:
            continue
        pos, faltando = 0, []
        for frag in fragmentos:
            f = _normalizar(frag)
            i = alvo.find(f, pos)
            if i < 0:
                faltando.append(frag)
            else:
                pos = i + len(f)
        if not faltando:
            return {"valido": True, "onde": nome, "faltando": [], "motivo": f"trecho encontrado literalmente em: {nome}"}
        faltando_por_texto[nome] = faltando
    melhor = min(faltando_por_texto.items(), key=lambda kv: len(kv[1]))[1] if faltando_por_texto else fragmentos
    return {"valido": False, "onde": None, "faltando": melhor,
            "motivo": "trecho NÃO encontrado literalmente — não cite entre aspas; parafraseie ou corrija"}


# --------------------------------------------------------------------------- #
# Controle de ritmo — disjuntor em arquivo, compartilhado entre processos      #
# (mesmo padrão de TJRO/TRF1: cada sessão do Claude sobe seu próprio processo  #
# deste servidor; estado em arquivo sob trava para todos dividirem o mesmo     #
# orçamento. Números abaixo são um DEFAULT DEFENSIVO genérico — o portal do    #
# TCE-RO não mostrou nenhum bloqueio nas ~20 requisições de mapeamento         #
# (13/09/2026); não há rate limit documentado nem observado para calibrar,    #
# então a escada é mais generosa que a do TJRO/TRF1 (que já viram bloqueio de  #
# verdade) e só aperta se um bloqueio REAL acontecer.)                        #
# --------------------------------------------------------------------------- #
_JANELA_MAX_REQS = 40
_ESCADA_JANELA_S = [60.0, 5 * 60.0, 10 * 60.0, 20 * 60.0, 30 * 60.0]
_SUCESSOS_PARA_RELAXAR = 100
_BACKOFF_INICIAL_S = 5 * 60.0
_BACKOFF_MAXIMO_S = 60 * 60.0
_ESPACAMENTO_MIN_S = 1.0
_ESPERA_MAXIMA_S = 30.0
_TENTATIVAS_MAX = 3  # backoff exponencial curto em erro de rede/5xx

_ARQUIVO_ESTADO_DISJUNTOR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".disjuntor_estado_tcero.json"
)

_ESTADO_PADRAO: dict[str, Any] = {
    "versao": 1,
    "requisicoes": [],
    "proximo_livre_em": 0.0,
    "bloqueado_ate": 0.0,
    "indice_janela": 0,
    "sucessos": 0,
    "backoff_s": _BACKOFF_INICIAL_S,
    "incidentes": [],
    "ultima_requisicao_em": 0.0,
    "total_requisicoes": 0,
}
_MAX_INCIDENTES = 20


@contextlib.contextmanager
def _trava_estado():
    f = None
    try:
        if fcntl is not None:
            f = open(_ARQUIVO_ESTADO_DISJUNTOR + ".lock", "w")
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    except Exception:
        f = None
    try:
        yield
    finally:
        if f is not None:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                f.close()
            except Exception:
                pass


def _ler_estado() -> dict[str, Any]:
    estado = dict(_ESTADO_PADRAO)
    try:
        with open(_ARQUIVO_ESTADO_DISJUNTOR, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception:
        return estado
    estado.update({k: v for k, v in dados.items() if k in _ESTADO_PADRAO})
    agora = time.time()

    def _num(v, padrao: float) -> float:
        try:
            n = float(v)
            return n if n == n and n not in (float("inf"), float("-inf")) else padrao
        except Exception:
            return padrao

    margem = _ESPERA_MAXIMA_S + _ESPACAMENTO_MIN_S
    reqs = estado.get("requisicoes") or []
    estado["requisicoes"] = [
        float(t) for t in reqs if isinstance(t, (int, float)) and float(t) <= agora + margem
    ]
    estado["proximo_livre_em"] = min(_num(estado.get("proximo_livre_em"), 0.0), agora + margem)
    estado["bloqueado_ate"] = max(0.0, min(_num(estado.get("bloqueado_ate"), 0.0), agora + _BACKOFF_MAXIMO_S))
    estado["indice_janela"] = max(0, min(int(_num(estado.get("indice_janela"), 0)), len(_ESCADA_JANELA_S) - 1))
    estado["backoff_s"] = max(_BACKOFF_INICIAL_S, min(_num(estado.get("backoff_s"), _BACKOFF_INICIAL_S), _BACKOFF_MAXIMO_S))
    inc = estado.get("incidentes")
    estado["incidentes"] = inc[-_MAX_INCIDENTES:] if isinstance(inc, list) else []
    return estado


_estado_memoria: dict | None = None
_persistencia_indisponivel: str | None = None


def _transacao(fn):
    global _estado_memoria, _persistencia_indisponivel
    with _trava_estado():
        if _persistencia_indisponivel and _estado_memoria is not None:
            estado = _estado_memoria
        else:
            estado = _ler_estado()
        resultado = fn(estado)
        try:
            tmp = f"{_ARQUIVO_ESTADO_DISJUNTOR}.{os.getpid()}.tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(estado, f)
            os.replace(tmp, _ARQUIVO_ESTADO_DISJUNTOR)
            _persistencia_indisponivel = None
            _estado_memoria = None
        except Exception as e:
            _persistencia_indisponivel = getattr(e, "strerror", None) or type(e).__name__
            _estado_memoria = estado
        return resultado


def _fmt_hms(segundos: float) -> str:
    segundos = max(0, int(segundos))
    m, s = divmod(segundos, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}min" if m else f"{h}h"
    if m:
        return f"{m}min{s:02d}s" if s else f"{m}min"
    return f"{s}s"


def _reservar_requisicao(agora: float | None = None) -> dict:
    agora = time.time() if agora is None else agora

    def _decidir(e: dict) -> dict:
        if agora < e["bloqueado_ate"]:
            return {"erro": (
                "O portal do TCE-RO (ePapyrus) recusou uma consulta recente (ou houve erro de "
                "rede repetido); para não insistir, esta ferramenta está evitando novas "
                f"tentativas por mais {_fmt_hms(e['bloqueado_ate'] - agora)}. Enquanto isso, o "
                "portal papyrus.tcero.tc.br segue acessível no navegador."
            )}
        janela = _ESCADA_JANELA_S[e["indice_janela"]]
        e["requisicoes"] = [t for t in e["requisicoes"] if agora - t <= janela]
        if len(e["requisicoes"]) >= _JANELA_MAX_REQS:
            espera = janela - (agora - e["requisicoes"][0])
            return {"erro": (
                f"Muitas consultas em pouco tempo (limite atual: {_JANELA_MAX_REQS} requisições a cada "
                f"{_fmt_hms(janela)}, compartilhado por todos os processos desta extensão nesta máquina). "
                f"Aguarde {_fmt_hms(espera)} e tente de novo."
            )}
        vaga = max(agora, e["proximo_livre_em"])
        esperar = vaga - agora
        if esperar > _ESPERA_MAXIMA_S:
            return {"erro": (
                f"Fila de espera longa demais ({_fmt_hms(esperar)}) — há consultas demais em "
                "andamento em paralelo. Refaça a busca daqui a pouco, de preferência uma por vez."
            )}
        e["proximo_livre_em"] = vaga + _ESPACAMENTO_MIN_S
        e["requisicoes"].append(vaga)
        e["ultima_requisicao_em"] = vaga
        e["total_requisicoes"] = int(e.get("total_requisicoes", 0)) + 1
        return {"esperar_s": esperar}

    return _transacao(_decidir)


def _registrar_bloqueio_detectado(agora: float | None = None, operacao: str = "?",
                                   subir_escada: bool = True, espera_minima_s: float = 0.0) -> None:
    agora = time.time() if agora is None else agora

    def _aplicar(e: dict) -> None:
        reqs = e.get("requisicoes") or []
        janela = _ESCADA_JANELA_S[e["indice_janela"]]
        anteriores = e.get("incidentes") or []
        e["incidentes"] = (anteriores + [{
            "quando": agora,
            "operacao": operacao,
            "nivel": e["indice_janela"],
            "janela_s": int(janela),
            "reqs_ultimos_60s": len([t for t in reqs if agora - t <= 60]),
            "reqs_na_janela": len([t for t in reqs if agora - t <= janela]),
            "desde_ultima_req_s": int(agora - e["ultima_requisicao_em"]) if e.get("ultima_requisicao_em") else None,
        }])[-_MAX_INCIDENTES:]
        e["bloqueado_ate"] = agora + max(e["backoff_s"], espera_minima_s)
        e["backoff_s"] = min(e["backoff_s"] * 2, _BACKOFF_MAXIMO_S)
        if subir_escada and e["indice_janela"] < len(_ESCADA_JANELA_S) - 1:
            e["indice_janela"] += 1
        e["sucessos"] = 0

    _transacao(_aplicar)


def _registrar_sucesso() -> None:
    def _aplicar(e: dict) -> None:
        e["backoff_s"] = _BACKOFF_INICIAL_S
        e["sucessos"] += 1
        if e["sucessos"] >= _SUCESSOS_PARA_RELAXAR:
            e["sucessos"] = 0
            if e["indice_janela"] > 0:
                e["indice_janela"] -= 1

    _transacao(_aplicar)


def _diagnostico_ritmo(agora: float | None = None) -> str:
    agora = time.time() if agora is None else agora
    with _trava_estado():
        e = _ler_estado()
    janela = _ESCADA_JANELA_S[e["indice_janela"]]
    na_janela = len([t for t in (e.get("requisicoes") or []) if agora - t <= janela])
    linhas = [
        "**Controle de ritmo do MCP TCE-RO (portal ePapyrus)**",
        f"- Nível atual: {e['indice_janela'] + 1} de {len(_ESCADA_JANELA_S)} "
        f"(limite: {_JANELA_MAX_REQS} requisições a cada {_fmt_hms(janela)})",
        f"- Orçamento usado agora: {na_janela}/{_JANELA_MAX_REQS} nesta janela",
        f"- Requisições desde o início (nesta máquina): {e.get('total_requisicoes', 0)}",
        (
            f"- ⚠️ BLOQUEADO (auto-imposto) — liberando em {_fmt_hms(e['bloqueado_ate'] - agora)}"
            if agora < e["bloqueado_ate"] else "- Situação: liberado"
        ),
        "- Nota: o portal do TCE-RO não mostrou WAF/captcha/bloqueio em nenhum teste até "
        "13/09/2026 — estes limites são um teto defensivo desta ferramenta, não um limite "
        "documentado pelo tribunal.",
    ]
    if _persistencia_indisponivel:
        linhas.insert(1, (
            f"- ⚠️ AVISO: não foi possível gravar {_ARQUIVO_ESTADO_DISJUNTOR} "
            f"({_persistencia_indisponivel}) — o orçamento NÃO está sendo compartilhado entre processos."
        ))
    inc = e.get("incidentes") or []
    if not inc:
        linhas.append("\nNenhum incidente registrado até agora nesta máquina.")
        return "\n".join(linhas)
    linhas.append(f"\n**Incidentes registrados: {len(inc)}** (mais recentes primeiro)")
    for i in list(reversed(inc))[:8]:
        quando = time.strftime("%Y-%m-%d %H:%M", time.localtime(i["quando"]))
        linhas.append(
            f"- {quando} · {i['reqs_ultimos_60s']} requisições no minuto anterior, "
            f"{i['reqs_na_janela']} na janela de {_fmt_hms(i['janela_s'])} · operação: {i['operacao']}"
        )
    return "\n".join(linhas)


# --------------------------------------------------------------------------- #
# Camada HTTP                                                                  #
# --------------------------------------------------------------------------- #
class PortalRecusou(RuntimeError):
    """Erro persistente do portal (5xx repetido, ou HTTP 403/429) — já registrado no disjuntor."""


async def _get_com_retentativa(cli: "httpx.AsyncClient", url: str, params: dict, operacao: str) -> httpx.Response:
    """GET com o disjuntor + backoff exponencial curto em erro de rede/5xx (poucas tentativas,
    como pedido — este portal não mostrou WAF, então o cuidado aqui é robustez genérica, não
    bypass de bloqueio)."""
    ultimo_erro: Exception | None = None
    for tentativa in range(_TENTATIVAS_MAX):
        reserva = _reservar_requisicao()
        if "erro" in reserva:
            raise RuntimeError(reserva["erro"])
        if reserva["esperar_s"] > 0:
            await asyncio.sleep(reserva["esperar_s"])
        try:
            r = await cli.get(url, params=params)
        except Exception as e:  # timeout, conexão recusada, DNS...
            ultimo_erro = e
            if tentativa < _TENTATIVAS_MAX - 1:
                await asyncio.sleep(2.0 * (tentativa + 1))
                continue
            _registrar_bloqueio_detectado(operacao=operacao, subir_escada=False)
            raise PortalRecusou(f"Falha de rede repetida ao consultar o portal do TCE-RO ({type(e).__name__}: {e}).") from e
        if r.status_code in (403, 429) or r.status_code >= 500:
            try:
                espera_minima = float(r.headers.get("retry-after") or 0)
            except ValueError:
                espera_minima = 0.0
            if r.status_code >= 500 and tentativa < _TENTATIVAS_MAX - 1:
                await asyncio.sleep(2.0 * (tentativa + 1))
                continue
            _registrar_bloqueio_detectado(operacao=operacao, subir_escada=(r.status_code in (403, 429)), espera_minima_s=espera_minima)
            raise PortalRecusou(
                f"O portal do TCE-RO respondeu HTTP {r.status_code} de forma persistente "
                "(bloqueio, recusa explícita, ou instabilidade do lado do tribunal). O portal "
                "papyrus.tcero.tc.br segue acessível no navegador."
            )
        _registrar_sucesso()
        return r
    raise PortalRecusou(f"Falha de rede repetida ao consultar o portal do TCE-RO: {ultimo_erro}")


async def _consultar_api(params: dict, operacao: str) -> dict:
    """GET em /api/espelho/buscar, com cache por processo (chave = params ordenados)."""
    if httpx is None:
        raise RuntimeError("pacote 'httpx' não instalado")
    chave = json.dumps(sorted(params.items()), ensure_ascii=False)
    em_cache = _cache_ler(chave)
    if em_cache is not None:
        return em_cache
    async with httpx.AsyncClient(timeout=45.0, follow_redirects=True, headers=HEADERS_BASE) as cli:
        r = await _get_com_retentativa(cli, ENDPOINT_BUSCAR, params, operacao)
        try:
            dados = r.json()
        except Exception as e:
            raise RuntimeError(f"O portal respondeu algo que não é JSON válido (HTTP {r.status_code}): {e}") from e
    if not isinstance(dados, dict) or "result" not in dados:
        raise RuntimeError("Resposta do portal em formato inesperado (sem a chave 'result') — o portal pode ter mudado de layout.")
    _cache_gravar(chave, dados)
    return dados


async def _relatores_conhecidos(operacao: str) -> list[dict]:
    """Lista de {id, nome} de /api/busca/relatores, cacheada por 1h. O `id` não serve para
    filtrar a busca (achado ao vivo — ver references/protocolo-papyrus.md); serve só para
    resolver, por aproximação de nome, o que o usuário quis dizer."""
    global _cache_relatores
    if _cache_relatores is not None and time.time() - _cache_relatores[0] <= _CACHE_RELATORES_TTL_S:
        return _cache_relatores[1]
    if httpx is None:
        return []
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=HEADERS_BASE) as cli:
        try:
            r = await _get_com_retentativa(cli, ENDPOINT_RELATORES, {}, operacao)
            lista = r.json()
        except Exception:
            return _cache_relatores[1] if _cache_relatores else []
    if not isinstance(lista, list):
        return _cache_relatores[1] if _cache_relatores else []
    _cache_relatores = (time.time(), lista)
    return lista


async def _resolver_relator(relator: str, operacao: str) -> tuple[str, str | None]:
    """A API exige o NOME EXATO do relator (não o id, não substring — achado ao vivo). Aqui
    tentamos aproximar por fold (sem caixa/acento) contra a lista conhecida; se não achar,
    manda o valor como veio e avisa que pode não bater exatamente."""
    alvo = _fold(relator)
    lista = await _relatores_conhecidos(operacao)
    for item in lista:
        nome = item.get("nome") or ""
        if _fold(nome) == alvo:
            return nome, None
    for item in lista:
        nome = item.get("nome") or ""
        if alvo and alvo in _fold(nome):
            return nome, f"relator {relator!r} não bateu exatamente com a lista conhecida — usando {nome!r} (nome mais próximo encontrado)"
    return relator, (
        f"relator {relator!r} não está na lista de {len(lista)} nome(s) que o portal expõe em "
        "/api/busca/relatores (pode ser uma lista parcial/desatualizada); a busca exige o nome "
        "EXATO — se vier zero resultado, confira grafia e acentuação"
    )


def _resolver_orgao(orgao: str) -> tuple[str, str | None]:
    alvo = _fold(orgao)
    for conhecido in ORGAOS_JULGADORES_CONHECIDOS:
        if _fold(conhecido) == alvo:
            return conhecido, None
    return orgao, (
        f"orgao_julgador {orgao!r} não é um dos {ORGAOS_JULGADORES_CONHECIDOS} (única lista "
        "encontrada, hardcoded no frontend do portal — não há endpoint de descoberta); a busca "
        "exige o valor EXATO — se vier zero resultado, é provável que seja isso"
    )


# --------------------------------------------------------------------------- #
# Implementação das ferramentas                                                #
# --------------------------------------------------------------------------- #
async def _buscar(texto_livre: str | None, numero_acordao: str | None, numero_processo: str | None,
                  relator: str | None, orgao_julgador: str | None, pagina: int, por_pagina: int,
                  detalhar: bool) -> str:
    avisos: list[str] = []
    params: dict[str, str] = {}
    if texto_livre and texto_livre.strip():
        params["textoLivre"] = texto_livre.strip()
    if numero_acordao and numero_acordao.strip():
        params["numeroAcordao"] = numero_acordao.strip()
    if numero_processo and numero_processo.strip():
        params["numeroProcesso"] = numero_processo.strip()
    try:
        if relator and relator.strip():
            nome, aviso = await _resolver_relator(relator.strip(), "busca")
            params["relatores"] = nome
            if aviso:
                avisos.append(aviso)
        if orgao_julgador and orgao_julgador.strip():
            nome_o, aviso_o = _resolver_orgao(orgao_julgador.strip())
            params["orgaosJulgadores"] = nome_o
            if aviso_o:
                avisos.append(aviso_o)
        if not params:
            return ("Informe pelo menos um critério: texto_livre, numero_acordao, numero_processo, "
                    "relator ou orgao_julgador. Uma busca sem nenhum filtro devolveria o acervo inteiro.")
        pagina = max(1, int(pagina or 1))
        por_pagina = int(por_pagina or POR_PAGINA_PADRAO)
        if not (1 <= por_pagina <= POR_PAGINA_MAX):
            raise ValueError(f"por_pagina inválido: {por_pagina}; use de 1 a {POR_PAGINA_MAX}")
        if detalhar and por_pagina > TETO_DETALHAR_NA_BUSCA:
            avisos.append(
                f"detalhar=true só se aplica aos primeiros {TETO_DETALHAR_NA_BUSCA} itens desta "
                f"página (pedidos: {por_pagina}) — para os demais, use obter_acordao_tcero(id_decisao=...)"
            )
        dados = await _consultar_api(params, "busca")
    except (ValueError, RuntimeError, PortalRecusou) as e:
        return f"Erro na consulta ao TCE-RO: {e}"
    except Exception as e:
        return f"Erro ao consultar o portal do TCE-RO ({type(e).__name__}): {e}"

    todos = dados.get("result") or []
    total = len(todos)
    inicio = (pagina - 1) * por_pagina
    pagina_itens = todos[inicio: inicio + por_pagina]
    total_paginas = max(1, -(-total // por_pagina)) if total else 1

    linhas: list[str] = []
    filtros_txt = "; ".join(f"{k}={v}" for k, v in params.items())
    cab = f"**{total} decisão(ões)** no portal ePapyrus/TCE-RO para `{filtros_txt}` · página {pagina}/{total_paginas} ({por_pagina} por página)"
    linhas.append(cab)
    for a in avisos:
        linhas.append(f"⚠️ {a}")
    if total > 200 and pagina == 1:
        linhas.append(
            "Dica: total alto — a API do TCE-RO não pagina no servidor (tudo já foi baixado e "
            "cacheado aqui por alguns minutos); restrinja com número de processo/acórdão, "
            "relator ou órgão julgador para uma busca mais direta."
        )
    if not pagina_itens:
        linhas.append("\nNenhuma decisão nesta página." + (" A busca casa palavras/valores; confira grafia, acentuação e se o total acima é 0." if total == 0 else " A página pedida está além do fim."))
        return "\n".join(linhas)

    for i, item in enumerate(pagina_itens, start=inicio + 1):
        s = item.get("source") or {}
        if detalhar and (i - (inicio + 1)) < TETO_DETALHAR_NA_BUSCA:
            linhas.extend(_detalhe_item(s))
        else:
            linhas.extend(_resumo_item(s, i))
    if not detalhar:
        linhas.append(
            "\nEmentas truncadas. Para o texto integral, dispositivo, informações adicionais e "
            "link do PDF de um item específico: obter_acordao_tcero(id_decisao=<id acima>)."
        )
    if total > pagina * por_pagina:
        linhas.append(f"\nPróxima página: pagina={pagina + 1} (mesmos parâmetros).")
    return "\n".join(linhas)


async def _obter_acordao(id_decisao: int | str | None, numero_acordao: str | None, numero_processo: str | None) -> str:
    if not id_decisao and not numero_acordao and not numero_processo:
        return "Informe id_decisao (mais direto), ou numero_acordao, ou numero_processo."
    try:
        if id_decisao:
            dados = await _consultar_api({"IdDecisao": str(id_decisao).strip(), "filtrarResultados": "false"}, "detalhe")
        else:
            params = {}
            if numero_acordao:
                params["numeroAcordao"] = numero_acordao.strip()
            if numero_processo:
                params["numeroProcesso"] = numero_processo.strip()
            dados = await _consultar_api(params, "detalhe")
    except (ValueError, RuntimeError, PortalRecusou) as e:
        return f"Erro na consulta ao TCE-RO: {e}"
    except Exception as e:
        return f"Erro ao consultar o portal do TCE-RO ({type(e).__name__}): {e}"

    resultados = dados.get("result") or []
    if not resultados:
        alvo = id_decisao or numero_acordao or numero_processo
        return f"Nenhuma decisão encontrada para {alvo!r} no portal do TCE-RO. Confira o número/id."
    linhas: list[str] = []
    if len(resultados) > 1:
        linhas.append(
            f"**{len(resultados)} decisões encontradas** sob esse número — o mesmo número de "
            "acórdão pode ter mais de um `idDecisao` no portal (achado real, 13/09/2026). "
            "Identifique pelo id antes de citar:"
        )
        for item in resultados:
            s = item.get("source") or {}
            linhas.append(f"- id {s.get('idDecisao')} · {_data_br(s.get('data') or '')} · Rel. {s.get('relator') or '?'} · {s.get('orgaoJulgador') or '?'}")
        linhas.append("\nChame de novo com obter_acordao_tcero(id_decisao=<id acima>) para o detalhe de cada um. Mostrando o primeiro:")
    s0 = (resultados[0].get("source") or {})
    linhas.extend(_detalhe_item(s0))
    return "\n".join(linhas)


async def _verificar_citacao(id_decisao: int | str | None, numero_acordao: str | None, trecho: str) -> str:
    if not (trecho or "").strip():
        return "Informe o trecho que pretende citar entre aspas."
    if not id_decisao and not numero_acordao:
        return "Informe id_decisao (preferível) ou numero_acordao."
    try:
        if id_decisao:
            dados = await _consultar_api({"IdDecisao": str(id_decisao).strip(), "filtrarResultados": "false"}, "verificacao")
        else:
            dados = await _consultar_api({"numeroAcordao": numero_acordao.strip()}, "verificacao")
    except (ValueError, RuntimeError, PortalRecusou) as e:
        return f"Erro na consulta ao TCE-RO: {e}"
    except Exception as e:
        return f"Erro ao consultar o portal do TCE-RO ({type(e).__name__}): {e}"

    resultados = dados.get("result") or []
    if not resultados:
        alvo = id_decisao or numero_acordao
        return f"Nenhuma decisão sob {alvo!r} — não há como verificar; não cite."
    linhas = []
    for item in resultados:
        s = item.get("source") or {}
        textos = {
            "ementa": s.get("ementa") or "",
            "dispositivo (acordaoDescricao)": _html_para_texto(s.get("acordaoDescricao") or ""),
        }
        r = _verificar_trecho(textos, trecho)
        marca = "✅ VÁLIDO" if r["valido"] else "❌ NÃO ENCONTRADO"
        linhas.append(f"{marca} · id {s.get('idDecisao')} · {s.get('sigla') or '?'} {s.get('numero') or '?'} · {r['motivo']}")
        if not r["valido"] and r["faltando"]:
            for f in r["faltando"][:3]:
                linhas.append(f"   fragmento sem correspondência: «{f[:160]}»")
    rodape = (
        "\nCobre ementa e dispositivo (`acordaoDescricao`, quando o portal o preenche) — NÃO o "
        "inteiro teor em PDF nem as \"informações adicionais\" (geradas por IA, não citáveis "
        "como texto do acórdão). Comparação tolerante a caixa, acento, pontuação e espaço; "
        "`[...]` separa fragmentos em ordem. Se ❌: não cite entre aspas — parafraseie, ou "
        "confira o inteiro teor no PDF."
    )
    return "\n".join(linhas) + rodape


# --------------------------------------------------------------------------- #
# Registro das ferramentas MCP                                                 #
# --------------------------------------------------------------------------- #
try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("Jurisprudência TCE-RO")

    @mcp.tool()
    async def buscar_jurisprudencia_tcero(
        texto_livre: str = "",
        numero_acordao: str | None = None,
        numero_processo: str | None = None,
        relator: str | None = None,
        orgao_julgador: str | None = None,
        pagina: int = 1,
        por_pagina: int = 10,
        detalhar: bool = False,
    ) -> str:
        """Pesquisa jurisprudência do TCE-RO (Tribunal de Contas do Estado de Rondônia) no portal
        oficial ePapyrus (papyrus.tcero.tc.br), sem login.

        É a fonte dos precedentes de controle externo em Rondônia — licitação, prestação de
        contas, responsabilização de gestor, imputação de multa/débito, atos de pessoal sujeitos
        a registro. Informe pelo menos um critério (texto_livre, numero_acordao, numero_processo,
        relator ou orgao_julgador); uma chamada sem nenhum devolveria o acervo inteiro.

        A API do portal NÃO pagina no servidor — devolve todos os resultados da consulta de uma
        vez (já visto: dezenas de milhares de caracteres em consultas amplas). Esta ferramenta
        pagina no CLIENTE (parâmetros pagina/por_pagina) e cacheia a resposta crua por alguns
        minutos, para trocar de página sem rebaixar tudo de novo. Por padrão devolve um resumo
        compacto (ementa truncada); use detalhar=true (só para os primeiros
        5 itens da página) ou obter_acordao_tcero para o texto integral.

        Args:
            texto_livre: Busca por texto no corpo/ementa. Aceita "frase exata" entre aspas e `+`
                para E (AND) — ex.: "dispensa+de+licitação". Sintaxe do próprio portal, pouco
                documentada; teste e ajuste se o resultado não vier como esperado.
            numero_acordao: Número do acórdão (ex.: "00055/26"). Pode haver mais de uma decisão
                (id diferente) sob o mesmo número — o TCE-RO já mostrou isso ao vivo.
            numero_processo: Número do processo administrativo (ex.: "02603/22").
            relator: Nome do relator. A API exige o NOME EXATO (sem tolerância a abreviação ou
                substring, confirmado ao vivo) — se vier zero resultado, confira grafia e acento;
                esta ferramenta tenta aproximar pela lista de /api/busca/relatores antes de
                enviar, e avisa quando não achou correspondência exata.
            orgao_julgador: Um dos valores EXATOS que o portal aceita: "1ª Câmara", "2ª Câmara"
                ou "Pleno" (lista fechada, hardcoded no frontend — não há endpoint de descoberta;
                se existir outro valor histórico, não foi localizado).
            pagina: Página de resultados (1+), sobre o array já recebido do portal.
            por_pagina: Itens por página (1 a 50). Padrão 10 — mantenha baixo em buscas amplas.
            detalhar: Se true, os primeiros itens desta página (até 5) vêm com ementa integral,
                dispositivo, informações adicionais (⚠️ geradas por IA) e link do PDF — o mesmo
                que obter_acordao_tcero traria, mas embutido na busca. Use com poucos itens por
                página para não estourar o contexto.

        Returns:
            Cabeçalho com o total real e os filtros usados; por decisão: sigla+número, id
            (chave para obter_acordao_tcero/verificar_citacao_tcero), processo, relator, órgão,
            data da sessão, resultado, citação pronta no padrão "(TCE-RO - SIGLA nº, Rel. ...,
            ÓRGÃO, j. DD/MM/AAAA, DOe DD/MM/AAAA)", ementa (trecho ou integral conforme
            detalhar), e aviso quando o próprio portal marca a decisão como cancelada ou
            vinculada a outra.
        """
        return await _buscar(texto_livre, numero_acordao, numero_processo, relator, orgao_julgador, pagina, por_pagina, detalhar)

    @mcp.tool()
    async def obter_acordao_tcero(
        id_decisao: int | str | None = None,
        numero_acordao: str | None = None,
        numero_processo: str | None = None,
    ) -> str:
        """Traz o detalhe COMPLETO de uma decisão do TCE-RO: ementa integral, dispositivo
        (`acordaoDescricao`, quando o portal o preenche), informações adicionais e legislação
        aplicada, link do inteiro teor em PDF, e avisos nativos do portal sobre cancelamento ou
        vínculo com outro acórdão.

        Use antes de citar qualquer decisão devolvida por buscar_jurisprudencia_tcero. Prefira
        id_decisao (busca direta pelo id, resposta menor e mais rápida); numero_acordao/
        numero_processo fazem uma busca normal e podem trazer mais de uma decisão sob o mesmo
        número — nesse caso a ferramenta lista os ids e mostra o detalhe do primeiro.

        ⚠️ O campo "informações adicionais" (Fatos/Questão Jurídica/Regras/Análise/Conclusão/
        Leitura Estratégica) é GERADO COM APOIO DE IA pelo DEJUR do próprio TCE-RO, com revisão
        da equipe técnica — mas não é o texto do acórdão. NUNCA tratar como fonte primária
        isolada: confira sempre contra a ementa/dispositivo e, quando possível, o inteiro teor.

        Args:
            id_decisao: Id numérico da decisão (`idDecisao`) — o jeito mais direto e confiável.
            numero_acordao: Número do acórdão (ex.: "00055/26"), se não tiver o id.
            numero_processo: Número do processo administrativo, se não tiver o id nem o
                número do acórdão (menos preciso — pode trazer várias decisões do mesmo processo).

        Returns:
            Citação pronta, metadados (processo, natureza, objeto, assunto, jurisdicionado,
            votação, resultado, situação), avisos de cancelamento/vínculo quando presentes,
            ementa integral, dispositivo integral, informações adicionais (com o aviso de IA),
            legislação aplicada e link do PDF do inteiro teor. Saída limitada a ~40 mil
            caracteres por decisão.
        """
        return await _obter_acordao(id_decisao, numero_acordao, numero_processo)

    @mcp.tool()
    async def verificar_citacao_tcero(
        trecho: str,
        id_decisao: int | str | None = None,
        numero_acordao: str | None = None,
    ) -> str:
        """Confere se um trecho aparece LITERALMENTE na ementa ou no dispositivo
        (`acordaoDescricao`) de uma decisão do TCE-RO, antes de ir entre aspas para a peça.

        USE antes de qualquer citação direta. Comparação tolerante a caixa, acento, pontuação e
        espaço; intolerante a palavra trocada ou omitida. `[...]` no trecho separa fragmentos
        que devem aparecer nessa ordem. Se vier ❌, não cite entre aspas: parafraseie (sem aspas)
        ou confira o inteiro teor em PDF. NÃO cobre as "informações adicionais" (conteúdo de IA,
        nunca citável como texto do acórdão) nem o inteiro teor em PDF (este servidor não lê PDF).

        Args:
            trecho: Texto que se pretende citar entre aspas (cortes marcados com [...]).
            id_decisao: Id numérico da decisão — preferível (mais direto).
            numero_acordao: Número do acórdão, se não tiver o id (pode haver mais de uma
                decisão sob o mesmo número; todas são conferidas).

        Returns:
            Por decisão encontrada: ✅/❌, onde foi encontrado (ementa ou dispositivo), e os
            fragmentos sem correspondência quando falhar.
        """
        return await _verificar_citacao(id_decisao, numero_acordao, trecho)

    @mcp.tool()
    async def diagnostico_ritmo_tcero() -> str:
        """Mostra por que as buscas do TCE-RO podem estar falhando.

        Relata o nível atual do limite de ritmo (auto-imposto — o portal do TCE-RO não
        documenta nem, até agora, mostrou nenhum rate limit próprio), o orçamento consumido, se
        há bloqueio em curso e o histórico de incidentes. Não faz nenhuma requisição.
        """
        return _diagnostico_ritmo()

    _HAS_MCP = True
except Exception as _erro_mcp:  # permite importar o módulo (testes) sem o pacote mcp instalado
    # Nunca silenciar (lição herdada do TRF1, 11/09/2026: erro de registro engolido aqui culpou
    # "pacote não instalado" com o pacote instalado).
    import traceback as _tb

    print(f"[servidor_tcero] registro MCP falhou: {type(_erro_mcp).__name__}: {_erro_mcp}", file=sys.stderr)
    _tb.print_exc(file=sys.stderr)
    mcp = None
    _HAS_MCP = False


# --------------------------------------------------------------------------- #
# Ponto de entrada                                                             #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import tempfile as _tempfile

        base = os.path.dirname(os.path.abspath(__file__))
        fx = os.path.join(base, "fixtures")

        def _ler(nome: str) -> dict:
            with open(os.path.join(fx, nome), encoding="utf-8") as f:
                return json.load(f)

        # --- 1. funções puras ---
        assert _data_br("2026-06-29T12:11:00") == "29/06/2026"
        assert _data_br("") == "" and _data_br("lixo") == ""
        assert _corrigir_link_pdf("//tce.ro.gov.br/AbrirPdfConvidado/abc123") == "https://tcero.tc.br/AbrirPdfConvidado/abc123"
        assert _corrigir_link_pdf("") == ""
        assert _corrigir_link_pdf("https://outro.dominio/x") == "https://outro.dominio/x"
        assert _truncar("a" * 100, 10).endswith("…") and len(_truncar("a" * 100, 10)) <= 11
        assert _truncar("curto", 100) == "curto"
        html_txt = _html_para_texto("<p>Item <b>um</b>.</p><ul><li>a</li><li>b</li></ul>&nbsp;fim")
        assert "Item um" in html_txt and "- a" in html_txt and "- b" in html_txt and "<" not in html_txt, html_txt
        assert _html_para_texto("") == ""
        assert "1 (única situação" in _situacao_rotulo(1)
        assert "não catalogado" in _situacao_rotulo(2)
        s_exemplo = {"sigla": "APL-TC", "numero": "00055/26", "relator": "FULANO", "orgaoJulgador": "Pleno",
                     "dataSessao": "2026-06-22T00:00:00", "dataDOE": "2026-06-30T00:00:00"}
        cit = _citacao(s_exemplo)
        assert cit == "(TCE-RO - APL-TC 00055/26, Rel. FULANO, Pleno, j. 22/06/2026, DOe 30/06/2026)", cit
        assert _citacao({"idDecisao": 1}) == "(TCE-RO - decisão id 1)"
        # avisos de cancelamento/vínculo (função pronta, sem caso real observado — ver references)
        av = _avisos_cancelamento_vinculo({"acordaoCanceladoId": 123})
        assert av and "CANCELADO" in av[0], av
        av2 = _avisos_cancelamento_vinculo({"vinculos": [1, 2]})
        assert av2 and "vinculado" in av2[0], av2
        av3 = _avisos_cancelamento_vinculo({"mesmoTema": [9]})
        assert av3 and "mesmo tema" in av3[0], av3
        assert _avisos_cancelamento_vinculo({"acordaoCanceladoId": None, "vinculos": [], "mesmoTema": []}) == []
        # resolver_orgao (sem rede)
        nome_o, aviso_o = _resolver_orgao("pleno")
        assert nome_o == "Pleno" and aviso_o is None, (nome_o, aviso_o)
        nome_o2, aviso_o2 = _resolver_orgao("plenario")
        assert nome_o2 == "plenario" and aviso_o2 and "não é um dos" in aviso_o2, (nome_o2, aviso_o2)
        # verificar_trecho
        textos = {"ementa": "A TESE fixada: benefício por incapacidade, art. 42.", "dispositivo (acordaoDescricao)": "aplicar multa"}
        assert _verificar_trecho(textos, "tese fixada: beneficio por incapacidade")["valido"]
        r_ok = _verificar_trecho(textos, "tese fixada [...] art 42")
        assert r_ok["valido"] and r_ok["onde"] == "ementa", r_ok
        r_neg = _verificar_trecho(textos, "tese fixada [...] art 43")
        assert not r_neg["valido"] and r_neg["faltando"] == ["art 43"], r_neg
        assert not _verificar_trecho(textos, "")["valido"]

        # --- 2. parsing dos fixtures reais ---
        d_proc = _ler("01_busca_numeroProcesso.json")
        assert len(d_proc["result"]) == 4, len(d_proc["result"])
        s0 = d_proc["result"][0]["source"]
        assert s0["idDecisao"] == 98114 and s0["numero"] == "00055/26" and s0["processo"] == "02603/22", s0
        resumo = _resumo_item(s0, 1)
        texto_resumo = "\n".join(resumo)
        assert "APL-TC 00055/26" in texto_resumo and "id 98114" in texto_resumo, texto_resumo
        assert "Citação: (TCE-RO -" in texto_resumo
        detalhe = "\n".join(_detalhe_item(s0))
        assert "Ementa (integral" in detalhe and "Inteiro teor (PDF): https://tcero.tc.br/" in detalhe, detalhe
        assert "GERADO COM APOIO DE IA" in detalhe or "não informado pelo portal" in detalhe
        d_ac = _ler("02_busca_numeroAcordao.json")
        assert len(d_ac["result"]) == 3
        ids = {item["source"]["idDecisao"] for item in d_ac["result"]}
        assert ids == {98114, 96141, 96083}, ids  # mesmo número, ids diferentes — achado real
        d_id = _ler("03_busca_idDecisao.json")
        assert len(d_id["result"]) == 1 and d_id["result"][0]["source"]["idDecisao"] == 98114
        d_rel = _ler("04_relatores.json")
        assert isinstance(d_rel, list) and len(d_rel) >= 5
        assert any(item["nome"].startswith("JOS") for item in d_rel), d_rel[:2]
        # informacoesAdicionais real (item com sigla APL-TC 00035/24) tem HTML de verdade
        s_info = next(item["source"] for item in d_proc["result"] if item["source"]["numero"] == "00035/24")
        assert s_info["informacoesAdicionais"] and "<p>" in s_info["informacoesAdicionais"]
        info_txt = _html_para_texto(s_info["informacoesAdicionais"])
        assert "<" not in info_txt and len(info_txt) > 50, info_txt[:200]
        detalhe_info = "\n".join(_detalhe_item(s_info))
        assert "GERADO COM APOIO DE IA" in detalhe_info

        # --- 3. disjuntor (estado em arquivo temporário) ---
        globals()["_ARQUIVO_ESTADO_DISJUNTOR"] = os.path.join(_tempfile.gettempdir(), "_selftest_disjuntor_tcero.json")

        def _limpar_estado() -> None:
            for suf in ("", ".lock"):
                try:
                    os.unlink(_ARQUIVO_ESTADO_DISJUNTOR + suf)
                except OSError:
                    pass
            _cache_respostas.clear()

        _limpar_estado()
        t0 = 1_000_000.0
        r1 = _reservar_requisicao(t0)
        assert "erro" not in r1 and r1["esperar_s"] == 0, r1
        r2 = _reservar_requisicao(t0 + 0.05)
        assert "erro" not in r2 and r2["esperar_s"] >= 0.9, r2
        _limpar_estado()
        t0 = 2_000_000.0
        for i in range(_JANELA_MAX_REQS):
            assert "erro" not in _reservar_requisicao(t0 + i * 1.5), i
        estourou = _reservar_requisicao(t0 + _JANELA_MAX_REQS * 1.5)
        assert "Muitas consultas" in estourou["erro"], estourou
        _limpar_estado()
        t0 = 3_000_000.0
        _registrar_bloqueio_detectado(t0)
        recuo = _reservar_requisicao(t0 + 1)
        assert "evitando novas tentativas" in recuo["erro"], recuo
        assert "erro" not in _reservar_requisicao(t0 + 5 * 60 + 1)
        _limpar_estado()
        t = 7_000_000.0
        for i in range(6):
            _reservar_requisicao(t + i * 1.5)
        _registrar_bloqueio_detectado(t + 20, "busca")
        rel = _diagnostico_ritmo(t + 21)
        assert "BLOQUEADO" in rel and "Incidentes registrados: 1" in rel and "operação: busca" in rel, rel
        _limpar_estado()
        assert "Nenhum incidente registrado" in _diagnostico_ritmo(9_000_000.0)
        # saneamento de estado corrompido
        agora = time.time()
        with open(_ARQUIVO_ESTADO_DISJUNTOR, "w", encoding="utf-8") as fh:
            json.dump({"bloqueado_ate": agora + 99 * 3600, "backoff_s": -5000, "indice_janela": 999,
                       "requisicoes": "nao e lista", "incidentes": {"x": 1}}, fh)
        est = _ler_estado()
        assert est["bloqueado_ate"] <= agora + _BACKOFF_MAXIMO_S + 1 and est["backoff_s"] >= _BACKOFF_INICIAL_S
        assert est["indice_janela"] == len(_ESCADA_JANELA_S) - 1 and est["requisicoes"] == [] and est["incidentes"] == []
        _limpar_estado()
        resid = [x for x in os.listdir(_tempfile.gettempdir()) if x.startswith("_selftest_disjuntor_tcero.json.") and x.endswith(".tmp")]
        assert not resid, resid
        # cache
        _cache_gravar("k", {"a": 1})
        assert _cache_ler("k") == {"a": 1} and _cache_ler("zzz") is None

        # --- 4. buscar/obter/verificar com rede mockada (fixtures, sem tocar o portal) ---
        async def _consultar_fake(params, operacao):
            if params.get("IdDecisao"):
                return d_id
            if params.get("numeroAcordao"):
                return d_ac
            if params.get("numeroProcesso"):
                return d_proc
            return {"result": []}

        _orig_consultar = globals()["_consultar_api"]
        globals()["_consultar_api"] = _consultar_fake
        try:
            saida = asyncio.run(_buscar(None, None, "02603/22", None, None, 1, 2, False))
            assert "**4 decisão(ões)**" in saida and "página 1/2" in saida, saida[:200]
            assert "Próxima página: pagina=2" in saida, saida
            saida_p2 = asyncio.run(_buscar(None, None, "02603/22", None, None, 2, 2, False))
            assert "3. " in saida_p2 and "4. " in saida_p2, saida_p2
            saida_det = asyncio.run(_buscar(None, None, "02603/22", None, None, 1, 1, True))
            assert "Ementa (integral" in saida_det, saida_det[:300]
            saida_vazia = asyncio.run(_buscar(None, None, None, None, None, 1, 10, False))
            assert "Informe pelo menos um critério" in saida_vazia
            saida_od = asyncio.run(_obter_acordao(98114, None, None))
            assert "Ementa (integral" in saida_od and "id 98114" in saida_od, saida_od[:200]
            saida_od_multi = asyncio.run(_obter_acordao(None, "00055/26", None))
            assert "3 decisões encontradas" in saida_od_multi, saida_od_multi[:200]
            saida_vc = asyncio.run(_verificar_citacao(98114, None, "CONTROLE EXTERNO"))
            assert "✅ VÁLIDO" in saida_vc, saida_vc
            saida_vc_neg = asyncio.run(_verificar_citacao(98114, None, "frase que não existe no acórdão nenhum"))
            assert "❌ NÃO ENCONTRADO" in saida_vc_neg, saida_vc_neg
        finally:
            globals()["_consultar_api"] = _orig_consultar

        print("selftest offline OK")

        if "--online" in sys.argv:
            _limpar_estado()
            globals()["_ARQUIVO_ESTADO_DISJUNTOR"] = os.path.join(base, ".disjuntor_estado_tcero.json")

            async def _run() -> None:
                print("\n=== busca online: numero_processo (estreita) ===")
                print((await _buscar(None, None, "02603/22", None, None, 1, 5, False))[:3000])
                print("\n=== obter_acordao online (id direto) ===")
                print((await _obter_acordao(98114, None, None))[:3000])
                print("\n=== busca online: relator (resolvido por aproximação) + órgão ===")
                print((await _buscar(None, None, None, "jose euler potyguara pereira de mello", "pleno", 1, 3, False))[:2500])
                print("\n=== verificar_citacao online ===")
                print(await _verificar_citacao(98114, None, "CONTROLE EXTERNO [...] LICITAÇÃO PÚBLICA"))
                print("\n" + _diagnostico_ritmo())

            asyncio.run(_run())
    elif _HAS_MCP:
        mcp.run()
    else:
        sys.exit("registro MCP falhou (ver traceback acima) — se for ImportError, instale: pip install 'mcp[cli]' httpx truststore")
