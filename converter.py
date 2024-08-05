import ezdxf
import trimesh
import numpy as np
import shapely.geometry  # Import the shapely.geometry module


def dxf_to_extruded_stl(dxf_path, stl_path):
    """
    Converts a DXF file to an extruded STL mesh for 3D printing.
    """

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    meshes = []
    for entity in msp:
        if entity.dxftype() == 'MESH' and entity.dxf.layer == 'buildings':
            # Extract vertices and their elevations from the MESH entity
            vertices = entity.vertices 
            elevations = [v[2] for v in vertices] 

            # Calculate extrusion height (assuming top face is at max elevation)
            extrusion_height = max(elevations)

            # Convert FaceList to a NumPy array of integers
            faces = np.array([(f[0], f[1], f[2]) for f in entity.faces], dtype=np.int32)

            # Create a trimesh mesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

            # Optionally, translate the mesh downwards if the base is not at z=0
            if min(elevations) != 0:
                mesh.apply_translation([0, 0, -min(elevations)])

            
            # Attempt to repair the combined mesh
            trimesh.repair.fix_winding(mesh)  # Fix winding order if needed
            trimesh.repair.fill_holes(mesh)   # Fill holes in the mesh 


            meshes.append(mesh)

        else:
            continue  # Ignore other entity types         
    # Combine all meshes
    combined_mesh = trimesh.util.concatenate(meshes)

    # Scale down to fit within max_dimension
    max_dimension = 200.0
    bounds = combined_mesh.bounds
    max_extent = np.max(bounds[1] - bounds[0])  # Get the largest dimension
    if max_extent > max_dimension:
        scale_factor = max_dimension / max_extent
        combined_mesh.apply_scale(scale_factor)



    # Create a base layer (adjust dimensions and thickness as needed)
    base_width = 200.0
    base_length = 200.0
    base_thickness = 4.0 
    base_mesh = trimesh.creation.box(extents=[base_width, base_length, base_thickness])

    # Union the base layer with the combined mesh
    #combined_mesh = combined_mesh.union(base_mesh)

    # Export to STL
    combined_mesh.export(stl_path)

# Example usage
dxf_file = 'cadmapper-atlanta-georgia-us.dxf'
stl_file = 'output.stl'
#extrusion_height = 50.0  # Adjust as needed

dxf_to_extruded_stl(dxf_file, stl_file)
