import simplekml
import math
from map import renderMap, GOLDEN_STAKE, distanceBearingFromCenter, ELEVATION, YEAR
import os
import zipfile

# KML generation
kml = simplekml.Kml()
kml_folder = kml.newfolder(name=f"Burning Man Map {YEAR}")

# Global variables
LINE_COLOR = simplekml.Color.blue
ARCH_COLOR = simplekml.Color.red
CIRCLE_COLOR = simplekml.Color.changealphaint(100, simplekml.Color.green)
ICON_SCALE = 1.0
FEET_PER_POINT = 100  # This determines the number of nodes
DEGREES_PER_POINT = 7.5
MIN_CURCLE_POINTS = 10

# List to keep track of used icons
used_icons = []

# Utility function to convert geopy Point to a list
def point_to_list(point, altitude=ELEVATION):
    return [point[1], point[0], altitude]

# Function to render an arch
def renderKmlArch(startAngle, endAngle, archRadius, center):
    coords = []
    angle = startAngle

    while angle <= endAngle:
        rounded_angle = round(angle / DEGREES_PER_POINT) * DEGREES_PER_POINT
        if rounded_angle > startAngle and rounded_angle < endAngle:
            coords.append(point_to_list(distanceBearingFromCenter(archRadius, rounded_angle, center)))
        angle += DEGREES_PER_POINT

    coords.insert(0, point_to_list(distanceBearingFromCenter(archRadius, startAngle, center)))
    coords.append(point_to_list(distanceBearingFromCenter(archRadius, endAngle, center)))
    return coords

# Function to render a circle
def renderKmlCircle(radius, center):
    points_per_circle = max(MIN_CURCLE_POINTS, int((2 * math.pi * radius) / FEET_PER_POINT))
    angleStep = 360 / points_per_circle
    coords = []
    angle = 0

    while angle <= 360:
        coords.append(point_to_list(distanceBearingFromCenter(radius, angle, center)))
        angle += angleStep

    coords.append(point_to_list(distanceBearingFromCenter(radius, 0, center)))
    return coords

# Function to add arches to the KML file
def addKmlArch(startAngle, endAngle, archRadius, center, name):
    coords = renderKmlArch(startAngle, endAngle, archRadius, center)
    
    # Create a line for the arch
    line = kml_folder.newlinestring(name=name)
    line.coords = coords
    line.style.linestyle.color = ARCH_COLOR
    line.style.linestyle.width = 2

# Function to add lines to the KML file
def addKmlLine(startCoordinates, endCoordinates, name):
    startCoord = point_to_list(startCoordinates)
    endCoord = point_to_list(endCoordinates)
    coords = [startCoord, endCoord]
    
    # Create a line
    line = kml_folder.newlinestring(name=name)
    line.coords = coords
    line.style.linestyle.color = LINE_COLOR
    line.style.linestyle.width = 2

# Function to add circles to the KML file
def addKmlCircle(location, width, name):
    radius = width / 2
    coords = renderKmlCircle(radius, location)

    # Create a polygon for the circle
    polygon = kml_folder.newpolygon(name=name)
    polygon.outerboundaryis = coords
    polygon.style.polystyle.color = CIRCLE_COLOR

# Function to add icons to the KML file
def addKmlIcon(filename, centerX, centerY, width, name, rotation=0):
    global used_icons
    if filename not in used_icons:
        used_icons.append(filename)
    
    # Create a point for the icon
    point = kml_folder.newpoint(name=name)
    point.coords = [(centerX, centerY, ELEVATION)]
    point.iconstyle.icon.href = filename
    point.iconstyle.scale = width / 100 * ICON_SCALE
    point.iconstyle.heading = rotation

# Function to create a point
def createPoint(location, name):
    point = kml_folder.newpoint(name=name)
    point.coords = [point_to_list(location)]

# Function to add the Man icon or circle
def addMan(location, width, name):
    location_list = point_to_list(location)
    if os.path.isfile('man.svg'):
        addKmlIcon('man.svg', location_list[0], location_list[1], width, name)
    else:
        addKmlCircle(location, width, name)

# Function to add the Temple icon or circle
def addTemple(location, width, name):
    location_list = point_to_list(location)
    if os.path.isfile('temple.svg'):
        addKmlIcon('temple.svg', location_list[0], location_list[1], width, name)
    else:
        addKmlCircle(location, width, name)

# Render the map elements
renderMap(addKmlArch, addKmlLine, addKmlCircle, addMan, addTemple)

# Save the KML file
kml_file_name = f"../renders/burning_man_map_{YEAR}.kml"
kmz_file_name = f"../renders/burning_man_map_{YEAR}.kmz"
kml.save(kml_file_name)

# Create KMZ file
with zipfile.ZipFile(kmz_file_name, 'w') as kmz:
    # Add the KML file to the KMZ archive
    kmz.write(kml_file_name, arcname=kml_file_name)
    
    # Add the used icon files to the KMZ archive
    for icon in used_icons:
        kmz.write(icon, arcname=icon)
