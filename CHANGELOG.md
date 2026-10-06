# Changelog — servidor_tcero.py

## 1.4.0 — 06/10/2026

- `verificar_citacao_tcero` ganha a POSIÇÃO NO JULGADO: ementa do cadastro, autuação e cabeçalho de página do PDF, ementa (com as seções do TCE-RO: Contexto fático, Questão técnica e/ou jurídica, Entendimento, Fundamento), ACÓRDÃO, relatório, voto ou proposta de decisão do relator, dispositivo e voto de outro conselheiro (pelo nome no título, comparado com o relator da autuação). Medido às cegas: **88% numa validação de 62 trechos novos** (97% na amostra de ajuste).
- NEGAÇÃO mais estreita: só avisa com a negação até 6 palavras antes do trecho; não avisa quando ela nega um particípio ("não utilizado pelo…") ou recusa uma alternativa ("…, e não sobre…"); "não é outro o entendimento", "não se desconhece" e "não se pode deixar de" afirmam. Gabarito cego e duplo: ajuste em 617 trechos já rotulados (TJSE, STJ, TRT14, OAB, TCE-RO), validação em 120 trechos NOVOS de cinco tribunais (concordância 114/120, 6 adjudicados): precisão 38% → 44%, falso alarme 42% → 31%, cobertura 100% → 98%. Continua o alerta mais fraco do bloco: é aviso para ler a frase, não veredito.
- OBITER DICTUM? reconhece também "registre-se, por oportuno", "a título de registro" e "apenas para registro" (6 de 6 obiter às cegas). Outras marcas testadas ficaram de fora por imprecisas: "de passagem" 67%, "por cautela" 25%, "ainda que se entenda/admita" 30%.
- Extensão `tcero-jurisprudencia-mcpb` 1.4.0 com o mesmo localizador (módulo `posicao2.js`, idêntico nas extensões do TRT14, TRF1 e OAB); paridade das posições Python×Node: 40.263 casos, 0 diferentes.

## 1.3.0 — 06/10/2026

- `verificar_citacao_tcero`: NEGAÇÃO por ALCANCE (operador de negação ou rejeição sem quebra de oração até o trecho,
  alcançando 3+ palavras dele; "não há dúvida", "não obstante" e "ainda que assim não fosse" não negam; "sem razão" nega),
  ENTRE ASPAS por PAREAMENTO das aspas no documento inteiro, e o alerta novo OBITER DICTUM? ("ainda que assim não fosse",
  "a título de argumentação") — o bloco de regras do TJRO v1.13/1.16, o mesmo de STJ, TRT14, TJSE, TRF1 e OAB. TRANSCRIÇÃO,
  PARECER DO MPC/CORPO TÉCNICO e ALEGAÇÃO DA PARTE continuam os do TCE-RO. Sem o texto bruto, valem as regras antigas.
- Medido às cegas sobre 13 acórdãos baixados em 06/10/2026 (85 trechos, dois rotuladores, kappa 0,82-1,00), ponderado por
  estrato: **NEGAÇÃO 88% de precisão e 75% de cobertura, contra 31% e 72% da regra antiga** (que avisava em toda negação nos
  80 caracteres anteriores: 34% de falso alarme); OBITER 5 de 5 disparos corretos. ENTRE ASPAS sem caso positivo na amostra:
  os acórdãos de contas medidos só têm aspas curtas, que não contam.
- ENTRE ASPAS medido depois, no mesmo dia, sem mudar a regra: 23 acórdãos novos escolhidos por temas que transcrevem texto
  entre aspas (`harness/baixar_aspas.py`, um pedido por vez, 15 s entre pedidos) e 85 trechos rotulados às cegas por dois
  rotuladores (concordância 84/85, uma divergência adjudicada no texto), ponderado por estrato: **precisão 94%, cobertura 100%,
  falso alarme 0%, contra 16%, 45% e 14% da regra antiga**.
- Extensão `tcero-jurisprudencia-mcpb` 1.3.0 com as mesmas regras; a paridade passou a comparar com o servidor ATUAL. As duas
  diferenças que ela acusa (texto do PDF e `texto_parecer_mpc`) já existiam e vêm da extração de PDF (PyMuPDF × pdfjs).

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
