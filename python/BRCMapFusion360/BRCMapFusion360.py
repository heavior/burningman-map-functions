import sys
import os
import adsk.core, adsk.fusion, traceback
from geopy.distance import geodesic

# Add the parent directory to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from map import renderMap, GOLDEN_STAKE, diameterKInFeet
import math

# Global variables
HEIGHT_Z = 0
FLIP_Z = True
MIRROR_X = True
SKETCH_NAME = "BRC map"
CITY_DIAMETER_CM = 4.7  # Diameter of the city in centimeters
FEET_PER_CM = diameterKInFeet / CITY_DIAMETER_CM

# Fusion 360 Application
app = adsk.core.Application.get()
ui = app.userInterface
design = app.activeProduct

def log_message(message):
    log_file = os.path.join(current_dir, "plugin_log.txt")
    with open(log_file, "a") as f:
        f.write(message + "\n")

def calculate_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used to calculate the bearing is:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to +180° which is not what we want for a compass bearing
    # The compass bearing needs to be in the range of 0° to 360°
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def convertGeoToFeet(coordinates):
    # Calculate the distance and bearing from the GOLDEN_STAKE
    distance = geodesic(GOLDEN_STAKE, coordinates).feet
    bearing = calculate_bearing(GOLDEN_STAKE, coordinates)
    angle = math.radians(bearing)
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)
    return x, y

def point_to_cm(point):
    x, y = convertGeoToFeet(point)
    if MIRROR_X:
        x = -x
    if FLIP_Z:
        y = -y
    return [x / FEET_PER_CM, y / FEET_PER_CM]

def find_or_create_sketch():
    sketches = design.rootComponent.sketches
    sketch = None
    for sk in sketches:
        if sk.name == SKETCH_NAME:
            sketch = sk
            break
    
    if sketch:
        # Clear existing sketch
        sketch.deleteMe()
    
    sketch = sketches.add(design.rootComponent.xYConstructionPlane)
    sketch.name = SKETCH_NAME
    return sketch

def add_circle(sketch, location, radius, name):
    x, y = point_to_cm(location)
    circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, HEIGHT_Z), radius / FEET_PER_CM)
    circle.name = name

def add_heart(sketch, center, size, name):
    x, y = point_to_cm(center)
    size = size / FEET_PER_CM

    if FLIP_Z:
        y = -y
    if MIRROR_X:
        x = -x

    # Define key points for the heart shape
    center_point = adsk.core.Point3D.create(x, y, HEIGHT_Z)  # Center of the heart
    bottom_tip = adsk.core.Point3D.create(x, y - size, HEIGHT_Z)  # Bottom tip of the heart

    # Define the control points for the bottom and top curves
    left_bottom = adsk.core.Point3D.create(x - size * 0.5, y - size * 0.25, HEIGHT_Z)
    right_bottom = adsk.core.Point3D.create(x + size * 0.5, y - size * 0.25, HEIGHT_Z)
    left_top = adsk.core.Point3D.create(x - size * 0.25, y + size * 0.25, HEIGHT_Z)
    right_top = adsk.core.Point3D.create(x + size * 0.25, y + size * 0.25, HEIGHT_Z)

    # Adjust points for MIRROR_X and FLIP_Z
    if MIRROR_X:
        left_bottom.x = -left_bottom.x
        right_bottom.x = -right_bottom.x
        left_top.x = -left_top.x
        right_top.x = -right_top.x
        center_point.x = - center_point.x
        bottom_tip.x = - bottom_tip.x
    if FLIP_Z:
        left_bottom.y = -left_bottom.y
        right_bottom.y = -right_bottom.y
        left_top.y = -left_top.y
        right_top.y = -right_top.y
        center_point.y = - center_point.y
        bottom_tip.y = - bottom_tip.y

    # Create bottom left line
    bottom_left_line = sketch.sketchCurves.sketchLines.addByTwoPoints(bottom_tip, left_bottom)

    # Create bottom right line
    bottom_right_line = sketch.sketchCurves.sketchLines.addByTwoPoints(bottom_tip, right_bottom)

    # Create top left arc
    top_left_arc = sketch.sketchCurves.sketchArcs.addByThreePoints(left_bottom, left_top, center_point)

    # Create top right arc
    top_right_arc = sketch.sketchCurves.sketchArcs.addByThreePoints(right_bottom, right_top, center_point)

def add_fusion_arch(sketch, startAngle, endAngle, archRadius, center, name):
    centerX, centerY = point_to_cm(center)
    radius_cm = archRadius / FEET_PER_CM

    start_angle_rad = math.radians(startAngle)
    end_angle_rad = math.radians(endAngle)

    start_x = radius_cm * math.cos(start_angle_rad)
    start_y = radius_cm * math.sin(start_angle_rad)
    end_x = radius_cm * math.cos(end_angle_rad)
    end_y = radius_cm * math.sin(end_angle_rad)

    # Apply MIRROR_X transformation
    if MIRROR_X:
        start_x = -start_x
        end_x = -end_x

    # Apply FLIP_Z transformation
    if FLIP_Z:
        start_y = -start_y
        end_y = -end_y

    start = adsk.core.Point3D.create(centerX + start_x, centerY + start_y, HEIGHT_Z)
    end = adsk.core.Point3D.create(centerX + end_x, centerY + end_y, HEIGHT_Z)

    # Adjust the order of points for FLIP_Z and MIRROR_X combinations
    if FLIP_Z and MIRROR_X:
        arc = sketch.sketchCurves.sketchArcs.addByCenterStartEnd(adsk.core.Point3D.create(centerX, centerY, HEIGHT_Z), start, end)
    elif FLIP_Z:
        arc = sketch.sketchCurves.sketchArcs.addByCenterStartEnd(adsk.core.Point3D.create(centerX, centerY, HEIGHT_Z), end, start)
    else:
        arc = sketch.sketchCurves.sketchArcs.addByCenterStartEnd(adsk.core.Point3D.create(centerX, centerY, HEIGHT_Z), start, end)

def add_fusion_line(sketch, startCoordinates, endCoordinates, name):
    startX, startY = point_to_cm(startCoordinates)
    endX, endY = point_to_cm(endCoordinates)
    start_point = adsk.core.Point3D.create(startX, startY, HEIGHT_Z)
    end_point = adsk.core.Point3D.create(endX, endY, HEIGHT_Z)
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start_point, end_point)
    line.name = name

def add_fusion_circle(sketch, location, width, name):
    radius = width / 2
    add_circle(sketch, location, radius, name)

def render_map():
    try:
        log_message("Starting the render_map function")
        sketch = find_or_create_sketch()
        renderMap(
            lambda startAngle, endAngle, archRadius, name: add_fusion_arch(sketch, startAngle, endAngle, archRadius, name),
            lambda startCoordinates, endCoordinates, name: add_fusion_line(sketch, startCoordinates, endCoordinates, name),
            lambda location, width, name: add_fusion_circle(sketch, location, width, name),
            lambda location, width, name: add_fusion_circle(sketch, location, width, name),  # addMan
            lambda location, width, name: add_heart(sketch, location, width / 2, name)  # addTemple
        )
        log_message("Finished rendering the map")
    except:
        if ui:
            error_message = 'Failed:\n{}'.format(traceback.format_exc())
            log_message(error_message)

# Run the rendering
render_map()
