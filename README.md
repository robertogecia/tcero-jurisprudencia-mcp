# MCP — Jurisprudência do TCE-RO (portal ePapyrus)

Servidor MCP pessoal que pesquisa a jurisprudência do **TCE-RO** (Tribunal de Contas do Estado
de Rondônia) no portal oficial ePapyrus (`https://papyrus.tcero.tc.br/`), sem login. Irmão do
`~/MCP/tjro-jurisprudencia` e do `~/MCP/trf1-jurisprudencia` — mesma disciplina (disjuntor
compartilhado entre processos, citação pronta, paginação segura), API bem mais simples: JSON
puro, sem WAF, sem sessão, sem ViewState.

Criado em 13/09/2026. Contrato completo da API (achados ao vivo, inclusive o que diverge do
que se supunha antes de testar) em `references/protocolo-papyrus.md`; respostas cruas reais em
`fixtures/`.

## Ferramentas

| Tool | O que faz |
|---|---|
| `buscar_jurisprudencia_tcero` | busca por texto livre e/ou por número de acórdão, número de processo, relator ou órgão julgador; paginação **no cliente** (a API do portal não pagina no servidor); resumo compacto por padrão, `detalhar=true` para os primeiros itens da página |
| `obter_acordao_tcero` | detalhe completo de uma decisão — ementa integral, dispositivo (`acordaoDescricao`), informações adicionais (⚠️ geradas por IA pelo DEJUR do próprio tribunal), legislação aplicada, link do PDF do inteiro teor; prefira `id_decisao` (busca direta, resposta pequena) |
| `verificar_citacao_tcero` | confere se um trecho aparece literalmente na ementa ou no dispositivo antes de ir entre aspas — `[...]` separa fragmentos, ❌ vem com o que não bateu |
| `diagnostico_ritmo_tcero` | estado do disjuntor/limitador, sem rede |

## Por que este servidor é mais simples que os irmãos

O TJRO tem WAF (STIC) e o TRF1 tem sessão JSF com ViewState — os dois precisam de engenharia
razoável para simular um navegador e detectar bloqueio. O TCE-RO **não tem nada disso**:
confirmado ao vivo com `curl` puro, sem cookie, sem header especial além de um User-Agent
identificável, em ~20 requisições de mapeamento (13/09/2026). O problema aqui não é
autenticação — é volume: a API devolve a consulta inteira de uma vez.

## O problema real: a API não pagina no servidor

`GET /api/espelho/buscar` devolve **todo** o array `result` da consulta, sem `pagina`/`tamanho`
no servidor. Confirmado ao vivo: uma busca de dois termos (`pregão+eletrônico`) já veio com
4,03 MB de JSON em 0,35 s; buscas mais genéricas passam de 10 MB (866 resultados, medido antes
deste servidor existir). Por isso:

- **A paginação é sempre no cliente** (`pagina`/`por_pagina` da tool fatiam o array já
  recebido).
- **Resumo compacto por padrão** — ementa truncada a 600 caracteres, sem `informacoesAdicionais`
  nem `veja`; o texto integral só sai com `detalhar=true` (limitado aos 5 primeiros itens da
  página, para não estourar o contexto de quem chama) ou com `obter_acordao_tcero`.
- **Cache da resposta crua por 5 minutos**, por combinação de parâmetros — trocar de página da
  mesma busca não rebaixa o mesmo payload de novo. Teto de 24 entradas **e** de 48 MB.
- **Orçamento de saída em três níveis**: ~12 mil caracteres por campo de texto, ~40 mil por
  decisão detalhada, ~60 mil na resposta inteira de qualquer ferramenta. Todo corte é declarado
  na saída (`[SAÍDA CORTADA …]`).

Red team adversarial de 13/09/2026 (Opus, 2 requisições de rede): 21 achados, todos corrigidos
com regressão no `--selftest` — relatório em `references/red-team-2026-09-13.md`. Os quatro
piores: saída de até 850 mil caracteres numa busca com `detalhar=true`; parâmetro só com
espaços virando filtro vazio (= acervo inteiro, 10 MB); estado corrompido do disjuntor
derrubando as quatro ferramentas, inclusive o `diagnostico_ritmo_tcero`, que existe para
explicar a falha; e a aproximação de relator escolhendo em silêncio entre os dois `FRANCISCO`
e os quatro `SILVA` da lista real do portal. Hipóteses que só teste online resolve (semântica
do `+` depois do encoding; formato real dos campos de vínculo/cancelamento): registradas lá,
sem resultado inventado.

## Achados ao vivo que corrigem o que se supunha antes de testar

Levantamento completo em `references/protocolo-papyrus.md`; os pontos que **divergem** do que
constava no briefing original desta tarefa:

1. **`relatores` pede o NOME EXATO do relator, não o `id`.** `/api/busca/relatores` devolve
   pares `{id, nome}`, mas o próprio frontend do portal descarta o `id` e manda só o nome — e
   testes ao vivo confirmam: `relatores=<id>` e `relatores=<nome parcial>` devolvem **zero**
   resultados; só o nome completo e exato funciona. Esta ferramenta busca a lista de
   `/api/busca/relatores` e tenta aproximar o que o usuário digitou (sem caixa/acento) antes de
   mandar a query, avisando quando não achou correspondência exata.
2. **Não existe endpoint de descoberta para órgão julgador.** Procurado (`/api/orgaos*`,
   `/api/busca/orgaos*`) — tudo 404. É uma lista fechada de 3 valores, hardcoded no bundle do
   frontend: `1ª Câmara`, `2ª Câmara`, `Pleno`, exigidos **exatamente** (mesmo comportamento
   estrito do `relatores`: `orgaosJulgadores=plenario` devolve zero).
3. **Existe uma busca direta por id** — `GET /api/espelho/buscar?IdDecisao=<n>&filtrarResultados=false`
   devolve exatamente 1 resultado, resposta pequena (~13 KB). Não estava no briefing original;
   é a base de `obter_acordao_tcero(id_decisao=...)` — mais rápida e mais barata que filtrar
   pelo número.
4. **`acordaoDescricao`** é um campo a mais (não estava catalogado antes de testar): quando
   presente, é o DISPOSITIVO de fato (HTML com entidades), mais confiável que `resultado`
   (que é só um rótulo curto, tipo "Imputação de Multa"). Nem toda decisão o preenche.
5. **`linkArquivo` aponta para um host que redireciona.** Vem como
   `//tce.ro.gov.br/AbrirPdfConvidado/<hash>`; esse host devolve 301 para
   `https://tcero.tc.br/AbrirPdfConvidado/<hash>`, onde o PDF é servido de fato — confirmado
   baixando um PDF real (200, `application/pdf`, 10 páginas). Esta ferramenta já entrega o
   link corrigido, apontando direto para `tcero.tc.br`.
6. **Cancelamento e vínculo entre acórdãos (`acordaoCanceladoId`, `vinculos`, `mesmoTema`,
   `acordaoVinculoPai/Filho`) — capacidade nativa do portal que TJRO e TRF1 não têm pronta —
   está implementada (a tool avisa quando algum desses campos vem preenchido), mas
   **nenhuma das decisões reais consultadas nos testes trouxe isso populado.** Não foi
   possível confirmar ao vivo o formato de um acórdão cancelado de verdade; tratar como
   capacidade pronta e não testada em caso real, não como funcionalidade validada.
7. **`situacao`** só apareceu com o valor `1` em todas as amostras. O significado de outros
   valores não foi localizado — a ferramenta expõe o valor cru, sem inventar rótulo.

## `informacoesAdicionais` — conteúdo de IA do próprio tribunal

O campo `informacoesAdicionais` (Fatos / Questão Jurídica / Regras / Análise / Conclusão /
Leitura Estratégica) é **gerado com apoio de IA pelo DEJUR do TCE-RO**, com revisão da equipe
técnica do tribunal — não é o texto do acórdão. `obter_acordao_tcero` sempre mostra esse aviso
junto do conteúdo. **Nunca tratar como fonte primária isolada**: confira sempre contra a
ementa/dispositivo e, quando possível, o inteiro teor em PDF. `verificar_citacao_tcero`
propositalmente NÃO cobre este campo — só ementa e dispositivo.

## Como pesquisar bem

Informe pelo menos um critério (`texto_livre`, `numero_acordao`, `numero_processo`, `relator`
ou `orgao_julgador`) — sem nenhum, a chamada é recusada (evita devolver o acervo inteiro por
engano). `texto_livre` aceita `"frase exata"` entre aspas e `+` para E/AND (confirmado ao vivo:
`dispensa+de+licitação`); o operador `e` (OU/OR) citado na própria página do portal não foi
testado a fundo — se o resultado não vier como esperado, tente reformular. Para relator e órgão
julgador, use exatamente o nome/valor que o portal conhece (a tool tenta aproximar e avisa
quando não bateu). Depois de achar o precedente certo na busca, use o **id** (`idDecisao`) para
tudo o que vier depois — é mais direto que buscar de novo pelo número.

## Instalação (pessoal)

```bash
cd ~/MCP/tcero-jurisprudencia
python3 -m venv .venv && .venv/bin/pip install "mcp[cli]>=1.4.0,<2" "httpx>=0.27" "truststore>=0.9"
# mcp<2 de propósito: o 2.x renomeou FastMCP → MCPServer (o registro das tools falha em silêncio)
.venv/bin/python servidor_tcero.py --selftest            # offline, contra os fixtures
.venv/bin/python servidor_tcero.py --selftest --online   # + operações reais (poucas, moderado)
```

### Registro em `~/.claude.json`

```json
"tcero_jurisprudencia": {
  "command": "/Users/robertogrecia/MCP/tcero-jurisprudencia/.venv/bin/python",
  "args": ["/Users/robertogrecia/MCP/tcero-jurisprudencia/servidor_tcero.py"],
  "env": {}
}
```

O processo MCP só carrega código novo depois de reiniciar o Claude.

## Ritmo e disjuntor

Estado em `.disjuntor_estado_tcero.json` (ao lado do script, sob trava `fcntl`), compartilhado
por todos os processos desta máquina — mesmo mecanismo de TJRO/TRF1. **Os números aqui são um
teto defensivo genérico, não um limite documentado ou observado do TCE-RO**: em ~20
requisições de mapeamento (13/09/2026) o portal não mostrou nenhum sinal de rate limit, WAF ou
bloqueio. Por isso a janela inicial é mais generosa que a dos irmãos (40 requisições/minuto,
escada 1→5→10→20→30 min, cooldown de 5 min dobrando até 1 h) e só aperta se um bloqueio de
verdade acontecer. Backoff exponencial curto (até 3 tentativas) em erro de rede/5xx —
diferente do disjuntor (que reage a recusa persistente), isso cobre instabilidade passageira.

## Pontos frágeis (onde olhar se quebrar)

- `orgaosJulgadores` hardcoded no frontend (`1ª Câmara`, `2ª Câmara`, `Pleno`) — se o TCE-RO
  criar/renomear uma câmara, esta lista fica desatualizada até alguém notar um filtro que
  deveria achar algo e não acha.
- `relatores` via aproximação de nome contra `/api/busca/relatores` — se essa lista for parcial
  (parece trazer só relatores "correntes", não o histórico completo — não confirmado), um
  relator antigo pode não ser encontrado por aproximação e a busca vai com o nome cru. Desde
  13/09/2026 a aproximação por substring só vale com **um** candidato: a lista real tem dois
  `FRANCISCO`, quatro `SILVA` e `OMAR PIRES DIAS` ao lado de `OMAR PIRES DIAS - Substituição em
  Vacância`, então nome ambíguo é recusado com a lista de candidatos, nunca resolvido no chute.
- `linkArquivo` → `tcero.tc.br`: se o tribunal um dia desligar o redirect de `tce.ro.gov.br`
  sem avisar, o link já corrigido nesta ferramenta continua funcionando (aponta direto pro
  host final); se for o CONTRÁRIO (desligar `tcero.tc.br` e manter só `tce.ro.gov.br`), aí sim
  quebra — não há como prever qual vai sobreviver.
- `acordaoDescricao` nem sempre vem preenchido — quando ausente, o dispositivo "real" não está
  disponível por este servidor; só o `resultado` (rótulo curto) ou o PDF do inteiro teor.

## Não confundir

- Não é o `tjro_jurisprudencia` (Poder Judiciário, WAF STIC) nem o `trf1_jurisprudencia`
  (Justiça Federal, portal JSF do CJF). Este é o **TCE-RO** — Tribunal de Contas, controle
  externo (licitação, prestação de contas, responsabilização de gestor) — tribunal e
  jurisdição diferentes dos outros dois.
