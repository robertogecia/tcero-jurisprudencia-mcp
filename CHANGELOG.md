# Changelog — servidor_tcero.py

## 1.2.0 — 22/09/2026

- `buscar_jurisprudencia_tcero`: novo parâmetro `ordenar` (`"relevancia"`, **padrão**, offline —
  pontua termos distintos de `texto_livre`/`grupos`, núcleo ementa+dispositivo peso 2,
  informações adicionais de IA peso 1, desempate por data; `"data"`, ordem do portal). Decisão
  de tornar `"relevancia"` padrão baseada em medição real (`harness/medir.py` + `gold.json`,
  gabarito cego de 6 consultas contra snapshot de 5.052 decisões): recall@10 médio 2% (data) →
  62% (relevância) → 72% (grupos+relevância), melhora em todas as 6 consultas, nenhuma piorou —
  ver `harness/medicao-2026-09-22.md`. Cada item mostra `termos casados: N/M` quando
  `ordenar="relevancia"`. Valor inválido é recusado sem gastar requisição.
- Novo bloco "Panorama" (facetas offline: órgão, ano, sigla, natureza, top-5 relatores) ao final
  da página 1, só quando a busca tem 3+ decisões.
- `_orgao_do_fecho`: agora devolve `None` quando o PDF contém fechos de órgãos julgadores
  DIFERENTES (acórdão de embargos/recurso que transcreve o fecho do acórdão embargado); dois
  fechos iguais continuam contando como um só. Amostra ampliada para N=18 (4 PDFs de
  `fixtures/pdf/` + 14 baixados em 22/09/2026 para `harness/_pdfs/`, distribuídos entre 1ª
  Câmara/2ª Câmara/Pleno e siglas normais + embargos/recurso): **18/18 bateram, 0
  divergências** — `harness/fecho-2026-09-22.md`. Aviso de divergência em
  `obter_acordao_tcero(..., ler_inteiro_teor=True)` continua **desligado** (nenhum caso real
  na amostra).
- `--selftest` ganhou regressões para os três itens acima (ranking, panorama, fecho
  conflitante), permanecendo 100% offline (usa só os 4 PDFs de `fixtures/pdf/`, não os de
  `harness/_pdfs/`, que ficam fora do git por tamanho).
- Harness completo montado e rodado em 22/09/2026: `harness/_fetch_snapshot.py`,
  `harness/_explore.py`, `harness/gold.json`, `harness/_db_index.json`, `harness/medir.py`,
  `harness/medicao-2026-09-22.md`, `harness/_resultado_bruto.json`, `harness/_fetch_pdfs.py`,
  `harness/fecho-2026-09-22.md`, `harness/_log_rede.json` (30/30 requisições do orçamento da
  tarefa, todas bem-sucedidas).

- Red team (b) do mesmo dia (`references/red-team-2026-09-22b.md`): o gabarito regex é circular
  (olha os mesmos campos que o ranking); em anotação cega de 130 itens o top-10 pertinente foi
  3 % (data) × 70 % (relevância) × 68 % (grupos+relevância) — o padrão `relevancia` se sustenta,
  `grupos` NÃO ordena melhor que `texto_livre`. Corrigidos: `"frase exata"` vira um termo,
  palavras vazias não pontuam, panorama tolera campo em lista e conta relator uma vez,
  `_orgao_do_fecho` reconhece "Tribunal Pleno"/"Primeira Câmara". Fecho × cadastro: 18/18.
- Pacote `.mcpb` (porte Node, `~/MCP/tcero-jurisprudencia-mcpb`): mesmas 4 ferramentas, 38 testes,
  paridade Node × Python 9/12 byte a byte (as 3 diferenças são só espaçamento da extração de PDF).

## 1.1.0 e anteriores

Ver histórico de commits e `references/` — changelog formal só começou neste porte.
