# Protocolo do portal ePapyrus (TCE-RO) — engenharia reversa, 13/09/2026

Portal: `https://papyrus.tcero.tc.br/` — SPA Vue.js (bundle `/js/app-busca.js`), backend em
ASP.NET (`x-aspnetmvc-version` visto no domínio de arquivo). Pesquisa de jurisprudência do
Tribunal de Contas do Estado de Rondônia, pública, **sem login, sem WAF, sem captcha** —
confirmado ao vivo com `curl` puro (sem cookies, sem navegador) em 13/09/2026.

## Endpoint principal

```
GET https://papyrus.tcero.tc.br/api/espelho/buscar
```

Parâmetros (querystring, todos string, todos opcionais — mas pelo menos um deve vir preenchido
ou o portal devolve o acervo inteiro):

| Parâmetro | O que faz | Confirmado ao vivo |
|---|---|---|
| `textoLivre` | Busca por texto livre (ementa/corpo/informações adicionais). SEMPRE OU (OR) termo a termo — espaço, `+`, a palavra `e` e até `AND`/`+termo` literais (o que o frontend realmente manda) são todos idênticos entre si; `"frase exata"` entre aspas funciona como frase exata. Ver "Experimentos 13/09/2026, online" abaixo — **refuta** a hipótese original de que `+` seria AND | **sim, integralmente confirmado, em duas rodadas** — 10 requisições, 13/09/2026 |
| `numeroAcordao` | Busca pelo número do acórdão (ex.: `00055/26`). **Precisa vir zero-preenchido para 8 caracteres** — o frontend faz `.padStart(8, '0')` antes de mandar; sem isso (`55/26`) o portal devolve zero, silenciosamente | sim — pode devolver MAIS de um `idDecisao` para o MESMO número (3 decisões distintas sob `00055/26` no teste); padding confirmado ao vivo em 13/09/2026 (Experimento C) |
| `numeroProcesso` | Busca pelo número do processo administrativo (ex.: `02603/22`). Mesmo zero-preenchimento de 8 caracteres do `numeroAcordao` (inferido do bundle, não testado isoladamente) | sim, quanto à busca em si; o padding foi confirmado só para `numeroAcordao` (Experimento C) — para `numeroProcesso` é inferência por simetria do mesmo trecho do bundle |
| `relatores` | Filtro por relator — **precisa do NOME EXATO**, não do id | sim, com ressalva importante abaixo |
| `orgaosJulgadores` | Filtro por órgão julgador — **precisa do valor EXATO** de uma lista fechada de 3 | sim, com ressalva abaixo |
| `IdDecisao` (maiúsculas assim mesmo) + `filtrarResultados=false` | Busca DIRETA por id da decisão — devolve exatamente 1 resultado, resposta pequena (13 KB) | sim — achado que NÃO estava no briefing original; é o endpoint certo para `obter_acordao_tcero` |

### `relatores`: id ≠ valor de busca (achado ao vivo, diverge do que se supunha)

`GET /api/busca/relatores` devolve uma lista de `{"id": N, "nome": "..."}` (10 itens na
amostra, provavelmente só os relatores "correntes"/em destaque, não o histórico completo — não
confirmado). **Mas o próprio bundle do frontend (`app-busca.js`) descarta o `id` e manda só o
`nome`** (`data.map(item => item.nome)`), e testes ao vivo confirmam:

- `relatores=11` (o id de "JOSÉ EULER...") → **0 resultados**.
- `relatores=EULER` (nome parcial) → **0 resultados**.
- `relatores=JOSÉ EULER POTYGUARA PEREIRA DE MELLO` (nome completo, exato, com acento) →
  resultados corretos.

Ou seja: **o parâmetro é o nome completo e exato do relator**, sem tolerância a substring,
maiúsculas/minúsculas ou falta de acento (não testada a fundo a sensibilidade a acento
isoladamente, mas o comportamento com id e substring já mostra que não há fuzzy match). O
`id` de `/api/busca/relatores` não serve para nada na busca — só teria uso de `key` no
componente Vue do combobox.

### `orgaosJulgadores`: lista fechada, hardcoded no frontend — sem endpoint próprio

**Não existe endpoint irmão de `/api/busca/relatores` para órgãos julgadores.** Procurado:
tentativas de `/api/orgaosJulgadores`, `/api/orgaos`, `/api/busca/orgaos*` — todas HTTP 404.
O bundle do frontend traz o valor **hardcoded**:

```js
orgaosJulgadores: ['1ª Câmara', '2ª Câmara', 'Pleno']
```

Teste ao vivo confirma exigência de valor EXATO (mesmo tratamento de string do `relatores`):
`orgaosJulgadores=Pleno` funciona; `orgaosJulgadores=plenario` (minúsculo, sem o "Pleno" exato)
devolve 0. Não testado se há outros valores históricos fora desses 3 (ex.: câmaras extintas);
"não localizado" para qualquer coisa além dessa lista de 3.

## Autenticação / robustez de rede

Nenhuma das chamadas acima precisou de cookie, sessão ou header especial além de um
`User-Agent` identificável. Sem qualquer página de desafio, sem 403/429 observado em ~20
requisições moderadas de mapeamento (13/09/2026). Diferença relevante em relação ao TJRO
(WAF STIC) e ao TRF1 (Cloudflare no domínio de arquivo): aqui não há nada disso a contornar.

## Estrutura da resposta

```json
{
  "sugestoesPesquisa": [ ... ],
  "result": [
    {
      "highlights": { "ementa": { "documentId": "...", "field": "ementa", "highlights": ["...<em>termo</em>..."] } },
      "source": { ... }
    }
  ]
}
```

`result` é a lista COMPLETA da consulta — **a API não pagina no servidor**. Uma busca de texto
livre pouco restrita já devolve múltiplos MB (confirmado: 4,03 MB para `pregão+eletrônico`;
o usuário já havia visto 10,8 MB / 866 resultados para `dispensa+de+licitação` antes deste
levantamento). A resposta é rápida mesmo assim (0,35 s no teste de 4 MB) — o custo é de
contexto do lado de quem consome, não de latência do portal. **Toda paginação neste servidor
MCP é no cliente**, fatiando `result` já recebido, com cache da resposta crua por 5 minutos
(mesmo padrão do TRF1) para não rebaixar o mesmo payload grande a cada mudança de página.

### Campos de `source` (superset do que o briefing original trazia — confirmado ao vivo)

Todos os campos abaixo apareceram nas 8 amostras reais coletadas (`fixtures/`):

```
idDecisao, sigla, numero, data, natureza, ementa, acordaoDescricao, objeto, votacao, dataDOE,
resultado, transitoEmJulgado, dataTransitadoJulgado, processo, relator, assunto, orgaoJulgador,
dataSessao, jurisdicionado, linkArquivo, situacao, classificacao, mesaId, mesa,
informacoesAdicionais, veja, relatorAcordao, palavrasResgate, acordaoId, acordaoMesmoTemaPai,
mesmoTema, revisoes, dataVinculacao, acordaosOutrosTribunais, legislacoes, inteiroTeor,
informado, acordaoVinculoId, acordaoVinculoPai, acordaoVinculoFilho, vinculos, favoritos,
acordaoCanceladoId, acordaoCancelado, relatorSubstituto, principal, jurisprudenciaSelecionada,
exibirNaBuscaLivre, numberOfRows, id, dataCriacao, usuarioCriacao, dataUltimaAlteracao,
usuarioUltimaAlteracao
```

Achado não previsto no briefing: **`acordaoDescricao`** — quando presente, é o DISPOSITIVO
efetivo do acórdão (texto livre em HTML com entidades: `&uacute;`, `&ccedil;`...), distinto do
`resultado` (rótulo curto, ex.: "Imputação de Multa", "Descumprimento de Decisão"). Nem sempre
vem preenchido (`null` em metade da amostra). Quando presente, é literal e citável (com
`html.unescape` + remoção de tags) — mais confiável que `resultado`, que é só uma etiqueta.

### `situacao` — não caracterizado além do valor `1`

Nas 8 amostras originais e nas 267 do Experimento B de 13/09/2026 (ver abaixo), `situacao`
trouxe **sempre** `1` (267/267). Nenhuma pista sobre o que outros valores significariam
apareceu organicamente. **Não localizado** — o servidor MCP expõe o valor cru sem tentar
rotulá-lo. N maior não elimina a possibilidade de outros valores existirem fora da amostra.

### `acordaoCanceladoId` / `acordaoCancelado` / `vinculos` / `mesmoTema` / `acordaoVinculo*`

**Atualizado 13/09/2026 (Experimento B, N=267 — ver seção "Experimentos 13/09/2026, online"):**
`acordaoCanceladoId`/`acordaoCancelado`/`acordaoVinculoPai`/`acordaoVinculoFilho`/
`acordaoMesmoTemaPai`/`revisoes` continuam **não localizados populados** (0/267 mesmo numa
amostra bem maior — a checagem de cancelamento segue implementada e sem caso real para
confirmar formato). Mas **`vinculos` (33/267) e `mesmoTema` (15/267) e `acordaoVinculoId`
(25/267) VIERAM populados** — ver a seção dedicada abaixo para o formato real de cada um e a
correção aplicada em `_avisos_cancelamento_vinculo`.

### `linkArquivo` — domínio muda com redirect 301

O campo vem como `//tce.ro.gov.br/AbrirPdfConvidado/<hash>` (protocolo-relativo). Esse host
**redireciona (301) para `https://tcero.tc.br/AbrirPdfConvidado/<hash>`**, onde o PDF é servido
de fato (200, `content-type: application/pdf`, confirmado baixando um PDF real de 10 páginas /
538.981 bytes, sem cookie nem header especial). O cliente HTTP precisa seguir redirects
(`follow_redirects=True`); o `Content-Type` da PRIMEIRA resposta (301, antes do redirect) é
`text/html` — não usar esse header isoladamente para decidir se deu certo.

## Endpoints irmãos vistos no bundle (não usados por este servidor, registrados por
completude)

`/api/busca/form`, `/api/busca/index`, `/api/busca/refinadores`, `/api/busca/resultados` — nomes
de módulos Vue/rotas internas do SPA, não confirmados como endpoints JSON próprios de dados
(podem ser só nomes de componente/rota do frontend). Não investigados a fundo — fora do escopo
do que este servidor precisa.

## Experimentos 13/09/2026, online

Fecha os pontos que o red team de `references/red-team-2026-09-13.md` deixou como
`[NÃO TESTADO]`, em duas rodadas no mesmo dia (a segunda depois de uma leitura do bundle do
frontend, `/js/app-busca.js`, apontar uma variável que a primeira rodada não tinha controlado).
Script reprodutível: `scripts/experimentos-2026-09-13.py`. Respostas cruas em
`fixtures/exp_*.json` (e `fixtures/exp_log.json` com bytes/tempo de cada requisição) e
`fixtures/05_vinculos_reais.json` (3 registros reais extraídos, usados em regressão do
`--selftest`). **10 requisições ao portal no total (6 na 1ª rodada — Experimentos A e B — mais
4 na 2ª — Experimento C), todas HTTP 200, espaçadas ≥5 s, nunca em rajada, mesmo `User-Agent`
do servidor de produção (`HEADERS_BASE`, importado direto de `servidor_tcero.py`, não
duplicado).**

### Experimento A — semântica de `textoLivre`

Termos escolhidos: **"reincidência"** e **"direcionamento"** (técnicos, individualmente
estreitos, coocorrência rara — lidos nas ementas reais de `fixtures/01_*.json` e `02_*.json`
antes de escolher). 5 requisições, mesmo par de termos, 5 sintaxes:

| # | rótulo | URL (textoLivre) | HTTP | bytes | tempo | resultados |
|---|---|---|---|---|---|---|
| 1 | A1 | `reincid%C3%AAncia%20direcionamento` (espaço → `%20`) | 200 | 2.558.607 | 0,78 s | 156 |
| 2 | A2 | `reincid%C3%AAncia%2Bdirecionamento` (`+` → `%2B`, o que o servidor manda hoje) | 200 | 2.558.607 | 0,26 s | 156 |
| 3 | A3 | `reincid%C3%AAncia+direcionamento` (`+` CRU na URL — controle: ASP.NET decodifica como espaço) | 200 | 2.558.607 | 0,29 s | 156 |
| 4 | A4 | `%22reincid%C3%AAncia%20direcionamento%22` (frase exata entre aspas) | 200 | 36 | 0,07 s | 0 |
| 5 | A5 | `reincid%C3%AAncia%20e%20direcionamento` (operador `e` da instrução da página) | 200 | 3.438.665 | 0,40 s | 267 |
| 6 (extra) | A6 | `textoLivre=e` (isola o `e` sozinho, fora do plano original de 5) | 200 | 895.102 | 1,80 s | 114 |

**Conclusão, por contagem E por leitura das ementas (não só contagem):**

- **A1 = A2 = A3, byte a byte, idênticos.** `%20`, `%2B` e um `+` cru (que o ASP.NET decodifica
  como espaço) produzem a **mesma resposta exata** — mesmos 156 `idDecisao`, mesma ordem, mesmo
  tamanho em bytes. **Isto refuta a hipótese do briefing original de que `+` seria lido como
  AND**: se fosse, A2 teria de divergir de A3 (que é comprovadamente espaço). Não diverge.
  `%2B` não é operador nenhum aqui — é sinônimo de espaço.
- **A1/A2/A3 são OU (OR), confirmado por leitura, não só por contagem.** Dos 156 resultados:
  112 contêm SÓ "reincidência" (substring, sem acento/caixa), 17 contêm SÓ "direcionamento",
  **ZERO contêm as duas** (verificado em `ementa` + `acordaoDescricao` + demais campos textuais
  — nenhuma das 156 decisões tem as duas palavras juntas), e 27 não têm nenhuma das duas nesses
  campos — mas TÊM uma delas em `informacoesAdicionais` (conferido nos 27: todos batem via esse
  campo, que a busca também indexa mas cujo `highlights` o portal não devolve). 112+17+27=156.
  Ou seja: **a resposta é a UNIÃO de quem contém "reincidência" com quem contém
  "direcionamento", nunca a interseção** — isto é OR, não AND.
- **A4 (frase exata entre aspas) funciona como frase exata**: 0 resultados, consistente com o
  fato (já demonstrado acima) de que as duas palavras nunca aparecem juntas nessas 156+
  decisões — muito menos na ordem exata "reincidência direcionamento". A sintaxe de aspas está
  correta e é a única forma de exigir adjacência/ordem encontrada.
- **`e` NÃO é um operador especial — é só mais um termo OU'd**, confirmado de forma decisiva
  pelo experimento A6: isolar `textoLivre=e` sozinho devolve 114 resultados, e
  `ids(A5) == ids(A1) ∪ ids(A6)` **exatamente** (igualdade de conjuntos, não aproximação — as
  267 decisões de A5 são exatamente as 156 de A1 mais as 114 de A6, com overlap zero: A6 não
  compartilha nenhum id com A1). Ou seja, `"termo1 e termo2"` é tratado pelo portal como três
  tokens OU'd — `{termo1} OU {e} OU {termo2}` — e o fato de a página descrever isso como "e =
  OU" é tecnicamente verdadeiro só porque **tudo** no `textoLivre` é OU por padrão; `e` não tem
  nenhum comportamento distinto de qualquer outra palavra do texto.
- **Nenhuma sintaxe de AND foi encontrada.** Não há forma testada de exigir "os dois termos, em
  qualquer lugar, em qualquer ordem" — só a união (padrão) ou a frase exata (aspas, que exige
  adjacência e ordem). Isto não foi testado a fundo o suficiente para dizer que AND **não
  existe** no portal — só que as sintaxes óbvias (`+`, espaço, `e`) não o implementam. Se
  precisar de interseção real, a forma prática hoje é rodar duas buscas separadas e cruzar os
  `idDecisao` manualmente (é exatamente o que este experimento fez para provar o ponto).

> **⚠️ RESSALVA adicionada depois, mesmo dia — ver "Experimento C" abaixo.** O teste acima usou
> a palavra `e` **crua**, entre espaços. Descobriu-se depois (leitura de
> `/js/app-busca.js`, o bundle do frontend) que **o site nunca manda esse `e` cru**: ele
> converte ` e `/` E ` → ` AND ` e ` ou `/` OU ` → ` OR ` no navegador, ANTES de chamar a API.
> O Experimento C testou o que o site realmente manda (`AND` literal, `+termo` com espaço) e o
> resultado foi o MESMO: nem `AND` nem `+termo` mudam a resposta. A conclusão de que **não há
> AND** continua de pé — só o caminho para chegar lá mudou (o `e` cru nunca foi o que importava;
> o que importa é que `AND`/`+termo`, o que o site de fato manda, também não funcionam).

### Experimento B — campos nunca vistos populados

Reaproveitada a maior resposta do Experimento A (A5, 267 decisões, "reincidência e
direcionamento") — **zero requisições novas**, conforme instruído. Tabulação 100% offline sobre
`fixtures/exp_A5_operador_e.json`.

| Campo | Não-vazios / 267 | Formato real observado |
|---|---|---|
| `acordaoCanceladoId` | 0 | — (não localizado, mesmo em N=267) |
| `acordaoCancelado` | 0 | — (não localizado) |
| `vinculos` | 33 | **lista de INTEIROS** (ids de decisão) — ex. `[77649, 57039, 84267]`. **SELF-INCLUSIVE em 33/33**: a própria decisão sempre aparece dentro da própria lista `vinculos` (tamanhos observados: 2 a 6, sempre ≥2). Não é "outras decisões vinculadas" — é o grupo de vínculo inteiro, incluindo a própria. |
| `mesmoTema` | 15 | **lista de OBJETOS completos** (schema recursivo idêntico ao de `source`, com `ementa`/`acordaoDescricao`/etc. inteiros dentro) — NUNCA self-inclusive (0/15 continham o próprio id). |
| `acordaoVinculoId` | 25 | **escalar inteiro** (ex. `18045`). Em nenhuma das 25 amostras esse valor aparece dentro do respectivo `vinculos`, nem bate com nenhum `idDecisao` observado na amostra inteira — não é id de decisão, é (aparentemente) o id interno do REGISTRO de vínculo no portal (chave de agrupamento). Sempre que populado, `vinculos` também estava populado (25/25) — mas o contrário não é verdade (33 `vinculos` vs 25 `acordaoVinculoId`). |
| `acordaoVinculoId` isolado (sem `vinculos`) | 0 dos 25 | — |
| `acordaoVinculoPai` | 0 | — (não localizado) |
| `acordaoVinculoFilho` | 0 | — (não localizado) |
| `acordaoMesmoTemaPai` | 0 | — (não localizado) |
| `revisoes` | 0 | — (não localizado) |

Achado real → **correção aplicada em `_avisos_cancelamento_vinculo`** (código): a função antiga
(a) mostrava a lista crua de `vinculos`, incluindo o próprio id, dando a entender que a decisão
estava "vinculada a si mesma" — agora o próprio id é filtrado da exibição; (b) **não tratava
`acordaoVinculoId` de jeito nenhum** (gap real: um campo populado em 25/267 decisões e a
ferramenta ficava muda sobre ele) — agora gera um aviso explícito dizendo que não é id de
decisão. Os 3 registros reais usados para validar (`idDecisao` 80049 com `mesmoTema`, 77649 com
`vinculos` self-inclusive, 77568 com `vinculos` + `acordaoVinculoId` juntos) estão salvos em
`fixtures/05_vinculos_reais.json` e viraram regressão no `--selftest`.

Demais campos tabulados (informativos, sem ação de código — nenhum é citado em nenhum aviso ou
citação pronta hoje):

- `situacao`: 267/267 = `1` (reforça, com N maior, o que as 8 amostras originais já mostravam).
- `dataSessao` nulo: 0/267 (nenhum exemplo; hipótese do achado 6 do red team segue sem
  ocorrência real, mecanismo continua corrigido preventivamente).
- `principal=false`: 159/267 (59%) — comum, não raro.
- `jurisprudenciaSelecionada=false`: 264/267 (99%) — quase universal.
- `exibirNaBuscaLivre=false`: 0/267 — nunca observado false nesta amostra (faz sentido: tudo
  que veio de uma busca livre está, por definição, marcado para aparecer nela).
- `relatorSubstituto=true`: 11/267 (4%) — ocorre, consistente com a nota já existente sobre
  "OMAR PIRES DIAS - Substituição em Vacância" na lista de relatores.

**Tempo da requisição grande vs timeout de 45 s do servidor**: a maior resposta obtida (A5,
3.438.665 bytes) levou 0,40 s; a mais lenta (A6, 895.102 bytes) levou 1,80 s. Nenhuma chegou
perto do timeout de 45 s — mas isto **não** é uma medição direta da hipótese 5 do red team
(payload de ~10 MB): por extrapolação linear grosseira (0,40 s para 3,4 MB ⇒ ~1,2 s para 10 MB),
não há indício de risco, mas não foi medido um payload de fato próximo de 10 MB neste
levantamento — **[NÃO TESTADO DIRETAMENTE]**, só inferido por escala.

### Experimento C — o que o frontend REALMENTE manda (segunda rodada, mesmo dia)

Motivado por leitura de `/js/app-busca.js` (bundle do frontend do portal, baixado em
`/tmp/app-busca.js`): confirmado por grep no próprio arquivo (não só inferido) que:

```js
operadores: { 'e': 'AND', 'ou': 'OR' }
// _prepararTextoLivreParaConsulta(textoLivre): para cada operador,
// textoLivre.replace(new RegExp("\\s(e|E)\\s", 'g'), " AND ") — e o mesmo para "ou"/"OU" → " OR "
```

e que `numeroAcordao`/`numeroProcesso` passam por `.padStart(8, '0')` antes de `axios.get`. Ou
seja: o Experimento A testou `" e "` **cru**, que o site nunca manda — o site sempre converte
para `" AND "` antes. Isto pedia um teste novo com o que o site de fato envia.

Par de termos trocado para um com coocorrência REAL (o par anterior, "reincidência"/
"direcionamento", tinha coocorrência ZERO — não serve para testar se AND intersecta): consegui
por leitura offline do fixture A1 que **56 das 156 decisões já baixadas continham as duas
palavras "reincidência" E "multa"** juntas — "multa" escolhida por aparecer ao lado de
"REINCIDÊNCIA" já na primeira ementa amostrada em `fixtures/01_busca_numeroProcesso.json`.
4 requisições (orçamento desta rodada: até 4):

| # | rótulo | URL (textoLivre / numeroAcordao) | HTTP | bytes | tempo | resultados |
|---|---|---|---|---|---|---|
| C1 | AND literal | `reincid%C3%AAncia%20AND%20multa` | 200 | 20.142.444 | 2,79 s | 1.141 |
| C2 | controle OU | `reincid%C3%AAncia%20multa` | 200 | 20.142.444 | 1,66 s | 1.141 |
| C3 | `+termo` obrigatório | `reincid%C3%AAncia%20%2Bmulta` (espaço, depois `+multa` colado) | 200 | 20.142.444 | 1,45 s | 1.141 |
| C4 | padStart | `numeroAcordao=55%2F26` (SEM padding) | 200 | 36 | 0,09 s | 0 |

⚠️ **"multa" acabou sendo um termo muito mais comum do que o esperado** (>15 MB nas 3
primeiras) — a escolha de par "individualmente estreito" falhou aqui; registrado para não
repetir consultas desta amplitude, conforme a regra do orçamento. Não invalida a conclusão
(ver abaixo) — na verdade a reforça, porque a diferença de tamanho entre "reincidência"
(129 ocorrências) e "multa" (1.069 ocorrências) tornaria uma interseção real (61) claramente
menor e distinguível de uma união (1.141); não houve distinção nenhuma.

**Conclusões:**

- **C1 = C2 = C3, byte a byte, idênticos** (mesmos 1.141 `idDecisao`, mesma ordem). Nem `AND`
  literal maiúsculo nem `+multa` (sintaxe "obrigatório" de motores estilo Elasticsearch/Lucene,
  `+` colado ao termo, com espaço antes) mudaram o resultado em NADA — nem um id a mais, nem um
  a menos, em relação ao controle sem operador nenhum.
- Por leitura (sobre C1, 1.141 decisões): 129 contêm "reincidência", 1.069 contêm "multa", **61
  contêm as duas** — essa seria a interseção real, se AND funcionasse. Como o resultado teve
  1.141 (a união, idêntica a C2), fica provado que **`AND` foi tratado como se não estivesse na
  consulta** (nenhuma decisão adicional apareceu por conter a palavra "AND" — 0/1.141 continham
  o token "AND" literalmente, o que faz sentido: é uma palavra inglesa rara em ementas em
  português).
- **C4 confirma o `padStart` do frontend por necessidade, não só por leitura do bundle**:
  `numeroAcordao=55/26` (sem zero-preenchimento) devolveu `{"result": []}` — 36 bytes, ZERO
  decisões — para o MESMO acórdão que `numeroAcordao=00055/26` (com padding) sempre devolveu
  desde os fixtures originais (`fixtures/02_busca_numeroAcordao.json`). Sem o padding, o portal
  não erra nem avisa — devolve silenciosamente um conjunto vazio, indistinguível de "não existe
  jurisprudência". Corrigido em `_padronizar_numero` (código), aplicado a `numero_acordao` e
  `numero_processo` nas três ferramentas que os usam.
- **`(d) "termo1 OR termo2"` explícito foi deliberadamente OMITIDO** desta rodada para caber no
  orçamento de 4: o Experimento A já provou por dois caminhos diferentes que o padrão sem
  operador nenhum já é OR (união), então testar a palavra `OR` explícita tinha baixo valor
  marginal frente à hipótese distinta do `padStart` (C4). Se algum dia for preciso, a
  expectativa (não testada) é que `OR` se comporte como `AND` se comportou aqui — token inerte,
  idêntico ao controle — mas isto é **inferência por simetria, não resultado observado**.

**Conclusão final, juntando Experimento A e C**: o portal ePapyrus **não implementa nenhum
operador booleano conhecido** em `textoLivre` — nem a sintaxe que o site converte (`e`/`E`,
nunca usada de fato) nem a sintaxe crua que a conversão produz (`AND`, `+termo`). Tudo em
`textoLivre` é OU (união) por padrão, e a única forma confirmada de restringir por mais de uma
palavra é a frase exata entre aspas (adjacência + ordem, não interseção livre). **Não** implica
que o site "engana" o usuário — implica que o próprio backend do TCE-RO não trata esses
marcadores como operadores, então o comportamento acaba sendo o mesmo (OR) para quem digita
"termo1 e termo2" no site ou manda `"termo1 termo2"` direto pela API.

## Ordem dos resultados e por que `grupos` é no cliente

Achado offline, 13/09/2026, sobre `fixtures/exp_C2_controle_or.json` (a mesma resposta real de
1.141 decisões do Experimento C, busca nativa "reincidência multa"): **o portal ordena por
`dataSessao` decrescente, não por relevância**. Confirmado por leitura direta do array — os
primeiros 15 itens vêm em ordem estritamente não-crescente de `dataSessao` (22/06 → 15/06 →
… → 27/04/2026).

Consequência prática, medida sobre os mesmos dados: das **61** decisões que continham
"reincidência" E "multa" ao mesmo tempo (substring simples, sem fronteira de palavra — a
contagem "oficial" do filtro implementado é 59, ver abaixo), só **1 estava entre as 10
primeiras** posições da resposta nativa e só **4 entre as 50 primeiras**. Ou seja: o OU nativo
do portal, combinado com a ordenação cronológica, **esconde exatamente o que um E de verdade
encontraria** — um agente que lê só a primeira página de uma busca de dois conceitos está lendo
majoritariamente ruído (decisões com só UM dos dois termos).

Como a API já devolve o array COMPLETO da consulta (não pagina no servidor — ver "Estrutura da
resposta" acima) e o portal não implementa nenhum operador booleano (Experimentos A e C, acima),
a solução ficou óbvia: **fazer o E no cliente**, sem gastar requisição extra. Implementado como
o parâmetro `grupos` de `buscar_jurisprudencia_tcero` (mesmo vocabulário de `grupos` no
`tjro_jurisprudencia`/`trf1_jurisprudencia`: dentro do grupo é OU, entre grupos é E):

1. A ferramenta manda ao portal um `textoLivre` com TODAS as palavras de TODOS os grupos, soltas
   e sem aspas (`_montar_texto_livre_com_grupos`) — maximiza o recall nativo (é tudo OU mesmo).
2. Filtra o array já baixado (`_filtrar_por_grupos`), mantendo só as decisões em que CADA grupo
   tem pelo menos um termo presente, em ementa + dispositivo (`acordaoDescricao`, HTML limpo) ou
   informações adicionais (`_campos_casamento`/`_termo_casa`/`_decisao_casa_grupos`) — nunca
   muta os dicts cacheados (mesma disciplina já auditada pelo red team para o resto do módulo).
3. Pagina o resultado FILTRADO, não o bruto; o cabeçalho mostra os dois números.

**Critério de casamento e por que a contagem "oficial" é 59, não 61**: termo com espaço casa
como frase (substring direto); termo de uma palavra casa por substring com fronteira de palavra
só à ESQUERDA (regex `\btermo`). A contagem informal de 61 (citada acima, no Experimento A/C)
usava um radical truncado ("reincidenc") sem fronteira de palavra nenhuma — isso casava também
com **"reincidente"** (palavra diferente — nunca contém a string "reincidência" como substring)
e com **"multirreincidência"** (contém "reincidência" como substring, mas SEM começar numa
fronteira de palavra — é outra palavra, não o termo pesquisado). Os 4 ids que saem do conjunto
com o critério correto (81.969, 84.690, 84.681, 95.941) foram inspecionados manualmente um a um
— todos caem exatamente nesses dois casos, nenhum é uma ocorrência real de "reincidência"
perdida pelo filtro. **59 é o número correto**; 61 era contagem grosseira de um script de
análise ad hoc, não do código do servidor.

Também confirmado: 14 das 59 decisões só bateram um dos dois grupos nas informações adicionais
(texto de apoio gerado com IA pelo DEJUR) — nunca na ementa nem no dispositivo — e a ferramenta
avisa isso por decisão (ex.: `idDecisao` 96429, grupo "multa" só em informações adicionais;
`idDecisao` 94915, grupo "reincidência" só em informações adicionais). Regressão completa (com
estes ids reais) no `--selftest`, usando os fixtures já existentes — nenhuma requisição nova.

## Leitura do inteiro teor em PDF — 14/09/2026

Capacidade nova, pedida pelo usuário ("deveria o resultado das pesquisas voltar [...] com todo
o julgado, não só a ementa"): `obter_acordao_tcero(..., ler_inteiro_teor=true)` baixa o
`linkArquivo` (já corrigido para `tcero.tc.br` — ver achado 5 acima) e extrai o texto real com
PyMuPDF (`fitz`). Diferente do TRF1, que desiste de propósito porque o inteiro teor lá fica
atrás de um desafio Cloudflare: aqui o mesmo link que a busca já devolve baixa **sem login, sem
cookie, sem JavaScript** — confirmado ao vivo baixando 5 PDFs reais em 13-14/09/2026 (o 6º
achado de 13/09 já tinha confirmado isto para 1 PDF; agora confirmado para mais 4, mais 1 ponta
a ponta pelo próprio `--selftest --online`).

### 4 PDFs baixados para fixtures (`fixtures/pdf/*.pdf`), 14/09/2026

Espaçados ≥3,5s, mesmo `HEADERS_BASE` do servidor, todos HTTP 200:

| id | sigla | páginas | bytes PDF | tempo | chars extraídos | chars da ementa |
|---|---|---|---|---|---|---|
| 98114 | APL-TC 00055/26 | 24 | 781.830 | 1,46s | 69.140 | 3.491 |
| 96141 | AC1-TC 00055/26 | 6 | 488.028 | 0,44s | 14.409 | 780 |
| 85572 | APL-TC 00035/24 | 33 | 538.981 | 0,36s | 95.026 | 1.370 |
| 77649 | APL-TC 00127/22 | 36 | 761.891 | 0,49s | 127.460 | 1.638 |

Um 5º download real (mesmo id 98114, via `--selftest --online`) confirmou a ponta a ponta —
total de 5 dos 6 downloads do orçamento de rede desta tarefa, 1 em reserva.

**Prova de que a extração é real, não ilusão de já ter esse conteúdo**: em TODOS os 4 PDFs, o
texto extraído contém as palavras estruturais "RELATÓRIO" e "VOTO" — nenhuma das duas aparece
na `ementa` correspondente (que é só o resumo padronizado). Trecho real do id 98114 (RELATÓRIO,
ausente da ementa): *"Trata-se de processo autuado para análise do Pregão Eletrônico n.
11/CIMCERO/2021, cujo objeto é a formação de registro de preços [...]"*; trecho do VOTO
(também ausente): *"VOTO CONSELHEIRO JOSÉ EULER POTYGUARA PEREIRA DE MELLO [...] cinge-se o
objeto da presente deliberação à análise do cumprimento do item II do Acórdão APL-TC
00035/24..."*. A razão entre chars extraídos e chars da ementa varia de ~18× (96141) a ~78×
(77649) — o PDF sempre traz muito mais do que a API JSON expõe hoje.

### Detecção de PDF sem texto (digitalização) — sem caso real, testado sinteticamente

Nenhum dos 4 PDFs reais baixados veio sem camada de texto (todos são nativos, gerados
digitalmente pelo sistema do TCE-RO — "DP-SPJ" no rodapé de cada página). A detecção de
"PDF sem texto extraível" (limiar: `LIMIAR_CHARS_POR_PAGINA` = **250** caracteres não-espaço por
página, em média — era 30 até o red team de 14/09/2026, ver adiante) foi testada com um PDF
sintético gerado em memória com o próprio `fitz`
(página em branco, sem `insert_text`) — sem gastar nenhum download do orçamento de rede. Não
faz OCR: já testado antes em processo grande (382 páginas, ver
`docling-nao-vale-pena-processo-grande` na memória do usuário) e não valeu a pena — lento e
ainda falhava em PDF com texto digital.

### Orçamento de caracteres (`ORCAMENTO_PDF` = 45.000), corte com começo E fim

Maior que `ORCAMENTO_DETALHE` (40.000) porque o PDF é o documento inteiro (relatório+voto+
ementa+dispositivo), não um campo isolado — mas ainda finito: o maior PDF real testado (id
77649, 36 páginas) já extraiu 127.460 caracteres, quase 3× o teto. `ORCAMENTO_SAIDA` (60.000)
continua valendo por cima; desde 14/09/2026 o bloco do PDF é montado **já com o que sobra** da
resposta (`min(ORCAMENTO_PDF, ORCAMENTO_SAIDA − já usado − reserva)`), em vez de ser montado com
45.000 fixos e depois descartado inteiro pelo `_cortar_bloco` — que corta em fronteira de LINHA,
e o texto do PDF é uma linha só.

O corte guarda **começo e fim** (55%/45%), com o miolo marcado: o voto e o dispositivo ficam no
FIM do documento (id 77649: "VOTO" no caractere 115.259 e "É como voto" no 122.759, de 127.460),
então cortar só pela cabeça entregava o relatório e descartava exatamente a parte citável.

### Cache e rede

Texto extraído cacheado por 1h por `id_decisao` (TTL bem maior que o da busca, 5min — o inteiro
teor de um acórdão não muda). Guarda só o TEXTO, nunca os bytes do PDF, no máximo 24 entradas.
Download do PDF usa `tcero.tc.br`, um host DIFERENTE de
`papyrus.tcero.tc.br` (API de busca) — não compartilha o disjuntor da API, só um espaçamento
mínimo próprio de 3s e um lock em memória, para não bloquear a busca de jurisprudência por
causa de um PDF. Teto de 20 MB por PDF (checado por `Content-Length` e também durante o
streaming, caso o header falte ou minta) — nenhum dos 4 PDFs reais chegou perto (todos < 800 KB).

Host em lista fechada (`_HOSTS_PDF_PERMITIDOS` = `tcero.tc.br`, `tce.ro.gov.br` e subdomínios,
só http/https), conferido antes de pedir e de novo no destino final do redirect. **Se o TCE-RO
passar a servir os PDFs de um terceiro host** (CDN, por exemplo), o download passa a falhar com
`[LEITURA DE PDF NÃO REALIZADA — ... aponta para fora do TCE-RO]` e a correção é acrescentar o
host à lista no servidor — não contornar.

### Tetos da EXTRAÇÃO (`TETO_PAGINAS_PDF` = 400, `TETO_SEGUNDOS_PDF` = 20s) — red team 14/09/2026

`TETO_BYTES_PDF` limita só o arquivo **comprimido**; o que o PyMuPDF processa depois de abrir
não tem relação com isso. Medido: 3.000 páginas cheias de texto cabem em **1,43 MB** e levavam
**9,0s / 9,4 milhões de caracteres / 112 MB de pico de memória**; 10.000 páginas em branco,
1,7 MB e 1,1s. Como o servidor roda dentro do processo do Claude do usuário, travar ali trava a
sessão. Com os tetos: as mesmas 3.000 páginas levam **0,95s / 15 MB**. A parada é conferida a
cada página (cooperativa, interrompe de verdade) e há um `asyncio.wait_for` sobre
`asyncio.to_thread` como rede de segurança para uma única página patológica — a thread órfã
segue até terminar (Python não interrompe CPU-bound síncrono de dentro do processo), mas a
sessão do usuário é devolvida. Acórdãos reais têm 6 a 36 páginas, então 400 é ~11× o maior caso
conhecido.

### Limiar de "sem texto": por que 30 não servia

Um PDF **digitalizado** com o carimbo de assinatura digital em texto no rodapé de cada página
rende ~83 caracteres não-espaço por página — passava pelo limiar de 30 e ganhava a linha
"inteiro teor lido (PDF)" sobre um documento de que não se leu uma palavra do conteúdo. Os 4
PDFs reais: 2.844 (77649), 2.395 (98114), 2.356 (85572) e 1.950 (96141) chars/página. 250 fica
~8× abaixo do menor caso real e ~3× acima do rodapé-carimbo. Além disso, acima de 30% de páginas
quase sem texto (`_FRACAO_PAGINAS_VAZIAS_AVISO`, caso do PDF misto: acórdão nativo + anexos
digitalizados) a saída avisa quantas páginas são e rebaixa a verificação.

### `"inteiro teor lido"` × `"inteiro teor lido em parte"`

A frase forte só sai quando o documento coube inteiro, sem corte, sem parada por teto e sem
suspeita de PDF misto — e nomeia a decisão (`sigla numero, id N`), porque com
`numero_acordao`/`numero_processo` o portal pode devolver várias decisões e só a PRIMEIRA é
lida. Nos demais casos sai `Verificação: "inteiro teor lido em parte (PDF)"`, com o aviso de que
serve para citar o que está literalmente ali, não para afirmar que algo não consta do acórdão, e
que não pode entrar na ficha de precedente como "inteiro teor lido". Dos 4 PDFs reais, só o
96141 (6 páginas, 14.409 chars) cabe inteiro.

### Por que NÃO estender a mesma capacidade a `buscar_jurisprudencia_tcero`

Decisão deliberada: `detalhar=true` já tem teto de 5 itens por página porque É caro (embute
ementa+dispositivo+informações integrais). `ler_inteiro_teor` seria mais caro ainda — download
real de um arquivo de terceiro, não só formatação de texto já em memória. Numa busca paginada
com `por_pagina` até 50, aplicar isso a vários itens de uma vez viraria uma avalanche de N
downloads de PDF numa única chamada — exatamente a rajada que a moderação de rede deste
projeto (e o `feedback-subagent-runaway-spawning` da memória do usuário, por analogia) existe
para evitar. Em `obter_acordao_tcero`, cada chamada já é uma decisão específica do agente sobre
UM acórdão por vez — o lugar certo para este parâmetro, sem esse risco.

## Resumo do que diverge do briefing original

1. `relatores` pede o **nome exato**, não o `id` de `/api/busca/relatores` (o id não serve
   pra nada na query — achado ao vivo).
2. `orgaosJulgadores` **não tem endpoint de descoberta**; é uma lista fechada de 3 valores
   fixos no frontend (`1ª Câmara`, `2ª Câmara`, `Pleno`), exigidos exatamente.
3. Existe um endpoint de busca DIRETA por id (`IdDecisao=<n>&filtrarResultados=false`), mais
   enxuto que filtrar pelo número — não estava no briefing e é a base de `obter_acordao_tcero`.
4. `acordaoDescricao` (dispositivo em HTML) é um campo a mais que o briefing não citava.
5. `linkArquivo` aponta para um host (`tce.ro.gov.br`) que redireciona para outro
   (`tcero.tc.br`) — o PDF de fato mora no segundo.
6. Cancelamento (`acordaoCanceladoId`/`acordaoCancelado`) e o significado de `situacao` além de
   `1` **seguem não confirmados** mesmo em N=267 (Experimento B, 13/09/2026) — capacidade
   implementada, sem caso real. `vinculos`, `mesmoTema` e `acordaoVinculoId`, por outro lado,
   **foram confirmados populados e com formato real conhecido** (Experimento B) — ver seção
   dedicada acima.
7. `textoLivre` é **sempre OU (OR)** termo a termo — `+`, espaço, a palavra `e` e até o `AND`
   literal (o que o frontend realmente manda no lugar de `e`, confirmado lendo
   `/js/app-busca.js`) são todos idênticos entre si; `+termo` (sintaxe "obrigatório" de
   Elasticsearch/Lucene) também não muda nada. Não existe AND funcional encontrado — só a
   frase exata entre aspas restringe por mais de uma palavra. Isto **contradiz** o que o
   briefing original (e a própria página do portal) sugeriam (Experimento A + C, 13/09/2026,
   10 requisições no total — ver seções dedicadas acima).
8. O frontend zero-preenche `numeroAcordao`/`numeroProcesso` para 8 caracteres
   (`.padStart(8, '0')`, ex.: "55/26" → "00055/26") ANTES de mandar — achado no bundle e
   confirmado ao vivo: sem esse preenchimento, o mesmo acórdão que existe devolve ZERO
   resultados, silenciosamente (Experimento C, 13/09/2026). Corrigido nesta ferramenta
   (`_padronizar_numero`).
9. O portal ordena por `dataSessao` decrescente, não por relevância — descoberta offline,
   13/09/2026, sobre uma resposta real de 1.141 decisões: das 61 que continham dois termos ao
   mesmo tempo, só 1 estava nas 10 primeiras posições e só 4 nas 50 primeiras. Isso motivou o
   parâmetro `grupos` (E entre grupos, OU dentro do grupo), implementado no CLIENTE — ver seção
   dedicada "Ordem dos resultados e por que `grupos` é no cliente" acima.
