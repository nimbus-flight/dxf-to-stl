import ezdxf
import trimesh
import numpy as np
import shapely.geometry  # Import the shapely.geometry module


def dxf_to_extruded_stl(dxf_path, stl_path, max_dimension=180.0):
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
            trimesh.repair.fix_normals(mesh) # Fix face normals

            building_meshes.append(mesh) # Append to building_meshes

        else:
            continue  # Ignore other entity types         
 
    # Combine building meshes 
    combined_building_mesh = trimesh.util.concatenate(building_meshes)

    # Scale down buildings to fit within max_dimension
    bounds = combined_building_mesh.bounds
    max_extent = np.max(bounds[1] - bounds[0]) 
    if max_extent > max_dimension:
        scale_factor = max_dimension / max_extent
        combined_building_mesh.apply_scale(scale_factor)

    # Add the combined building mesh to the final meshes list
    meshes.append(combined_building_mesh) 
    
    # Repair the combined building mesh to fix common issues
    # 1. Fix normals and winding order
    trimesh.repair.fix_normals(combined_building_mesh)
    trimesh.repair.fix_winding(combined_building_mesh) 

    # 2. Fill smaller holes (be careful as this can change the mesh shape)
    combined_building_mesh.fill_holes()


    # Center the combined building mesh (in X and Y only) before creating the base
    combined_building_mesh.apply_translation(
        [-combined_building_mesh.centroid[0], -combined_building_mesh.centroid[1], 0]
    )


    # Create the base layer mesh (centered at Z=0)
    base_thickness = 4.0  # Adjust base thickness as needed
    base_mesh = trimesh.creation.box(
        extents=[max_dimension*1.2, max_dimension*1.2, base_thickness],
        center=[0, 0, 0],
    )

     # Lower the combined building mesh by a small amount
    lowering_amount = -1.0  # Lower by 1.0mm
    combined_building_mesh.vertices[:, 2] += lowering_amount  


    # Find the lowest Z value in the combined building mesh
    #lowest_z = combined_building_mesh.bounds[0][2]  # Get Z from lower corner of bounding box
    # Find the LOWEST point of the lowered building mesh
    lowest_building_z = np.min(combined_building_mesh.vertices[:, 2]) 

    # Create a boolean union of the base and buildings 
    #boolean_result = base_mesh.union(combined_building_mesh)

    # The boolean union should have resulted in a single mesh. Extract the mesh and fix normals.
    #combined_mesh = boolean_result.result
    #combined_mesh.fix_normals()
    combined_mesh = trimesh.util.concatenate([base_mesh, combined_building_mesh])
    # Export to STL
    combined_mesh.export(stl_path)

# Example usage
dxf_file = 'cadmapper-atlanta-georgia-us.dxf'
stl_file = 'output.stl'

dxf_to_extruded_stl(dxf_file, stl_file)
