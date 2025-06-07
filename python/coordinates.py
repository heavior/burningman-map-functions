# source: https://github.com/heavior/burningman-map-functions
# don't forget to push changes there as well!

from geopy.distance import distance as geopy_distance
import re
import math

YEAR = 2024 # Important: Man moves, so you need to check the latest

GOLDEN_STAKE = (40.78695, -119.20409)
ELEVATION = 3904

manToTempleInFeet = 2500 # not in the measurements, number is taken from 2023 official printed BRC map
templeRadiusInFeet = 200 # not in the measurements, number is taken from 2023 official printed BRC map
manRadiusInFeet = 400 # not in the measurements, number is taken from 2023 official printed BRC map

fencePoints = [
    (40.783385, -119.233837),
    (40.807359, -119.217774),
    (40.803149, -119.182806),
    (40.776576, -119.177278),
    (40.764366, -119.208810)
]
greetersGap = (40.773876, -119.221322) # not used anywhere in this script

AIRPORT_COORDINATES = (40.76707, -119.20906)

HOUR_DEGREE = 30
MINUTE_DEGREE = .5

# True North/South follows the 4:30 axis
southHour = 4
southMinute = 30
midnightBearing = 180 - (southHour * HOUR_DEGREE + southMinute * MINUTE_DEGREE)

# Promenades are 40’ wide on the 3:00/9:00 and 6:00/12:00 axis, with lantern spires approximately every 150’.
promenadeWidthInFeet = 40

"""
Later: center camp coordinates, art coordinates (time and distance), camp orientation (leverage street widths)
"""



"""
The center of the first road “Esplanade” is 2,500’ from the Man. Esplanade to Agog block is
400’ deep, blocks Agog through Intrigue are 250’ deep. Blocks Intrigue through Kelter are
150’ deep. Mid-city double blocks between Enchant and Fascinate are 450’ deep. Measured
to the road center, the outer road Kelter is 11,490’ in diameter.
"""
distanceToEsplanadeInFeet = 2500
depthEsplanadeToAInFeet = 400  # Esplanade to A
depthAtoIInFeet = 250  # standard streets
depthItoKInFeet = 150  # outer streets
depthEtoFInFeet = 450  # double block
diameterKInFeet = 11490

"""
The radial avenues 2:30, 3:00, 4:30, 5:30, 6:00, 6:30, 7:30, 9:00, and 9:30 are 40 feet wide.
All annular streets are 30 feet wide except Esplanade, at 40 feet, and Kelter, at 50 feet.
Pedestrian and bicycle Community Paths are between Facinate and Kelter at
3:45, 4:15, 4:45, 5:15, 6:45, 7:15, 7:45, and 8:15 are 15 feet wide.
"""
radialAvenueWidthInFeet = 40 # The radial avenues 2:30, 3:00, 4:30, 5:30, 6:00, 6:30, 7:30, 9:00, and 9:30 are 40 feet wide.
annularStreetWidthInFeet = 30 # All annular streets are 30 feet wide except
esplanadeWidthInFeet = 40 # Esplanade, at 40 feet, and 

# streetWidthInFeet = 40
outerStreetWidthInFeet = 50  # Kelter, at 50 feet. 
quaterHourStreetWidthinFeet = 15 # 3:45, 4:15, 4:45, 5:15, 6:45, 7:15, 7:45, and 8:15 are 15 feet wide.

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

streetDepths['esplanade'] -= annularStreetWidthInFeet - (esplanadeWidthInFeet - annularStreetWidthInFeet)/2
for street, depth in streetDepths.items():
    cumulative_distance += depth + annularStreetWidthInFeet
    distanceToStreetCenter[street] = cumulative_distance
streetDepths['esplanade'] += annularStreetWidthInFeet
distanceToStreetCenter['esplanade'] -= (esplanadeWidthInFeet - annularStreetWidthInFeet)/2

distanceToStreetCenter['k'] += (outerStreetWidthInFeet-annularStreetWidthInFeet)/2

assert distanceToStreetCenter['k'] * 2 == diameterKInFeet, f"Street width calculations do not match defined K street diameter {distanceToStreetCenter['k'] * 2} vs {diameterKInFeet}"

"""
Man to the center of Central Canopy = 2,999’

????? Center Camp theme camp area radius: 320’ to inside and 763’ to outside
????? (783’ radius to the center of the Rod’s Ring Road)
"""
manToCenterOfCenterCampInFeet = 2999

centerCampRadiusInsideInFeet = 250 # eyeballing based on PDF map, NO OFFICIAL DATA YET

# centerCampRadiusOutsideInFeet = 763
# centerCampRadiusToRodsRingInFeet = 783

centerCampRadiusOutsideInFeet = math.sqrt(
    manToCenterOfCenterCampInFeet*manToCenterOfCenterCampInFeet + distanceToStreetCenter['a']*distanceToStreetCenter['a']
    - 2*manToCenterOfCenterCampInFeet * distanceToStreetCenter['a']*math.cos(math.radians(MINUTE_DEGREE * 30)))

centerCampRadiusToRodsRingInFeet = centerCampRadiusOutsideInFeet


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
9:00. The Esplanade mouth of the portal at Center Camp is 210’
"""
portalMouthInFeet = 210 # not used, I think

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
Plazas are at 3:00, 4:30, 7:30 and 9:00 and Baffle, centered 3215’ from the Man. A ring
of mid-city plazas at 3:00, 4:30, 6:00, 7:30, and 9:00 are at Gobsmack, centered 4,815’
from the Man.

"""
innerPlazaToManInFeet = 3215 # Not used, using center of intersection to render plazas
outerPlazaToManInFeet = 4815 # Not used, using center of intersection to render plazas
plazaWidth = 5 * radialAvenueWidthInFeet # magical number

plazaOuterWidth = 0 # defines circles around plazas on the map
plazaOuterWidth6 = 2*(depthAtoIInFeet + annularStreetWidthInFeet) # plaza behind center camp - magical number

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

def parseHoursMinutes(s):
    if s is None:
        raise ValueError(f"None value for parsing time")
    
     # Split the string by ':'
    parts = s.split(':')
    
    # Check if the string was split into exactly two parts
    if len(parts) != 2:
        raise ValueError(f"String format is incorrect: {s}")
    
    try:
        # Convert the parts to integers
        num1 = int(parts[0])
        num2 = int(parts[1])
    except ValueError:
        # Raise an exception if conversion to integers fails
        raise ValueError(f"String contains non-numeric parts: {s}")
    
    return num1, num2


def parsePlazaAddress(s):
    # Define the regex pattern to match the expected format

    if 'Center Camp Plaza' in s:
        return 6, 0, 'A'

    pattern = r"(\d+):(\d+)\s+([A-Z])\s+Plaza"
    
    # Use regex to match the pattern
    match = re.match(pattern, s)
    
    if not match:
        raise ValueError(f"String format is incorrect: {s}")
    
    # Extract the matched groups
    hours = int(match.group(1))
    minutes = int(match.group(2))
    letter = match.group(3)
    
    return hours, minutes, letter

def exactLocationToBearing (exact_location, man_bearing):
    face_man = man_bearing + 180
    bearings = {
        'Mid-block facing man': 0,  # further from center - so moving to 180
        'Mid-block facing mountain': 180, # closer to center - so moving to 0

        'Mid-block facing 2:00': 90,
        'Mid-block facing 10:00': -90,

        'Corner - facing man & 2:00': 45,
        'Corner - facing man & 10:00': -45,
        'Corner - facing mountain & 2:00': 180 - 45,
        'Corner - facing mountain & 10:00': 180 + 45,
    }

    if not exact_location in bearings and not exact_location is None:
        raise ValueError (f"Unknown exact_location: {exact_location}")
    if exact_location is None:
        return None
    
    value = face_man + bearings [exact_location] + 180 

    while(value < 0):
        value += 360

    while(value >= 360):
        value -= 360
    
    return value

def calculateExactLocation(hours, minutes, letter, radius, exact_location):
    # find center of the plaza
    center = addressToCoordinate (letter, hours, minutes)
    man_bearing = bearing(hours, minutes)

    center_bearing = exactLocationToBearing (exact_location, man_bearing) 
    # step by plaza radius in that direction
    if center_bearing is None:
        print(f"no center bearing calculateExactLocation({hours}, {minutes}, {letter}, {radius}, {exact_location})")
        return center
    result =  distanceBearingFromCenter(radius, center_bearing, center)
    # print(f"calculateExactLocation({hours}, {minutes}, {letter}, {radius}, {exact_location}) -> {center_bearing} -> {result}")
    return result



def locationObjectToCoordinate(location):
    # this function takes location of the art or camp from the database, and returns a best guess about coordinates


    # simplest case, likey art:
    if 'gps_latitude' in location and 'gps_longitude' in location:
        return [location['gps_latitude'], location['gps_longitude']]
    
    # use-case 2: art
    if 'hour' in location and 'minute' in location and 'distance' in location and \
                not (location['distance'] is None or location['hour'] is None or location['minute'] is None):
        return distanceToCoordinate(location['distance'],location['hour'], location['minute']);

    # ValueError: Cannot parse street location: {'string': '', 'frontage': None, 'intersection': None, 'intersection_type': '&', 'dimensions': 'x', 'exact_location': None}
    if location["string"] == '':
        return None, None

    # Plaza locations have no interestion type:
    if "intersection_type" not in location or \
            location["intersection_type"] is None or \
            location["intersection"] is None or \
                (location["intersection_type"] == '@' and 'Plaza' in location["frontage"] and not 'Center Camp' in location["frontage"]):
        #  "intersection": null, "intersection_type": null,  - plazas and weird locations, need a vocabulary
        if 'Plaza' in location["frontage"]:
            """
                "location": {
                    "string": "3:00 G Plaza None None",
                    "frontage": "3:00 G Plaza",
                    "intersection": null,
                    "intersection_type": null,
                    "dimensions": "50+ x 250",
                    "exact_location": null
                },
                6 to 13 camps at the same plaza frontage!
                ignoring camp dimensions  since there is a lot of camps at the same point, it's not safe to point inside the camp
            """
            # parse Plaza address
            hours, minutes, letter = parsePlazaAddress( location["frontage"])
            radius = (plazaOuterWidth if hours != 6 else plazaOuterWidth6)/2
            # use "exact location" field to find angle position relative to the plaza center, 

            return calculateExactLocation(hours, minutes, letter, radius, location["exact_location"])
        
        if 'Airport Road' == location["frontage"]:
            return AIRPORT_COORDINATES
        
        if 'Portal' in location['frontage']:
            # special case - a portal, it has time
            location["frontage"] = location["frontage"].replace (' Portal','')
            is_portal = True

            hours, minutes = parseHoursMinutes(location["frontage"])
            letter = "esplanade"
            radius = portalMouthInFeet/2 # square diagonal 

            return calculateExactLocation(hours, minutes, letter, radius, location["exact_location"])

        raise ValueError (f"Non-plaza location with no intersection: {location}")

    # {'frontage': '5:30', 'intersection_type': '@', 'intersection': 'B', 'dimensions': '50 x 100', 'exact_location': 'Corner - facing mountain & 2:00', 'string': '5:30 @ B'}

    # Center camp, "intersection_type": "@"
    if location["intersection_type"] == '@':
        """
        "location": {
                "string": "Rod's Ring Road @ 8:15",
                "frontage": "Rod's Ring Road",
                "intersection": "8:15",
                "intersection_type": "@",
                "dimensions": "60 x 50",
                "exact_location": null
            },
        "location": {
            "string": "Center Camp Plaza @ 8:00",
            "frontage": "Center Camp Plaza",
            "intersection": "8:00",
            "intersection_type": "@",
            "dimensions": "50 x 135",
            "exact_location": null
        },

        'location': {'frontage': '9:00 G Plaza', 
            'intersection_type': '@', 
            'intersection': '5:30', 
            'dimensions': '80+ x 150', 
            'exact_location': 'Corner - facing man & 10:00',
            'string': '9:00 G Plaza @ 5:30'},

        """
        # Only one camp is observed for reach direction, so ignoring exact_location here
        
        # Find center of the Center camp
        center = distanceToCoordinate(manToCenterOfCenterCampInFeet, 6, 00)
        hours, minutes = parseHoursMinutes(location["intersection"])
        # translate "intersection" into bearing
        center_bearing = bearing(hours, minutes)

        if  'Center Camp Plaza' == location['frontage']:
            radius = centerCampRadiusInsideInFeet
        elif "Rod's Ring Road" == location['frontage']: # this is here for compatibility with 2023 map, but it's not maintained - so not checked for accuracy
            radius = centerCampRadiusOutsideInFeet
        else:
            raise ValueError (f"Unknown location with @-intersection: {location['string']}")

        # step by center camp radius in that direction
        return distanceBearingFromCenter(radius, center_bearing, center)

    # City camps, "intersection_type": "&"

    if location["intersection_type"] == '&':
        """
        camps: 
            "location": {
            "string": "3:30 & D",
            "frontage": "3:30",
            "intersection": "D",
            "intersection_type": "&",
            "dimensions": "100 x 100",
            "exact_location": null
            },
        
        it can have up to 43 camps at the same address (4:00 E)

        flips also exist, for example:
        4:45 & F: 4, F & 4:45: 16
        """
        """
        TODO:
        
        2) find intersection
        3) using exact location, step to the corner of the intersection or to the mid-block
        4) MAYBE USE frontage to make another step
        """

        # 1) identify street and clock
        frontage_letter = None
        if not "frontage" in location or location["frontage"] is None :
            raise ValueError (f"Cannot parse street location: {location}")
        
        
        if  not "intersection" in location or location["intersection"] is None:
            # 'frontage': '4:30 G Plaza',
            pass
        is_portal = False
        try:
            if ' Portal' in location["intersection"]:
                location["intersection"] = location["intersection"].replace (' Portal','')
                is_portal = True

            hours, minutes = parseHoursMinutes(location["intersection"])
            letter = location["frontage"]
            frontage_letter = True
        except ValueError:
            if ' Portal' in location["frontage"]:
                location["frontage"] = location["frontage"].replace (' Portal','')
                is_portal = True
        
            hours, minutes = parseHoursMinutes(location["frontage"])
            letter = location["intersection"]
            frontage_letter = False

        # TODO: How to use frontage here?
        # TODO: maybe use better calculation for street sizes - different streets = different points
        radius = math.sqrt(annularStreetWidthInFeet**2 + radialAvenueWidthInFeet**2)/2 # fiagonal

        # if is_portal:
        #     print(f"TODO: find better width for the portal depending on the crossing street {location}")

        return calculateExactLocation( hours, minutes, letter, radius, location["exact_location"])


       
    raise ValueError (f"Cannot parse location: {location}")
  
    
