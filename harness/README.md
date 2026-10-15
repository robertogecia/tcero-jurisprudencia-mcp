# Harness — servidor_tcero.py (estado em 22/09/2026; v1.6.0 em 15/10/2026, ver o fim)

Padrão do harness do TJSE (`~/MCP/tjse-jurisprudencia/harness/`): gabarito montado CEGO à
implementação (regex Python direto sobre ementa+`acordaoDescricao`, nunca usando
`_buscar`/`_filtrar_por_grupos` do próprio servidor), snapshot do acervo guardado localmente
para medir offline, medição reprodutível comparando estratégias de busca.

## O que existe

- `harness/_fetch_snapshot.py` — baixou 8 buscas amplas de uma palavra (`licitacao`,
  `aposentadoria`, `debito`, `multa`, `contrato`, `pessoal`, `prestacao`, `obra`), sem acento de
  propósito (evita problema de encoding na querystring — `textoLivre` já é OU puro, então isso
  não muda o que é encontrado). Gravou `harness/_snapshot/acervo.json` (**5.052 decisões
  únicas** por `idDecisao`) e `harness/_snapshot/contagem.md` (por órgão, ano, sigla). Suporta
  `--from-cache` para reconstruir sem gastar rede, a partir dos `_raw_<palavra>.json` também
  salvos em `_snapshot/`. As fixtures da raiz do projeto (`fixtures/*.json`) foram checadas para
  reaproveito, mas os ids das buscas específicas de lá já estavam cobertos pelas 8 buscas
  amplas — 0 decisões novas vieram só de lá nesta corrida.
- `harness/_explore.py` — monta `harness/gold.json` (6 consultas típicas de advogado em matéria
  de contas) e `harness/_db_index.json` (idDecisao → sigla/numero/orgão/relator/ementa[:300]),
  por regex cega sobre o `acervo.json`, nunca sobre `informacoesAdicionais`. Todas as 6
  consultas têm ≥8 itens `essencial` (a maioria com 10).
- `harness/gold.json` — o gabarito: pergunta, termos que um advogado digitaria, a regex usada
  para achar o gabarito (declarada, não escondida), e as listas `essencial`/`desejavel` com
  `idDecisao` + justificativa. A divisão essencial/desejável é só "os N mais recentes que casam
  a regex" — não há leitura humana de mérito por trás; ver limitações abaixo.
- `harness/medir.py` — roda o `_buscar` REAL do servidor com `_consultar_api` mockado para
  servir do snapshot local (zero rede), nas três formas pedidas: (a) texto_livre "ingênuo" +
  `ordenar="data"`; (b) o mesmo texto_livre + `ordenar="relevancia"`; (c) `grupos` de sinônimos
  (o que um pesquisador experiente montaria, sabendo que o portal só faz OU) + relevância.
  Grava `harness/medicao-2026-09-22.md` (tabela completa + diagnóstico + decisão) e
  `harness/_resultado_bruto.json` (ids devolvidos por consulta/forma, para auditoria).
- `harness/_fetch_pdfs.py` + `harness/_pdfs_plano.json` — baixou 14 PDFs adicionais reais
  (dentro do orçamento de rede da tarefa) para `harness/_pdfs/`, escolhidos offline sobre o
  snapshot: 3 de cada sigla normal (AC1-TC/AC2-TC/APL-TC) e 2–1 de cada sigla de
  embargos/recurso (AC1R-TC/AC2R-TC/APLR-TC), cobrindo os três órgãos julgadores.
- `harness/_fecho.py` — roda `_orgao_do_fecho` real sobre os 4 PDFs de `fixtures/pdf/` + os 14
  novos, grava `harness/fecho-2026-09-22.md`: **18/18 bateram com o cadastro, 0 divergências**.
- `harness/_log_rede.json` — log das 30 requisições gastas nesta sessão (8 buscas amplas do
  snapshot + 8 de uma corrida anterior do mesmo script, que crashou num bug antes de gravar o
  cache em disco e por isso teve de ser refeita + 14 downloads de PDF) — 30/30 do orçamento da
  tarefa, todas bem-sucedidas (status 200).

## Resultado da medição (resumo — ver `medicao-2026-09-22.md` para a tabela completa)

Recall@10 médio contra o gold regex: **(a) data = 2%**, **(b) texto_livre+relevância = 62%**,
**(c) grupos+relevância = 75%** (era 72% antes do red team 22/09/2026-b corrigir o parser do
`medir.py`, que contava ids citados dentro de ementas). Relevância melhorou recall@10 nas 6
consultas, sem piorar nenhuma — por isso `ordenar="relevancia"` virou o padrão de
`buscar_jurisprudencia_tcero` (era `"data"`).

**Leitura corrigida (red team 22/09/2026-b):** o gold regex é circular com o ranking (mesmos
campos, quase as mesmas palavras, mesmo desempate por data), então ele só serve para comparar
(a) com (b). A medida independente — pool cego top-10 de a/b/c anotado contra a PERGUNTA
(`references/red-team-2026-09-22b/anotacao.json`) — dá P@10 **(a) 3%, (b) 70%, (c) 68%**: o
padrão `relevancia` se sustenta; a vantagem de `grupos` sobre texto_livre, não. A coluna antiga
"recall total" era o top-25; agora é o conjunto inteiro (100% em a/b por construção — a ordem
não muda o conjunto).

## Limitações conhecidas

- O gold da consulta 5 é quase todo pensão por morte "temporária" (falso positivo da regex
  `temporaria`+`servidor`) — não é contratação temporária; ver a coluna P@10 cega.
- Gabarito de **um revisor só** (sem segunda leitura cega), mesma ressalva do harness do TJSE.
- `essencial`/`desejavel` são cortados só pela data mais recente entre os que casam a regex —
  não há juízo humano de qual É de fato mais relevante entre os que casam; isso pediria leitura
  manual de cada decisão, fora do escopo deste gabarito automático.
- `informacoesAdicionais` (texto de IA do DEJUR) nunca entra no gabarito, só como campo de
  baixo peso no ranking do servidor.
- O portal não pagina no servidor; o snapshot (5.052 decisões, 8 buscas de uma palavra) é um
  recorte, não o acervo inteiro do TCE-RO.
- `harness/_pdfs/` e `harness/_snapshot/` ficam fora do git (`.gitignore`) por tamanho — quem
  quiser reproduzir a medição sem gastar rede de novo roda `_fetch_snapshot.py --from-cache`
  (se ainda tiver os `_raw_*.json` locais) ou aceita que o `--selftest` do servidor continua
  100% offline com só os 4 PDFs de `fixtures/pdf/`.
- N=18 no fecho×cadastro é maior que o N=4 anterior, mas ainda pequeno para uma conclusão
  definitiva sobre a confiabilidade geral do cadastro do TCE-RO — 0 divergências não prova que
  não existam, só que não apareceram nesta amostra.

## v1.6.0 (15/10/2026) — sugerir_termos_tcero

- `harness/gerar_fundo.py` — gera `fundo_vocabulario.json` (ao lado do servidor): df de palavras (>= 3) e de pares de palavras adjacentes (>= 5) sobre as 5.052 decisões do snapshot, com a mesma tokenização do servidor (`_tokens_vocab`). É dado de runtime de `sugerir_termos_tcero`.
- `harness/medir_sugestoes.py` — mede as sugestões sobre as 6 consultas do `gold.json` (mock do OU nativo de `medir.py`, zero rede), em quatro formas de `grupos` (A base; B3/B5 = + 3/5 sugestões em OU no grupo mais estreito; C3 = + 3 como grupo E), contra o gold (circular) e contra a anotação independente de `references/red-team-2026-09-22b/anotacao.json`. O fundo é refeito sem as decisões casadas de cada consulta. Saída: `harness/_resultado_sugestoes.json` e `harness/medicao-sugerir-termos-2026-10-15.md` (números, protocolo e limites).
- Conclusão registrada: as sugestões ampliam o conjunto (43 → 47 de 49 anotados), mas coladas em bloco derrubam o topo (36 → 27 de 47). **Não declarado como ganho de busca.** Falta rotulagem cega e dupla de amostra nova.
- Rede desta rodada (smoke de cada ferramenta nova): 4 requisições, registradas em `harness/_log_rede.json` (itens 31 a 34).

## v1.7.0 (15/10/2026) — julgados_que_citam_tcero e saídas novas

- Sem script novo: tudo coberto pelo bloco de selftest da v1.7.0 (offline, pastas temporárias, `fixtures/` e `fixtures/pdf/98114.pdf`), inclusive a identidade dos 21 campos do recibo em relação à v1.6.0.
- Comportamento do portal conferido nas fixtures antes de escrever a ferramenta: `fixtures/exp_A4_frase_exata.json` (frase entre aspas honrada: 0 resultados para uma frase inexistente) e `fixtures/exp_C2_controle_or.json` (OU puro: 1.141 decisões). Pela própria fixture de 1.141 decisões, 17 trazem `00037/23` no texto (fora a própria); o filtro local é o que impede de listar a base.
- Rede desta rodada (ao vivo, 3 requisições, intervalo >= 2,5 s, só no fim; `harness/_log_rede.json`, itens 35 a 37): `textoLivre="00037/23"` (28 decisões, 307 KB), `textoLivre=00037/23` sem aspas (366 decisões, 4,7 MB) e a ferramenta ponta a ponta (a mesma consulta com aspas, 24 achados). As mesmas 24 decisões trazem o número no texto nos dois primeiros casos.
- Limites: uma única amostra de número (`00037/23`); número só em ementa/dispositivo/informações adicionais; nenhuma medição de quantas citações seguem ou afastam o julgado, então a saída não dá porcentagem.

