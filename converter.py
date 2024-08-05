import ezdxf
import trimesh
import numpy as np
import shapely.geometry  # Import the shapely.geometry module


def dxf_to_extruded_stl(dxf_path, stl_path, max_dimension=200.0,):
    """
    Converts a DXF file to an extruded STL mesh for 3D printing.
    """

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    meshes = []
    building_meshes = [] # Separate list for building meshes


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


            # Attempt to repair the combined mesh
            trimesh.repair.fix_winding(mesh)  # Fix winding order if needed
            trimesh.repair.fill_holes(mesh)   # Fill holes in the mesh 
 
            building_meshes.append(mesh) # Append to building_meshes

        else:
            continue  # Ignore other entity types         
 
  # Combine building meshes 
    if building_meshes:  # Check if there are any building meshes
        combined_building_mesh = trimesh.util.concatenate(building_meshes)

        # Scale down buildings to fit within max_dimension
        bounds = combined_building_mesh.bounds
        max_extent = np.max(bounds[1] - bounds[0]) 
        if max_extent > max_dimension:
            scale_factor = max_dimension / max_extent
            combined_building_mesh.apply_scale(scale_factor)

        # Add the combined building mesh to the final meshes list
        meshes.append(combined_building_mesh) 

    # Combine all meshes (now including both base and buildings)
    combined_mesh = trimesh.util.concatenate(meshes)

    # Export to STL
    combined_mesh.export(stl_path)

# Example usage
dxf_file = 'cadmapper-atlanta-georgia-us.dxf'
stl_file = 'output.stl'

dxf_to_extruded_stl(dxf_file, stl_file)
