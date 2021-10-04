# Wind forecast routing
The plugin is based on [libweatherrouting routing library](https://github.com/dakk/libweatherrouting/) ©2021 Davide Gessa, Riccardo Apolloni, Enrico Ferreguti

## For newbies

* install QGIS following instructions in https://www.qgis.org/en/site/forusers/download.html
* optionally load your map or a base map from ``QGIS>Browser>XYZ Tiles>OpenStreetMap``
* zoom to your area of interest

## The plugin itself

For the time being the plugin is installed manually, by downloading the zip from: https://github.com/enricofer/wind_forecast_routing/archive/refs/heads/master.zip (soon it will be published in the official repository of QGIS, therefore it will be installed via ``Plugins>Manage and install plugins``, then search and click on ``Install``).
The plugin will be shown under ``Processing`` tab.
To generate an optimal route:
* download a GRIB file, e.g. using https://plugins.qgis.org/plugins/gribdownloader/
 * suggested parameters: model from `ICON_EU`, interval 1 (1 hour), period 5
 * better if you dowload only the needed layer (wind)
* check that the GRIB has the correct projection (EPSG:4326); if not, assign it by hand
* if you downloaded only wind, the param `Wind Grib Dataset index` should be set at 0; if not, please check which one contains the wind, using `Layer>Properties>Source>Datasets` (the first one has index 0
* if your layer is not shown, deactivate the time panel
* doble check that your start and end point fall outside land masses; currently the plugin uses a rough coastline (natural earth `ne_10m_ocean`, you can find it in the plugin source directory)
