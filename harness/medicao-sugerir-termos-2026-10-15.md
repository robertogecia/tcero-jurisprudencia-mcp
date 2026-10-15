# Medição de `sugerir_termos_tcero` — 15/10/2026

Reprodução: `.venv/bin/python harness/gerar_fundo.py` (uma vez) e `.venv/bin/python harness/medir_sugestoes.py` (zero rede; usa `harness/_snapshot/acervo.json`, que fica fora do git). Saída bruta em `harness/_resultado_sugestoes.json`.

## Leia isto antes dos números

- O **gold é circular** (regex sobre ementa + dispositivo, os mesmos campos e quase as mesmas palavras do ranking; ver `references/red-team-2026-09-22b.md`). Adicionar sinônimos em OU a um grupo **não consegue** subir o recall do gold (o gold já é 100% do que casa a regex) e o que entra de novo conta como falso positivo. O recall do gold só serve para ver se algo QUEBROU.
- O número que vale é o da **anotação independente** (`references/red-team-2026-09-22b/anotacao.json`: 1 anotador, 6 consultas, decisões relevantes para a PERGUNTA, escolhidas dentro do pool top-10 das buscas de 22/09). Limites: um anotador só; o pool vem das buscas antigas, então **decisão relevante que nenhuma delas trouxe não está na anotação** (o ganho de recall que as sugestões trariam fora do pool é invisível aqui); 6 consultas.
- O mock do portal é o OU nativo de `medir.py` (palavras soltas, sem frase); a resposta real tem teto de 2.000 resultados (visto ao vivo em 15/10/2026).
- O fundo de vocabulário foi refeito, para cada consulta, **sem as decisões que casaram** (para a frequência de fundo não conter as próprias casadas). O fundo que acompanha o servidor usa as 5.052 decisões inteiras.

## Protocolo

Para cada consulta de `medir.py`: (1) sugestões calculadas sobre a consulta **ingênua** (`texto_livre`); (2) quatro formas de montar `grupos`: **A** = o que o pesquisador montou; **B3/B5** = A + as 3/5 primeiras palavras sugeridas como alternativas **em OU no grupo mais estreito**; **C3** = A + as 3 primeiras como grupo novo (E, estreita). Ordenação por relevância (padrão da ferramenta).

## Resultado agregado (6 consultas)

| Forma | Tamanho médio do conjunto | Recall do gold (média) | Recall@10 essencial do gold (média) | Anotados relevantes no TOP-10 (de 47 possíveis) | Anotados relevantes no CONJUNTO (de 49) |
|---|---|---|---|---|---|
| A (base) | 356 | 0.928 | 0.783 | 36 | 43 |
| B3 (+3 em OU) | 550 | 0.945 | 0.45 | 27 | 47 |
| B5 (+5 em OU) | 630 | 0.945 | 0.2 | 19 | 47 |
| C3 (+3 como E) | 324 | 0.594 | 0.333 | 22 | 32 |

## Por consulta (anotados relevantes no top-10 / no conjunto)

| # | Pergunta | A | B3 | B5 | C3 | Nº de anotados |
|---|---|---|---|---|---|---|
| 1 | Há precedente do TCE-RO sobre direcionamento/fraude em licitação? | 7 / 7 | 2 / 7 | 3 / 7 | 2 / 5 | 7 |
| 2 | Aposentadoria/ato de pessoal questionando tempo de contribuição — o qu | 10 / 10 | 7 / 10 | 0 / 10 | 7 / 10 | 10 |
| 3 | Reincidência no descumprimento de determinação do Tribunal — como se d | 4 / 4 | 1 / 5 | 0 / 5 | 1 / 4 | 5 |
| 4 | Dano ao erário com imputação de débito solidário entre gestores — prec | 8 / 12 | 8 / 12 | 9 / 12 | 4 / 4 | 12 |
| 5 | Contratação temporária de servidor sem concurso público — o TCE-RO já  | 0 / 3 | 4 / 5 | 4 / 5 | 3 / 3 | 7 |
| 6 | Obra pública paralisada/em atraso — há precedente de responsabilização | 7 / 7 | 5 / 8 | 3 / 8 | 5 / 6 | 8 |

## Leitura honesta

- **Recall total dos anotados sobe com as sugestões em OU** (43 → 47 de 49; subiu em 3 consultas — a 3, a 5 e a 6 —, ficou igual nas outras 3). Na consulta 5 (contratação temporária) a base não achava 4 dos 7 anotados e o topo tinha 0/7; com 3 sugestões em OU ('seletivo', 'simplificado', 'edital') o topo passou a 4/7. Esse é o ganho real: vocabulário que o advogado não tinha digitado.
- **Mas coladas em bloco as sugestões DERRUBAM o topo**: anotados no top-10 caem de 36 para 27 (B3) e 19 (B5); o recall@10 do essencial do gold cai de 0,78 para 0,45 e 0,20. Piorou em 4 de 6 consultas com 3 sugestões (1, 2, 3, 6), ficou igual em 1 (4) e melhorou em 1 (5). Motivo: o ranking conta termos DISTINTOS casados, então uma palavra genérica sugerida ('empresa', 'contrato', 'dever') empurra para cima decisões que só têm a palavra genérica.
- **Como grupo novo (E) estreita** e perde relevantes (32 de 49 no conjunto). Não é o uso recomendado.
- Conclusão para o texto da ferramenta: **sugestão para curadoria, não para colar em bloco**. A ferramenta diz isso na saída e no README. **Não se declara ganho de busca**; declara-se que a lista mostra vocabulário real das ementas, com ruído.

## Qualidade das sugestões (leitura minha, NÃO cega, um avaliador só)

Cada sugestão classificada, lendo a lista, como pertinente ao tema da pergunta (P), genérica do direito de contas (G) ou ruído (N). 107 sugestões em 6 consultas: **P = 63 (59%), G = 27 (25%), N = 17 (16%)** — LEITURA NÃO CEGA, SUPERADA: a rotulagem cega por 2 anotadores independentes (Sonnet e Opus, 15/10/2026, concordância 74%, kappa 0,60): pertinentes nos dois 26% (28 de 107), em pelo menos um 37%; 21 termos foram ruído nos dois. A estimativa anterior de 59% (leitura minha, não cega) estava inflada e não vale. Por consulta (P/G/N): 1 = 10/6/0; 2 = 16/3/1; 3 = 4/7/5; 4 = 13/1/6; 5 = 14/5/1; 6 = 6/5/4. A consulta 3 (reincidência/dosimetria) é a pior (palavras como 'evitar', 'parte', 'ensejar', 'regência'); a 4 tem ruído de baixa cobertura (palavras que só 3 de 10 ementas trazem). Para comparação, o TJRO mediu 65% de pertinência e 4% de ruído com rotulagem cega e dupla — **este número NÃO é comparável** (avaliador único, sem cegueira, amostra pequena): é um teste de sanidade, não uma validação.

## Listas medidas

**1. Há precedente do TCE-RO sobre direcionamento/fraude em licitação?** — 18 casadas, 437 no restante, k=2

inidoneidade; pregao; empresa; participacao; edital; participar; declaracao; precos; certame; empresas; competicao; propostas; pregao eletronico; agentes publicos; regimento interno; pressupostos admissibilidade

**2. Aposentadoria/ato de pessoal questionando tempo de contribuição — o que o TCE-RO já decidiu?** — 1857 casadas, 3194 no restante, k=3

idade; voluntaria; ofertada; professor; ultima; transicao; concessorio; integrais; previdenciario; proventos; redutor; laborado; ultima remuneracao; base ultima; regra transicao; atos pessoal; emenda constitucional; remuneracao paridade; considerar legal; registro concessorio

**3. Reincidência no descumprimento de determinação do Tribunal — como se dosimetra a multa?** — 45 casadas, 1155 no restante, k=2

evitar; descumprimento; responsaveis; dever; accountability; expedidas; regencia; sancao; ensejar; parte; prazo; ressalvas; aplicacao pena; ressalvas contas; regular ressalvas; julgamento regular

**4. Dano ao erário com imputação de débito solidário entre gestores — precedentes?** — 10 casadas, 5041 no restante, k=4

deixarem; reputar; suportar; imputacao; tomada; insigne; especial; idonea; irregular; administrador; pagamentos; efetuados; contas especial; tomada contas; devendo suportar; pessoa juridica; acordao relativo; administrador deram; comprovar regularidade; consequente imputacao

**5. Contratação temporária de servidor sem concurso público — o TCE-RO já se pronunciou?** — 16 casadas, 2600 no restante, k=3

seletivo; simplificado; edital; pronuncia; nulidade; excepcional; ilegal; vagas; contratos; necessidade; interesse; seletivos; processo seletivo; edital processo; interesse publico; considerar ilegal; processos seletivos; atos contratos; seguranca juridica; administracao publica

**6. Obra pública paralisada/em atraso — há precedente de responsabilização?** — 14 casadas, 354 no restante, k=2

contrato; contratual; gestor; empresa; basico; projeto; adequada; atribuida; rescisao; atribuicao; descumprimento; ordem; multa contratual; aplicacao multa; atos contratos

## O que falta para declarar ganho

Rotulagem cega e dupla (dois leitores independentes, sem saber de qual forma veio cada resultado) de uma amostra NOVA de resultados: ajustar numa amostra e validar noutra. Sem isso, os números acima são de ajuste e de sanidade.


## Rotulagem cega (15/10/2026)

Entrada embaralhada, sem métricas, dois anotadores independentes (Sonnet e Opus). Anotador A: 32 pertinentes, 47 genéricos, 28 ruído. Anotador B: 36, 39, 32. Concordância 74%, kappa 0,60. Pertinente nos dois: 28/107 (26%); em pelo menos um: 40/107 (37%). Ruído nos dois (exemplos): insigne, adequada, idonea, deixarem, efetuados, atribuida. Conclusão: o vocabulário sugerido é majoritariamente genérico ou ruído; a ferramenta serve para dar ideias, não para colar. Nenhum ajuste de filtro foi feito sobre esta amostra (ajuste exige amostra nova para validar).
