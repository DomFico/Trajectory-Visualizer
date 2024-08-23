import mdtraj as md
import numpy as np
from netCDF4 import Dataset
import os

# A simple utility function to map atom names to element symbols
def atom_name_to_element(atom_name):
    element_mapping = {
        'N': 'N', 'C': 'C', 'H': 'H', 'O': 'O', 'S': 'S',
        # Add other atom types if necessary, handle generic names
    }
    # Extract the first character (assuming it's the element) and map it
    element = atom_name[0].upper()
    return element_mapping.get(element, 'X')  # Default to 'X' if not found

def convert_parm7_nc_to_xyz(parm7_file, nc_file, output_xyz_dir, num_frames=10):
    # Create the output directory if it doesn't exist
    os.makedirs(output_xyz_dir, exist_ok=True)

    # Load topology using MDTraj (for atom names)
    topology = md.load_topology(parm7_file)

    # Manually load the NetCDF file using netCDF4
    nc_data = Dataset(nc_file)

    # Check how many frames are in the file
    total_frames = nc_data.variables['coordinates'].shape[0]
    frames_to_extract = min(num_frames, total_frames)

    # Get the atom names from the topology and map them to element symbols
    atom_elements = [atom_name_to_element(atom.name) for atom in topology.atoms]

    # Iterate over the first `num_frames` frames and write separate XYZ files
    for frame_idx in range(frames_to_extract):
        # Extract atom positions for the current frame from the NetCDF file
        coordinates_nm = np.array(nc_data.variables['coordinates'][frame_idx])
        coordinates_angstrom = coordinates_nm  # Assume it's already in Angstroms

        # Create the filename for the current frame
        output_xyz_file = os.path.join(output_xyz_dir, f"frame_{frame_idx + 1}.xyz")

        # Write to the XYZ file
        with open(output_xyz_file, 'w') as f:
            # Number of atoms
            f.write(f"{len(atom_elements)}\n")
            # Comment line
            f.write(f"Frame {frame_idx + 1} from {nc_file}, converted to XYZ\n")
            # Write each atom's element and its coordinates in Angstroms
            for atom_element, coords in zip(atom_elements, coordinates_angstrom):
                f.write(f"{atom_element} {coords[0]:.8f} {coords[1]:.8f} {coords[2]:.8f}\n")

        print(f"Frame {frame_idx + 1} saved as {output_xyz_file}")

    print(f"Conversion of {frames_to_extract} frames complete.")

# Example usage
parm7_file = '/home/dom/Desktop/Research/HalM2/CpHMD/THR42/no_loop/Results/THR42_no_loop.parm7'
nc_file = '/home/dom/Desktop/Research/HalM2/CpHMD/THR42/no_loop/Results/THR42_no_loop.nc'
output_xyz_dir = '/home/dom/Desktop/Coding/protein_website_2/xyz/'

convert_parm7_nc_to_xyz(parm7_file, nc_file, output_xyz_dir, num_frames=10)
