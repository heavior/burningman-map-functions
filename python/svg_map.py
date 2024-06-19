import math
from map import renderMap, GOLDEN_STAKE, YEAR
from geopy.distance import geodesic
import os
import xml.etree.ElementTree as ET

STROKE_COLOR = "black"
SVG_ANGLE_TURN = -90
SVG_FEET_PER_PIXEL = 10

LOWER_NUMBERS_FOLLOW_CLOCK = False
HOUR_FONT_SIZE = "24px"
HOUR_FONT = "Reef"

# SVG generation
svg_groups = {}
element_counters = {"arch": {}, "line": {}, "circle": {}, 'icon': {}}
max_distance = 0


def sanitize_name(name):
    return name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def convertGeoToXY(coordinates):
    distance = geodesic(GOLDEN_STAKE, coordinates).feet
    bearing = calculate_bearing(GOLDEN_STAKE, coordinates)
    angle = bearing + SVG_ANGLE_TURN
    angleRad = math.radians(angle)
    x = distance * math.cos(angleRad) / SVG_FEET_PER_PIXEL
    y = distance * math.sin(angleRad) / SVG_FEET_PER_PIXEL
    return x, y


def addSVGArch(startAngle, endAngle, archRadius, center, name):
    x, y = convertGeoToXY(center)
    name = sanitize_name(name)
    if name not in element_counters["arch"]:
        element_counters["arch"][name] = 0
    element_id = f"{name} arch_{element_counters['arch'][name]}"
    element_counters["arch"][name] += 1
    
    startAngleRad = math.radians(startAngle + SVG_ANGLE_TURN)
    endAngleRad = math.radians(endAngle + SVG_ANGLE_TURN)
    
    startX = x + archRadius * math.cos(startAngleRad) / SVG_FEET_PER_PIXEL
    startY = y + archRadius * math.sin(startAngleRad) / SVG_FEET_PER_PIXEL
    endX = x + archRadius * math.cos(endAngleRad) / SVG_FEET_PER_PIXEL
    endY = y + archRadius * math.sin(endAngleRad) / SVG_FEET_PER_PIXEL
    
    large_arc_flag = 1 if endAngle - startAngle > 180 else 0
    
    path = '<path id="{}" d="M {} {} A {} {} 0 {} 1 {} {}" fill="none" stroke="{}" />'.format(
        element_id, startX, startY, archRadius / SVG_FEET_PER_PIXEL, archRadius / SVG_FEET_PER_PIXEL, large_arc_flag, endX, endY, STROKE_COLOR)
    
    if name not in svg_groups:
        svg_groups[name] = []
    svg_groups[name].append(path)

def addSVGLine(startCoordinates, endCoordinates, name):
    global max_distance

    name = sanitize_name(name)
    if name not in element_counters["line"]:
        element_counters["line"][name] = 0
    element_id = f"{name} line_{element_counters['line'][name]}"
    element_counters["line"][name] += 1
    
    startX, startY = convertGeoToXY(startCoordinates)
    endX, endY = convertGeoToXY(endCoordinates)
    
    line = '<line id="{}" x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" />'.format(element_id, startX, startY, endX, endY, STROKE_COLOR)
    
    if name not in svg_groups:
        svg_groups[name] = []
    svg_groups[name].append(line)

    # Update max_distance
    max_distance = max(max_distance, abs(startX), abs(startY), abs(endX), abs(endY))

def calculate_bearing(pointA, pointB):
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def addSVGCircle(location, width, name):
    name = sanitize_name(name)
    if name not in element_counters["circle"]:
        element_counters["circle"][name] = 0
    element_id = f"{name} circle_{element_counters['circle'][name]}"
    element_counters["circle"][name] += 1
    
    x, y = convertGeoToXY(location)
    radius = width / (2 * SVG_FEET_PER_PIXEL)
    
    circle = '<circle id="{}" cx="{}" cy="{}" r="{}" fill="none" stroke="{}" />'.format(element_id, x, y, radius, STROKE_COLOR)
    
    if name not in svg_groups:
        svg_groups[name] = []
    svg_groups[name].append(circle)

def addSVGIcon(filename, centerX, centerY, width, name, rotation=0):
    name = sanitize_name(name)
    if name not in element_counters["icon"]:
        element_counters["icon"][name] = 0
    element_id = f"{name}_icon_{element_counters['icon'][name]}"
    element_counters["icon"][name] += 1

    # Parse the SVG file
    tree = ET.parse(filename)
    root = tree.getroot()

    # Get the width and height from the SVG file
    svg_width = float(root.attrib.get('width', '0').replace('px', ''))
    svg_height = float(root.attrib.get('height', '0').replace('px', ''))

    # Get the viewBox and use it for scaling if available
    viewBox = root.attrib.get('viewBox', None)
    if viewBox:
        min_x, min_y, vb_width, vb_height = map(float, viewBox.split())
        scale_factor = width / vb_width
        translate_x = -min_x - vb_width / 2
        translate_y = -min_y - vb_height / 2
    else:
        scale_factor = width / svg_width
        translate_x = -svg_width / 2
        translate_y = -svg_height / 2

    # Create a group element to wrap the icon
    group = ET.Element('g', id=element_id, transform=f"translate({centerX}, {centerY}) scale({scale_factor}) rotate({rotation}) translate({translate_x}, {translate_y})")

    # Add the SVG content to the group
    for element in root:
        group.append(element)

    # Convert the group element to a string
    svg_group_str = ET.tostring(group, encoding='unicode')

    # Add the group to svg_groups
    if name not in svg_groups:
        svg_groups[name] = []
    svg_groups[name].append(svg_group_str)

def addMan(location, width, name):
    x, y = convertGeoToXY(location)
    if os.path.isfile('man.svg'):
        addSVGIcon('man.svg', x, y, width / SVG_FEET_PER_PIXEL, name, rotation=0)
    else:
        addSVGCircle(location, width, name)

def addTemple(location, width, name):
    x, y = convertGeoToXY(location)
    if os.path.isfile('temple.svg'):
        addSVGIcon('temple.svg', x, y, width / SVG_FEET_PER_PIXEL, name, rotation=0)
    else:
        addSVGCircle(location, width, name)


def addHourLabel(hour, minute, location, bearing):
    if minute > 0:
        return

    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
    text = roman_numerals[hour - 1]  # Adjusting for hours starting at 1

    x, y = convertGeoToXY(location)

    if not LOWER_NUMBERS_FOLLOW_CLOCK and 90 < bearing < 270:
        bearing += 180

    # Create the SVG text element
    text_element = f'''
    <text x="{x}" y="{y}" transform="rotate({bearing}, {x}, {y})" text-anchor="middle" fill="{STROKE_COLOR}" font-size="{HOUR_FONT_SIZE}" font-family="{HOUR_FONT}">
        {text}
    </text>
    '''

    if "hour_labels" not in svg_groups:
        svg_groups["hour_labels"] = []
    svg_groups["hour_labels"].append(text_element)



renderMap(addSVGArch, addSVGLine, addSVGCircle, addMan, addTemple, addHourLabel, 1.5)

# Generate the SVG content
svg_group_elements = []
for name, paths in svg_groups.items():
    group = '<g id="{}">\n{}\n</g>'.format(name, "\n  ".join(paths))
    svg_group_elements.append(group)

# Set the viewBox size based on the maximum distance
viewBox_size = max_distance * 2

svg_content = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-{0} -{0} {1} {1}" width="{1}" height="{1}">
  {2}
</svg>
'''.format(viewBox_size / 2, viewBox_size, "\n  ".join(svg_group_elements))

# Write the SVG content to a file
with open(f"../renders/burning_man_map_{YEAR}.svg", "w") as svg_file:
    svg_file.write(svg_content)
