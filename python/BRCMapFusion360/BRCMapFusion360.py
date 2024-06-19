import sys, os, math
import adsk.core, adsk.fusion, traceback

# Add the parent directory to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dependencies_dir = os.path.join(current_dir, 'dependencies')
sys.path.append(parent_dir)
sys.path.append(dependencies_dir)

def log_message(message):
    log_file = os.path.join(current_dir, "plugin_log.txt")
    with open(log_file, "a") as f:
        f.write(message + "\n")

from geopy.distance import geodesic
from map import renderMap, GOLDEN_STAKE, diameterKInFeet

# Global variables
FLIP_Z = True
MIRROR_X = True
SKETCH_NAME = "BRC map"
CITY_DIAMETER_CM = 4.7  # Diameter of the city in centimeters
MOVE_X = 0
MOVE_Y = 0
MOVE_Z = 0

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

def point_to_cm(point, mirror_x, flip_z, feet_per_cm, move_x, move_y):
    x, y = convertGeoToFeet(point)
    if mirror_x:
        x = -x
    if flip_z:
        y = -y
    return [x / feet_per_cm + move_x, y / feet_per_cm + move_y]

def create_custom_plane(root_comp, origin, sketch_name):
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    offset_value = adsk.core.ValueInput.createByReal(origin.z)
    plane_input.setByOffset(root_comp.xYConstructionPlane, offset_value)
    custom_plane = planes.add(plane_input)
    custom_plane.name = sketch_name + " Plane"
    return custom_plane

def find_or_create_sketch(design, sketch_name, origin):
    root_comp = design.rootComponent
    sketches = root_comp.sketches

    # Check if the sketch already exists
    sketch = None
    for sk in sketches:
        if sk.name == sketch_name:
            sketch = sk
            break

    # If the sketch exists, delete it
    if sketch:
        sketch.deleteMe()

    # Create a custom plane at the desired origin
    custom_plane = create_custom_plane(root_comp, origin, sketch_name)
    
    # Create a new sketch on the custom plane
    sketch = sketches.add(custom_plane)
    sketch.name = sketch_name
    return sketch

def add_circle(sketch, location, radius, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z):
    x, y = point_to_cm(location, mirror_x, flip_z, feet_per_cm, move_x, move_y)
    circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, move_z), radius / feet_per_cm)
    circle.name = name

def add_heart(sketch, center, size, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z):
    x, y = point_to_cm(center, mirror_x, flip_z, feet_per_cm, move_x, move_y)
    size = size / feet_per_cm

    if flip_z:
        y = -y
    if mirror_x:
        x = -x

    center_point = adsk.core.Point3D.create(x, y, move_z)
    bottom_tip = adsk.core.Point3D.create(x, y - size, move_z)

    left_bottom = adsk.core.Point3D.create(x - size * 0.5, y - size * 0.25, move_z)
    right_bottom = adsk.core.Point3D.create(x + size * 0.5, y - size * 0.25, move_z)
    left_top = adsk.core.Point3D.create(x - size * 0.25, y + size * 0.25, move_z)
    right_top = adsk.core.Point3D.create(x + size * 0.25, y + size * 0.25, move_z)

    if mirror_x:
        left_bottom.x = -left_bottom.x
        right_bottom.x = -right_bottom.x
        left_top.x = -left_top.x
        right_top.x = -right_top.x
        center_point.x = -center_point.x
        bottom_tip.x = -bottom_tip.x
    if flip_z:
        left_bottom.y = -left_bottom.y
        right_bottom.y = -right_bottom.y
        left_top.y = -left_top.y
        right_top.y = -right_top.y
        center_point.y = -center_point.y
        bottom_tip.y = -bottom_tip.y

    sketch.sketchCurves.sketchLines.addByTwoPoints(bottom_tip, left_bottom)
    sketch.sketchCurves.sketchLines.addByTwoPoints(bottom_tip, right_bottom)
    sketch.sketchCurves.sketchArcs.addByThreePoints(left_bottom, left_top, center_point)
    sketch.sketchCurves.sketchArcs.addByThreePoints(right_bottom, right_top, center_point)

def add_fusion_arch(sketch, startAngle, endAngle, archRadius, center, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z):
    centerX, centerY = point_to_cm(center, mirror_x, flip_z, feet_per_cm, move_x, move_y)
    radius_cm = archRadius / feet_per_cm

    start_angle_rad = math.radians(startAngle)
    end_angle_rad = math.radians(endAngle)

    start_x = radius_cm * math.cos(start_angle_rad)
    start_y = radius_cm * math.sin(start_angle_rad)
    end_x = radius_cm * math.cos(end_angle_rad)
    end_y = radius_cm * math.sin(end_angle_rad)

    if mirror_x:
        start_x = -start_x
        end_x = -end_x
    if flip_z:
        start_y = -start_y
        end_y = -end_y

    start = adsk.core.Point3D.create(centerX + start_x, centerY + start_y, move_z)
    end = adsk.core.Point3D.create(centerX + end_x, centerY + end_y, move_z)

    if flip_z and mirror_x:
        arc = sketch.sketchCurves.sketchArcs.addByCenterStartEnd(adsk.core.Point3D.create(centerX, centerY, move_z), start, end)
    elif flip_z:
        arc = sketch.sketchCurves.sketchArcs.addByCenterStartEnd(adsk.core.Point3D.create(centerX, centerY, move_z), end, start)
    else:
        arc = sketch.sketchCurves.sketchArcs.addByCenterStartEnd(adsk.core.Point3D.create(centerX, centerY, move_z), start, end)

def add_fusion_line(sketch, startCoordinates, endCoordinates, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z):
    startX, startY = point_to_cm(startCoordinates, mirror_x, flip_z, feet_per_cm, move_x, move_y)
    endX, endY = point_to_cm(endCoordinates, mirror_x, flip_z, feet_per_cm, move_x, move_y)
    start_point = adsk.core.Point3D.create(startX, startY, move_z)
    end_point = adsk.core.Point3D.create(endX, endY, move_z)
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start_point, end_point)
    line.name = name

def add_fusion_circle(sketch, location, width, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z):
    radius = width / 2
    add_circle(sketch, location, radius, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z)

def render_map(sketch, flip_z, mirror_x, city_diameter_cm, move_x, move_y, move_z):
    feet_per_cm = diameterKInFeet / city_diameter_cm
    log_message("Starting the render_map function")
    renderMap(
        lambda startAngle, endAngle, archRadius, center, name: add_fusion_arch(sketch, startAngle, endAngle, archRadius, center, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z),
        lambda startCoordinates, endCoordinates, name: add_fusion_line(sketch, startCoordinates, endCoordinates, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z),
        lambda location, width, name: add_fusion_circle(sketch, location, width, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z),
        lambda location, width, name: add_fusion_circle(sketch, location, width, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z),  # addMan
        lambda location, width, name: add_heart(sketch, location, width / 2, name, flip_z, mirror_x, feet_per_cm, move_x, move_y, move_z)  # addTemple
    )
    log_message("Finished rendering the map")

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        
        origin = adsk.core.Point3D.create(0, 0, 0)
        sketch = find_or_create_sketch(design, SKETCH_NAME, origin)
        render_map(sketch, FLIP_Z, MIRROR_X, CITY_DIAMETER_CM, move_x=MOVE_X, move_y=MOVE_Y, move_z=MOVE_Z)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
