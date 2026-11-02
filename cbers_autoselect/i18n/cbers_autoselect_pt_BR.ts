<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1" language="pt_BR" sourcelanguage="en_US">
  <context>
    <name>CBERSAutoSelect</name>
    <message id="action">
      <source>Find latest suitable CBERS scene</source>
      <translation>Buscar cena CBERS adequada mais recente</translation>
    </message>
    <message id="tooltip">
      <source>CBERS AutoSelect — automatic scene suitability screening</source>
      <translation>CBERS AutoSelect — seleção automática de cenas adequadas</translation>
    </message>
    <message id="dialog_title">
      <source>CBERS AutoSelect</source>
      <translation>CBERS AutoSelect</translation>
    </message>
    <message id="heading">
      <source>Find latest suitable CBERS scene</source>
      <translation>Buscar cena CBERS adequada mais recente</translation>
    </message>
    <message id="source">
      <source>Source: INPE STAC catalog · CBERS-4A/WPM</source>
      <translation>Fonte: catálogo STAC/INPE · CBERS-4A/WPM</translation>
    </message>
    <message id="aoi">
      <source>Area of interest:</source>
      <translation>Área de interesse:</translation>
    </message>
    <message id="coverage_label">
      <source>Minimum spatial coverage:</source>
      <translation>Cobertura espacial mínima:</translation>
    </message>
    <message id="cloud_label">
      <source>Maximum potential cloudiness:</source>
      <translation>Nebulosidade potencial máxima:</translation>
    </message>
    <message id="product_label">
      <source>Product to load:</source>
      <translation>Produto a carregar:</translation>
    </message>
    <message id="fused">
      <source>PCA-fused RGB — 2 m</source>
      <translation>RGB fusionada por PCA — 2 m</translation>
    </message>
    <message id="l4">
      <source>Multispectral RGB — 8 m</source>
      <translation>RGB multiespectral — 8 m</translation>
    </message>
    <message id="note">
      <source>Potential cloudiness uses WPM Level-4 blue, green, red and NIR bands at 8 m. The spectral screening is experimental and may classify bright roofs as clouds.</source>
      <translation>A nebulosidade potencial utiliza as bandas azul, verde, vermelho e NIR do WPM Level-4 a 8 m. A avaliação espectral é experimental e pode confundir telhados claros com nuvens.</translation>
    </message>
    <message id="search">
      <source>Find latest suitable CBERS scene</source>
      <translation>Buscar cena CBERS adequada mais recente</translation>
    </message>
    <message id="cancel">
      <source>Cancel</source>
      <translation>Cancelar</translation>
    </message>
    <message id="no_polygon">
      <source>Load a polygon vector layer before searching.</source>
      <translation>Carregue uma camada vetorial poligonal antes de iniciar a busca.</translation>
    </message>
    <message id="already_searching">
      <source>A search is already running.</source>
      <translation>Já existe uma busca em andamento.</translation>
    </message>
    <message id="aoi_missing">
      <source>The selected area of interest is unavailable or has no valid CRS.</source>
      <translation>A área de interesse não está disponível ou não possui CRS válido.</translation>
    </message>
    <message id="aoi_empty">
      <source>The selected layer contains no valid geometries.</source>
      <translation>A camada selecionada não possui geometrias válidas.</translation>
    </message>
    <message id="aoi_invalid">
      <source>Could not repair the selected geometry.</source>
      <translation>Não foi possível corrigir a geometria selecionada.</translation>
    </message>
    <message id="aoi_invalid_bounds">
      <source>The selected area of interest extends beyond the supported spatial range.</source>
      <translation>A área de interesse está fora do intervalo espacial permitido.</translation>
    </message>
    <message id="progress_initial">
      <source>Preparing the area of interest…</source>
      <translation>Preparando a área de interesse…</translation>
    </message>
    <message id="progress_task">
      <source>CBERS AutoSelect — searching CBERS scenes</source>
      <translation>CBERS AutoSelect — pesquisando cenas CBERS</translation>
    </message>
    <message id="search_cancelled">
      <source>Search canceled.</source>
      <translation>Busca cancelada.</translation>
    </message>
    <message id="search_failed">
      <source>Could not complete the search.

{error}</source>
      <translation>Não foi possível concluir a busca.

{error}</translation>
    </message>
    <message id="unknown_error">
      <source>Unspecified error</source>
      <translation>Erro não identificado</translation>
    </message>
    <message id="no_scene">
      <source>No scene satisfied the specified thresholds within the search period.</source>
      <translation>Nenhuma cena atendeu aos critérios no período consultado.</translation>
    </message>
    <message id="load_failed">
      <source>A scene was selected but could not be loaded into QGIS:
{error}</source>
      <translation>A cena foi selecionada, mas não pôde ser carregada no QGIS:
{error}</translation>
    </message>
    <message id="success">
      <source>A suitable CBERS scene was selected and loaded.

Product: {id}
Date: {date}
Area: {aoi}
Spatial coverage: {coverage:.6f}%
Potential cloudiness: {cloud:.4f}%
Potential cloud pixels: {pixels}
Scenes evaluated: {reviewed}

Source: STAC/INPE</source>
      <translation>Cena CBERS adequada selecionada e carregada.

Produto: {id}
Data: {date}
Área: {aoi}
Cobertura espacial: {coverage:.6f}%
Nebulosidade potencial: {cloud:.4f}%
Pixels potencialmente associados a nuvens: {pixels}
Cenas avaliadas: {reviewed}

Fonte: STAC/INPE</translation>
    </message>
    <message id="loaded">
      <source>{id} loaded successfully.</source>
      <translation>{id} carregado com sucesso.</translation>
    </message>
    <message id="details_empty">
      <source>No rejected scenes</source>
      <translation>Nenhuma cena rejeitada</translation>
    </message>
    <message id="details_no_coverage">
      <source>coverage not evaluated</source>
      <translation>cobertura não avaliada</translation>
    </message>
    <message id="details_coverage">
      <source>coverage {value:.5f}%</source>
      <translation>cobertura {value:.5f}%</translation>
    </message>
    <message id="details_nocloud">
      <source>potential cloudiness not evaluated</source>
      <translation>nebulosidade potencial não avaliada</translation>
    </message>
    <message id="details_cloud">
      <source>potential cloudiness {value:.4f}%</source>
      <translation>nebulosidade potencial {value:.4f}%</translation>
    </message>
    <message id="grid_info">
      <source>AOI rasterized: {pixels:,} pixels at {resolution:g} m</source>
      <translation>AOI rasterizada: {pixels:,} pixels a {resolution:g} m</translation>
    </message>
    <message id="stac_window">
      <source>Querying STAC: {start} to {end}</source>
      <translation>Consultando STAC: {start} a {end}</translation>
    </message>
    <message id="stac_count">
      <source>{count} scenes found in this time window</source>
      <translation>{count} cenas encontradas nesta janela</translation>
    </message>
    <message id="analyzing">
      <source>Analyzing {id}</source>
      <translation>Analisando {id}</translation>
    </message>
    <message id="insufficient_coverage">
      <source>Insufficient spatial coverage</source>
      <translation>Cobertura espacial insuficiente</translation>
    </message>
    <message id="scene_rejected_coverage">
      <source>{id}: {value:.4f}% spatial coverage — rejected</source>
      <translation>{id}: {value:.4f}% de cobertura espacial — rejeitada</translation>
    </message>
    <message id="accepted">
      <source>Scene accepted: {id}</source>
      <translation>Cena aprovada: {id}</translation>
    </message>
    <message id="potential_cloud_high">
      <source>Potential cloudiness above threshold</source>
      <translation>Nebulosidade potencial acima do limite</translation>
    </message>
    <message id="scene_rejected_cloud">
      <source>{id}: {value:.4f}% potential cloudiness — rejected</source>
      <translation>{id}: {value:.4f}% de nebulosidade potencial — rejeitada</translation>
    </message>
    <message id="not_evaluated">
      <source>Scene not evaluated: {reason}</source>
      <translation>Cena não avaliada: {reason}</translation>
    </message>
    <message id="coverage_tif_missing">
      <source>No coverage GeoTIFF asset for this scene</source>
      <translation>Produto sem GeoTIFF de cobertura</translation>
    </message>
    <message id="matching_l4_missing">
      <source>No corresponding Level-4 acquisition</source>
      <translation>Não há produto Level-4 correspondente à passagem</translation>
    </message>
    <message id="l4_bands_missing">
      <source>Missing Level-4 bands B1/B2/B3/B4</source>
      <translation>Bandas Level-4 B1/B2/B3/B4 não encontradas</translation>
    </message>
    <message id="l4_nodata">
      <source>No valid Level-4 multispectral pixels in the AOI</source>
      <translation>Nenhum pixel multiespectral Level-4 válido na AOI</translation>
    </message>
    <message id="l4_incomplete">
      <source>Level-4 data cover only {value:.2f}% of the AOI; cloud screening would be incomplete</source>
      <translation>O produto Level-4 cobre apenas {value:.2f}% da AOI; a análise de nuvens seria incompleta</translation>
    </message>
    <message id="id_unknown">
      <source>Unrecognized CBERS date/orbit/point in item ID</source>
      <translation>ID CBERS sem data/órbita/ponto reconhecidos</translation>
    </message>
    <message id="no_aoi_pixels">
      <source>No grid pixels fall inside the AOI</source>
      <translation>Nenhum pixel da grade está contido na AOI</translation>
    </message>
    <message id="grid_invalid">
      <source>The AOI does not produce a valid metric grid</source>
      <translation>A área de interesse não gerou uma grade métrica válida</translation>
    </message>
    <message id="grid_too_large">
      <source>The grid requires {count:,} pixels (limit: {limit:,}). Reduce the AOI or use the 8 m product.</source>
      <translation>A grade exige {count:,} pixels (limite: {limit:,}). Reduza a AOI ou utilize o produto de 8 m.</translation>
    </message>
    <message id="gdal_open_fail">
      <source>Cannot open the remote GeoTIFF: {url}</source>
      <translation>Não foi possível abrir o GeoTIFF remoto: {url}</translation>
    </message>
    <message id="gdal_warp_fail">
      <source>Could not align the image to the AOI grid</source>
      <translation>Não foi possível alinhar a imagem à grade da AOI</translation>
    </message>
    <message id="fused_missing">
      <source>The fused product has no accessible GeoTIFF</source>
      <translation>O produto fusionado não contém GeoTIFF acessível</translation>
    </message>
    <message id="l4_missing">
      <source>Corresponding Level-4 product was not identified</source>
      <translation>O produto Level-4 correspondente não foi identificado</translation>
    </message>
    <message id="rgb_missing">
      <source>The Level-4 product has no usable RGB bands</source>
      <translation>O produto Level-4 não contém as bandas RGB necessárias</translation>
    </message>
    <message id="vrt_fail">
      <source>Could not build the RGB VRT</source>
      <translation>Não foi possível construir o VRT RGB</translation>
    </message>
    <message id="layer_invalid">
      <source>The selected raster cannot be opened in QGIS</source>
      <translation>O raster selecionado não pôde ser aberto no QGIS</translation>
    </message>
    <message id="stac_error">
      <source>STAC request failed: {message}</source>
      <translation>Falha na consulta STAC: {message}</translation>
    </message>
    <message id="stac_http">
      <source>STAC returned HTTP {status}</source>
      <translation>STAC retornou HTTP {status}</translation>
    </message>
    <message id="stac_json">
      <source>STAC response is not valid JSON</source>
      <translation>Resposta STAC não é um JSON válido</translation>
    </message>
    <message id="stac_host">
      <source>STAC pagination URL is outside the INPE catalog</source>
      <translation>URL de paginação STAC fora do catálogo INPE</translation>
    </message>
    <message id="stac_pagination_loop">
      <source>STAC pagination contains a repeated page</source>
      <translation>A paginação STAC retornou uma página repetida</translation>
    </message>
    <message id="stac_bad_method">
      <source>Unsupported STAC pagination method: {method}</source>
      <translation>Método de paginação STAC não suportado: {method}</translation>
    </message>
    <message id="stac_too_many">
      <source>STAC returned too many pages; refine the AOI</source>
      <translation>O STAC retornou páginas demais; reduza a área de interesse</translation>
    </message>
    <message id="stac_bad_response">
      <source>STAC response does not contain a valid feature list</source>
      <translation>A resposta STAC não contém uma lista válida de cenas</translation>
    </message>
    <message id="error_canceled">
      <source>Search canceled by the user</source>
      <translation>Busca cancelada pelo usuário</translation>
    </message>
  </context>
</TS>