# -*- coding: utf-8 -*-
# Copyright (C) 2017-2021 Davide Gessa
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
from .router import *

class LinearBestIsoRouter (Router):
	PARAMS = {
		'minIncrease': RouterParam('minIncrease', 'Minimum increase (nm)', 'float', 'Set the minimum value for selecting a new valid point', default=10.0, lower=1.0, upper=100.0, step=0.1, digits=1)
	}

	def route (self, lastlog, time, start, end):
		if lastlog != None and len (lastlog.isochrones) > 0:
			isoc = self.calculateIsochrones (time + datetime.timedelta(hours=1), lastlog.isochrones, end)
		else:
			isoc = self.calculateIsochrones (time + datetime.timedelta(hours=1), [[(start[0], start[1], time)]], end)

		position = start
		path = []
		for p in isoc[-1]:
			(twd,tws) = self.grib.getWindAt (time + datetime.timedelta(hours=1), p[0], p[1])
			maxReachDistance, maxspeed = self.polar.maxReachDistance(p, twd, tws)
			if utils.pointDistance (end[0],end[1], p[0], p[1]) < maxReachDistance*1.1:
				print ("LinearBestIsoRouter",utils.pointDistance (end[0],end[1], p[0], p[1]), time + datetime.timedelta(hours=1),maxspeed, maxReachDistance, twd, tws)
				if self.pointValidity or self.lineValidity(end[0],end[1], p[0], p[1]):
					path.append (p)
					for iso in isoc[::-1][1::]:
						path.append (iso[path[-1][2]])

					path = path[::-1]
					position = path[-1]
					break

		return RoutingResult(time=time + datetime.timedelta(hours=1), path=path, position=position, isochrones=isoc)
