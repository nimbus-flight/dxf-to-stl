# DXF to STL Converter

This Python script converts 2D DXF files (specifically from Cadmapper) into 3D STL models suitable for 3D printing. It extracts building footprints from the DXF and extrudes them to create 3D volumes.

## Features

* Handles LWPOLYLINE, LINE, and POLYLINE entities from DXF files.
* Extracts building heights from MESH entities (assuming they are available).
* Optionally assigns different extrusion heights based on layer names.
* Scales the model down to fit within a specified maximum dimension.
* Creates a separate base layer for the model.
* Attempts to repair mesh inconsistencies using `trimesh.repair` functions.

## Requirements

* Python 3.x
* Libraries listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/nimbus-flight/dxf-to-stl.git
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your DXF file (e.g., `cadmapper-atlanta-georgia-us.dxf`) in the same directory as the script.

2. Run the script:
   ```bash
   python3 converter.py
   ```

3. This will generate two STL files:
   * `output_base.stl`: The base layer of the model.
   * `output_buildings.stl`: The extruded buildings.

4. Import these STL files into your 3D modeling or slicing software and position them as needed.

## Customization

* You can adjust the `max_dimension` variable in the code to control the maximum size of the final model.
* You can modify the layer-based extrusion heights or add handling for other DXF entity types as needed. 

## Further improvements
This currently only imports buildings, if you want to add roads and other layers, you will need to add an entity.dxf.layer

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE   
 file for details.
