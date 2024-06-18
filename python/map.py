

from geopy.distance import distance as geopy_distance
import math

YEAR = 2024 # Important: Man moves, so you need to check the latest

GOLDEN_STAKE = (40.786400, -119.203500)
ELEVATION = 3904

manToTempleInFeet = 2500 # not in the measurements, number is taken from 2023 official printed BRC map
templeRadiusInFeet = 200 # not in the measurements, number is taken from 2023 official printed BRC map
manRadiusInFeet = 400 # not in the measurements, number is taken from 2023 official printed BRC map

fencePoints = [
    (40.782814, -119.233566),
    (40.807028, -119.217274),
    (40.802722, -119.181931),
    (40.775857, -119.176407),
    (40.763558, -119.208301)
]
greetersGap = (40.773203, -119.220953)

HOUR_DEGREE = 30
MINUTE_DEGREE = .5

# True North/South follows the 4:30 axis
southHour = 4
southMinute = 30
midnightBearing = 180 - (southHour * HOUR_DEGREE + southMinute * MINUTE_DEGREE)

# Promenades are 40’ wide on the 3:00/9:00 and 6:00/12:00 axis, with lantern spires approximately every 150’.
promenadeWidthInFeet = 40


"""
The center of the first road “Esplanade” is 2,500’ from the Man. Esplanade to Afanc block is
400’ deep, then blocks Afanc through Igopogo are 250’ deep. Blocks Igopogo through Kraken
are 150’ deep. Mid-city double blocks between Encantado and Frogbat are 450’ deep.
Measured to the road center, the outer road Kraken is 11,690’ in diameter.
"""
distanceToEsplanadeInFeet = 2500
depthEsplanadeToAInFeet = 400  # Esplanade to A
depthAtoIInFeet = 250  # standard streets
depthItoKInFeet = 150  # outer streets
depthEtoFInFeet = 450  # double block
diameterKInFeet = 11690


"""
All streets, radial and annular, are 40’ wide, except Kraken, which is 50’ wide.
Pedestrian and bicycle Community Paths are between Frogbat and Kraken at
3:45, 4:15, 4:45, 5:15, 6:45, 7:15, 7:45, and 8:15 are 15 feet wide.
"""
streetWidthInFeet = 40
outerStreetWidthInFeet = 50
quaterHourStreetWidthinFeet = 15

quaterHourStreetsStartAt = 'f'

streetDepths = {
    'esplanade': distanceToEsplanadeInFeet,
    'a': depthEsplanadeToAInFeet,
    'b': depthAtoIInFeet,
    'c': depthAtoIInFeet,
    'd': depthAtoIInFeet,
    'e': depthAtoIInFeet,
    'f': depthEtoFInFeet,
    'g': depthAtoIInFeet,
    'h': depthAtoIInFeet,
    'i': depthAtoIInFeet,
    'j': depthItoKInFeet,
    'k': depthItoKInFeet
}
lastStreet = 'k'

# A quick pass to create distance from man for each street
distanceToStreetCenter = {}
cumulative_distance = 0

streetDepths['esplanade'] -= streetWidthInFeet
for street, depth in streetDepths.items():
    cumulative_distance += depth + streetWidthInFeet
    distanceToStreetCenter[street] = cumulative_distance
streetDepths['esplanade'] += streetWidthInFeet

distanceToStreetCenter['k'] += (outerStreetWidthInFeet - streetWidthInFeet) / 2

assert distanceToStreetCenter['k'] * 2 == diameterKInFeet, "Street width calculations do not match defined K street diameter"

"""
Man to the center of Center Camp = 3,026’
Center Camp theme camp area radius: 320’ to inside and 763’ to outside
(783’ radius to the center of the Rod’s Ring Road)
"""
manToCenterOfCenterCampInFeet = 3026

centerCampRadiusInsideInFeet = 320  # canopy
centerCampRadiusOutsideInFeet = 763
centerCampRadiusToRodsRingInFeet = 783

centerCampStreetCrossRadius = 1 # some default setting
centerCampOuterRadius = centerCampRadiusToRodsRingInFeet # outer radius of center camp that look into playa

# defining the center camp circle road that breaks letter streets:
if YEAR == 2023:
    centerCampStreetName = "Rod’s Ring Road"  
    centerCampStreetCrossRadius = centerCampRadiusToRodsRingInFeet 
if YEAR == 2024:
    centerCampStreetName = "Center Camp"  
    centerCampStreetCrossRadius = centerCampRadiusInsideInFeet # 2024

        

"""
There are five plaza portals to the Esplanade: at 6:00 (Center Camp), 3:00, 4:30, 7:30, and
9:00. The Esplanade mouth of the portal at Center Camp is 317’
"""
portalMouthInFeet = 317

def bearing(hours, minutes):
    result =  midnightBearing + hours * HOUR_DEGREE + minutes * MINUTE_DEGREE
    if result < 0:
        result += 360
    if result > 360:
        result -= 360
    return result

def letterToDistance(letter):
    return distanceToStreetCenter[letter.lower()]

"""
Plazas are at 3:00, 4:30, 7:30 and 9:00 and Bigfoot, centered 3230’ from the Man. A ring
of mid-city plazas at 3:00, 4:30, 6:00, 7:30, and 9:00 are at Grootslang, centered 4,880’
from the Man.
"""
plazaToManInFeet = 4880
plazaWidth = 5 * streetWidthInFeet # magical number

plazaOuterWidth = 0 # defines circles around plazas on the map
plazaOuterWidth6 = 2*(depthAtoIInFeet + streetWidthInFeet) # plaza behind center camp

if YEAR == 2023: # in 2023, circles were around each plaza
    plazaOuterWidth = plazaOuterWidth6

# TODO: create formatName function and use it here to name plazas
plazas = [
    (3, 00, letterToDistance('b'), plazaWidth, plazaOuterWidth, "3:00 & B Plaza"),
    (4, 30, letterToDistance('b'), plazaWidth, plazaOuterWidth, "4:30 & B Plaza"),
    (7, 30, letterToDistance('b'), plazaWidth, plazaOuterWidth, "7:30 & B Plaza"),
    (9, 00, letterToDistance('b'), plazaWidth, plazaOuterWidth, "9:00 & B Plaza"),

    (3, 00, letterToDistance('g'), plazaWidth, plazaOuterWidth, "3:00 & G Plaza"),
    (4, 30, letterToDistance('g'), plazaWidth, plazaOuterWidth, "4:30 & G Plaza"),
    (6, 00, letterToDistance('g'), plazaWidth, plazaOuterWidth6, "6:00 & G Plaza"),
    (7, 30, letterToDistance('g'), plazaWidth, plazaOuterWidth, "7:30 & G Plaza"),
    (9, 00, letterToDistance('g'), plazaWidth, plazaOuterWidth, "9:00 & G Plaza"),
]

### WHERE IS TEMPLE?

"""
Later: center camp coordinates, art coordinates (time and distance), camp orientation (leverage street widths)
"""

# before calling view functions, convert Points to simple lists 
def point_to_list(point):
    return [point[0], point[1]]

"""
number of helpful functions to calculate coordinates based on stuff
"""
def distanceBearingFromCenter(distance, bearing, center):
    return point_to_list(geopy_distance(feet = distance).destination(center, bearing = bearing))
def distanceBearingToCoordinate(distance, bearing):
    return distanceBearingFromCenter(distance, bearing, GOLDEN_STAKE)
def distanceToCoordinate(distance, hours, minutes):
    return distanceBearingToCoordinate(distance, bearing(hours, minutes))
def addressToCoordinate(letter, hours, minutes):
    return distanceToCoordinate(letterToDistance(letter), hours, minutes)
def letterBearingToCoordinate(letter, bearing):
    return distanceBearingToCoordinate(letterToDistance(letter), bearing)


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

def renderTrashFence(addLine):
    lastPoint = fencePoints[-1]
    for point in fencePoints:
        addLine(lastPoint, point, "Trash Fence")
        lastPoint = point

    
def renderMap(addArch, addLine, addCircle, addMan, addTemple):
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
    renderTrashFence(addLine)
   