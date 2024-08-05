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


    # Create a base layer (adjust dimensions and thickness as needed)
    base_width = 200.0
    base_length = 200.0
    base_thickness = 4.0 
    base_mesh = trimesh.creation.box(extents=[base_width, base_length, base_thickness])

    meshes.append(base_mesh)  # Add the base mesh first

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


            # Check if the mesh is a valid volume
            #if not mesh.is_volume:
            #    print(f"Skipping invalid MESH entity (not a volume): {entity}")
            #    continue 

            # Attempt to repair the combined mesh
            trimesh.repair.fix_winding(mesh)  # Fix winding order if needed
            trimesh.repair.fill_holes(mesh)   # Fill holes in the mesh 
 
            # Translate the mesh upwards to sit on top of the base layer
            lowest_z = np.min(mesh.vertices[:, 2])  # Find the lowest Z-coordinate in the building mesh
            translation_vector = [0, 0, base_thickness - lowest_z]
            mesh.apply_translation(translation_vector)

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

        # Center the buildings on the base (horizontally only)
        base_centroid_xy = base_mesh.centroid[:2]  # Get only x and y components of the base centroid
        building_centroid_xy = combined_building_mesh.centroid[:2]
        translation_vector_xy = base_centroid_xy - building_centroid_xy 
        combined_building_mesh.apply_translation([translation_vector_xy[0], translation_vector_xy[1], 0])

        # Add the combined building mesh to the final meshes list
        meshes.append(combined_building_mesh) 

    # Combine all meshes (now including both base and buildings)
    combined_mesh = trimesh.util.concatenate(meshes)

    # Export to STL
    combined_mesh.export(stl_path)

# Example usage
dxf_file = 'cadmapper-atlanta-georgia-us.dxf'
stl_file = 'output.stl'
#extrusion_height = 50.0  # Adjust as needed

dxf_to_extruded_stl(dxf_file, stl_file)
