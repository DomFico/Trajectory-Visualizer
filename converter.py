import mdtraj as md
import os
import pickle

def convert_parm7_nc_to_pdb(parm7_file, nc_file, output_pdb_dir, token_file):
    """
    Convert `.parm7` and `.nc` trajectory files to `.pdb` format based on `.pkl` token data.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_pdb_dir, exist_ok=True)

    # Load the trajectory using MDTraj
    traj = md.load(nc_file, top=parm7_file)

    # Load token data from the `.pkl` file
    with open(token_file, 'rb') as f:
        token_data = pickle.load(f)

    # Extract and save only the frames specified in the `.pkl` file
    for frame_idx in token_data.keys():
        # Slice the trajectory for the current frame
        frame = traj.slice(frame_idx, copy=True)

        # Output file path
        output_pdb_file = os.path.join(output_pdb_dir, f"frame_{frame_idx}.pdb")

        # Save the frame as a PDB
        frame.save(output_pdb_file)
        print(f"Frame {frame_idx} saved as {output_pdb_file}")

    print(f"Conversion of specified frames to PDB complete.")

# Example usage
parm7_file = '/home/dom/Desktop/Research/HalM2/CpHMD/HalM2_Zn_Mg+/Results/Trajectories/HalM2_Zn_Mg+.parm7'
nc_file = '/home/dom/Desktop/Research/HalM2/CpHMD/HalM2_Zn_Mg+/Results/Trajectories/HalM2_Zn_Mg+.nc'
output_pdb_dir = '/home/dom/Desktop/Coding/protein_website_2/pdb/'
token_file = '/home/dom/Desktop/Research/HalM2/D2O/D2O_7.0/tokens_data1.pkl'

convert_parm7_nc_to_pdb(parm7_file, nc_file, output_pdb_dir, token_file)
