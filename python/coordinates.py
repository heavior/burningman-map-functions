from geopy.distance import distance as geopy_distance


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

def locationObjectToCoordinate(location):
    # this function takes location of the art or camp from the database, and returns a best guess about coordinates

    # simplest case, likey art:
    if 'gps_latitude' in location and 'gps_longitude' in location:
        return [location['gps_latitude'], location['gps_longitude']]
    
    # use-case 2: art
    if 'hour' in location and 'minute' in location and 'distance' in location and \
                not (location['distance'] is None or location['hour'] is None or location['minute'] is None):
        return distanceToCoordinate(location['distance'],location['hour'], location['minute']);

    # "intersection_type": "@", is used for center camp
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


    Find center of the Center camp, 
    translate "intersection" into direction
    step by center camp radius in that direction

    IGNORE EXACT_LOCATION here

    Each time has only one camp
    """


    #  "intersection": null, "intersection_type": null,  - plazas and weird locations, need a vocabulary

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

    TODO: parse "Plaza", 
    parse Plaza address, 
    find center of the plaza, 
    use "exact location" field to find angle position relative to the plaza center, 
    step by plaza radius in that direction

    ignore camp dimensions  since there is a lot of camps at the same point, it's not safe to point inside the camp
    """


    # & - normal camps inside the city

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

TODO:
1) identify street and clock
2) find intersection
3) using exact location, step to the corner of the intersection or to the mid-block
4) MAYBE USE frontage to make another step

"""


"""
Unique values for 'frontage': {'C', '9:00', '5:45', '8:15', 'D', '4:30 G Plaza', '9:00 B Plaza', '6:00', '7:30 B Plaza', '8:30', '7:45', '2:30', '6:30', 'K', '9:30', 'E', 'B', '4:30 B Plaza', '7:00', 'I', '4:45', '3:45', "Rod's Ring Road", '6:00 G Plaza', '3:00 Portal', '10:00', '6:00 Portal', '5:15', '7:15', '4:15', '3:00 G Plaza', '3:00', '3:15', '3:30', 'Center Camp Plaza', '6:15', '2:45', '9:45', 'Esplanade', '8:45', '7:30 Portal', '6:45', 'H', '7:30 G Plaza', 'Airport Road', '9:00 Portal', 'J', '8:00', '5:00', '7:30', '4:30 Portal', '9:00 G Plaza', 'F', '3:00 B Plaza', '2:15', 'A', None, '5:30', '4:30', '9:15', '4:00', 'G', '2:00'}
Unique values for 'intersection': {'C', '9:00', '5:45', '8:15', 'D', '10:15', '7:45', '8:30', '2:30', '6:30', 'K', '9:30', 'E', 'B', '7:00', '1:45', 'I', '4:45', '3:45', '5:15', '3:00 Portal', '6:00 Portal', '10:00', '7:15', '10:30', '4:15', '3:15', '2:45', '3:30', '3:00', '6:15', '9:45', '8:45', '7:30 Portal', '6:45', 'H', 'J', '9:00 Portal', '8:00', '5:00', '7:30', '4:30 Portal', 'F', '2:15', 'A', '1:00', '11:30', None, '5:30', '4:30', '9:15', '4:00', 'G', '2:00'}
Unique values for 'intersection_type': {'@', '&', None}
Unique values for 'exact_location': {'Mid-block facing man', 'Corner - facing mountain & 2:00', 'Corner - facing man & 10:00', None}

Mid-block facing man
Mid-block facing mountain
Mid-block facing 2:00
Mid-block facing 10:00
Corner - facing man & 2:00
Corner - facing man & 10:00
Corner - facing mountain & 2:00
Corner - facing mountain & 10:00

    """
    
