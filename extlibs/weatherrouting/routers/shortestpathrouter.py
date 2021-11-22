# -*- coding: utf-8 -*-
# Copyright (C) 2017-2021 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
# Copyright (C) 2012 Riccardo Apolloni
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For detail about GNU see <http://www.gnu.org/licenses/>.
'''

import datetime
from .. import utils
from .linearbestisorouter import *

class ShortestPathRouter (LinearBestIsoRouter):
	PARAMS = {
		'minIncrease': RouterParam('minIncrease', 'Minimum increase (nm)', 'float', 'Set the minimum value for selecting a new valid point', default=10.0, lower=1.0, upper=100.0, step=0.1, digits=1),
		'fixedSpeed': RouterParam('fixedSpeed', 'Fixed speed (kn)', 'float', 'Set the fixed speed', default=5.0, lower=1.0, upper=60.0, step=0.1, digits=1)
	}

	def route (self, lastlog, time, start, end) -> RoutingResult:
		return self._route(lastlog, time, start, end, lambda time, isoc, end: self.calculateShortestPathIsochrones (self.getParamValue('fixedSpeed'), time, isoc, end))
