# Jurisprudência do TCE-RO no Claude

[![tests](https://github.com/robertogecia/tcero-jurisprudencia-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/robertogecia/tcero-jurisprudencia-mcp/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Pesquise a jurisprudência do **Tribunal de Contas do Estado de Rondônia (TCE-RO)** dentro da
conversa com o Claude, sem abrir o portal do tribunal, sem login e sem mexer em código. Feito
para advogados **sem conhecimento nenhum de informática**. Comece pela instalação, logo abaixo.

## Instalar (3 passos, uns 2 minutos)

**Você precisa do "Claude Desktop"** — o *programa* do Claude instalado no computador (Mac ou
Windows), não o site no navegador nem o aplicativo do celular. Se você usa o Claude num
aplicativo separado, já tem. Se usa só pelo navegador, baixe primeiro o programa em
**[claude.com/download](https://claude.com/download)**, instale, entre com a sua conta e volte
aqui.

### Passo 1 — Baixe o arquivo

### ⬇️ [CLIQUE AQUI PARA BAIXAR (`Jurisprudencia-TCERO.mcpb`)](https://github.com/robertogecia/tcero-jurisprudencia-mcp/releases/latest/download/Jurisprudencia-TCERO.mcpb)

Um arquivo chamado `Jurisprudencia-TCERO.mcpb` (uns 21 MB) vai para a pasta **Downloads** (ou
"Transferências") do seu computador — o mesmo lugar onde caem os PDFs que você baixa da internet.
Você não precisa abri-lo agora, só saber onde ele está.

> **⚠️ Atenção a um erro comum:** se em vez de clicar no botão acima você navegou até a página
> principal do projeto no GitHub e clicou no botão verde **"Code" → "Download ZIP"**, isso baixou
> o arquivo errado (o código-fonte do programa, que não serve para instalar). Apague esse zip e
> use só o link do botão acima.

### Passo 2 — Abra o arquivo baixado

1. Abra a pasta **Downloads** do seu computador (no Mac, o ícone de seta para baixo na barra de
   baixo da tela costuma abrir direto nela; no Windows, é "Este Computador" → "Downloads").
2. Procure o arquivo **`Jurisprudencia-TCERO.mcpb`** e **dê dois cliques** nele, como faria para
   abrir uma foto ou um PDF.
3. O Claude Desktop deve abrir sozinho, numa tela perguntando se você quer instalar a extensão
   "Jurisprudência TCE-RO". Clique em **Instalar** (ou "Install").

   *Se nada abrir:* abra você mesmo o Claude Desktop, vá em **Configurações** (o ícone de
   engrenagem) → **Extensões**, e arraste o arquivo `Jurisprudencia-TCERO.mcpb` para dentro dessa
   janela com o mouse.

### Passo 3 — Confirme e teste

1. Se o Claude Desktop pedir para **reiniciar**, feche e abra o programa de novo.
2. Comece uma **conversa nova** (importante: conversa aberta antes da instalação não enxerga a
   extensão).
3. Digite algo como:
   > *pesquise no TCE-RO acórdãos sobre dispensa de licitação por emergência*
4. O Claude vai perguntar se pode usar a ferramenta de pesquisa do TCE-RO — é sinal de que
   funcionou. Autorize, e a busca aparece na conversa.

**Pronto.** Você não precisa instalar mais nada: o Claude Desktop já traz tudo o que a extensão
precisa para rodar. Funciona em computador **Mac ou Windows**. Em celular ou tablet, e no Claude
pelo site (sem o programa), esta pesquisa não funciona — veja ["Onde funciona"](#onde-funciona).

## Como vai funcionar no dia a dia

Você pede em português, como pediria a um estagiário, e o Claude usa a extensão por conta própria:

> "Pesquise no TCE-RO acórdãos sobre reincidência no descumprimento de determinação da Corte."
>
> "Há decisão do Pleno sobre contratação temporária sem concurso? Quero as mais pertinentes."
>
> "Abra o acórdão APL-TC 00055/26 e leia o inteiro teor."
>
> "Esse trecho que você citou está mesmo no acórdão? Confira."
>
> "O que eu já li do TCE-RO sobre reincidência e multa?"
>
> "Em que anos e em qual Câmara aparece o tema contratação temporária?"
>
> "Com que outras palavras o tribunal fala de direcionamento de licitação?"
>
> "Vale a pena ler o acórdão 98114 inteiro? Faça uma triagem antes."

O que você recebe de volta:

- **Uma lista de decisões, as mais pertinentes primeiro.** O portal do tribunal ordena só por
  data; a extensão reordena pelo tanto que cada decisão fala do seu assunto e diz, em cada uma,
  quantos dos seus termos ela contém. Cada item já vem com a **citação pronta** (sigla, número,
  relator, órgão, data), o resumo da ementa e o **link direto para o PDF** do acórdão no site do
  tribunal.
- **Um panorama da busca**, quando há três ou mais decisões: quantas são do Pleno e de cada
  Câmara, de que anos, de que tipo, e quais relatores mais aparecem. É um indício para escolher o
  que ler, nunca uma conclusão sobre a tese.
- **O acórdão inteiro**, não só a ementa: a extensão baixa o PDF do próprio tribunal e extrai o
  relatório e o voto. Quando o acórdão é longo demais para caber de uma vez, ela entrega o começo
  e o fim e **avisa que leu "em parte"** — nesse caso ela serve para citar o que está ali, mas não
  para afirmar que algo *não* consta do acórdão.
- **Conferência antes das aspas.** Peça para conferir um trecho e a extensão diz se ele está
  literalmente na ementa, no dispositivo ou no inteiro teor. Se está, ainda avisa **de quem é a
  frase**: acórdão de contas transcreve o parecer do Ministério Público de Contas, o relatório do
  corpo técnico e a defesa do gestor, e um trecho literal pode ser a alegação da parte, não a
  posição da Corte.
- **Um recibo guardado no seu computador** com o texto que o tribunal entregou, toda vez que uma
  decisão é aberta. Serve para provar depois, a olho ou por script, que a citação da peça veio do
  documento — e não da imaginação da IA.

**O que há de novo na versão 1.7.0, em linguagem simples:**

- **"Quem citou este julgado depois?" (`julgados_que_citam_tcero`).** Você dá o número de um
  processo ou de um acórdão (por exemplo `00037/23`) e a extensão mostra os acórdãos que o citam,
  com o trecho em volta, e diz de onde veio cada achado: do que o portal do tribunal indexa ou dos
  acórdãos que já passaram por este computador (sem rede). **É leitura assistida, não confirmação.**
  Ela **não detecta superação** (não diz se o julgado citado foi superado ou distinguido) e
  **resultado zero não prova que ninguém aplicou o julgado**: o portal só indexa o texto da ementa,
  do dispositivo e das informações adicionais, e o PDF do inteiro teor não é varrido, então muita
  citação só aparece lá dentro e não é achada.
- **A tese da ementa, literal.** Quando a ementa segue o modelo novo ("Tese de julgamento: ..."), a busca, a
  triagem e a leitura completa mostram a tese entre aspas, tal como está. Se ela é longa e foi cortada, vem o aviso
  "TESE INCOMPLETA" e a orientação de abrir o inteiro teor. Ementa do modelo antigo não mostra nada. A
  tese da ementa é o que o órgão enunciou, **não prova de que foi a razão de decidir**, e **para pôr entre aspas
  continua valendo a conferência de `verificar_citacao_tcero`**.
- **"VOZ DA CASA".** Ao conferir um trecho, se ele está na ementa, no dispositivo ou no fecho do
  próprio acórdão, a extensão avisa que ali quem fala é o TCE-RO, e não um parecer ou outro julgado
  transcrito dentro do voto. É o contrário dos avisos amarelos: é um sinal de que a frase é da Corte.
- **Placar no fim da busca.** Quantas consultas ao portal você já fez na janela do limitador e em
  que nível ele está, para você saber quanto ainda pode pesquisar antes de a extensão pedir uma pausa.
- **Aviso de consulta pouco seletiva.** Quando o portal devolve mil decisões ou mais (as palavras
  entram em OU), a busca diz que o topo é só uma amostra e sugere restringir por relator, órgão
  julgador ou ano, ou exigir os conceitos com `grupos`.
- **Resposta que nunca vem cortada no meio de uma decisão.** O teto de 60 mil caracteres já existia;
  agora, se a busca precisa cortar, ela corta no limite de uma decisão e diz até onde mostrou.

**O que as ferramentas novas da versão 1.6.0 fazem, em linguagem simples:**

- **"O que eu já li?" (`buscar_recibos_tcero`).** Procura nos acórdãos que o Claude já abriu para
  você neste computador, **sem consultar o tribunal** e sem gastar nenhuma consulta. Serve para
  reencontrar um acórdão da semana passada, ou achar uma expressão no voto de um acórdão que já
  passou por aqui. Atenção: ela só enxerga o que já foi aberto. **Resultado zero não quer dizer
  que o tribunal não tem decisão sobre o assunto** — para isso, a pesquisa normal.
- **"Quando e onde o tema aparece?" (`linha_do_tempo_tcero`).** Conta, ano a ano e por Câmara/Pleno,
  as decisões da sua pesquisa, e mostra as duas mais pertinentes de cada ano, com citação e link.
  É contagem do que o portal devolveu, **não prova de que a Corte mudou de entendimento**: serve
  para saber quais períodos ler.
- **"Com que outras palavras o tribunal fala disso?" (`sugerir_termos_tcero`).** O portal só acha as
  palavras que você digitou. Esta ferramenta olha as ementas das decisões que casaram a sua
  pesquisa e lista de 10 a 20 palavras e pares de palavras que costumam acompanhá-las. Você escolhe
  as que são mesmo sinônimas do seu assunto e refaz a busca. **Não cole a lista inteira na busca**:
  nos testes isso piorou o topo da lista na maioria dos casos (detalhes na parte técnica).
- **"Vale a pena ler este acórdão?" (`modo="triagem"` em `obter_acordao_tcero`).** Uma leitura
  barata (no acórdão 98114, 7,5 mil caracteres contra 55 mil do modo completo): citação, resultado, ementa,
  dispositivo e, se pedir o PDF, onde começam o relatório e o voto, o fecho com o que o colegiado
  decidiu e os pontos em que há parecer do Ministério Público de Contas, transcrição de outro
  julgado, alegação da parte ou voto de outro conselheiro. **A triagem nunca serve para pôr
  trecho entre aspas.**
- **"A extensão está falhando?" (`diagnostico_erros_tcero`).** A extensão anota, no seu computador,
  só os erros técnicos (rede, portal, PDF): nunca o que você pesquisou. Esta ferramenta resume os
  erros e entrega o link do formulário de relato já preenchido.
- **Avisos que agora dizem onde.** Quando um trecho está sob uma frase do tipo "ainda que se
  admitisse…" (obiter dictum) a conferência mostra a frase; quando o trecho está no voto de outro
  conselheiro, mostra o título do voto; e a posição no julgado ganha a página aproximada do PDF.

## O que ela NÃO faz (leia antes de confiar)

- **Não substitui a leitura do acórdão.** A citação pronta, o resumo e o panorama são ponto de
  partida. Confirme número, relator, órgão, data e o sentido do julgado no PDF antes de levar para
  a peça — é para isso que o link vem em cada resultado.
- **O portal traz um resumo feito com inteligência artificial pelo próprio tribunal** (a seção
  "informações adicionais": fatos, questão, regras, análise, conclusão). A extensão mostra esse
  texto sempre com aviso, **nunca** o usa para confirmar uma citação, e você também não deve
  citá-lo como se fosse o acórdão.
- **Não lê acórdão digitalizado como imagem** (PDF sem texto). Ela avisa e você abre o link no
  navegador.
- **A linha do tempo e as sugestões de palavras são indício, não conclusão.** A contagem por ano
  mistura volume de processos, composição das Câmaras e o que o portal publica; a lista de
  palavras vem das decisões que já casaram a sua busca e tem ruído (nos testes, cerca de uma em
  seis sugestões era ruído e uma em quatro, genérica).
- **Não pesquisa outros tribunais.** TJRO, TRF1, STJ e outros têm extensões próprias do mesmo
  autor; superação de entendimento vinda de cima (TCU, STF) se confere na fonte respectiva.
- **Não dá parecer.** Toda saída é rascunho para a sua revisão; a decisão sobre tese, pedido e
  protocolo é sua.

## Algo deu errado? Veja aqui antes de pedir ajuda

| O que aconteceu | O que fazer |
|---|---|
| Baixei um arquivo, mas quando abro vira uma **pasta cheia de arquivos**, e não a tela de instalação | Você baixou o arquivo errado (o código-fonte, não o instalador). Volte ao topo e use o botão **"CLIQUE AQUI PARA BAIXAR"**. |
| Dei dois cliques no `.mcpb` e **não abriu nada** | Use o caminho alternativo do Passo 2: Claude Desktop → Configurações → Extensões, e arraste o arquivo para essa janela. |
| Instalei, mas o Claude diz que **não tem essa ferramenta** | Abra uma **conversa nova**. Confira também se a extensão aparece **ativada** em Configurações → Extensões. |
| A busca devolve **zero** quando filtro por relator ou por órgão | O portal exige o nome **exatamente** como ele conhece e devolve vazio sem avisar. A extensão diz quando não reconheceu o filtro e lista os valores aceitos: corrija antes de concluir que "não há jurisprudência". |
| A extensão diz que o PDF **não tem texto** | O acórdão foi digitalizado como imagem. Abra o link do PDF no navegador e leia lá. |
| Apareceu uma mensagem dizendo para **esperar alguns minutos** | Não é defeito: a extensão se impõe um limite de consultas por cortesia com o servidor do tribunal. Espere o tempo indicado. |
| Erro de rede em toda busca, mas o portal abre no navegador | O tribunal pode ter mudado o portal. Veja se há [versão nova](https://github.com/robertogecia/tcero-jurisprudencia-mcp/releases/latest) (a própria mensagem de erro avisa quando há) e, se não houver, [relate o problema](../../issues). |
| Não tenho o Claude Desktop, só uso pelo site ou pelo celular | A pesquisa **não funciona** nesses casos — precisa do programa instalado no computador. |
| Nenhuma linha acima resolveu | Peça ajuda a alguém do escritório com mais prática em informática mostrando esta tabela — ou [abra uma issue](../../issues) descrevendo o que aconteceu (sem nome de parte nem número de processo: a página é pública). |

## Atualizar e desinstalar

- **Atualizar:** quando sair versão nova, a primeira resposta da conversa avisa. **Pelo Claude
  Desktop (arquivo `.mcpb`, o caminho deste guia):** baixe o arquivo novo pelo mesmo botão do
  Passo 1, dê dois cliques nele e confirme "Instalar" por cima; a versão antiga é substituída;
  feche e abra o Claude. **Se o seu escritório instalou pelo Python (cópia do código no
  computador):** rode `git pull` na pasta do programa e reinicie o Claude.
- **Desinstalar:** Claude Desktop → Configurações → Extensões → "Jurisprudência TCE-RO" →
  Remover. Se quiser, apague também a pasta de recibos `.tcero-jurisprudencia-recibos` na sua
  pasta de usuário.

## Reportar erro, pedir melhoria

- **Erro**: a própria mensagem de erro traz um link que abre o formulário de relato no GitHub já
  preenchido com os dados técnicos (versão, sistema, tipo do erro). **Nada da sua pesquisa vai
  junto**, e você revisa antes de enviar. Ou [abra uma issue](../../issues/new) à mão.
- **Sugestão**: [issue](../../issues/new) também. Diga o que tentou pesquisar (em abstrato — sem
  nome de parte nem número de processo, as issues são públicas) e o que esperava.
- Precisa de conta gratuita no GitHub. O autor mantém isto no tempo livre; a resposta pode
  demorar.

## Apoie o projeto

A extensão é gratuita e de código aberto, e é mantida no tempo livre de um advogado: cada
mudança do portal do TCE-RO exige diagnóstico, correção, testes e versão nova. Se ela economiza o
seu tempo, você pode apoiar a continuidade do trabalho com qualquer valor, por **Pix**:

> **Chave Pix (e-mail):** `robertogrecia@hotmail.com`

O apoio é voluntário e não muda nada no uso: a extensão continua igual para todos.

## Autor

**Roberto Grécia Bessa** — OAB/RO 7865-A
Instagram: [@robertogrecia](https://instagram.com/robertogrecia)

Irmã das extensões de jurisprudência do [TJRO](https://github.com/robertogecia/tjro-jurisprudencia-mcp),
do [TRF1](https://github.com/robertogecia/trf1-jurisprudencia-mcp) e do
[TJSE](https://github.com/robertogecia/mcp-tjse-jurisprudencia), do mesmo autor. Licença MIT —
veja [LICENSE](LICENSE).

---

# Para quem programa (ou quer entender por dentro)

Daqui para baixo o texto é técnico: como o servidor Python funciona, o que foi medido ao vivo,
como instalar pelo Claude Code, segurança e auditoria. Um advogado que só quer usar a extensão
não precisa ler nada disto.

## Ferramentas

| Tool | O que faz |
|---|---|
| `buscar_jurisprudencia_tcero` | busca por texto livre e/ou por número de acórdão, número de processo, relator ou órgão julgador; `grupos` (E entre grupos, OU dentro do grupo) filtra por 2+ conceitos — o E é feito **no cliente**, porque o portal só sabe fazer OU e ordena por data, não por relevância; paginação **no cliente** (a API do portal não pagina no servidor); resumo compacto por padrão (já com o link do PDF de cada item, corrigido para o host atual), `detalhar=true` para os primeiros itens da página |
| `obter_acordao_tcero` | detalhe completo de uma decisão — ementa integral, dispositivo (`acordaoDescricao`), informações adicionais (⚠️ geradas por IA pelo DEJUR do próprio tribunal), legislação aplicada, link do PDF do inteiro teor; prefira `id_decisao` (busca direta, resposta pequena); `ler_inteiro_teor=true` baixa esse PDF e EXTRAI O TEXTO REAL (relatório + voto, não só ementa/dispositivo) — ver seção dedicada abaixo; grava um **recibo de custódia** em disco a cada chamada — ver seção dedicada |
| `verificar_citacao_tcero` | confere se um trecho aparece literalmente na ementa, no dispositivo ou (quando já lido) no inteiro teor em PDF antes de ir entre aspas — `[...]` separa fragmentos, ❌ vem com o que não bateu; casamento por **palavra inteira** (não substring), mínimo de 15 caracteres não-espaço por fragmento; conferido primeiro contra o **recibo local** (zero requisição) quando ele existe, senão contra o portal; ✅ pode vir com **alertas de atribuição** (o trecho é literal, mas pode não ser a posição da Corte) — ver seção dedicada |
| `buscar_recibos_tcero` | **v1.6.0.** Busca SEM REDE nos recibos locais (`consulta`, `grupos`, `relator`, `orgao`, `limite`) — ver seção "Ferramentas da v1.6.0" |
| `diagnostico_erros_tcero` | **v1.6.0.** Resume o diário local de falhas (`dias`, `relatorio`) e devolve o link de relato já preenchido; sem rede |
| `linha_do_tempo_tcero` | **v1.6.0.** Contagem por ano e por órgão sobre UMA consulta, com as 2 decisões mais pertinentes por ano |
| `sugerir_termos_tcero` | **v1.6.0.** 10–20 palavras e pares de palavras distintivos das decisões que casaram, para montar `grupos` |
| `julgados_que_citam_tcero` | **v1.7.0.** Quem cita um processo/acórdão (`numero` NNNNN/AA, `limite`): UMA consulta ao portal (frase entre aspas no texto livre) + recibos locais sem rede; leitura assistida — ver seção "Ferramentas da v1.7.0" |
| `diagnostico_ritmo_tcero` | estado do disjuntor/limitador, sem rede; primeira linha traz a versão instalada |

`obter_acordao_tcero` ganhou o parâmetro `modo` (`"completo"`, padrão, ou `"triagem"`).

## v1.7.0 (15/10/2026) — porte do TJRO v1.35 / TRF1

Só muda a **saída** das ferramentas; o recibo de custódia (campos e serialização) é o da 1.6.0 — o selftest
compara os 21 campos, a ordem e o sha256, e o recibo gravado byte a byte por esta versão e pela 1.6.0 é idêntico.
Frases de saída estáveis (o pacote Node é porte deste arquivo).

### `julgados_que_citam_tcero(numero, limite?)`
- Entrada: `NNNNN/AA` (1 a 5 dígitos, barra, 2 dígitos; `37/23` vira `00037/23`). Só busca **texto**: uma consulta ao
  portal com `textoLivre="00037/23"` (frase entre aspas) e a mesma busca, sem rede, no campo `texto` dos recibos locais
  (ementa + dispositivo + PDF quando lido). **Não varre PDF.**
- O número de processo e o de acórdão têm o mesmo formato; a ferramenta não os distingue: acha quem cita um ou outro, e
  descarta a própria decisão (mesmo `numero` ou mesmo `processo`).
- Comportamento do portal, medido ao vivo em 15/10/2026 (3 requisições, `harness/_log_rede.json`, itens 35 a 37): com aspas, `"00037/23"` devolveu
  28 decisões (307 KB); sem aspas, 366 (4,7 MB, o OU de `00037` e `23`). As **mesmas 24** trazem o número no texto nos dois casos: a frase não
  perde nenhuma. Mesmo assim o filtro local (regex do número, sem recusar zeros à esquerda; recusa dígito colado, ano de 4 dígitos e data)
  é o que decide: se o portal deixar de honrar a frase, a saída não lista a base inteira (a fixture de 1.141 decisões, que simula isso, dá 17 achados).
- Janela de 350 caracteres antes e 250 depois da ocorrência, com a fonte de cada achado: `[ementa]`,
  `[dispositivo (acordaoDescricao)]`, `[informações adicionais (IA do DEJUR, não citável)]` ou `[recibo local (...; posição no julgado, página)]`.
  `fonte: portal`, `fonte: recibo local` ou `fonte: portal + recibo local`.
- Avisos obrigatórios (texto fixo): "NÃO detecta superação nem distinção"; "ZERO AQUI NÃO PROVA que ninguém aplicou o julgado";
  "o portal indexa texto ... e o PDF do inteiro teor NÃO é varrido; o recall é baixo"; "Os recibos locais cobrem só o que esta máquina já leu".
  Se o portal falhar: `[PESQUISA NÃO REALIZADA no portal] ...` e a saída segue só com os recibos.
- Não mede quanto as citações seguem ou afastam o julgado (o TJRO mediu 486 citações; aqui não há medição, então nenhum número é dado).

### Tese da ementa, VOZ DA CASA, placar, consulta pouco seletiva, corte
- `- TESE DA EMENTA (literal; tese enunciada pelo órgão, não prova de ratio; para aspas, confira com verificar_citacao_tcero): "..."`,
  com `⚠️ TESE INCOMPLETA: k de N itens` (ou `trecho parcial`) e ` […]` quando cortada em 1.000 caracteres. Usa o parser de seções da
  ementa que já existia; no modelo do TCE-RO a tese vem sob **III. Entendimento** (medido: 12 das 1.141 ementas da fixture trazem
  "Tese de julgamento:", todas sob Entendimento), no modelo do CNJ sob **IV. Dispositivo e tese**. Sem seções (modelo antigo) ou sem o
  rótulo: nada. Sai na busca (linha após a ementa), na triagem e no modo completo/`detalhar`. Nunca entra no recibo.
- `VOZ DA CASA:` em `verificar_citacao_tcero` (no resultado de `_verificar_trecho`, chave nova `notas`; `alertas` mantém o contrato da 1.6.0:
  vazio = nada a avisar). Linha `   ℹ VOZ DA CASA: o trecho está em <onde> (<página>) — é palavra do próprio TCE-RO ...`, com o mesmo "onde" da
  POSIÇÃO NO JULGADO. Dispara quando o trecho está na ementa ou no dispositivo do cadastro, ou no acórdão/fecho do PDF.
- Última linha da busca: `Placar: N consulta(s) ao portal na janela de ... (limite ...) · limitador: nível x/y, livre`.
- `⚠️ Consulta pouco seletiva: o portal devolveu N decisões ...` a partir de 1.000 (substitui a "Dica: total alto", que continua entre 200 e 999).
- Corte: já havia teto de 60.000 caracteres (`ORCAMENTO_SAIDA`) em fronteira de linha; agora a busca recua ao começo do resultado
  que ficaria pela metade e diz `Cortei na fronteira do resultado: N resultado(s) inteiro(s) acima`. O placar vem depois do corte.

## Ferramentas da v1.6.0 (15/10/2026)

Porte das ideias do TJRO v1.25–v1.34 (`recibos.js`, `erros.js`, `linhadotempo.js`, `vocabulario.js`,
modo `triagem`) adaptadas ao que o ePapyrus entrega. Toda a lógica nova tem uma função **pura**
(texto → texto) separada da rede, com frases de saída estáveis: o pacote Node (`.mcpb`) é porte
deste arquivo e é atualizado depois, a partir daqui.

### `buscar_recibos_tcero(consulta?, grupos?, relator?, orgao?, limite?)`

Zero requisição. Lê `~/.tcero-jurisprudencia-recibos/*.json` (ou `TCERO_MCP_DIR_RECIBOS`), ignora
recibo com hash que não confere (e diz quantos), e procura no campo `texto` (ementa + dispositivo +
PDF, **nunca** `texto_ia_dejur`). Palavra inteira com a mesma `_normalizar_casamento` do verificador
(caixa, acento, pontuação, aspas); `"frase exata"` em ordem; `multa*` = prefixo; `grupos` = OU dentro,
E entre grupos; `relator` = substring sem caixa/acento; `orgao` compara com o órgão do **cadastro**
(e, quando o PDF foi lido e o fecho diz outro órgão, o resultado avisa que vale o fecho). Por recibo:
citação pronta (`_citacao`, **sem a data do DOe**, que o recibo não guarda), id, link, a verificação
gravada (derivada de `texto_pdf_completo`: `None` = só ementa + dispositivo; `True` = extração completa,
sem registro de PDF misto; `False` = lido em parte), posição no julgado + página aproximada do primeiro
termo (`_posicao_tcero`, `_pagina_pdf_tcero`) e o trecho em volta. A saída diz quantos recibos existem,
quantos têm o PDF lido e que zero não é "não há jurisprudência". **O formato do recibo não mudou**
(nenhum campo novo; o lint da `peticao-rg` continua conferindo os mesmos hashes).

### Diário de erros e `diagnostico_erros_tcero(dias?, relatorio?)`

Toda falha de ferramenta (exceção; ou marcador `[LEITURA DE PDF NÃO REALIZADA`, `[PESQUISA…`, erro de
portal com rodapé; limitação parcial: `[EXTRAÇÃO PARCIAL`, PDF sem texto) grava uma linha JSON em
`$TCERO_MCP_DIR_ESTADO/erros.jsonl` (padrão `~/.tcero-jurisprudencia/erros.jsonl`; 0600, pasta 0700;
poda para as últimas 500 linhas acima de 400 KB). Campos: `quando`, `versao`, `sistema`, `ferramenta`,
`tipo`, `http`, `parcial`, `ms`, `args` (só presença/tamanho e enumerações seguras: nunca o texto da
busca, nome ou número), `limitador`, `mensagem` (sanitizada: URL sem consulta e sem hash de PDF, trecho
entre aspas vira `«…»`, número de processo/acórdão e id longo somem). Tipos novos além dos de
`_tipo_do_erro`: `pdf_falha`, `pdf_sem_texto`, `pdf_parcial`, `formato_inesperado`,
`dependencia_ausente`. Limite de ritmo auto-imposto **não** é registrado; erro de validação de entrada
do usuário também não. A tool resume por tipo × ferramenta, período, versões, causa provável e quem
corrige, e devolve o `_link_relato(tipo)` (só dado técnico). Selftest: um segredo nos parâmetros e na
mensagem não aparece no arquivo.

### `linha_do_tempo_tcero(texto_livre?, grupos?, relator?, orgao_julgador?, ano_inicio?, ano_fim?)`

Uma consulta (`_consulta_filtrada`, que monta os mesmos parâmetros de `_buscar`: a resposta de uma
busca idêntica feita há pouco vem do cache, zero requisição — o selftest compara os parâmetros e a
contagem de chamadas). Tabela ano × órgão (ano = ano da **sessão**; sem sessão = linha própria),
recorte `ano_inicio`/`ano_fim` no cliente, e por ano as 2 decisões de maior relevância (o mesmo
`_pontuar_relevancia`, desempate por data), com citação e link. Aviso fixo: é contagem do que o
portal devolveu para aquela consulta, não tendência da Corte.

### `sugerir_termos_tcero(texto_livre? | grupos?)`

Sobre a resposta da busca (cache; senão uma consulta). **Casadas** = decisões que casam, no núcleo
(ementa + dispositivo), o maior número de termos/grupos para o qual há pelo menos 10 decisões
(`_separar_casadas`); **restante** = o resto da resposta. Candidatas: palavras de 5+ letras e pares
adjacentes (sem palavras de ligação, sem os termos pedidos nem seus radicais, sem nomes de relator),
com piso de frequência entre as casadas de 20% (cai a 15/10/7% até haver 10 sugestões), frequência pelo
menos 1,3× a do restante (quando o restante tem 15+ decisões) e **lift sobre o fundo** pelo menos 5×
(`fundo_vocabulario.json`: df de palavras e pares sobre as 5.052 decisões do snapshot, gerado por
`harness/gerar_fundo.py`; o piso desce até 1,5× em consulta ampla, em que 5× é inatingível). Pontuação =
frequência × log(lift). Menos de 8 casadas, ou sem fundo e sem restante: não sugere e diz por quê. O
texto de IA do DEJUR nunca entra.

**Medição (15/10/2026, `harness/medir_sugestoes.py`, `harness/medicao-sugerir-termos-2026-10-15.md`).**
Seis consultas do `gold.json`, mock do OU nativo, fundo refeito sem as decisões casadas de cada
consulta. O gold é circular (ver `references/red-team-2026-09-22b.md`): adicionar sinônimos em OU
nunca derruba o recall do gold e o gold não vê o que entra de novo; por isso o número que vale é a
anotação independente (1 anotador, `references/red-team-2026-09-22b/anotacao.json`). Resultado, em
resumo: **as sugestões ampliam o conjunto, mas coladas em bloco derrubam o topo** — decisões anotadas
como relevantes: no conjunto 43 → 47 de 49 (3 sugestões em OU no grupo mais estreito); no top-10 36 → 27
(3 sugestões) e 19 (5 sugestões) de 47; piorou o topo em 4 de 6 consultas, igual em 1, melhorou em 1.
Das 107 sugestões listadas, rotulagem cega por 2 anotadores independentes (Sonnet e Opus, 15/10/2026, concordância 74%, kappa 0,60): pertinentes nos dois 26% (28 de 107), em pelo menos um 37%; 21 termos foram ruído nos dois. A estimativa anterior de 59% (leitura minha, não cega) estava inflada e não vale. Detalhes e ressalvas em `harness/medicao-sugerir-termos-2026-10-15.md`. **Não se declara ganho de busca.** O ganho que se sustenta é o de
descoberta de vocabulário, com ruído; a curadoria é de quem lê.

### Modo `triagem` em `obter_acordao_tcero`

`modo="triagem"`: citação, processo/natureza/assunto/votação/resultado, órgão do cadastro, avisos de
cancelamento/vínculo, ementa inteira (limite de 12 mil caracteres), dispositivo, link. Com
`ler_inteiro_teor=true`: do PDF, a estrutura (`_estrutura_pdf_tcero`: ACÓRDÃO, RELATÓRIO, VOTO,
voto de outro conselheiro, com página aproximada), o fecho (`_fecho_do_pdf`: de "ACORDAM os Senhores
Conselheiros" até o relatório/voto ou 1.800 caracteres, sem cabeçalho de página) e as linhas que os
detectores já marcam (os mesmos gatilhos dos campos do recibo: divergência/vista, parecer do MPC,
alegação da parte, transcrição, mais a marca de obiter), no máximo 3 por tipo, cada uma com a posição
no julgado e a página. Sem o texto corrido e sem a IA do DEJUR. No acórdão 98114: 7,5 mil caracteres
contra 55 mil do modo completo. **Recibo:** o mesmo caminho do modo completo (mesmo download/cache,
mesmas chamadas a `_texto_pdf_para_recibo` e `_gravar_recibo_tcero`); o selftest compara os dois
recibos campo a campo e confere que uma triagem sem PDF não rebaixa um recibo que já tem o PDF.

### Alertas que dizem onde

`OBITER DICTUM?` ganhou a frase onde está a marca (`A frase: «…» + o trecho.`) ou diz que a marca
está no começo do próprio trecho — mesma redação do TJRO v1.33. A posição "VOTO de outro conselheiro"
ganhou o título do voto (`(título: «…»)`), e `verificar_citacao_tcero`/`buscar_recibos_tcero` mostram
a página aproximada do PDF (`p. ~N de M`, lida do cabeçalho "N de M" que o TCE-RO repete em toda folha).
**Não há rótulo `VOTO DIVERGENTE` no TCE-RO** (o equivalente aqui é a posição de outro conselheiro) e
não foi criado um sem medir. Em 900 janelas amostradas dos 36 recibos locais, nada além disso mudou
em relação à v1.5.1 (mesmos valores, alertas e posições).

### Atualizar

No Python, atualizar é `git pull` + reiniciar o cliente; no Claude Desktop (`.mcpb`), baixar o arquivo
da release e dar dois cliques. O aviso de versão nova passou a trazer as duas instruções
(`COMO_ATUALIZAR`). **A ferramenta que baixa o `.mcpb` sozinha (`atualizar_extensao`, com SHA-256
conferido, como no TJRO) fica para o porte Node:** no Python não faria sentido, pois quem usa o
Python já tem o `git`.

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

## Recibo de custódia — 22/09/2026

`obter_acordao_tcero` grava, a cada chamada, um JSON por decisão em
`~/.tcero-jurisprudencia-recibos/<idDecisao>.json` (diretório configurável por
`TCERO_MCP_DIR_RECIBOS`, fora do OneDrive por padrão; diretório `0700`, arquivo `0600`).
Contrato de campos (combinado com o lint da `peticao-rg`,
`~/.claude/skills/peticao-rg/scripts/lint_citacoes.py`):

```
tribunal, id_documento, sigla, numero, processo, nr_processo (= processo, para o lint achar
recibos irmãos do mesmo processo), relator, orgao_cadastro, data_sessao, link, gravado_em,
fonte, texto, texto_pdf_completo, texto_ia_dejur, texto_transcrito, texto_divergente,
texto_alegacao_parte, texto_parecer_mpc, sha256
```

`texto` é ementa + dispositivo (+ o texto do PDF, quando já lido com `ler_inteiro_teor=true`) —
**nunca** `informacoesAdicionais` (conteúdo de IA do DEJUR, que vai à parte em
`texto_ia_dejur`; misturar aprovaria como literal do acórdão algo que o tribunal não escreveu).
`texto_pdf_completo` é sobre a EXTRAÇÃO do PDF (páginas/tempo), não sobre o orçamento de saída
da tool — o recibo guarda o texto ÍNTEGRO extraído, nunca o cortado para caber na resposta.
`sha256` é do campo `texto`; um recibo com hash divergente é recusado na leitura (nunca tratado
como íntegro). As quatro listas `texto_transcrito`/`texto_divergente`/`texto_alegacao_parte`/
`texto_parecer_mpc` guardam excertos BRUTOS (não normalizados) em torno de cada gatilho de
atribuição — heurística de janela fixa (320 caracteres), não de frase; vazias quando o detector
não achou nada.

`verificar_citacao_tcero` confere primeiro contra o recibo (ZERO requisição) quando ele existe
para o `id_decisao` informado; sem recibo, cai para o portal como antes. A saída diz sempre de
onde veio o texto conferido (`recibo` ou `portal`).

## Alertas de atribuição — 22/09/2026

Porte do TJSE/TRT14: um trecho pode casar literalmente e ainda não ser "a posição da Corte" —
pode ser transcrição de outro tribunal, voto vencido, alegação da parte, citação entre aspas
ou, caso **próprio do TCE-RO** (acórdão de contas transcreve rotineiramente o parecer
ministerial e o relatório técnico), posição do MPC ou do corpo técnico. `verificar_citacao_tcero`
examina a vizinhança de todo trecho ✅ e lista os alertas que se aplicam — NEGAÇÃO (até ~80
caracteres antes), TRANSCRIÇÃO (STF/STJ/TCU/Súmula/Tema/"in verbis"), PARECER DO MPC / CORPO
TÉCNICO, ALEGAÇÃO DA PARTE e ENTRE ASPAS — sem nunca trocar ✅ por ❌: o trecho É literal, só
pode não ser da Corte.

Medição (22/09/2026, offline, sobre os 4 PDFs reais de `fixtures/pdf/`): 240 janelas de 400
caracteres normalizados amostradas aleatoriamente (60 por PDF, seed fixa), cada uma testada
como se um trecho terminasse no fim da janela —

| Alerta | Disparos | Taxa |
|---|---|---|
| PARECER DO MPC / CORPO TÉCNICO | 35/240 | 14,6% |
| NEGAÇÃO | 17/240 | 7,1% |
| ALEGAÇÃO DA PARTE | 9/240 | 3,8% |
| TRANSCRIÇÃO | 4/240 | 1,7% |
| ENTRE ASPAS | 0/240 | 0,0% |

PARECER DO MPC dispara mais que os outros — esperado em acórdão de contas, que cita
"Secretaria"/"relatório técnico"/"parecer" com frequência bem maior que um acórdão cível. Não é
sinal de limiar sensível demais: é a proporção real do vocabulário do TCE-RO. ENTRE ASPAS não
disparou nenhuma vez nesta amostra — os PDFs reais usam pouca aspa tipográfica reconhecível
pelo padrão par/ímpar; N pequeno (4 PDFs), não conclusivo sobre a sensibilidade desse alerta
especificamente.

**Atualização 06/10/2026 (v1.3.0):** com aspas por pareamento no documento inteiro, ENTRE ASPAS foi medido às cegas em 85
trechos de 23 acórdãos que transcrevem texto entre aspas (dois rotuladores, concordância 84/85): precisão 94%, cobertura 100%,
falso alarme 0% — a regra antiga, na mesma amostra, tinha 16%, 45% e 14%. Detalhes no `CHANGELOG.md`.

## Órgão pelo fecho do PDF — só medição, não ligado (22/09/2026)

No TJRO o cadastro errava a câmara em 15/24 processos; no TRT14 acertou 5/5; no TJSE divergia
na grafia. No TCE-RO **ninguém tinha medido**. `_orgao_do_fecho(texto)` extrai o órgão do FECHO
do acórdão ("ACORDAM os Senhores Conselheiros do Pleno/da 1ª Câmara/da 2ª Câmara do Tribunal de
Contas...") e foi testada contra os 4 PDFs reais:

| id | cadastro (`orgaoJulgador`) | fecho do PDF | bate? |
|---|---|---|---|
| 77649 | Pleno | Pleno | sim |
| 85572 | Pleno | Pleno | sim |
| 96141 | 1ª Câmara | 1ª Câmara | sim |
| 98114 | Pleno | Pleno | sim |

4/4 bateram — **N=4 não permite concluir nada** sobre a confiabilidade geral do cadastro do
TCE-RO (o TJRO só revelou o problema em N=24). A função existe, é testada no `--selftest`, mas
**não está ligada** a nenhuma citação ou verificação: ligar o fecho como fonte da citação (em
vez do cadastro) é decisão da conversa principal, depois de uma amostra maior.

`_orgao_do_fecho` agora também devolve `None` quando o PDF tem fechos de órgãos **diferentes**
no mesmo texto — típico de acórdão de embargos/recurso que transcreve o fecho do acórdão
embargado (dois fechos IGUAIS não é conflito). Regressão coberta no `--selftest` (com os 4 PDFs
de `fixtures/pdf/`). Amostra ampliada em 22/09/2026 com 14 PDFs adicionais reais (baixados para
`harness/_pdfs/`, fora do git), distribuídos entre 1ª Câmara, 2ª Câmara, Pleno e siglas normais
+ embargos/recurso (AC1R-TC/AC2R-TC/APLR-TC) — tabela completa em
`harness/fecho-2026-09-22.md`: **18/18 bateram, 0 divergências**. Com N=18 e zero divergências,
o aviso de divergência em `obter_acordao_tcero(..., ler_inteiro_teor=True)` **continua
desligado** — não há caso real para ele apontar ainda.

## Ordenar por relevância — `ordenar` (22/09/2026)

`buscar_jurisprudencia_tcero(..., ordenar=...)` reordena a página, no cliente, sobre a
resposta já baixada: conta quantos termos DISTINTOS de `texto_livre`/`grupos` aparecem em cada
decisão (ementa+dispositivo pesam 2 por termo, informações adicionais de IA pesam 1) e ordena
por essa pontuação, desempatando por data. Não muda ementa/dispositivo, só a ordem.

**`"relevancia"` é o PADRÃO desde 22/09/2026** (era `"data"` antes). Decisão baseada em medição
real: `harness/medir.py` rodou o `_buscar` de verdade (com a API mockada a partir de um
snapshot local de 5.052 decisões, sem rede) contra um gabarito cego de 6 consultas típicas de
contas (`harness/gold.json`) em três formas — (a) texto_livre + ordenar=data (o de sempre),
(b) o mesmo texto_livre + ordenar=relevancia, (c) grupos de sinônimos + ordenar=relevancia.
Resultado (`harness/medicao-2026-09-22.md`): recall@10 médio **2% (a) → 62% (b) → 72% (c)**,
melhora em TODAS as 6 consultas, nenhuma piorou. Sem `texto_livre` nem `grupos` não há termo
para pontuar — `"relevancia"` se comporta como `"data"` nesse caso, então o novo padrão não
muda nada em buscas só por número/relator/órgão. Peça `ordenar="data"` explicitamente para a
ordem cronológica pura do portal. Cada item, com `ordenar="relevancia"`, mostra
`termos casados: N/M`.

## Panorama (facetas offline)

Buscas com 3+ decisões na página 1 ganham, ao final da resposta, um bloco "Panorama" com
contagem por órgão julgador, ano, sigla, natureza e os 5 relatores mais frequentes — só um
indício para escolher o que ler, nunca conclusão sobre a tese. Não aparece com menos de 3
decisões nem fora da página 1. Campo ausente conta como "sem informação".

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

## Onde funciona

Este é um **servidor MCP em Python**. Funciona em qualquer cliente que fale MCP por `stdio`:

| Cliente | Funciona? |
|---|---|
| **Claude Code** (terminal, desktop app, extensão do VS Code/JetBrains) | Sim — é onde o autor usa todo dia |
| **Claude Desktop** (programa instalado no Mac/Windows) | Sim, de duas formas: **instalador de um clique** `Jurisprudencia-TCERO.mcpb` (porte em Node, mesmas 4 ferramentas e mesmas saídas — baixe na [página de releases](https://github.com/robertogecia/tcero-jurisprudencia-mcp/releases/latest), arraste em Configurações → Extensões); ou registrando este servidor Python no `claude_desktop_config.json` (abaixo) |
| Claude pelo **site** (claude.ai no navegador) ou pelo **celular** | **Não.** Precisa ser um programa instalado no computador, que consiga rodar Python |
| Outros clientes MCP (Cursor, Windsurf, Cline…) | Em tese sim (`stdio`), mas não foi testado pelo autor |

## Instalar no Claude Desktop com um clique (.mcpb)

1. Baixe `Jurisprudencia-TCERO.mcpb` na [última release](https://github.com/robertogecia/tcero-jurisprudencia-mcp/releases/latest) (cerca de 21 MB — leva dentro o leitor de PDF).
2. No Claude Desktop: Configurações → Extensões → arraste o arquivo (ou "Instalar extensão…").
3. Abra uma conversa nova e peça uma busca no TCE-RO.

O pacote é um porte em Node do servidor Python deste repositório (código-fonte em [tcero-jurisprudencia-mcpb](https://github.com/robertogecia/tcero-jurisprudencia-mcpb)) (fonte de verdade: mudança de comportamento entra primeiro aqui, com red team, depois no pacote, com o teste de paridade). Diferenças conhecidas: a extração de texto do PDF (pdfjs-dist × PyMuPDF) não é byte-idêntica no espaçamento — o casamento de citações e o recibo funcionam igual, mas um recibo gravado pelo pacote não tem o mesmo hash de um gravado pelo Python para o mesmo acórdão; e o diagnóstico de ritmo mostra horas em UTC. Precisa de Node? Não: o Claude Desktop traz o runtime.

## Instalar o servidor Python (uns 5 minutos)

Você precisa de **Python 3.11 ou mais novo** e de **git**. No Mac, os dois já vêm ou se instalam com as ferramentas de linha de comando da Apple; no Windows, instale o Python em [python.org](https://www.python.org/downloads/) (marque "Add to PATH").

### Passo 1 — Baixe o código

```bash
git clone https://github.com/robertogecia/tcero-jurisprudencia-mcp.git
cd tcero-jurisprudencia-mcp
```

### Passo 2 — Crie o ambiente e instale as dependências

```bash
python3 -m venv .venv
.venv/bin/pip install "mcp[cli]>=1.4.0,<2" "httpx>=0.27" "truststore>=0.9" pymupdf
```

(No Windows: `.venv\Scripts\pip` no lugar de `.venv/bin/pip`, e `.venv\Scripts\python` no lugar de `.venv/bin/python`, aqui e nos passos seguintes.)

`mcp<2` é de propósito: a versão 2.x renomeou `FastMCP` e o registro das ferramentas falha em silêncio. `pymupdf` é o que lê o PDF do inteiro teor.

### Passo 3 — Confira que está tudo certo, sem tocar no portal

```bash
TCERO_MCP_SEM_AVISO_ATUALIZACAO=1 .venv/bin/python servidor_tcero.py --selftest
```

Deve terminar com `selftest offline OK`. Esse teste roda contra respostas reais gravadas no repositório e **não faz nenhuma requisição** ao TCE-RO.

### Passo 4 — Registre no seu cliente

**Claude Code** (troque o caminho pelo da pasta onde você clonou):

```bash
claude mcp add tcero_jurisprudencia -- /caminho/para/tcero-jurisprudencia-mcp/.venv/bin/python /caminho/para/tcero-jurisprudencia-mcp/servidor_tcero.py
```

**Claude Desktop**: abra Configurações → Desenvolvedor → Editar configuração (é o arquivo `claude_desktop_config.json`) e acrescente, dentro de `"mcpServers"`:

```json
"tcero_jurisprudencia": {
  "command": "/caminho/para/tcero-jurisprudencia-mcp/.venv/bin/python",
  "args": ["/caminho/para/tcero-jurisprudencia-mcp/servidor_tcero.py"],
  "env": {}
}
```

### Passo 5 — Abra uma conversa nova e teste

Conversa antiga não percebe o servidor novo. Numa conversa nova, peça algo como *"pesquise no TCE-RO acórdãos sobre dispensa de licitação por emergência"* — o Claude deve chamar `buscar_jurisprudencia_tcero`. Se quiser ver que o servidor está de pé sem gastar nenhuma consulta, peça o `diagnostico_ritmo_tcero`: a primeira linha traz a versão instalada.

## Algo deu errado? (instalação pelo Python)

| O que aconteceu | O que fazer |
|---|---|
| `pip install` reclama de versão do Python | Precisa de Python 3.11+. `python3 --version` mostra a sua. |
| Instalei, mas o Claude diz que **não tem essa ferramenta** | Abra uma **conversa nova**. No Claude Code, `claude mcp list` mostra se o servidor está registrado e conectando; no Claude Desktop, confira se o JSON ficou válido (uma vírgula a mais derruba a configuração inteira). |
| O servidor registra mas as ferramentas não aparecem | Quase sempre é `mcp` 2.x instalado por engano. Rode o Passo 2 de novo, com o `<2`. |
| A busca devolve **zero** com filtro de relator ou de órgão | O portal exige o valor **exato** e devolve vazio sem erro. A ferramenta avisa quando não reconheceu o filtro: corrija a grafia (a mensagem lista os valores aceitos) antes de concluir que não há jurisprudência. |
| A busca devolve centenas de resultados fora do assunto | O portal só sabe fazer OU entre palavras e ordena por data. Use `grupos` (E entre conceitos) — veja "Como pesquisar bem". |
| `ler_inteiro_teor=true` diz que o PDF **não tem texto extraível** | O acórdão foi digitalizado como imagem. A ferramenta não faz OCR de propósito: abra o link do PDF no navegador. |
| Erro de rede repetido | Confira se o portal abre no navegador ([papyrus.tcero.tc.br](https://papyrus.tcero.tc.br/)). Se abre e a ferramenta não, veja "Se a busca parar de funcionar". |
| Nenhuma linha acima resolveu | [Abra uma issue](../../issues) descrevendo o que aconteceu — a própria mensagem de erro traz um link com o formulário já preenchido com os dados técnicos (versão, sistema, tipo do erro). |

## Se a busca parar de funcionar

O portal do TCE-RO **não tem WAF, captcha nem login** (confirmado em todos os testes até a data deste README), então bloqueio por "verificação de navegador", como acontece no TJRO, nunca foi visto aqui. O que pode acontecer:

- **O portal mudou.** O ePapyrus é uma aplicação do tribunal e pode trocar a API sem aviso. Nesse caso a ferramenta passa a devolver erro em toda busca, mesmo com o portal abrindo normalmente no navegador. Veja se há [versão mais nova](https://github.com/robertogecia/tcero-jurisprudencia-mcp/releases/latest) — a própria mensagem de erro avisa quando há — e, se não houver, [relate](../../issues) com a mensagem de erro.
- **Limite de ritmo da própria ferramenta.** Ela se impõe um teto de consultas por minuto, por cortesia com o servidor do tribunal (o portal não documenta limite nenhum). O erro diz quanto esperar; esse erro **não** traz link de relato, porque se resolve esperando.
- **Sem internet, ou o portal fora do ar.** A mensagem distingue os dois casos.

## Reportar erro (detalhes técnicos)

- **Erro**: use o link que vem na própria mensagem de erro (abre o formulário de issue do GitHub já preenchido com versão, sistema operacional, tipo do erro e estado do limitador — **nada da sua pesquisa vai junto**, e você revisa antes de enviar). Ou [abra uma issue](../../issues/new) à mão com esses mesmos dados.
- **Sugestão**: [issue](../../issues/new) também. Diga o que você tentou pesquisar (em abstrato — sem nome de parte nem número de processo, as issues são públicas) e o que esperava.
- Precisa de conta gratuita no GitHub. O autor mantém isto no tempo livre; resposta pode demorar.

## Segurança e auditoria

Pensado para ser fácil de verificar antes de instalar, não só "confie em mim":

- **Só leitura, sem credenciais.** As buscas fazem requisições HTTP `GET` à API pública do portal (`papyrus.tcero.tc.br`); o inteiro teor baixa o PDF de `tcero.tc.br`. Não pedem login, token nem chave de API. O host do PDF é conferido contra uma lista fechada antes e depois de qualquer redirecionamento — o servidor não segue link para fora do tribunal.
- **Sem coleta de dados.** Nenhuma telemetria. As únicas conexões são ao tribunal e, uma vez por processo, um `GET` sem dados seus a `api.github.com` para o **aviso de versão nova** (abaixo).
- **Recibo de custódia (anti-alucinação).** Toda vez que uma decisão é aberta com `obter_acordao_tcero`, o texto que o portal entregou (ementa, dispositivo e, se lido, o PDF) fica gravado em `~/.tcero-jurisprudencia-recibos/<id da decisão>.json`, com hash. Serve para conferir depois, por script ou a olho, se o trecho que foi para a peça está mesmo no documento do tribunal — e não só no que a IA diz ter lido. É texto público de acórdão e fica só na sua máquina; pode apagar a pasta quando quiser. Outra pasta: variável de ambiente `TCERO_MCP_DIR_RECIBOS`.
- **Diário de erros local (v1.6.0).** Falhas de ferramenta ficam em `~/.tcero-jurisprudencia/erros.jsonl` (outra pasta: `TCERO_MCP_DIR_ESTADO`), só com dado técnico — ferramenta, tipo, mensagem curta sanitizada, versão, sistema, data. Nunca o texto da busca, nome de parte, número de processo ou trecho citado; nada sai da máquina por causa dele. `diagnostico_erros_tcero` o resume.
- **O texto de IA do próprio tribunal é marcado.** O ePapyrus traz, em cada decisão, um resumo (Fatos/Questão/Regras/Análise/Conclusão) gerado com apoio de IA pelo DEJUR do TCE-RO. A ferramenta o mostra sempre com esse aviso, **nunca** o usa para confirmar uma citação e não o grava como texto do acórdão no recibo.
- **Aviso de versão nova.** Ao subir, o servidor pergunta ao GitHub qual é a release mais recente. Se houver uma mais nova, a primeira resposta da sessão termina com uma linha avisando, com o endereço da página de releases (fixo no código, nunca tirado da resposta do GitHub). Ele **não baixa nem instala nada** — atualizar é `git pull` na pasta e reiniciar o cliente (Python) ou baixar o `.mcpb` da release e dar dois cliques (Claude Desktop); a linha do aviso traz as duas instruções. Sem internet o aviso não aparece (espera de no máximo 5 segundos, em segundo plano). Para desligar: `TCERO_MCP_SEM_AVISO_ATUALIZACAO=1`.
- **Quando algo dá errado, a própria mensagem diz o que fazer** — se há versão nova, e como relatar (ver "Reportar erro").
- **Um arquivo, legível.** Toda a lógica está em [`servidor_tcero.py`](servidor_tcero.py); o `--selftest` roda offline contra respostas reais gravadas em `fixtures/`. Os red teams que auditaram o código, com os achados e o que foi corrigido, estão em [`references/`](references/).

## Atualizar (Python)

```bash
cd /caminho/para/tcero-jurisprudencia-mcp && git pull
```

Depois, reinicie o Claude (Code ou Desktop). Se o `pip` de dependências mudou, o README da versão nova diz.

Resumo das duas formas de atualizar (é o que o aviso de versão nova também diz): **Python** = `git pull`
na pasta do servidor + reiniciar o Claude; **Claude Desktop (`.mcpb`)** = baixar o arquivo da versão
nova na página de versões e dar dois cliques nele. Uma ferramenta que baixe o `.mcpb` sozinha existe
no pacote do TJRO (`atualizar_extensao_tjro`) e fica para o porte Node desta extensão.

A versão 1.6.0 acrescenta o arquivo `fundo_vocabulario.json` ao lado do `servidor_tcero.py`
(usado por `sugerir_termos_tcero`); o `git pull` já o traz. Se ele faltar, a ferramenta ainda funciona,
só com o contraste dentro da própria resposta do portal.

## Desinstalar (Python)

Claude Code: `claude mcp remove tcero_jurisprudencia`. Claude Desktop: apague o bloco `tcero_jurisprudencia` do `claude_desktop_config.json`. Depois apague a pasta clonada e, se quiser, `~/.tcero-jurisprudencia-recibos/`.

## Ritmo e disjuntor

Estado em `.disjuntor_estado_tcero.json` (ao lado do script, sob trava `fcntl`), compartilhado
por todos os processos desta máquina — mesmo mecanismo de TJRO/TRF1. **Os números aqui são um
teto defensivo genérico, não um limite documentado ou observado do TCE-RO**: em ~20
requisições de mapeamento (13/09/2026) o portal não mostrou nenhum sinal de rate limit, WAF ou
bloqueio. Por isso a janela inicial é mais generosa que a dos irmãos (40 requisições/minuto,
escada 1→5→10→20→30 min, cooldown de 5 min dobrando até 1 h) e só aperta se um bloqueio de
verdade acontecer. Backoff exponencial curto (até 3 tentativas) em erro de rede/5xx —
diferente do disjuntor (que reage a recusa persistente), isso cobre instabilidade passageira.
**Timeout/queda de conexão NÃO arma o disjuntor** (22/09/2026, determinação TJSE→TRF1 replicada
aqui): o TCE-RO tem respostas reais de até ~20 MB (ver `protocolo-papyrus.md`), e estourar o
timeout de leitura nelas é esperado, não é recusa do portal — só retentativa moderada, sem
incidente nem cooldown (`_falha_transitoria`, regressão no `--selftest`).

**Versão e aviso de atualização (22/09/2026):** `diagnostico_ritmo_tcero` mostra a versão
instalada na primeira linha. Em segundo plano, no máximo uma consulta por processo a
`api.github.com/repos/robertogecia/tcero-jurisprudencia-mcp/releases/latest` (timeout de 5s,
nunca bloqueia uma busca, nunca baixa nem instala nada) — se houver versão mais nova, toda
saída de tool subsequente ganha uma linha `⬆️ Há versão nova (vX.Y.Z): ...`; desligável por
`TCERO_MCP_SEM_AVISO_ATUALIZACAO=1` (o `--selftest` já desliga sozinho, sem rede real). Erro de
portal/rede ganha um rodapé com versão, sistema operacional, estado do limitador e — exceto
para erro de limite de ritmo, que o próprio usuário resolve esperando — um link pré-preenchido
para relatar em `.../issues/new`, só com dado técnico (nunca o texto da busca, número de
processo ou nome de parte).

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
