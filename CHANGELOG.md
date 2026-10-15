# Changelog — servidor_tcero.py

## 1.7.0 — 15/10/2026

Porte do TJRO v1.35 / TRF1. Só muda a saída das ferramentas: **o recibo é o da 1.6.0** (21 campos, mesma ordem e serialização; conferido no selftest e byte a byte contra a 1.6.0). Frases de saída estáveis para o porte Node.

- **`julgados_que_citam_tcero`** (`numero` NNNNN/AA, `limite`): quem cita um processo ou acórdão, só por texto (portal, `textoLivre` entre aspas, 1 consulta) + recibos locais (sem rede); a fonte de cada achado vem dita; janela de contexto; avisos de que não detecta superação, de que zero não prova nada e de que o recall é baixo (PDF não é varrido). O filtro local do número garante que um portal que não honre a frase nunca despeja a base inteira. Ao vivo (3 requisições): com aspas 28 decisões, sem aspas 366, as mesmas 24 com o número no texto.
- **TESE DA EMENTA (literal)** na busca, na triagem e no modo completo, com `⚠️ TESE INCOMPLETA` quando cortada; no TCE-RO a tese está sob "III. Entendimento" (modelo do CNJ: "IV. Dispositivo e tese"); modelo antigo não mostra nada; a linha manda conferir aspas em `verificar_citacao_tcero`.
- **VOZ DA CASA** no verificador (`notas`, linha `ℹ`), quando o trecho está na ementa, no dispositivo ou no fecho do próprio acórdão. `alertas` não mudou.
- **Placar** de consultas e nível do limitador no fim da busca.
- **Consulta pouco seletiva** a partir de 1.000 resultados do portal.
- **Corte da busca no limite de um resultado** (o teto de 60 mil já existia; ganhou a fronteira de resultado e o aviso).
- Selftest: bloco novo (fixtures e PDFs reais, pastas temporárias) para cada item e para a identidade dos campos do recibo. `VERSAO = "1.7.0"`.
- **Correção de número (sugerir_termos):** a estimativa de 59% de sugestões pertinentes (v1.6.0) era leitura minha, não cega, e estava inflada. Rotulagem cega por 2 anotadores independentes (Sonnet e Opus): pertinentes nos dois 26% (28/107), em pelo menos um 37%; concordância 74% (kappa 0,60). Use uma sugestão por vez, com critério seu.

## 1.6.0 — 15/10/2026

Porte das ideias do TJRO v1.25–v1.34 para o TCE-RO. O pacote Node (`.mcpb`) é porte deste arquivo e será atualizado depois; a lógica nova está em funções puras (texto → texto), separadas da rede, com frases de saída estáveis.

- **`buscar_recibos_tcero`** (`consulta`, `grupos`, `relator`, `orgao`, `limite`): busca sem rede nos recibos locais — ementa, dispositivo e texto do PDF, nunca o texto de IA do DEJUR. Palavra inteira com a normalização do verificador. Devolve citação pronta (sem DOe: o recibo não o guarda), id, link, a verificação gravada, onde o termo aparece (posição + página aproximada) e o trecho. Diz quantos recibos existem e que zero não é "não há jurisprudência". O formato do recibo não mudou (nenhum campo novo).
- **Diário de erros e `diagnostico_erros_tcero`** (`dias`, `relatorio`): falha de ferramenta (exceção, `[LEITURA DE PDF NÃO REALIZADA`, erro de portal, formato inesperado; também PDF sem texto e extração parcial, como "parcial") grava uma linha em `~/.tcero-jurisprudencia/erros.jsonl` (`TCERO_MCP_DIR_ESTADO`; poda acima de 400 KB), só com dado técnico e mensagem sanitizada; nunca o texto da busca nem trecho citado. A tool resume por tipo e período e devolve o link de relato já existente.
- **`linha_do_tempo_tcero`**: contagem por ano (da sessão) e por órgão sobre UMA consulta (mesmos parâmetros de `_buscar`, então o cache de uma busca idêntica vale), com as 2 decisões mais pertinentes de cada ano, citação e link. Avisa que é contagem do que o portal devolveu, não tendência da Corte.
- **`sugerir_termos_tcero`**: 10–20 palavras e pares distintivos das ementas + dispositivos que casaram a consulta (frequência nas casadas × restante da resposta × fundo de vocabulário `fundo_vocabulario.json`, novo arquivo ao lado do servidor, gerado por `harness/gerar_fundo.py`). **Medido, sem declarar ganho:** as sugestões ampliam o conjunto (decisões anotadas como relevantes: 43 → 47 de 49), mas coladas em bloco derrubam o topo (36 → 27 de 47 com 3 sugestões em OU; piorou em 4 de 6 consultas). Qualidade, por leitura minha e não cega: 59% pertinentes, 25% genéricas, 16% ruído. O gold é circular; ver `harness/medicao-sugerir-termos-2026-10-15.md`.
- **`obter_acordao_tcero(..., modo="triagem")`**: citação, resultado, ementa inteira, dispositivo, órgão do cadastro, link; com `ler_inteiro_teor`, do PDF só a estrutura (acórdão, relatório, voto, voto de outro conselheiro, com página), o fecho e as linhas que os detectores marcam (divergência, parecer do MPC, alegação, transcrição, obiter), cada uma com o lugar. 7,5 mil caracteres contra 55 mil no acórdão 98114. Nunca serve para aspas. O recibo gravado é idêntico ao do modo completo (conferido campo a campo no selftest).
- **Alertas que dizem onde:** `OBITER DICTUM?` mostra a frase da marca (ou que a marca está no começo do trecho); a posição "VOTO de outro conselheiro" mostra o título do voto; `verificar_citacao_tcero` e a busca de recibos mostram a página aproximada do PDF (`p. ~N de M`). Não se criou rótulo `VOTO DIVERGENTE` (não medido). Em 900 janelas dos 36 recibos locais, o resto não mudou em relação à 1.5.1.
- **Atualizar:** o aviso de versão nova e o README trazem as duas instruções (Python: `git pull` + reiniciar; Claude Desktop: baixar o `.mcpb` da release e dar dois cliques). A ferramenta que baixa o `.mcpb` (como `atualizar_extensao_tjro`) fica para o porte Node.
- `_excertos_raw` agora delega a `_excertos_raw_com_pos` (mesmo resultado; a posição serve à triagem). Selftest: bloco novo de regressões (diário sem vazamento de segredo, busca de recibos, linha do tempo com a fixture de 1.141 decisões, sugestão, triagem com os PDFs reais, alertas); a asserção do aviso de versão passou a incluir as instruções de atualização.

## Extensão 1.5.1 — 07/10/2026

- Aviso de versão nova com link DIRETO do arquivo .mcpb e a instrução "dê dois cliques no arquivo baixado e reinicie o Claude Desktop" (antes, só o link da página de versões; o texto em itálico terminava colado ao link e podia quebrá-lo).
- NEGAÇÃO, segunda validação cega (120 trechos de documentos inéditos, 102/120 concordes, 18 adjudicados): o alerta forte acertou 63% (na primeira, 80%) e 13% das negações reais ficaram sem aviso (na primeira, 28%) — a variação entre amostras é grande, por isso vão os dois números. Testado e REJEITADO baixar o alcance mínimo de 3 para 1 palavra: os casos novos são quase todos fragmentos de ementa ("NÃO [COMPROVADA. …]") e a perda de precisão não compensa (sem aviso 13% → 10%, forte 63% → 59%).

## 1.5.1 — 07/10/2026

- Correção: o servidor Python não abria no Python 3.10 e 3.11 (SyntaxError: barra invertida dentro da expressão de uma f-string, no texto do alerta de POSIÇÃO — só o Python 3.12+ aceita). Afetava as versões publicadas desde 06/10/2026; o CI do GitHub acusava. A extensão .mcpb (Node) não tinha o defeito.

## 1.5.0 — 07/10/2026

- NEGAÇÃO em dois níveis. Continua "NEGAÇÃO:" quando a negação está colada ao trecho (até uma palavra antes) ou é existencial ("não há/houve/existe …", até cinco palavras). O resto que a regra anterior pegava sai como "NEGAÇÃO (distante)?", dizendo que em geral ela fecha a própria oração e não inverte o recorte. Gabarito cego e duplo em 120 trechos NOVOS de cinco tribunais (TJRO, TJSE, STJ, TCE-RO e TED-OAB; concordância 108/120, 12 adjudicados pela definição escrita), ponderado pela população: o alerta forte acerta 80% (falso alarme 6%); a regra anterior, sozinha, acertava 50% (falso alarme 33%) nesta amostra. Somados, os dois níveis avisam nos mesmos 72% das negações reais; o forte sozinho pega 53%.
- Paridade Python×Node (`test/paridade.py` da extensão): as duas diferenças antigas passam a ser classificadas pela causa, sem divergência real. (1) No PDF grande, o PyMuPDF devolve mais espaço em branco que o pdf.js, então o orçamento de caracteres acaba em pontos diferentes e o miolo omitido — sempre dito na saída — começa em lugar diferente; o começo é idêntico depois de normalizar espaço. (2) Os excertos do parecer do MPC usam janela em caracteres brutos: com mais espaço, cabe uma palavra a menos. Igualar exigiria normalizar o texto do PDF, o que mudaria o hash dos recibos novos e o texto em que a POSIÇÃO foi medida — decisão: registrar, não mexer.

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
