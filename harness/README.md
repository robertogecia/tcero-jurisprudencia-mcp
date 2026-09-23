# Harness — servidor_tcero.py (estado em 22/09/2026)

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

Recall@10 médio: **(a) data = 2%**, **(b) texto_livre+relevância = 62%**, **(c)
grupos+relevância = 72%**. Relevância melhorou recall@10 nas 6 consultas, sem piorar nenhuma —
por isso `ordenar="relevancia"` virou o padrão de `buscar_jurisprudencia_tcero` (era `"data"`).

## Limitações conhecidas

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
