# Resultados, discussão e conclusão (rascunho)

Rascunho em 22/10/2026. Todos os números vêm de `registro_dados_e_experimentos.md` (seções indicadas entre colchetes). Trechos marcados com **[CONFERIR]** dependem de algo que só você pode confirmar. Ajuste o tom e a pessoa verbal ao resto do texto.

---

## 5. Resultados

### 5.1 Reanálise do Tiny-GenImage: o resultado bruto reflete o formato do arquivo [reg. 2]

Em um subconjunto de 200 imagens do Tiny-GenImage (100 reais e 100 falsas, sorteadas com semente fixa), o UnivFD obteve AUC de 0,879 e o FSD de 0,430. Uma auditoria da amostra mostrou que o rótulo estava perfeitamente correlacionado com o formato do arquivo: 100% das reais eram JPEG e 100% das falsas eram PNG, e as falsas incluíam imagens muito pequenas (menor lado de 128 px, contra 240 px nas reais).

O escore do FSD acompanhou o tamanho da imagem, não a classe: a correlação de Spearman entre o menor lado e o escore foi ρ = −0,594. Ao igualar tamanho e formato (recorte central de 256×256 em PNG para todas as imagens, n = 190), o FSD caiu para o acaso (AUC 0,508) e o UnivFD manteve 0,870.

Esse segundo valor deve ser lido com cuidado: o PNG iguala o contêiner, mas as imagens reais seguem com a história de compressão JPEG, e 256 px está abaixo do regime de uso do FSD (padrão de 1024 px). O achado é que **o desempenho observado dependia de propriedades do arquivo**, não que o FSD falhe em geral.

### 5.2 Conjunto político brasileiro [reg. 3.1, 3.3, 3.4]

Foram reunidas 513 fotos reais de 50 políticos (Wikimedia Commons, licenças livres, triagem manual de 40 imagens) e 514 imagens falsas geradas por mim com Stable Diffusion 1.5, SDXL e SDXL-Turbo. Cada falsa foi gerada a partir de uma legenda (BLIP, sem nomes) de uma foto real, de modo que as duas classes tenham distribuição de cenas semelhante. Todas as falsas retratam pessoas fictícias. Antes da avaliação, as duas classes passaram pelo mesmo processamento: recorte central de 512×512 sem reamostragem e um único JPEG de qualidade 90 (condição A). Uma segunda condição simula compartilhamento em rede social (384×384 e JPEG q75, condição B).

### 5.3 Auditoria de viés [reg. 3.5, 3.8]

Antes de avaliar os detectores, testei se atributos triviais (tamanho do arquivo, nitidez, gradiente, estatísticas de cor) bastavam para separar as classes. Um classificador logístico com 11 atributos, validado em 5 partes, obteve **AUC de 0,946** no conjunto padronizado. O atributo mais forte foi a variância do laplaciano (AUC 0,793): as reais têm cerca de quatro vezes mais detalhe de alta frequência por pixel (mediana 0,0164 contra 0,0040).

Repeti a auditoria em outras condições de processamento (Tabela 1). Em nenhuma o viés desapareceu.

**Tabela 1. Atalhos triviais ainda separam as classes em todas as condições testadas.**

| Condição | AUC dos atalhos (11 atributos) | Mediana do laplaciano (reais × falsas) |
|---|---|---|
| A: JPEG q90 nas duas classes | 0,938 | 0,0151 × 0,0040 |
| C: PNG, sem JPEG novo | 0,974 | 0,0164 × 0,0041 |
| D: falsas com q95 + q90, reais com q90 | 0,941 | 0,0151 × 0,0058 |

Igualar o número de compressões (D) reduziu a diferença de nitidez, mas o conjunto continuou separável. Isso indica que o viés não decorre do número de recompressões. Minha hipótese, **ainda não testada**, é que as fotos reais do Commons são miniaturas reduzidas a partir de originais grandes (mais detalhe por pixel e duas gerações de compressão), enquanto as falsas são pixels nativos de modelos de difusão, mais lisos.

### 5.4 Desempenho dos detectores [reg. 3.6, 3.8]

**Tabela 2. AUC dos detectores no conjunto político completo (n = 1027), com IC de 95% por bootstrap.**

| Detector | Condição | AUC | IC95 |
|---|---|---|---|
| UnivFD | A (JPEG q90) | 0,323 | [0,29; 0,35] |
| UnivFD | B (rede social) | 0,379 | [0,34; 0,41] |
| UnivFD | C (PNG, sem JPEG novo) | 0,412 | [0,38; 0,45] |
| FSD | A | 0,464 | [0,43; 0,50] |
| FSD | B | 0,474 | [0,44; 0,51] |
| FSD | C | 0,339 | [0,31; 0,37] |

Nas condições A, B e C o UnivFD ficou **abaixo de 0,5**: ele atribui às imagens geradas escores de "real" mais altos que às fotos reais. Com o limiar padrão (0,5), classificou quase tudo como real (recall de 0,021 na condição A). O FSD, no limiar padrão (−2,0), classificou **todas** as imagens como falsas (especificidade zero), e a AUC mostra que o ordenamento dos escores também não separa as classes. Os resultados por gerador seguem o mesmo padrão (UnivFD na condição A: SD 1.5 0,299, SDXL 0,350, SDXL-Turbo 0,319).

A condição C foi pensada como melhor caso para os detectores: sem nenhuma compressão JPEG adicional. A ausência de melhora relevante mostra que **a recompressão do meu pipeline não explica o resultado**.

### 5.5 Subconjunto pareado por nitidez e tamanho [reg. 3.7, 3.8]

Como os atalhos explicam parte do resultado, pareei cada imagem falsa a uma real com escore de propensão semelhante (regressão logística sobre os 11 atributos, calibre de 0,05). Nesse subconjunto os atalhos deixam de separar as classes (AUC 0,457 na condição A; 0,384 na C).

**Tabela 3. AUC dos detectores no subconjunto pareado.**

| Detector | Condição | Pares | AUC | IC95 |
|---|---|---|---|---|
| UnivFD | A | 119 | 0,435 | [0,37; 0,51] |
| UnivFD | B | 119 | 0,487 | [0,41; 0,56] |
| UnivFD | C | 69 | 0,496 | [0,40; 0,59] |
| FSD | A | 119 | 0,358 | [0,29; 0,43] |
| FSD | B | 119 | 0,373 | [0,30; 0,44] |
| FSD | C | 69 | 0,445 | [0,35; 0,54] |

O UnivFD ficou compatível com o acaso (todos os intervalos incluem 0,5), o que sugere que sua inversão no conjunto completo é em grande parte efeito de nitidez e tamanho (de 0,32 para 0,44 na condição A). O FSD permaneceu abaixo de 0,5 nas condições A e B, de modo que sua inversão não se explica apenas por esses atributos; na condição C o intervalo inclui 0,5. Os subconjuntos das condições A/B e C têm tamanhos diferentes (119 e 69 pares) e não são diretamente comparáveis.

---

## 6. Discussão

Os resultados apontam para duas conclusões complementares.

**Primeiro, o desempenho aparente dos detectores é sensível a propriedades do arquivo.** No Tiny-GenImage, o AUC de 0,879 do UnivFD e o resultado do FSD coexistiam com um viés de formato e de tamanho. No conjunto político, mesmo após padronizar tamanho, recorte e codificação, atributos triviais separavam as classes com AUC de 0,94 a 0,97. Avaliar detectores nesses conjuntos sem uma auditoria desse tipo produziria números enganosos, tanto para cima quanto, como aqui, para baixo (AUC invertido).

**Segundo, nas condições testadas, nenhum dos dois detectores discriminou imagens reais de geradas além do que nitidez e tamanho explicam.** O UnivFD ficou no acaso no subconjunto pareado, e o FSD ficou no acaso ou abaixo dele. A condição sem JPEG adicional, tomada como melhor caso para os detectores, não alterou essa conclusão.

Há uma ressalva de interpretação importante: **a nitidez baixa também é um sinal legítimo de imagens geradas por difusão.** O subconjunto pareado responde à pergunta "o detector funciona além do que nitidez e tamanho explicam?", e não "o detector é bom ou ruim". Além disso, a condição C não é um controle positivo limpo, pois as reais continuam sendo miniaturas recodificadas pelo Commons. A pergunta "os detectores funcionam quando as reais são nativas e não há JPEG algum?" permanece em aberto. **[CONFERIR: se os recortes nativos forem concluídos a tempo, substitua este parágrafo pelo resultado da condição C com reais nativas.]**

Os resultados também não permitem afirmar que o UnivFD e o FSD falham em geral. Hipóteses plausíveis, **não testadas aqui**, são que o UnivFD, treinado com outro tipo de gerador, não generalize para SD 1.5, SDXL e SDXL-Turbo, e que o FSD, avaliado a 512 px, esteja fora do seu regime de uso (padrão de 1024 px).

---

## 7. Conclusão

Neste trabalho avaliei dois detectores de imagens geradas por IA (UnivFD e FSD) em fotos de contexto político brasileiro e, antes disso, em um subconjunto do Tiny-GenImage. Em ambos os casos, os números brutos refletiam em grande parte viés de processamento (formato e tamanho no Tiny-GenImage; nitidez no conjunto político), e não a capacidade dos detectores. Após controlar esses fatores, nenhum dos dois detectores demonstrou capacidade de discriminar imagens reais de geradas em 119 pares (condições A e B) e 69 pares (condição C): o UnivFD ficou no acaso e o FSD ficou no acaso ou abaixo dele, para os geradores de difusão estudados (SD 1.5, SDXL e SDXL-Turbo).

A contribuição prática do trabalho é metodológica: uma auditoria de atalhos triviais deve preceder a avaliação de detectores, e relatar apenas AUC ou acurácia em conjuntos não auditados pode superestimar ou subestimar o desempenho. Fica como trabalho futuro avaliar os mesmos detectores com fotos reais em resolução nativa, com geradores adicionais e com imagens falsas de fato circuladas (os poucos casos verificados por agências de checagem coletados aqui não bastam para estatísticas).

## 8. Limitações

1. Amostras pequenas: 200 imagens no Tiny-GenImage, 119 e 69 pares nos subconjuntos pareados, 9 a 21 imagens por gerador no Tiny-GenImage.
2. O experimento preliminar original (Tiny-GenImage, 200 imagens, 08/10/2026) não é reproduzível: os arquivos de resultados se perderam.
3. O viés de processamento não foi eliminado (AUC dos atalhos de 0,94 a 0,97).
4. As reais vêm de miniaturas recodificadas do Commons e as falsas de pixels nativos; a condição sem JPEG usa as mesmas miniaturas.
5. A identidade dos políticos nas fotos não foi verificada pela imagem (apenas título e descrição do Commons).
6. As falsas foram geradas só por modelos de difusão, com pessoas fictícias; não representam deepfakes de políticos reais. Falsas realmente circuladas são apenas dois casos e uma imagem editada, usados como estudo de caso e fora das estatísticas.
7. O FSD foi avaliado a 512 px, abaixo do padrão de 1024 px; limiares fixos (UnivFD 0,5; FSD −2,0), sem validação independente.
8. O pareamento por escore de propensão foi feito nos mesmos dados em que foi avaliado (possível otimismo), e com n pequeno a margem do AUC é de cerca de ±0,07 a ±0,10.
9. Fotos de agência com painéis e texto legível nas reais podem introduzir viés de conteúdo; as falsas costumam errar texto.
