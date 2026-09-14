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
| `buscar_jurisprudencia_tcero` | busca por texto livre e/ou por número de acórdão, número de processo, relator ou órgão julgador; `grupos` (E entre grupos, OU dentro do grupo) filtra por 2+ conceitos — o E é feito **no cliente**, porque o portal só sabe fazer OU e ordena por data, não por relevância; paginação **no cliente** (a API do portal não pagina no servidor); resumo compacto por padrão (já com o link do PDF de cada item, corrigido para o host atual), `detalhar=true` para os primeiros itens da página |
| `obter_acordao_tcero` | detalhe completo de uma decisão — ementa integral, dispositivo (`acordaoDescricao`), informações adicionais (⚠️ geradas por IA pelo DEJUR do próprio tribunal), legislação aplicada, link do PDF do inteiro teor; prefira `id_decisao` (busca direta, resposta pequena); `ler_inteiro_teor=true` baixa esse PDF e EXTRAI O TEXTO REAL (relatório + voto, não só ementa/dispositivo) — ver seção dedicada abaixo |
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
e os quatro `SILVA` da lista real do portal. As duas hipóteses que só teste online resolvia
(semântica do `+` depois do encoding; formato real dos campos de vínculo/cancelamento) foram
fechadas no mesmo dia, em duas rodadas (10 requisições controladas no total — a 2ª depois de
uma leitura do bundle do frontend apontar uma variável não controlada na 1ª) — ver
`references/protocolo-papyrus.md`, seção "Experimentos 13/09/2026, online": **não existe AND
funcional em `textoLivre`** — nem `+`, nem `e`/`E`, nem o `AND` literal que o frontend realmente
manda no lugar de `e` (confirmado lendo `/js/app-busca.js` e testando ao vivo: `AND` e `+termo`
devolvem resultado byte a byte idêntico ao controle sem operador) — tudo é sinônimo de OU;
`vinculos`/`mesmoTema`/`acordaoVinculoId` **apareceram populados de verdade** (formato real
documentado, código corrigido); e o frontend zero-preenche `numeroAcordao`/`numeroProcesso`
para 8 caracteres antes de mandar (`"55/26"` → `"00055/26"`) — sem isso o portal devolve zero
silenciosamente, confirmado ao vivo e agora replicado nesta ferramenta. Regressão no
`--selftest` para os três.

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
6. **Cancelamento e vínculo entre acórdãos** — capacidade nativa do portal que TJRO e TRF1 não
   têm pronta. Atualizado 13/09/2026 (Experimento B, N=267 decisões — ver
   `references/protocolo-papyrus.md`): `acordaoCanceladoId`/`acordaoCancelado`/
   `acordaoVinculoPai`/`acordaoVinculoFilho`/`acordaoMesmoTemaPai`/`revisoes` continuam **nunca
   vistos populados**, mesmo numa amostra bem maior — tratar como capacidade pronta, sem caso
   real. Mas **`vinculos` (33/267), `mesmoTema` (15/267) e `acordaoVinculoId` (25/267) vieram
   populados de verdade**, com formatos bem diferentes entre si: `vinculos` é uma lista de ids
   de decisão que **inclui o próprio id do registro** (corrigido: a ferramenta agora omite o
   próprio id da exibição, em vez de parecer "vinculado a si mesmo"); `mesmoTema` é uma lista de
   OBJETOS completos (não ids); `acordaoVinculoId` é um id interno do registro de vínculo do
   portal — **não** um id de decisão (a ferramenta antes não dizia nada sobre este campo; agora
   avisa e deixa explícito que não serve para `obter_acordao_tcero`).
7. **`situacao`** só apareceu com o valor `1` em todas as amostras, inclusive nas 267 do
   Experimento B de 13/09/2026. O significado de outros valores não foi localizado — a
   ferramenta expõe o valor cru, sem inventar rótulo.

## `informacoesAdicionais` — conteúdo de IA do próprio tribunal

O campo `informacoesAdicionais` (Fatos / Questão Jurídica / Regras / Análise / Conclusão /
Leitura Estratégica) é **gerado com apoio de IA pelo DEJUR do TCE-RO**, com revisão da equipe
técnica do tribunal — não é o texto do acórdão. `obter_acordao_tcero` sempre mostra esse aviso
junto do conteúdo. **Nunca tratar como fonte primária isolada**: confira sempre contra a
ementa/dispositivo e, quando possível, o inteiro teor em PDF. `verificar_citacao_tcero`
propositalmente NÃO cobre este campo — só ementa e dispositivo.

## Leitura do inteiro teor em PDF — 14/09/2026

`obter_acordao_tcero(..., ler_inteiro_teor=true)` baixa o PDF do `linkArquivo` (já corrigido
para `tcero.tc.br`) e **extrai o texto real com PyMuPDF (`fitz`)** — relatório e voto completos,
não só a ementa/dispositivo que a API JSON já trazia. É uma capacidade que os servidores irmãos
não têm: o **TRF1 desiste de propósito** porque o inteiro teor lá fica atrás de um desafio
Cloudflare; aqui não há esse obstáculo — confirmado ao vivo, o mesmo `linkArquivo` que a busca
já devolve baixa **sem login, sem cookie, sem JavaScript** (é só um GET).

### Como funciona

1. Pega o `linkArquivo` da primeira decisão encontrada (mesma que o detalhe normal já mostra),
   já corrigido para `tcero.tc.br`.
2. Confere o host contra uma lista fechada (`_HOSTS_PDF_PERMITIDOS`: `tcero.tc.br`,
   `tce.ro.gov.br` e subdomínios, só http/https) **antes de pedir e de novo depois de seguir os
   redirects**. A URL não é escrita pelo servidor: vem do campo `linkArquivo` do JSON do portal,
   e o cliente segue redirects — sem a lista, um campo alterado mandaria o downloader a qualquer
   host, inclusive a rede local da máquina do usuário.
3. Baixa o PDF com o mesmo `User-Agent` identificável do resto deste servidor, mas **sem usar o
   disjuntor compartilhado da API de busca** — é outro host, e misturar os dois orçamentos
   bloquearia a busca de jurisprudência por causa de downloads de PDF, sem motivo real. Em vez
   disso, um espaçamento mínimo próprio de 3s e um lock em memória (moderação básica, suficiente
   porque cada chamada é uma decisão específica do agente, nunca um laço sobre uma página
   inteira de resultados).
4. Extrai o texto com PyMuPDF, com **teto de 400 páginas e de 20s de wall-clock**
   (`TETO_PAGINAS_PDF`/`TETO_SEGUNDOS_PDF`, conferidos a cada página, mais um timeout de thread
   como rede de segurança). Os 20 MB de `TETO_BYTES_PDF` limitam só o arquivo *comprimido*:
   3.000 páginas cheias cabem em 1,4 MB e, sem esses tetos, levavam 9s e 112 MB de memória —
   dentro do processo do Claude do usuário, ou seja, travando a sessão dele. Parada por teto sai
   marcada como `EXTRAÇÃO PARCIAL`.
5. Corte sempre dito explicitamente, num teto de ~45 mil caracteres (`ORCAMENTO_PDF`) — ou no
   que sobrar dos ~60 mil da resposta inteira (`ORCAMENTO_SAIDA`), o que for menor: o bloco é
   montado já com o espaço que resta, para não montar uma seção que o corte final descartaria
   inteira. **O corte guarda começo E fim do documento**, com o miolo marcado no meio, porque o
   voto e o dispositivo — a parte citável — ficam no FIM (no id 77649 o "VOTO" começa no
   caractere 115.259 de 127.460; cortar só pela cabeça entregava o relatório e jogava fora
   exatamente o que se queria citar).
6. Cacheia o texto extraído por 1h, por `id_decisao` (ou hash do link, se faltar id) — pedir de
   novo o mesmo acórdão na mesma sessão não baixa o PDF outra vez. O cache guarda só o TEXTO
   (nunca os bytes do PDF), no máximo 24 entradas.

### PDF sem camada de texto (digitalização/imagem)

Se a extração devolver texto vazio ou quase vazio (menos de **250** caracteres não-espaço por
página, em média — `LIMIAR_CHARS_POR_PAGINA`), a ferramenta **não finge que leu**: diz explicitamente "PDF sem texto
extraível (provável digitalização) — inteiro teor não pôde ser lido automaticamente; abra o
link no navegador" e a saída NÃO ganha a linha `Verificação: "inteiro teor lido (PDF)"`. Não
faz OCR de propósito — já testado antes em processo grande (382 páginas) e não valeu a pena
(lento, ainda falhava em PDF com texto digital). Falha de rede ao baixar (timeout, 404, 5xx)
também não vira "não encontrado": vira `[LEITURA DE PDF NÃO REALIZADA — motivo]`, porque a
decisão existe — só a leitura automática do PDF falhou.

O limiar era 30 chars/página até o red team de 14/09/2026: um PDF **digitalizado** com o carimbo
de assinatura digital em texto no rodapé rende ~83 caracteres por página e passava por 30,
ganhando indevidamente a linha "inteiro teor lido (PDF)". Os 4 PDFs reais em `fixtures/pdf/` têm
de 1.950 a 2.844 chars/página, então 250 fica ~8× abaixo do menor caso real e ~3× acima do
rodapé-carimbo. Recusar é sempre seguro (manda abrir no navegador); reivindicar leitura de um
scan, não. **PDF misto** (acórdão nativo + anexos digitalizados): acima de 30% das páginas
praticamente sem texto, a saída avisa quantas e rebaixa a verificação para parcial.

### Semântica de `verificacao` — categoria nova, e a variante "em parte"

Quando a extração tem sucesso, traz texto substancial **e o documento coube inteiro**, a saída
inclui explicitamente a linha `Verificação: "inteiro teor lido (PDF)"` (nomeando a decisão) —
categoria **mais forte** que "só ementa/dispositivo" (o que este servidor sempre devolveu até
agora) porque é a primeira vez que ele consegue ler o julgado inteiro sem intervenção humana no
navegador. Isto é o campo `verificacao` que a ficha de precedente usa
(`pesquisador-juridico`/`segundo-cerebro`) — só escrever essa frase depois desta ferramenta ter
de fato devolvido essa linha, nunca por conta própria.

Quando o texto foi cortado pelo orçamento, a extração parou num teto de páginas/tempo, ou o PDF
é misto, a linha sai **rebaixada**: `Verificação: "inteiro teor lido em parte (PDF)"`. A
diferença não é cosmética — serve para citar o que está literalmente ali, **não** serve para
afirmar que algo *não* consta do acórdão, e essa decisão não pode entrar na ficha como "inteiro
teor lido". Dos 4 PDFs reais, só o menor (96141, 6 páginas) cabe inteiro nos 45 mil caracteres;
os outros três saem como "em parte". A linha também nomeia de qual decisão é o PDF, porque com
`numero_acordao`/`numero_processo` o portal pode devolver várias decisões e só a primeira é lida.

### Exemplo real (id 98114, APL-TC 00055/26, 14/09/2026)

A ementa tem 3.491 caracteres. O PDF (24 páginas, 781.830 bytes) extraiu **69.140 caracteres**
de texto real — quase 20× mais — incluindo o RELATÓRIO ("Trata-se de processo autuado para
análise do Pregão Eletrônico n. 11/CIMCERO/2021...") e o VOTO ("VOTO CONSELHEIRO JOSÉ EULER
POTYGUARA PEREIRA DE MELLO... cinge-se o objeto da presente deliberação à análise do
cumprimento do item II do Acórdão APL-TC 00035/24...") — nenhum dos dois está na ementa, que é
só o resumo. Outros 3 PDFs reais testados no mesmo levantamento (ids 96141, 85572, 77649; 6 a 36
páginas) confirmam o padrão: o inteiro teor sempre traz muito mais do que ementa+dispositivo, e
em todos os 4 o texto extraído continha as palavras estruturais "RELATÓRIO"/"VOTO" que a ementa
nunca tem. Fixtures reais em `fixtures/pdf/*.pdf`, regressão completa no `--selftest`.

### Por que NÃO existe em `buscar_jurisprudencia_tcero`

Decisão deliberada, não esquecimento: `detalhar=true` já tem teto de 5 itens por página porque
é caro; `ler_inteiro_teor` seria mais caro ainda (download real de PDF, não só formatação).
Numa busca paginada, aplicar isso a vários itens de uma vez viraria uma avalanche de downloads
de PDF numa única chamada — exatamente o tipo de rajada que a moderação de rede deste projeto
proíbe. Em `obter_acordao_tcero`, ao contrário, cada chamada já é uma decisão específica do
agente sobre UM acórdão por vez — o lugar certo para este parâmetro.

## Como pesquisar bem

Informe pelo menos um critério (`texto_livre`, `numero_acordao`, `numero_processo`, `relator`
ou `orgao_julgador`) — sem nenhum, a chamada é recusada (evita devolver o acervo inteiro por
engano). `texto_livre` é **sempre OU (OR)** termo a termo — confirmado ao vivo em 13/09/2026,
em duas rodadas (ver `references/protocolo-papyrus.md`): espaço, `+`, a palavra solta `e` e até
`AND`/`+termo` literais (o que o frontend do portal manda de verdade no lugar de `e` — lido no
bundle `/js/app-busca.js` e confirmado ao vivo) se comportam de forma IDÊNTICA entre si (todos
OR); nenhum funciona como AND. `"frase exata"` entre aspas continua funcionando como frase
exata/adjacente. Não há sintaxe NATIVA do portal para exigir dois conceitos em qualquer
ordem — para isso use o parâmetro `grupos` (ver seção dedicada logo abaixo), que faz o E no
cliente. `numero_acordao`/`numero_processo` aceitam
o número sem zero-preenchimento (`"55/26"`) — esta ferramenta completa para 8 caracteres
sozinha, como o frontend do portal faz, porque sem isso o portal devolve zero resultados
silenciosamente. Para relator e órgão
julgador, use exatamente o nome/valor que o portal conhece (a tool tenta aproximar e avisa
quando não bateu). Depois de achar o precedente certo na busca, use o **id** (`idDecisao`) para
tudo o que vier depois — é mais direto que buscar de novo pelo número.

## Ordem dos resultados e por que `grupos` é no cliente

Achado offline, 13/09/2026, sobre uma resposta real de 1.141 decisões
(`fixtures/exp_C2_controle_or.json`, busca "reincidência multa"): o portal **ordena por
`dataSessao` decrescente**, não por relevância. Das 61 decisões que continham "reincidência" E
"multa" ao mesmo tempo, só **1 estava entre as 10 primeiras** da resposta e só **4 entre as 50
primeiras** — o resto (57 de 61) estava espalhado no meio de mais de mil decisões que só tinham
UM dos dois termos. Um agente que lê só a primeira página de uma busca de dois conceitos está,
na prática, lendo ruído.

Como o motor do portal não implementa nenhum operador booleano (ver "Como pesquisar bem" acima)
e a API já devolve o array inteiro da consulta (não pagina no servidor), o parâmetro `grupos`
resolve isso **no cliente**: manda ao portal um OU de todas as palavras de todos os grupos
(recall máximo, uma requisição só) e depois mantém, do array já baixado, só as decisões em que
CADA grupo tem pelo menos um termo presente — antes de paginar. O cabeçalho da resposta mostra
os dois números: "N no portal (OU nativo) → M após exigir todos os grupos". Casamento: fold de
caixa/acento, sobre ementa + dispositivo + informações adicionais; termo com espaço casa como
frase, termo de uma palavra casa por substring com fronteira de palavra à ESQUERDA (pega
"multas"/"multada", não pega "tumulto" nem "multirreincidência"). Quando o único casamento de
um grupo foi nas informações adicionais (texto de apoio gerado com IA pelo DEJUR, não o texto
do acórdão), a ferramenta avisa isso por decisão.

## Instalação (pessoal)

```bash
cd ~/MCP/tcero-jurisprudencia
python3 -m venv .venv && .venv/bin/pip install "mcp[cli]>=1.4.0,<2" "httpx>=0.27" "truststore>=0.9" "pymupdf>=1.24"
# mcp<2 de propósito: o 2.x renomeou FastMCP → MCPServer (o registro das tools falha em silêncio)
# pymupdf (fitz): extração de texto do inteiro teor em PDF, ver obter_acordao_tcero(ler_inteiro_teor=true)
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
