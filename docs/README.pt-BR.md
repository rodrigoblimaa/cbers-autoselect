# CBERS AutoSelect — documentação em português

O **CBERS AutoSelect** é um plugin experimental para QGIS que seleciona automaticamente a **cena CBERS-4A/WPM adequada mais recente** para uma área de interesse (AOI), consultando o catálogo STAC do INPE.

## O que o usuário informa

1. **Área de interesse:** qualquer camada vetorial poligonal carregada no QGIS (perímetro urbano, município, bacia etc.).
2. **Cobertura espacial mínima:** padrão de 99,99%.
3. **Nebulosidade potencial máxima:** padrão de 1,00%.
4. **Produto a carregar:** RGB fusionada por PCA a 2 m ou RGB multiespectral a 8 m.

O plugin consulta o STAC retrospectivamente, em janelas de 180 dias, testa a cena mais recente primeiro e seleciona a **primeira** que atende aos dois critérios. Em seguida, adiciona o produto ao QGIS com seu **ID original do STAC** como nome da camada.

## Instalação e operação

No QGIS, abra **Complementos → Gerenciar e Instalar Complementos → Instalar a partir de ZIP** e selecione o arquivo `CBERS_AutoSelect_0.1.0_QGIS.zip`. Não utilize o ZIP completo do GitHub para instalar o plugin.

Carregue uma camada poligonal, clique em **Buscar cena CBERS adequada mais recente**, escolha os critérios e inicie a consulta. A busca permite cancelamento. As mensagens serão exibidas automaticamente em português quando o QGIS estiver configurado em português do Brasil; em inglês, se estiver configurado em inglês.

## Metodologia resumida

A cobertura é calculada pela proporção de pixels válidos dentro da AOI rasterizada em grade métrica fixa (2 m ou 8 m, conforme o produto). A avaliação de nebulosidade utiliza as bandas azul, verde, vermelho e infravermelho próximo (NIR) do WPM Level-4, em 8 m. O teste emprega limiares provisórios: brilho RGB ≥600 DN, NIR ≥550 DN e desvio relativo RGB ≤0,18.

**Importante:** o percentual é de **nebulosidade potencial**, não uma máscara oficial ou uma classificação validada de nuvens. Telhados e superfícies muito claras podem gerar falsos positivos. Para reduzir resultados incompletos, o plugin não aprova o teste espectral quando os dados multiespectrais válidos cobrem menos de 95% da AOI.

O processamento em memória tem limite de 40 milhões de pixels por grade. A imagem é acessada remotamente (COG/VRT); uma conexão com a internet continua necessária para visualizá-la ao reabrir o projeto.

## Desenvolvimento, código e licença

- Fonte de dados: STAC público do INPE, coleções `CB4A-WPM-PCA-FUSED-1` e `CB4A-WPM-L4-DN-1`.
- Código-fonte: <https://github.com/rodrigoblimaa/cbers-autoselect>
- Dúvidas e erros: <https://github.com/rodrigoblimaa/cbers-autoselect/issues>
- Licença: GNU GPL v2.0, conforme o arquivo `LICENSE`.
- Situação: **0.1.0 — experimental**, ainda dependendo de testes com outras AOIs, sistemas operacionais e situações de nebulosidade.

**Uso de IA:** o ChatGPT (OpenAI) auxiliou no desenvolvimento, revisão, depuração e documentação do código. A definição dos requisitos, a avaliação dos resultados e a responsabilidade científica são do autor humano.


## Ambiente de teste confirmado

O plugin foi instalado e seu funcionamento foi relatado como satisfatório em **QGIS 3.44.8 (Solothurn), macOS 14.8.7**, com Python 3.12.11, Qt 5.15.18 e GDAL 3.12.0. Ainda são necessários testes em outros sistemas operacionais, AOIs e condições de nebulosidade.
