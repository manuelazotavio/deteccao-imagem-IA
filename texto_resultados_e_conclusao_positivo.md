# Resultados, discussão e conclusão (rascunho, versão com ênfase nas contribuições)

Rascunho em 22/10/2026. Mesmos números e mesmas conclusões da versão anterior (`texto_resultados_e_conclusao.md`); mudam o enquadramento e a ordem. Os números vêm de `registro_dados_e_experimentos.md`. **[CONFERIR]** marca o que só você pode confirmar.

---

## 5. Resultados

### 5.1 Um protocolo de avaliação que revela o que os números brutos escondem [reg. 2]

Em um subconjunto de 200 imagens do Tiny-GenImage, o UnivFD obteve AUC de 0,879 e o FSD de 0,430. Em vez de aceitar esses valores, auditei a amostra e identifiquei a causa: o rótulo estava perfeitamente correlacionado com o formato do arquivo (100% das reais em JPEG, 100% das falsas em PNG), e as falsas incluíam imagens muito pequenas.

A auditoria permitiu explicar o comportamento do FSD: seu escore acompanhou o tamanho da imagem (Spearman ρ = −0,594). Ao igualar tamanho e formato (recorte central de 256×256 em PNG, n = 190), o FSD foi para o acaso (AUC 0,508) e o UnivFD manteve 0,870. O resultado mostra o valor de controlar o formato do arquivo antes de comparar detectores. Ele não prova que o FSD falhe em geral, já que 256 px está abaixo do regime de uso do método (padrão de 1024 px).

### 5.2 Um conjunto de dados brasileiro pareado por conteúdo [reg. 3.1, 3.3, 3.4]

Construí um conjunto de 1027 imagens de contexto político brasileiro:

- **513 fotos reais** de 50 políticos, do Wikimedia Commons, com licenças livres e triagem manual de 40 imagens;
- **514 imagens geradas** por Stable Diffusion 1.5, SDXL e SDXL-Turbo, cada uma a partir da legenda (BLIP, sem nomes) de uma foto real, de modo que as duas classes tenham distribuição de cenas semelhante.

Todas as falsas retratam pessoas fictícias. Autoria, licença, gerador, prompt e semente de cada imagem estão registrados, e as sementes são fixas, o que torna o conjunto reproduzível. As duas classes passaram pelo mesmo processamento: recorte central de 512×512 sem reamostragem e um único JPEG q90 (condição A). Uma segunda condição simula compartilhamento em rede social (384×384, JPEG q75, condição B).

### 5.3 A auditoria de atalhos como etapa de validação [reg. 3.5, 3.8]

Antes de avaliar qualquer detector, testei se 11 atributos triviais (tamanho do arquivo, nitidez, gradiente, cor) separavam as classes. Separavam: AUC de 0,946 no conjunto padronizado, com a variância do laplaciano como atributo mais forte (AUC 0,793; as reais têm cerca de 4× mais detalhe de alta frequência por pixel).

Testei se o processamento era o responsável (Tabela 1).

**Tabela 1. O padrão de atalhos se repete em três condições de processamento.**

| Condição | AUC dos atalhos | Mediana do laplaciano (reais × falsas) |
|---|---|---|
| A: JPEG q90 nas duas classes | 0,938 | 0,0151 × 0,0040 |
| C: PNG, sem JPEG novo | 0,974 | 0,0164 × 0,0041 |
| D: falsas com q95 + q90, reais com q90 | 0,941 | 0,0151 × 0,0058 |

O número de recompressões não explica a diferença: igualá-lo (D) reduziu a distância de nitidez, mas o conjunto continuou separável. Isso aponta para uma diferença de origem entre as classes. Minha hipótese, que deixo como próximo passo a testar, é que as reais são miniaturas reduzidas de fotos grandes e as falsas são pixels nativos de difusão. Esse diagnóstico só foi possível por causa da auditoria.

### 5.4 Desempenho dos detectores [reg. 3.6, 3.8]

**Tabela 2. AUC no conjunto político completo (n = 1027), IC de 95% por bootstrap.**

| Detector | Condição | AUC | IC95 |
|---|---|---|---|
| UnivFD | A | 0,323 | [0,29; 0,35] |
| UnivFD | B (rede social) | 0,379 | [0,34; 0,41] |
| UnivFD | C (sem JPEG novo) | 0,412 | [0,38; 0,45] |
| FSD | A | 0,464 | [0,43; 0,50] |
| FSD | B | 0,474 | [0,44; 0,51] |
| FSD | C | 0,339 | [0,31; 0,37] |

Nesse conjunto, os dois detectores não apresentaram o desempenho observado em outras bases. O AUC abaixo de 0,5 sugere que os escores acompanham os atalhos (as falsas, mais lisas, parecem "mais reais" a eles) e não a origem da imagem; o subconjunto pareado, a seguir, testa essa leitura. Com os limiares padrão, o UnivFD classificou quase tudo como real (recall de 0,021 na condição A) e o FSD classificou tudo como falso. O padrão se repetiu nos três geradores (UnivFD na condição A: SD 1.5 0,299, SDXL 0,350, SDXL-Turbo 0,319). A condição C, que remove o JPEG adicional, mostrou que a recompressão do pipeline não é a causa.

### 5.5 Isolando o efeito dos atalhos: subconjunto pareado [reg. 3.7, 3.8]

Para separar o efeito dos atalhos do sinal dos detectores, pareei cada falsa a uma real de nitidez e tamanho semelhantes (escore de propensão, calibre 0,05). Nesse subconjunto os atalhos deixam de separar as classes (AUC 0,457 na condição A e 0,384 na C).

**Tabela 3. AUC no subconjunto pareado.**

| Detector | Condição | Pares | AUC | IC95 |
|---|---|---|---|---|
| UnivFD | A | 119 | 0,435 | [0,37; 0,51] |
| UnivFD | B | 119 | 0,487 | [0,41; 0,56] |
| UnivFD | C | 69 | 0,496 | [0,40; 0,59] |
| FSD | A | 119 | 0,358 | [0,29; 0,43] |
| FSD | B | 119 | 0,373 | [0,30; 0,44] |
| FSD | C | 69 | 0,445 | [0,35; 0,54] |

Com o pareamento, a inversão do UnivFD praticamente desaparece (de 0,32 para 0,44 na condição A; todos os intervalos incluem 0,5), o que mostra que ela vinha em grande parte de nitidez e tamanho. No FSD, os resultados das condições A e B seguem abaixo de 0,5, o que indica que há algo além desses atributos a investigar; na condição C o intervalo inclui 0,5. Os subconjuntos de 119 e 69 pares não são diretamente comparáveis.

---

## 6. Discussão

**O principal resultado é metodológico.** Os números brutos de ambos os detectores, em ambas as bases, refletiam em boa parte propriedades do arquivo: formato e tamanho no Tiny-GenImage, nitidez no conjunto político. A auditoria de atalhos, combinada ao pareamento, permitiu dizer o que os números significam, algo que a leitura direta de AUC e acurácia não permitiria. Esse protocolo é reaproveitável com qualquer detector e qualquer conjunto.

**O segundo resultado é informativo para o uso desses detectores.** Nas condições testadas (três geradores de difusão, fotos de contexto político), o UnivFD e o FSD não discriminaram real de gerada além do que nitidez e tamanho explicam. Para quem pensa em usá-los na checagem de imagens políticas, isso é um alerta útil: a resposta depende do gerador e do processamento, e não se deve confiar em um escore sem validar o detector com dados de condições comparáveis.

**O que o trabalho deixa em aberto** são perguntas claras para os próximos passos:

- Os detectores funcionam quando as reais são fotos nativas, sem recodificação do Commons? A condição C aproxima essa situação, mas ainda usa miniaturas. **[CONFERIR: se os recortes nativos forem concluídos a tempo, substitua este item pelo resultado.]**
- O UnivFD, treinado com outro tipo de gerador, generaliza para modelos de difusão mais recentes? O FSD melhora no seu regime de uso (1024 px)? São hipóteses, não testadas aqui.
- Como se comportam em imagens falsas realmente circuladas? Os poucos casos verificados que coletei (dois geradas e uma editada) servem como estudo de caso e já preparam esse caminho.

---

## 7. Conclusão

Este trabalho oferece três contribuições: **(1)** um protocolo de avaliação que inclui auditoria de atalhos triviais e pareamento por escore de propensão, que mostrou como o formato e a nitidez distorcem o desempenho aparente de detectores; **(2)** um conjunto reproduzível de 1027 imagens de contexto político brasileiro, com 513 fotos reais licenciadas e 514 imagens geradas pareadas por conteúdo, com origem, gerador, prompt e semente registrados; e **(3)** uma avaliação controlada de dois detectores recentes (UnivFD e FSD), que mostra que, nas condições estudadas, eles não discriminaram imagens reais de geradas por SD 1.5, SDXL e SDXL-Turbo além do que nitidez e tamanho explicam.

Esse resultado não encerra a questão: aponta para onde olhar a seguir, com fotos reais em resolução nativa, mais geradores e imagens falsas efetivamente circuladas. A principal mensagem prática é que, antes de confiar em um detector, é preciso auditar o conjunto de avaliação. O protocolo e o conjunto aqui apresentados servem de base para essa verificação.

## 8. Escopo e limitações

Para que as conclusões sejam lidas no escopo correto:

1. As amostras são pequenas (200 imagens no Tiny-GenImage; 119 e 69 pares nos subconjuntos pareados; margem do AUC de cerca de ±0,07 a ±0,10), e o pareamento foi feito nos mesmos dados em que foi avaliado.
2. O experimento preliminar original (08/10/2026) não é reproduzível, pois os arquivos se perderam; os resultados reproduzíveis são os da reanálise e do conjunto político.
3. O viés de processamento não foi eliminado (AUC dos atalhos de 0,94 a 0,97). As reais são miniaturas recodificadas do Commons e as falsas são pixels nativos; a condição sem JPEG usa as mesmas miniaturas.
4. A identidade dos políticos não foi verificada pela imagem (apenas título e descrição do Commons).
5. As falsas vêm só de modelos de difusão e retratam pessoas fictícias; não representam deepfakes de políticos reais.
6. O FSD foi avaliado a 512 px, abaixo do padrão (1024 px); os limiares foram fixos (UnivFD 0,5; FSD −2,0).
7. Fotos de agência com painéis e texto legível nas reais podem introduzir viés de conteúdo.
