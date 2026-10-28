# Registro de dados e experimentos: detecção de imagens geradas por IA (contexto político brasileiro)

Atualizado em 14/10/2026. Documento de registro técnico, **não** é o texto do projeto. Todos os números abaixo vêm das saídas que você colou nas conversas. Onde algo é hipótese, está marcado como hipótese.

## 0. Resumo em dez linhas
1. No Tiny-GenImage (subconjunto de 200 imagens) o UnivFD teve AUC 0,88 e o FSD teve AUC 0,43. Esses números **refletem viés do dataset** (formato e tamanho), não só a capacidade dos detectores.
2. Controlando tamanho e formato (recorte 256×256 em PNG), o FSD foi para o acaso (AUC 0,51) e o UnivFD ficou em 0,87.
3. Montei um dataset político brasileiro: 513 fotos reais (Wikimedia Commons, 50 nomes) e 514 imagens falsas geradas por mim (SD 1.5, SDXL, SDXL-Turbo), pareadas por conteúdo via legendas.
4. Depois de padronizar (recorte 512×512 + JPEG q90), **atalhos triviais ainda separam as classes com AUC 0,946**. O viés persiste.
5. Nesse conjunto, o UnivFD teve AUC **0,32** e o FSD **0,46**: o UnivFD ficou **invertido** (acha as falsas mais reais).
6. Pareando por nitidez e tamanho (119 pares), os atalhos caíram para 0,46. Aí o UnivFD ficou no acaso (0,44) e o FSD ficou **abaixo do acaso** (0,36).
7. Conclusão provisória: com essas imagens e gerações, **nenhum dos dois detectores discrimina** real de gerada, e os resultados brutos são enganosos por causa de viés de processamento.
8. Controle sem JPEG extra (condição C, reais ainda como miniaturas do Commons): UnivFD AUC 0,41 e FSD 0,34 no conjunto todo; 0,50 e 0,45 no pareado (seção 3.8). A versão com reais nativas ainda não foi feita.
9. Há 16 dias até o prazo (30/10/2026).
10. Limitações importantes: amostras pequenas, identidades dos políticos não verificadas, geradores só de difusão, sem imagens falsas reais em volume.

---

## 0.1 Linha do tempo
Legenda da fonte: **[arq]** = carimbo de data/hora de arquivo no seu computador; **[conv]** = data da conversa; **[PDF]** = documento original. Eventos no Colab não têm carimbo confiável; estão situados entre dois marcos e marcados como "entre".

| Data | Evento | Fonte |
|---|---|---|
| 08/10/2026 | Registro dos experimentos preliminares (FSD, UnivFD, Grok em 11/20 imagens) | [PDF] |
| 11/10/2026 | Pesquisa sobre o 8º Prêmio Carolina Bori (inscrições até 30/10); leitura do edital | [conv] |
| 11/10/2026 12:48 | Primeiro script de análise rápida (`resultados_rapidos_colab.py`) | [arq] |
| 11/10/2026 12:58 | Configuração do servidor MCP do Colab (`.mcp.json`); depois descartado por instabilidade | [arq] |
| 11/10/2026 (tarde) | Reanálise do Tiny-GenImage no novo runtime: amostra (semente 42), auditoria JPEG × PNG, UnivFD (AUC 0,879), controle JPEG, per-gerador | [conv] |
| 11/10/2026 14:46 | Notebook `tcc_detectores.ipynb` gerado (UnivFD + FSD + análise) | [arq] |
| 11/10/2026 (entre 14:46 e o fim do dia) | Resultados do FSD (AUC 0,43), análise por tamanho (ρ = −0,59), controle 256×256 (FSD 0,51; UnivFD 0,87) | [conv] |
| 12/10/2026 10:08 | Planilha-modelo do dataset político criada | [arq] |
| 12/10/2026 10:58 a 11:00 | Páginas das checagens baixadas; F001 salva; início do download das fotos reais | [arq] |
| 12/10/2026 11:00 a 11:31 | 514 arquivos em `real_oficial/` (primeira e última foto), em quatro rodadas de download | [arq] |
| 12/10/2026 11:05 a 11:33 | Consolidação de `dataset_politicos_br.csv` (557 linhas, depois 517 após remover 40 imagens na triagem) | [arq] |
| 12/10/2026 11:12 e 11:13 | Notebooks `2_gerar_falsas` e `3_avaliar_politico` criados | [arq] |
| 12/10/2026 11:33 a 11:34 | `real_oficial.zip` criado (154 MB) | [arq] |
| 12/10/2026 12:34 | `2_gerar_falsas` corrigido (extração do zip do Windows, conflito de `torchao`) | [arq] |
| entre 12/10 12:34 e 14/10 manhã | Geração das 514 falsas no Colab (cerca de 1 h por gerador no SDXL); limite de GPU atingido ao tentar rodar a avaliação | [conv] |
| 14/10/2026 09:10 | `3_avaliar_politico` atualizado (modo CPU, correção `M["std"]`) | [arq] |
| 14/10/2026 (manhã a tarde) | Auditoria de viés (AUC 0,946), detectores no conjunto político (UnivFD 0,32; FSD 0,46), subconjunto pareado (119 pares) | [conv] |
| 14/10/2026 15:14 a 18:40 | Download dos recortes nativos dos originais do Commons (431 arquivos até 18:40); log às 18:22 | [arq] |
| 14/10/2026 18:38 | Este registro criado | [arq] |
| 30/10/2026 23:59 | Fim das inscrições do prêmio | [conv/edital] |

**Datas que eu não tenho:** quando exatamente você enviou a mensagem à Lupa e se houve resposta; quando o orientador combinou escrever a carta; quando a geração no Colab começou e terminou; a data do primeiro contato com o tema (anterior a 08/10).

---

## 1. Experimentos preliminares (anteriores, do PDF original)
Dataset Tiny-GenImage, 200 imagens (100 reais, 100 falsas), FSD com `max_size=512` e UnivFD com limiar 0,5.

| | FSD | UnivFD |
|---|---|---|
| Acurácia | 60,0% | 63,0% |
| Precisão (fake) | 67,9% | 86,1% |
| Recall (fake) | 38,0% | 31,0% |
| F1 (fake) | 48,7% | 45,6% |
| AP | | 72,62% |
| Matriz (TN, FP, FN, TP) | 82, 18, 62, 38 | 95, 5, 69, 31 |

Teste exploratório com o Grok em 11 de 20 imagens: 5 acertos, 5 erros, 1 inconclusiva (as 6 falsas avaliadas: 5 "autênticas" e 1 inconclusiva).
**Esses experimentos não são reproduzíveis:** o runtime do Colab foi reciclado e os CSVs (`resultados_fsd_512.csv`, `resultados_univfd.csv`) se perderam. As amostras de imagens também não são as mesmas das usadas depois.

---

## 2. Reanálise do Tiny-GenImage (novo runtime, reproduzível)

### 2.1 Amostra
- Fonte: Hugging Face `TheKernel01/Tiny-GenImage`, arquivo `data/validation-00000-of-00004.parquet` (1750 linhas: 875 reais e 875 falsas).
- Sorteio com `numpy.random.default_rng(42)`: 100 reais e 100 falsas.
- Falsas por gerador: ADM 17, BigGAN 9, GLIDE 14, Midjourney 13, SD 1.5 12, VQDM 14, Wukong 21.

### 2.2 Auditoria da amostra (achado)
| | Reais | Falsas |
|---|---|---|
| Formato | **100% JPEG** | **100% PNG** |
| Largura média | 491 px | 429 px |
| Menor dimensão | 240 | 128 |
| Tamanho médio do arquivo | 132 KB | 344 KB |

Ou seja, o rótulo está perfeitamente correlacionado com o formato do arquivo, e as falsas incluem imagens muito pequenas (128 a 256 px).

### 2.3 Detectores e versões
- **UnivFD:** `github.com/Yuheng-Li/UniversalFakeDetect`, commit `030495aea3300a8b54c0ec37ec7fe1dd7e63c619`. CLIP ViT-L/14, pesos `pretrained_weights/fc_weights.pth`. Pré-processamento: `CenterCrop(224)`, normalização do CLIP, `sigmoid`, limiar 0,5.
- **FSD:** `github.com/ductai199x/Forensic-Self-Descriptions-CVPR25`, commit `50f2eae06efdac2e5a33f407ca9a27a2295133ac` (v1.1.0), pesos baixados automaticamente. Limiar -2,0 (z-score), `max_size=512` (padrão 1024). Obs.: o link `ganjiajun/...` que você tinha colado **não existe**.
- Ambiente: Colab, GPU T4, Python 3.13.

### 2.4 UnivFD, resultados
| Condição | AUC | AP | Acurácia | Precisão | Recall | Especificidade |
|---|---|---|---|---|---|---|
| Original | 0,879 | 0,880 | 0,665 | 0,923 | 0,36 | 0,97 |
| Todas em JPEG q95 | 0,828 | 0,821 | 0,600 | 0,917 | 0,22 | 0,98 |
| Todas em JPEG q75 | 0,780 | 0,752 | 0,565 | 0,783 | 0,18 | 0,95 |

Matriz (original): TN 97, FP 3, FN 64, TP 36. Limiar de Youden = 0,033, acurácia 0,795 (**otimista**, escolhido nos mesmos dados).
AUC por gerador (contra as reais): BigGAN 0,988 (recall 0,89), VQDM 0,968 (0,71), Wukong 0,898 (0,48), ADM 0,882 (0,12), SD 1.5 0,822 (0,17), GLIDE 0,822 (0,07), Midjourney 0,786 (0,23). Com 9 a 21 imagens por gerador, a incerteza é de cerca de ±0,1.

### 2.5 FSD, resultados
| Condição | AUC | AP | Acurácia | Precisão | Recall | Especificidade |
|---|---|---|---|---|---|---|
| Original (512) | 0,430 | 0,560 | 0,490 | 0,489 | 0,45 | 0,53 |
| JPEG q95 | 0,428 | 0,552 | 0,465 | 0,458 | 0,38 | 0,55 |
| JPEG q75 | 0,417 | 0,564 | 0,435 | 0,433 | 0,42 | 0,45 |

Matriz (original): TN 53, FP 47, FN 55, TP 45. As colunas de "limiar de Youden" do FSD **não têm significado** (a AUC é menor que 0,5).
AUC por gerador: Wukong 0,923, SD 1.5 0,905, GLIDE 0,458, Midjourney 0,297, ADM 0,090, BigGAN 0,096, VQDM 0,010.
Comparação FSD × UnivFD (limiares padrão): só o FSD acertou 34, só o UnivFD acertou 69, ambos 64, nenhum 33; McNemar p = 0,001. Esse teste compara um detector que funciona com um invertido, então **não** deve ser lido como "UnivFD melhor que FSD".

### 2.6 Por que o FSD ficou invertido: análise
- Correlação de Spearman entre o lado menor da imagem e o z-score: **ρ = −0,594** (p ≈ 2·10⁻²⁰).
- z médio por faixa de tamanho: falsas de até 300 px ficam em −0,5 a −0,8 ("parecem reais"); falsas de 400 a 600 px ficam em −8,9; reais de 400 a 600 px ficam em −4,2.
- Leitura do código do FSD (`fsd/fsd_computation.py`): no modo `resize_and_crop` os resíduos são **ampliados por interpolação bilinear** até o lado menor chegar a `max_size`, com `antialias=False`.
- Controle: recorte central 256×256 em PNG para todas as imagens (n = 190: 99 reais e 91 falsas; descartadas as com lado menor < 256), `max_size=256`:
  - **FSD AUC 0,508**, UnivFD AUC **0,870**.
  - Por gerador (FSD / UnivFD): ADM 0,495 / 0,882; GLIDE 0,791 / 0,828; Midjourney 0,552 / 0,790; SD 1.5 0,503 / 0,827; VQDM 0,283 / 0,967; Wukong 0,456 / 0,898.
- Interpretação: o escore do FSD acompanha o tamanho da imagem, não a classe. Com tamanho e formato igualados, ele cai ao acaso. Mas 256 px está fora do regime de uso do FSD (padrão 1024), então isso **não** prova que o método falhe em geral.
- Ressalva do controle: o PNG iguala o contêiner, mas as reais continuam com a história de compressão JPEG.
- Observação: a especificidade do FSD nesta amostra (53%) difere da do PDF (82%). A amostra é outra e não sei explicar a diferença.

---

## 3. Dataset político brasileiro

### 3.1 Fotos reais (513 usadas)
- Fonte: **Wikimedia Commons**, 50 nomes de políticos, baixadas pela API como miniaturas de 1024 px de largura.
- Filtros do script: JPEG, largura ≥ 1000 px, licenças livres (CC BY, CC BY-SA, CC0, domínio público), nome no **título** do arquivo, no máximo 12 por pessoa e 2 por data de evento, deduplicação por SHA-256.
- Triagem manual em folhas de contato numeradas: **40 imagens removidas** (documento de identidade com dados pessoais, assinaturas, pinturas, esporte, logos, foto com criança, repetição do painel "GOVERNO FEDERAL"). Antes, 8 fotos "Lula" eram da posse da Dilma e foram descartadas, e fotos de plenário com a pessoa minúscula também.
- **Limitação:** a coluna `politico` é o que o Commons diz. **A identidade não foi verificada pela imagem.** Todas as licenças e autores estão na planilha.
- Arquivo: `dataset/dataset_politicos_br.csv` (557 linhas na consolidação anterior; hoje 517 após a limpeza, das quais 514 reais). Pasta `dataset/real_oficial/`.

### 3.2 Falsas verificadas por checadores (estudo de caso)
| ID | Caso | Fonte | Observação |
|---|---|---|---|
| F001 | Bolsonaro visitando Lula no hospital | Aos Fatos, 12/12/2024 | marca d'água do Grok segundo a checagem |
| F002 | Diretor da Quaest com Flávio Bolsonaro | Aos Fatos, 17/09/2026 | |
| F003 | Lula "chorando" na Record | Aos Fatos, 15/09/2026 | **editada** com IA, classe separada |
| R001 | foto real da matéria da Piauí (comparação) | via Lupa, 04/10/2026 | URL da Piauí pendente |

São recortes de capturas de tela (legenda, interface, compressão da rede social) e ficam como **estudo de caso**, fora das estatísticas. Casos identificados mas não baixados: elefante abatido (Lupa), capas falsas Veja/GloboNews (Lupa), Lula "171" (Aos Fatos), site de campanha com 140 imagens de IA (Lupa).

### 3.3 Falsas geradas (514)
- Para cada foto real: legenda com **BLIP** (`Salesforce/blip-image-captioning-large`, prefixo "a photograph of", sem nomes). Prompt = legenda + `", press photograph, natural light, realistic, Brazil"`. Prompt negativo (SDXL e SD 1.5): `text, watermark, logo, caption, cartoon, painting, illustration`.
- Geradores alternados, semente `1000 + i`:
  | Gerador | Repositório | Passos | Guidance | Tamanho | Imagens |
  |---|---|---|---|---|---|
  | SDXL | `stabilityai/stable-diffusion-xl-base-1.0` | 30 | 6,0 | 1024 | 172 |
  | SD 1.5 | `stable-diffusion-v1-5/stable-diffusion-v1-5` | 30 | 7,5 | 512 | 171 |
  | SDXL-Turbo | `stabilityai/sdxl-turbo` | 4 | 0,0 | 512 | 171 |
- Pessoas **fictícias** (nenhum nome de político no prompt). SDXL levou cerca de 33 s por imagem na T4. As imagens estão em `MyDrive/tcc_politicos/fake_geradas/`, com o log em `geradas_log.csv`.
- Não foi feita conferência visual sistemática das falsas.

### 3.4 Padronização (igual para as duas classes)
- **Condição A:** recorte central 512×512 com pixels nativos (sem reamostragem), sem metadados, **um único JPEG q90**.
- **Condição B (tipo rede social):** a mesma imagem reduzida a 384×384 (Lanczos) e JPEG q75.
- Resultado: 1027 imagens (513 reais e 514 falsas); 1 real descartada (lado menor < 512).

### 3.5 Auditoria de viés (11 atributos triviais, regressão logística, 5-fold)
- **AUC com todos os atributos: 0,946.** Por atributo: variância do laplaciano 0,793, tamanho do arquivo 0,756, gradiente 0,700, saturação 0,676, desvio do canal R 0,659.
- Por gerador: SD 1.5 0,949; SDXL 0,956; SDXL-Turbo 0,981.
- Medianas (reais × falsas): tamanho 64,9 × 50,5 KB; laplaciano 0,0164 × 0,0040; gradiente 0,0289 × 0,0200; saturação 0,140 × 0,102. As reais têm cerca de **4× mais detalhe de alta frequência** por pixel.
- **Hipótese (não testada):** as miniaturas do Commons foram reduzidas a partir de fotos grandes (mais detalhe por pixel e duas gerações de compressão), e as falsas são pixels nativos de difusão (mais lisos).

### 3.6 Resultados dos detectores no conjunto político
| Detector | Condição | n | AUC | IC95 (bootstrap) | Acurácia (limiar padrão) | Recall | Especificidade |
|---|---|---|---|---|---|---|---|
| UnivFD | A | 1027 | **0,323** | [0,29; 0,35] | 0,471 | 0,021 | 0,922 |
| UnivFD | B | 1027 | 0,379 | [0,34; 0,41] | 0,495 | 0,008 | 0,982 |
| FSD | A | 1027 | 0,464 | [0,43; 0,50] | 0,500 | 1,000 | 0,000 |
| FSD | B | 1027 | 0,474 | [0,44; 0,51] | 0,500 | 1,000 | 0,000 |

AUC do UnivFD por gerador (A): SD 1.5 0,299; SDXL 0,350; SDXL-Turbo 0,319. FSD: 0,425; 0,487; 0,479.
O FSD, no limiar −2, classificou **tudo** como falso, então o limiar padrão não serve neste conjunto.

### 3.7 Subconjunto pareado
- Pareamento 1:1 por **escore de propensão** (regressão logística sobre os 11 atributos, predições fora da amostra), com calibre de 0,05: **119 pares** (238 imagens). AUC dos atributos no subconjunto: **0,457**.

| Detector | Condição | AUC | IC95 |
|---|---|---|---|
| UnivFD | A | 0,435 | [0,37; 0,51] |
| UnivFD | B | 0,487 | [0,41; 0,56] |
| FSD | A | **0,358** | [0,29; 0,43] |
| FSD | B | **0,373** | [0,30; 0,44] |

- Leitura: a inversão do UnivFD é, em grande parte, efeito de nitidez e tamanho (0,32 → 0,44), e ele fica no acaso. A inversão do **FSD persiste** (0,36), então não se explica só por esses atributos.
- Ressalva: nitidez baixa também é um indício legítimo de geração por difusão. O subconjunto pareado responde "o detector funciona além do que nitidez e tamanho explicam?", não "o detector é bom ou ruim". O pareamento foi feito nos mesmos dados (possível otimismo), e n = 238 dá margem de cerca de ±0,07.

---

### 3.8 Condição C com miniaturas do Commons (notebook `4b_controle_positivo_miniaturas.ipynb`, 22/10/2026)
- Reais = as mesmas miniaturas de 1024 px do Commons usadas antes; falsas = as 514 geradas. Recorte central 512×512 (alinhado a 8 px) e **PNG nas duas classes, sem nenhum JPEG novo**. Só a condição C foi rodada (as condições A e D do notebook não).
- Resultado (saída colada em 22/10/2026):

| Detector | Conjunto | n | AUC | IC95 (bootstrap) |
|---|---|---|---|---|
| UnivFD | todas | 1027 | 0,412 | [0,38; 0,45] |
| UnivFD | pareado | 138 (69 pares) | 0,496 | [0,40; 0,59] |
| FSD | todas | 1027 | 0,339 | [0,31; 0,37] |
| FSD | pareado | 138 (69 pares) | 0,445 | [0,35; 0,54] |

- AUC dos atalhos no subconjunto pareado: 0,384 (abaixo de 0,5 por validação cruzada em amostra pequena, ou seja, sem separação). 
- Auditoria de atalhos no conjunto todo (11 atributos triviais, regressão logística, 5-fold; as três condições rodaram a auditoria, mas só a C teve detectores):

| Condição | AUC atalhos (todos) | Laplaciano (AUC isolado) | Tamanho do arquivo | Gradiente | Mediana do laplaciano (reais × falsas) |
|---|---|---|---|---|---|
| C (PNG, sem JPEG) | **0,974** | 0,793 | 0,561 | 0,701 | 0,0164 × 0,0041 |
| A (JPEG q90) | 0,938 | 0,776 | 0,706 | 0,683 | 0,0151 × 0,0040 |
| D (falsas q95+q90) | 0,941 | 0,718 | 0,575 | 0,635 | 0,0151 × 0,0058 |

- Leitura: o viés **não caiu** em nenhuma condição (antes: 0,946). Em C ele é o maior (0,974), e as reais têm cerca de 4× mais detalhe de alta frequência que as falsas. Em D, igualar o número de compressões reduz a diferença de nitidez (0,0058 contra 0,0151, cerca de 2,6×), mas o conjunto continua separável (0,941). Ou seja, o viés não vem do número de recompressões; é uma diferença de conteúdo/processamento (hipótese anterior: miniaturas do Commons reduzidas de fotos grandes × pixels nativos de difusão), ainda não testada com originais.
- Leitura: tirar o JPEG extra **não fez os detectores funcionarem**. O UnivFD sobe de 0,32 (condição A) para 0,41, mas continua abaixo de 0,5 com IC que não inclui 0,5. O FSD fica pior (de 0,46 para 0,34). No subconjunto pareado os dois ficam compatíveis com o acaso (IC incluem 0,5), mas o pareado agora tem 69 pares, contra 119 antes, então os dois pareados não são diretamente comparáveis.
- Ressalva central: as reais continuam sendo miniaturas reduzidas e recodificadas pelo Commons, então **isto não é um controle positivo limpo**. Mostra que a recompressão que o meu pipeline aplicou não é a causa do resultado, não que o viés das reais foi removido.
- Esses detectores podem não generalizar para SD 1.5, SDXL e SDXL-Turbo por motivos próprios (o UnivFD foi treinado em outro tipo de gerador; o FSD foi usado a 512 px, abaixo do padrão). Isso é hipótese e não foi testado aqui.

### 3.9 Auditoria com reais NATIVAS (notebook `4_nativo_controle_positivo.ipynb`, 24/10/2026)
- Reais: 513 recortes centrais 512×512 de originais do Commons (baixados em 22 e 23/10 por `3c_baixar_real_nativo_local.ps1`; o Wikimedia limita o download de originais com 429 e `Retry-After: 600`), PNG, sem reamostragem. Falsas: as mesmas 514. Condições C (PNG), A (JPEG q90) e D (falsas q95+q90).
- **Rodada anterior descartada:** em 24/10 o notebook `4b` (miniaturas) foi aberto por engano no lugar do 4 e repetiu exatamente os números do UnivFD da seção 3.8 (AUC 0,412 e pareado 0,496). Serviu de checagem de reprodutibilidade; os resultados estão em `MyDrive/tcc_politicos/controle_miniaturas/`.

| Condição | AUC atalhos (11 atributos) | Laplaciano (AUC isolado) | Tamanho do arquivo | Gradiente | Mediana do laplaciano (reais × falsas) |
|---|---|---|---|---|---|
| C (PNG, sem JPEG) | 0,956 | 0,643 | 0,707 | 0,598 | 0,0025 × 0,0041 |
| A (JPEG q90) | 0,923 | 0,627 | 0,509 | 0,592 | 0,0026 × 0,0040 |
| D (falsas q95+q90) | 0,931 | 0,713 | 0,636 | 0,645 | 0,0026 × 0,0058 |

- **Achado:** com reais nativas, o sentido da diferença de nitidez **se inverteu**. Nas miniaturas as reais tinham ~4× mais detalhe de alta frequência que as falsas (laplaciano 0,0164 × 0,0041); nos recortes nativos têm **menos** (0,0025 × 0,0041). Isso é compatível com a hipótese da seção 3.5 (as miniaturas do Commons ganhavam nitidez ao serem reduzidas de originais grandes), agora com evidência direta, mas a hipótese ainda não foi testada de forma isolada.
- **O viés total não caiu:** os atalhos continuam separando as classes (AUC 0,92 a 0,96; antes 0,946 e 0,974). O laplaciano sozinho caiu de 0,79 para 0,64 na condição C, então a separação agora vem de outros atributos. **Falta identificar quais** (a saída colada mostra só laplaciano, tamanho e gradiente; os 11 atributos estão na memória do notebook).
- AUC dos detectores com reais nativas: **pendente** (células 4 e 5 ainda não coladas).

## 4. Em andamento
- **Recortes nativos dos originais** (`dataset/real_nativo/`): a primeira rodada (14/10) chegou a 431 de 513, mas essas imagens **não estão mais neste computador**. A tentativa de refazer no Colab falhou (32 de 514; o Wikimedia devolve 429) e a de refazer localmente (`3c_baixar_real_nativo_local.ps1`) está limitada pelo Wikimedia: o servidor de originais responde 429 com `Retry-After: 600`, então o ritmo é de cerca de 1 imagem a cada 30 s ou menos. Recorte central 512×512 alinhado à grade 8×8, PNG, sem reamostragem.
- **Condição C com reais nativas (controle positivo limpo):** depende dessas imagens. Se não chegar a tempo, o texto usa a condição C com miniaturas (seção 3.8) e declara a limitação.
- **Pendências externas:** carta do orientador (ele se comprometeu a escrever; prazo sugerido 25/10), resposta da Lupa (mensagem enviada por WhatsApp), Lattes e mini-bio.

---

## 5. Limitações (para constar no texto)
1. Amostras pequenas: 200 imagens no Tiny-GenImage; 119 pares no subconjunto pareado; 9 a 21 imagens por gerador.
2. O experimento preliminar original não é reproduzível (dados perdidos).
3. Viés de processamento não eliminado: AUC 0,946 dos atributos triviais no conjunto padronizado.
4. As reais vêm de miniaturas recodificadas do Commons; as falsas, de pixels nativos.
5. Identidade dos políticos nas fotos **não verificada** (só título e descrição do Commons).
6. Falsas geradas só por modelos de difusão (SD 1.5, SDXL, SDXL-Turbo), com **pessoas fictícias**; não representam deepfakes de políticos reais.
7. Falsas **reais** (circuladas) são só 2 e 1 editada, usadas como estudo de caso.
8. O FSD foi avaliado em 512 px, abaixo do regime de uso padrão (1024).
9. Limiares fixos (UnivFD 0,5; FSD −2,0), sem otimização com validação independente.
10. Estimativas de tempo e custo computacional são aproximadas.
11. Fotos de agência com painéis e texto legível nas reais podem introduzir viés de conteúdo; falsas geradas costumam errar texto.
12. O controle sem JPEG (condição C) usa reais que são miniaturas recodificadas do Commons; não há ainda controle positivo com reais nativas nem com um conjunto em que os detectores sabidamente funcionem.

---

## 6. Arquivos e onde estão
**No computador (`C:\Users\manue\carolina-bori\`):**
- `2_gerar_falsas.ipynb`, `3_avaliar_politico.ipynb`, `tcc_detectores.ipynb` (Tiny-GenImage)
- `dataset/dataset_politicos_br.csv`, `dataset/real_oficial/`, `dataset/real_nativo/`, `dataset/real_oficial.zip`
- `dataset/_descartadas/`, `dataset/_triagem/` (material de trabalho)
- `dataset_politicos_br_modelo.csv`, `resultados_rapidos_colab.py`, `.mcp.json`

**No Google Drive (`MyDrive/tcc_politicos/`):**
- `real_oficial.zip`, `fake_geradas/`, `legendas.csv`, `geradas_log.csv`
- `padronizado_meta.csv`, `auditoria_features.csv`, `resultados_politico.csv`, `resumo_politico.csv`, `auc_por_gerador_politico.csv`, `roc_politico.png`

**Reprodução:** sementes fixas (42 no Tiny-GenImage; 1000+i na geração; 0 e 1 nos pareamentos e bootstraps). Versões dos repositórios nos commits listados na seção 2.3.

---

## 7. O que só você pode registrar (autoria e protagonismo)
O edital pede que o projeto mostre o que foi seu e o que foi apoio. Preencha com fatos:
- O que você decidiu, executou e analisou sozinha:
- O que fez com apoio do orientador (quando, em quê):
- Onde usou assistente de IA (código dos notebooks, buscas de fontes, rascunhos) e o que você conferiu e rodou por conta própria:
- Marcos com data (ex.: primeiros experimentos, descoberta do viés de formato, decisão de criar o dataset brasileiro):
