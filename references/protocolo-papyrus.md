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
| `textoLivre` | Busca por texto livre (ementa/corpo). Aceita `"frase exata"` entre aspas, `+` para E (AND — ex.: `pregão+eletrônico`), `e` para OU (OR) — conforme instrução da própria página; não testado a fundo | parcial — `+` funciona (4.030.588 bytes para `pregão+eletrônico`, 0,35 s) |
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

Todas as 8 decisões amostradas trazem `situacao: 1`. Nenhuma pista sobre o que outros valores
significariam apareceu organicamente nos testes moderados feitos. **Não localizado** — o
servidor MCP expõe o valor cru sem tentar rotulá-lo.

### `acordaoCanceladoId` / `acordaoCancelado` / `vinculos` / `mesmoTema` / `acordaoVinculo*`

Campos existem no schema e a ferramenta os expõe como aviso quando não vazios, mas **nenhuma
das 8 decisões amostradas os trouxe preenchidos** — não foi possível confirmar ao vivo o
formato de um acórdão cancelado ou vinculado de verdade (só a forma vazia: `null`/`[]`). Achar
um exemplo real exigiria uma varredura maior, que o prompt pede para não fazer sem necessidade
concreta. Tratar a capacidade de aviso como **implementada mas não testada em caso real**.

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
6. Cancelamento/vínculo (`acordaoCanceladoId`, `vinculos`, `mesmoTema`) e o significado de
   `situacao` além de `1` **não foram confirmados ao vivo** — capacidade implementada no
   servidor, mas sem caso real testado.
