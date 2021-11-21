# Wind forecast routing
The plugin is based on [libweatherrouting routing library](https://github.com/dakk/libweatherrouting/) ©2021 Davide Gessa, Riccardo Apolloni, Enrico Ferreguti

## For newbies

* install QGIS following instructions in https://www.qgis.org/en/site/forusers/download.html
* optionally load your map or a base map from ``QGIS>Browser>XYZ Tiles>OpenStreetMap``
* zoom to your area of interest

## The plugin itself

Install the plugin from ``Plugins > Manage and install plugins`` menu; search for it and click on ``Install``.
The plugin will be shown under ``Plugins`` menu: ``Wind forecast routing``.
To generate an optimal route you just need to activate the plugin, choose the parameters, and press ``Run``. The plugin will download the wind model cosen for the area of interest, and will calculate the fastes track.
Please double check that:
* your start and end point fall outside land masses; currently the plugin uses a rough coastline (natural earth `ne_10m_ocean`, you can find it in the plugin source directory)
* if your layer is not shown, deactivate the time panel.

Please report any issue on the bugrtracker.
