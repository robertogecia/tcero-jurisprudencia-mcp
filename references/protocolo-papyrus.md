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
| `textoLivre` | Busca por texto livre (ementa/corpo/informações adicionais). SEMPRE OU (OR) termo a termo — espaço, `+` e a palavra `e` são idênticos entre si; `"frase exata"` entre aspas funciona como frase exata. Ver "Experimentos 13/09/2026, online" abaixo — **refuta** a hipótese original de que `+` seria AND | **sim, integralmente confirmado** — 6 requisições, 13/09/2026 ~23:22-23:25 |
| `numeroAcordao` | Busca pelo número do acórdão (ex.: `00055/26`) | sim — pode devolver MAIS de um `idDecisao` para o MESMO número (3 decisões distintas sob `00055/26` no teste) |
| `numeroProcesso` | Busca pelo número do processo administrativo (ex.: `02603/22`) | sim |
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

Fecha os dois pontos que o red team de `references/red-team-2026-09-13.md` deixou como
`[NÃO TESTADO]`. Script reprodutível: `scripts/experimentos-2026-09-13.py`. Respostas cruas em
`fixtures/exp_*.json` (e `fixtures/exp_log.json` com bytes/tempo de cada requisição) e
`fixtures/05_vinculos_reais.json` (3 registros reais extraídos, usados em regressão do
`--selftest`). **6 requisições ao portal, todas HTTP 200, espaçadas ≥5 s, nunca em rajada,
mesmo `User-Agent` do servidor de produção (`HEADERS_BASE`, importado direto de
`servidor_tcero.py`, não duplicado).**

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
7. `textoLivre` é **sempre OU (OR)** termo a termo — `+`, espaço e a palavra `e` são idênticos
   entre si; não existe AND encontrado; aspas fazem frase exata. Isto **contradiz** o que o
   briefing original (e a própria página do portal) sugeriam sobre `+` = AND (Experimento A,
   13/09/2026, 6 requisições — ver seção dedicada acima).
