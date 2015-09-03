import math
from boatd_client import Boat

radiusOfEarth = 3963.1676 #this is the raduis of the earth in miles, approxamatly
# number of miles per degree is (pi/180)*raduisOfEarth*math.cos("lattitude")
numOfMilesInADegree = 60.0405

# Very simple, downwind, "try to face right direction" program - working on XTE and tacking seperately

# This file uses plane sailing, which is fine for short distances.
# If we implement great circle sailing, the great circle could be divided
# into a series of straight lines and the same ideas can be used

boat = Boat()

class Line(object): # a plane sailing line between two points. works out the bearing and distance between them
	def __init__(self, a, b): # takes two sets of co-ordinates in tuples
		self.pointA = a
		self.pointB = b
		self.latA = self.pointA[0]
		self.latB = self.pointB[0]
		self.longA = self.pointA[1]
		self.longB = self.pointB[1]
		
		print("POSITION:")
		print(a)
		print("WAYPOINT:")
		print(b)
		
		self.dLong = self.longB - self.longA
		self.dLat = self.latB - self.latA
		self.mLat = self.latA + self.dLat/2
		self.departure = self.dLong*math.cos(math.radians(self.mLat))
		
		# give the angle, theta, in radians between pointA, north, and pointB. Positive values are east from north, negative is west.
		self.theta = math.atan2(self.departure,self.dLat)
		
		# convert theta to a 360 degree bearing
		if self.dLong >= 0:
			self.bearing = math.degrees(self.theta)
		else:
			self.bearing = 360 + math.degrees(self.theta)
			
		if self.dLong != 0:
			self.distance = (self.departure/math.sin(self.theta))*numOfMilesInADegree
		else:
			self.distance = self.dLat*numOfMilesInADegree
			
	def getBearing(self): # returns 360 degree bearing between start and endpoint
		return self.bearing
		
	def getDistance(self): # returns length of line in Nautical Miles
		return self.distance

class SimplePilot(object):
	def __init__(self, waypointList, maxRudder, headingbMargin, waypointError):
		self.waypoints = waypointList
		self.maxRudder = maxRudder
		self.headingMargin = headingMargin
		self.waypointError = waypointError
		
	def setSail(self, windDir): # these values come from tracksail-ai
		if windDir < 180:
			if windDir < 70:
				newSailAngle = 0
			elif windDir < 80:
				newSailAngle = 18
			elif windDir < 90:
				newSailAngle = 36
			elif windDir < 110:
				newSailAngle = 54
			else:
				newSailAngle = 72
		else:
			if windDir >= 290:
				newSailAngle = 0
			elif windDir >= 280:
				newSailAngle = 342
			elif windDir >= 270:
				newSailAngle = 324
			elif windDir >= 250:
				newSailAngle = 306
			else:
				newSailAngle = 288
				
		boat.sail(newSailAngle)
	
	def compareDirections(self, a, b): # returns difference (-180 to +180) between two directiobns.
		difference = b - a
		if abs(difference) > 180:
			if difference < 0:
				difference += 360
			else:
				difference -= 360
		return difference
		
	def withinMarginCheck(self, difference, margin): # returns False if difference in directions is larger than the margin
		return abs(difference) < margin
		
	def turn(self, bearingDifference): # A PI CONTROLLER MIGHT BE BETTER FOR THIS
		newRudderAngle = bearingDifference/90 * self.maxRudder # interpolates so that rudder angle is greatest when the heading/bearing difference is 90+
		if newRudderAngle > self.maxRudder:
			newRudderAngle = self.maxRudder
		elif newRudderAngle < -1*self.maxRudder:
			newRudderAngle = -1*self.maxRudder
		boat.rudder(newRudderAngle)
		
	def go(self):
		print(boat.wind)
		waypointIndex = 0
		print self.waypoints
		while True:
			currentWaypoint = self.waypoints[waypointIndex]
			position = boat.position
			
			fixedLat = position[0].encode('ascii','ignore').strip("'x\\0\0") # a load of baloney to sort out the position form boatd
			fixedLong = position[1].encode('ascii','ignore').strip("'x\\0\0")
			fixedPosition = (float(fixedLat),float(fixedLong))
			position = fixedPosition
	
			
			line = Line(position, currentWaypoint)
			if line.getDistance() < self.waypointError: # checks if we have reached waypoint. DISTANCE CURRENTLY IN NM
				waypointIndex += 1
				continue
			
			self.setSail(boat.wind)
			
			bearingDifference = self.compareDirections(boat.heading, line.getBearing())
			if bearingDifference > self.headingMargin:
				self.turn(bearingDifference)


pilot = SimplePilot([(52.394092609521316, -4.102116831945741)
,(52.394092609521316, -4.0)
],45, 5, 0.0001)
pilot.go()
