
import math
from coordinates import *

### WHERE IS TEMPLE?

# function defines plaza/circle width
def abAngleInTriangle(streetDistance, plazaDistance, plazaRadius):
    # cos theorem:
    # (plazaWidth/2)^2 = plazaDistance^2 + streetDistance^2 - 2*plazaDistance*streetDistance* cos (alpha)
    if plazaRadius <= abs(streetDistance - plazaDistance):
        return None  # no crossing
    return math.degrees(math.acos(-(plazaRadius ** 2 - plazaDistance ** 2 - streetDistance ** 2) / (2 * plazaDistance * streetDistance)))

"""
Letter streets are arches

breakForPlazas = true also forces breakForCenterCamp
"""
def generateLetterStreet(letter, addArch, breakForPlazas=True, breakForCenterCamp=None):
    letter = letter.lower()
    archRadius = letterToDistance(letter)

    archAngles = [bearing(2, 00)]
    if breakForPlazas:
        breakForCenterCamp = True # force
        # find angle at which plazas cross the street
        for (hour, minute, distance, width, outerWidth, name) in plazas:
            angle = abAngleInTriangle(archRadius, distance, width / 2)
            if angle is None: # does not cross
                continue 
            plazaCenter = bearing(hour, minute)
            archAngles.append(plazaCenter - angle)
            archAngles.append(plazaCenter + angle)

    if breakForCenterCamp: # here we will check if street breaks for center camp
        if letter=='esplanade': # special treatment - outer circle of center camp
            angle = abAngleInTriangle(archRadius, manToCenterOfCenterCampInFeet, centerCampOuterRadius)
        else:
            angle = abAngleInTriangle(archRadius, manToCenterOfCenterCampInFeet, centerCampStreetCrossRadius)

        if not angle is None:
            centerCampBearing = bearing(6, 00)
            archAngles.append(centerCampBearing - angle)
            archAngles.append(centerCampBearing + angle)

    archAngles.append(bearing(10, 00))

    prevAngle = None
    for currentAngle in sorted(archAngles):
        if prevAngle is None:
            prevAngle = currentAngle
            continue
        addArch(prevAngle, currentAngle, archRadius, GOLDEN_STAKE, letter)
        prevAngle = None

def generateLetterStreets(addArch):
    for key in streetDepths:
        generateLetterStreet(key, addArch)

def generateRadialStreet(streetHour, streetMinute, addLine, breakForPlazas=True, breakForCenterCamp=None):
    shortStreet =  streetMinute % 30 == 15
    startAt = "esplanade" if not shortStreet else quaterHourStreetsStartAt

    linePoints = [addressToCoordinate(startAt, streetHour, streetMinute)]

    if breakForPlazas: 
        breakForCenterCamp = True;
     
    if breakForCenterCamp and not shortStreet:
        angle = abAngleInTriangle(manToCenterOfCenterCampInFeet, manToCenterOfCenterCampInFeet, centerCampStreetCrossRadius)
        if abs(bearing(streetHour, streetMinute) - bearing(6,00)) < angle: # check if street crosses the circle
            linePoints = [ distanceToCoordinate (manToCenterOfCenterCampInFeet + centerCampStreetCrossRadius, streetHour, streetMinute) ]
      
    if breakForPlazas:
        # find angle at which plazas cross the street
        for (hour, minute, distance, width, outerWidth, name) in plazas:
            if (streetHour != hour) or (streetMinute != minute):
                continue

            # plaza is on this street
            # move the point to the golden spike by width/2
            # then move it out by width/2

            linePoints.append( distanceToCoordinate (distance-width/2,hour, minute))
            linePoints.append( distanceToCoordinate (distance+width/2,hour, minute))


   
    linePoints.append(addressToCoordinate(lastStreet, streetHour, streetMinute))


    name = f"{streetHour:02}:{streetMinute:02}"
    start = None
    for end in linePoints:
        if start is None:
            start = end
            continue 
        addLine(start, end, name)
        start = None
    pass

def generateRadialStreets(addLine):
    firstStreetTime = 2*60
    lastStreetTime = 10*60
    streetStep = 15

    currentStreetTime = firstStreetTime
    while currentStreetTime <= lastStreetTime:
        generateRadialStreet(math.floor(currentStreetTime/60), currentStreetTime%60, addLine)
        currentStreetTime += streetStep

# this function will place hour labels. It will also place the 12 hour mark above man, so the renderer needs to decide what to do with it
def generateRadialStreetNames(addHourLabel, extendByFeet=0):

    firstStreetTime = 2*60
    lastStreetTime = 10*60
    streetStep = 15

    currentStreetTime = firstStreetTime

    radialStreetNameDistance = diameterKInFeet/2 + extendByFeet

    while currentStreetTime <= lastStreetTime:
        hour = math.floor(currentStreetTime/60)
        minute = currentStreetTime%60
        rotation = bearing(hour, minute)
        coordinate = distanceBearingToCoordinate(radialStreetNameDistance, rotation)
        addHourLabel(hour, minute, coordinate, rotation)
        currentStreetTime += streetStep

    rotation = bearing(12, 0)
    coordinate = distanceBearingToCoordinate(radialStreetNameDistance, rotation)
    addHourLabel(12, 0, coordinate, rotation)




def generatePlazas(addCircle):
    for (hour, minute, distance, width, outerWidth, name) in plazas:
        center = distanceToCoordinate(distance, hour, minute)
        addCircle(center, width, name)
        if outerWidth:
            addCircle(center, outerWidth, name)

def generateCenterCamp(addLine, addArch, addCircle):

    center = distanceToCoordinate(manToCenterOfCenterCampInFeet, 6, 00)
    addCircle(center, centerCampRadiusInsideInFeet*2, "Center Camp") # so far seems to be constant

    if YEAR == 2024:
        angle = abAngleInTriangle(centerCampOuterRadius, manToCenterOfCenterCampInFeet, letterToDistance('a'))
        addArch(midnightBearing-angle, midnightBearing+angle, centerCampOuterRadius,  center, "Center Camp")

        addLine(distanceToCoordinate(manToCenterOfCenterCampInFeet - centerCampRadiusInsideInFeet,6,00), 
                distanceToCoordinate(manToCenterOfCenterCampInFeet - centerCampOuterRadius,6,00), 
                "Center Camp")
        return
    
    if YEAR == 2023:
        addCircle(center, centerCampOuterRadius*2, centerCampStreetName)

        addLine(distanceToCoordinate(manToCenterOfCenterCampInFeet + centerCampRadiusInsideInFeet,6,00), 
                distanceToCoordinate(manToCenterOfCenterCampInFeet + centerCampOuterRadius,6,00), 
                "Center Camp")
        
        magicalAngle = 150/2 # something approximate, I wasn't able to find it in the spec
        addLine(addressToCoordinate('a', 6, 30), 
                distanceBearingFromCenter(centerCampRadiusInsideInFeet, midnightBearing + 360-magicalAngle, center),
                "Center Camp")
        addLine(addressToCoordinate('a', 5, 30), 
                distanceBearingFromCenter(centerCampRadiusInsideInFeet, midnightBearing + magicalAngle, center),
                "Center Camp")
        return
    

def renderPromenades(addLine):
    addLine( 
        distanceToCoordinate(manToCenterOfCenterCampInFeet - centerCampOuterRadius, 6, 00),
        distanceToCoordinate(manRadiusInFeet, 6, 00),
        "6:00 Promenade"
    )
    addLine( 
        addressToCoordinate('esplanade', 3, 00),
        distanceToCoordinate(manRadiusInFeet, 3, 00),
        "3:00 Promenade"
    )
    addLine( 
        addressToCoordinate('esplanade', 9, 00),
        distanceToCoordinate(manRadiusInFeet, 9, 00),
        "9:00 Promenade"
    )
    addLine( 
        distanceToCoordinate(manToTempleInFeet - templeRadiusInFeet, 12, 00),
        distanceToCoordinate(manRadiusInFeet, 12, 00),
        "12:00 Promenade"
    )
    

def renderManAndTemple(renderMan, renderTemple):
    ### renderMan, renderTemple are compatible with renderCircle
    renderMan(GOLDEN_STAKE, manRadiusInFeet*2, "Man")
    renderTemple(distanceToCoordinate(manToTempleInFeet, 12, 00), templeRadiusInFeet*2, "Temple")

def renderAirport(addAirport):
    addAirport(AIRPORT_COORDINATES, airportWidth, "airport") 

def renderTrashFence(addLine):
    lastPoint = fencePoints[-1]
    for point in fencePoints:
        addLine(lastPoint, point, "Trash Fence")
        lastPoint = point

    
def renderMap(addArch, addLine, addFenceLine, addCircle, addMan, addTemple, addHourLabel = None, addAirport = 0, extendRadialNamesByBlocks = 0):
    """ Missing elements:
    Portals
    Airport
    Greeters
    """
    generateLetterStreets(addArch)
    generateRadialStreets(addLine)
    generatePlazas(addCircle)
    generateCenterCamp(addLine, addArch, addCircle)
    renderPromenades(addLine)
    renderManAndTemple(addMan,addTemple) 
    if not addAirport is None:
        renderAirport(addAirport)
    renderTrashFence(addFenceLine)
    if not addHourLabel is None:
        generateRadialStreetNames(addHourLabel, extendRadialNamesByBlocks * depthAtoIInFeet)
   