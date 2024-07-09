from geopy.distance import distance as geopy_distance
import re
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
Later: center camp coordinates, art coordinates (time and distance), camp orientation (leverage street widths)
"""



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
    bearing_correction = 180 - man_bearing
    bearings = {
        'Mid-block facing man': 0 + bearing_correction, 
        'Mid-block facing mountain': 180 + bearing_correction,
        'Mid-block facing 2:00': 90 + bearing_correction,
        'Mid-block facing 10:00': 270 + bearing_correction,
        'Corner - facing man & 2:00': 45 + bearing_correction,
        'Corner - facing man & 10:00': -45 + bearing_correction,
        'Corner - facing mountain & 2:00': 135 + bearing_correction,
        'Corner - facing mountain & 10:00': -135 + bearing_correction,
    }

    if not exact_location in bearings and not exact_location is None:
        raise ValueError (f"Unknown exact_location: {exact_location}")
    if exact_location is None:
        return None
    
    value = bearings [exact_location]
    while(value < 0):
        value += 360

    while(value >= 360):
        value -= 360
    
    return value


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
    if "intersection_type" not in location or location["intersection_type"] is None or location["intersection"] is None:
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
            # find center of the plaza
            center = addressToCoordinate (letter, hours, minutes)
            man_bearing = bearing(hours, minutes)
            radius = (plazaOuterWidth if hours != 6 else plazaOuterWidth6)/2
            # use "exact location" field to find angle position relative to the plaza center, 
            center_bearing = exactLocationToBearing (location["exact_location"], man_bearing) 
            # step by plaza radius in that direction
            if center_bearing is None:
                return center
            return distanceBearingFromCenter(radius, center_bearing, center)
        
        if 'Airport Road' == location["frontage"]:
            print(f"TODO: return Airport location for {location}")
            return None, None
        
        if 'Portal' in location['frontage']:
            # special case - a portal, it has time
            location["frontage"] = location["frontage"].replace (' Portal','')
            is_portal = True

            hours, minutes = parseHoursMinutes(location["frontage"])
            letter = "esplanade"

            # find intersection
            center = addressToCoordinate (letter, hours, minutes)

            radius = portalMouthInFeet/2 # square diagonal 
            # use "exact location" field to find angle position relative to the plaza center, 
            man_bearing = bearing(hours, minutes)
            center_bearing = exactLocationToBearing (location["exact_location"], man_bearing) 
            # step by plaza radius in that direction

            if center_bearing is None:
                return center
            # using exact location, step to the corner of the intersection or to the mid-block
            return distanceBearingFromCenter(radius, center_bearing, center)

        raise ValueError (f"Non-plaza location with no intersection: {location}")


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
        """
        # Only one camp is observed for reach direction, so ignoring exact_location here
        
        # Find center of the Center camp
        center = distanceToCoordinate(manToCenterOfCenterCampInFeet, 6, 00)
        hours, minutes = parseHoursMinutes(location["intersection"])
        # translate "intersection" into bearing
        center_bearing = bearing(hours, minutes)

        if  'Center Camp Plaza' == location['frontage']:
            radius = centerCampRadiusOutsideInFeet
        elif "Rod's Ring Road" == location['frontage']:
            radius = centerCampRadiusInsideInFeet
        else:
            raise ValueError (f"Unknown location with @-intersection: {location['string']}")

        # print("Check if need to step away or use inner radius")
        # centerCampRadiusInsideInFeet = 320  # canopy
        # centerCampRadiusOutsideInFeet = 763

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

        # find intersection
        center = addressToCoordinate (letter, hours, minutes)

        radius = streetWidthInFeet/2 * math.sqrt(2) # square diagonal 
        if is_portal:
            print("TODO: find better width for the portal depending on the crossing street")
        # use "exact location" field to find angle position relative to the plaza center, 
        man_bearing = bearing(hours, minutes)
        center_bearing = exactLocationToBearing (location["exact_location"], man_bearing) 
        # step by plaza radius in that direction
        
        if center_bearing is None:
            return center
        # using exact location, step to the corner of the intersection or to the mid-block
        return distanceBearingFromCenter(radius, center_bearing, center)


       
    raise ValueError (f"Cannot parse location: {location}")
  
    
