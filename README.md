
This project is not affiliated with or endorsed by Burning Man Project or Black Rock City LLC.

"The Burning Man symbol (logo), “Burning Man,” “Burning Man Project,” “Black Rock City,” “Decompression,” “Precompression,” “Burnal Equinox” and “Flambé Lounge” are protected trademarks. The design of the Burning Man (aka “the Man”) and Man base, the map and layout of Black Rock City, the design of the City’s lampposts and the Ten Principles are protected copyrights."
https://burningman.org/about/about-us/press-media/trademarks-images-faq


# Burning Man Map Functions

## Overview

This library generates Black Rock City map in different formats

Core ideas
1) Script operates with BRC coordinate sytem when possible - using time and letters to identify locations
2) Map logic is separated from rendering logic, this allows replacing the "view" and create different renderers 
(kml and svg are implemented, as well as Autodesk Fusion 360)
3) Library provides center lines, and the view portion can tweak the rendering the way it likes (see how KML circles are rendered). Currently, script doesn't  provide polygons


IMPORTANT: 
1) Man moves! So for the current year, get the latest GEO data.
here is the old one that is used for debug: https://bm-innovate.s3.amazonaws.com/2023/2023%20BRC%20Measurements.pdf
If you need data for the upcoming event, start with this page: https://innovate.burningman.org/apis-page/
2) Map changes! plazas and center camp could have a different configuration this year, so make sure to check stuff

## TODO:
* Portals, greeters and airport are not rendered
* Implement function that will return camp coordinates based on intersection and position (new data in 2024)


## Project Structure
- `map.py`: Contains core logic and functions for calculating coordinates and rendering the map. This is the center script that defines the geographic and structural parameters of the Burning Man event.
- `kml_map.py`: Uses the functions from `map.py` to generate a KML file for viewing in Google Earth/Google My Maps/etc. It also packages the KML file into a KMZ archive, including any necessary icons, though I couldn't make icon work in Google My Maps
- `svg_map.py`: Uses the functions from `map.py` to generate an vector file for printing or manufacturing.
- `BRCMapFusion360`: a plugin that generates a sketch for Autodesk Fusion 360 with a BRC map. Supports flipping the render and scaling based on the city circle diameter. Check hardcoded parameters inside


## Usage

### Generate the Map

1. **Configure Parameters:**
   The `map.py` file contains all the core configurations and parameters needed to generate the map. You can adjust variables such as street widths, distances, and other geographical parameters with latest data.

2. **Generate KML File:**
   To generate a KML file for Google Earth, run:
   \`\`\`sh
   python kml_map.py
   \`\`\`
   This will create a `burning_man_map_YEAR.kml` and `burning_man_map_YEAR.kmz` file

3. **Generate SVG File:**
   To generate an SVG file, run:
   \`\`\`sh
   python svg_map.py
   \`\`\`
   This will create a `burning_man_map_YEAR.svg` file 

## Key Files and Functions

### map.py

- **Functions:**
  - `distanceBearingFromCenter(distance, bearing, center)`: Calculates coordinates given a distance and bearing from a center point.
  - `distanceBearingToCoordinate(distance, bearing)`: Calculates coordinates given a distance and bearing from the GOLDEN_STAKE.
  - `distanceToCoordinate(distance, hours, minutes)`: Converts address to coordinates based on distance and clock direction.
  - `addressToCoordinate(letter, hours, minutes)`: Converts street address to coordinates.

### kml_map.py

- **Functions:**
  - `addKmlArch(startAngle, endAngle, archRadius, name)`: Adds an arch to the KML file.
  - `addKmlLine(startCoordinates, endCoordinates, name)`: Adds a line to the KML file.
  - `addKmlCircle(location, width, name)`: Adds a circle to the KML file.
  - `addKmlIcon(filename, centerX, centerY, width, name, rotation=0)`: Adds an icon to the KML file.
  - `createPoint(location, name)`: Creates a point in the KML file.
  - `addMan(location, width, name)`: Adds the Man icon or circle.
  - `addTemple(location, width, name)`: Adds the Temple icon or circle.

#By implementing consistent set of functions, you can implement your renderer#

### svg_map.py

- **Functions:**
  - `addSVGArch(startAngle, endAngle, archRadius, name)`: Adds an arch to the SVG file.
  - `addSVGLine(startCoordinates, endCoordinates, name)`: Adds a line to the SVG file.
  - `addSVGCircle(location, width, name)`: Adds a circle to the SVG file.
  - `addSVGIcon(filename, centerX, centerY, width, name, rotation=0)`: Adds an icon to the SVG file.


## BRCMapFusuion360
This is a plugin for Autodesk Fusion 360. Make sure that dependencies are available, you can install them to the `BRCMapFusuion360/dependencies` forlder
See `plugin_log.txt` for errors if nothing works

## License

This project is licensed under the MIT License. See the LICENSE file for details.
