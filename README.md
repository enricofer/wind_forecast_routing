# Wind forecast routing

To generate an optimal route:
* download a GRIB file, e.g. using https://plugins.qgis.org/plugins/gribdownloader/
 * suggested parameters: model from `ICON_EU`, interval 1 (1 hour), period 5
 * better if you dowload only the needed layer (wind)
* check that the GRIB has the correct projection (EPSG:4326); if not, assign it by hand
* if you downloaded only wind, the param `Wind Grib Dataset index` should be set at 0; if not, please check which one contains the wind, using `Layer>Properties>Source>Datasets` (the first one has index 0
* if your layer is not shown, deactivate the time panel
* doble check that your start and end point fall outside land masses; currently the plugin uses a rough coastline (natural earth `ne_10m_ocean`, you can find it in the plugin source directory)
