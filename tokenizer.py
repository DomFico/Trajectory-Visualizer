import os
import subprocess
import tempfile
import numpy as np
import torch
import mdtraj as md
from esm.sdk import client
from esm.sdk.api import ESMProtein
from esm.utils.structure.protein_chain import ProteinChain
import Bio.PDB
import pickle
import time
from collections import defaultdict

##############################################################################
# Hard-coded ESM model token from Forge console
##############################################################################
TOKEN = "5sugG3EWDXFnxFvqaXipIV"

##############################################################################
# Initialize ESM model client
##############################################################################
esm_model = client(
    model="esm3-open-2024-03",
    url="https://forge.evolutionaryscale.ai",
    token=TOKEN
)

##############################################################################
# Residue name mapping for non-standard residues (constant pH simulations)
##############################################################################
RESNAME_MAPPING = {
    "AS4": "ASP",
    "GL4": "GLU",
    "HIP": "HIS",
    "HIE": "HIS",
    "HID": "HIS",
    "CYM": "CYS"
}

##############################################################################
# File paths
##############################################################################
DIRECTORY = "/home/dom/Desktop/Research/HalM2/CpHMD/HalM2_Zn_Mg+/Results/Trajectories"
TOPOLOGY_FILE = os.path.join(DIRECTORY, "HalM2_Zn_Mg+.parm7")
TRAJECTORY_FILE = os.path.join(DIRECTORY, "HalM2_Zn_Mg+.nc")

##############################################################################
# Global parameter: skip frames in increments of SKIP_FRAMES
##############################################################################
SKIP_FRAMES = 25

##############################################################################
# Convert .nc trajectory to .dcd using cpptraj
##############################################################################
def convert_trajectory(topology_file, trajectory_file, output_file):
    """
    Convert a NetCDF trajectory to DCD format using cpptraj.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.in', delete=False) as temp_input:
        temp_input.write(f"parm {topology_file}\n")
        temp_input.write(f"trajin {trajectory_file}\n")
        temp_input.write(f"trajout {output_file} dcd\n")
        temp_input.write("go\n")
        temp_input_path = temp_input.name

    try:
        subprocess.run(['cpptraj', '-i', temp_input_path], check=True)
        print("Conversion to DCD successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting trajectory: {e}")
        raise
    finally:
        os.unlink(temp_input_path)

##############################################################################
# Main execution
##############################################################################
if __name__ == "__main__":
    script_start_time = time.time()

    # 1) Convert .nc to .dcd
    with tempfile.NamedTemporaryFile(suffix='.dcd', delete=False) as temp_output:
        converted_trajectory = temp_output.name
    convert_trajectory(TOPOLOGY_FILE, TRAJECTORY_FILE, converted_trajectory)

    try:
        # 2) Load the trajectory
        traj = md.load(converted_trajectory, top=TOPOLOGY_FILE)
        n_frames = traj.n_frames
        print(f"Total frames: {n_frames}")

        # 3) Determine which frames to process
        frame_indices = range(0, n_frames, SKIP_FRAMES)
        print(f"Will process frames: {list(frame_indices)}")

        # Prepare a parser for PDB structures
        parser = Bio.PDB.PDBParser(QUIET=True)

        # Create a dictionary to store tokens
        tokens_dict = {}

        # We need to determine the chain ID from the first frame
        first_frame = traj[0]
        with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as tmp_pdb:
            first_frame.save_pdb(tmp_pdb.name)
            pdb_path = tmp_pdb.name

        structure = parser.get_structure('protein', pdb_path)
        os.remove(pdb_path)

        # Rename non-standard residues in the first frame
        for residue in structure.get_residues():
            original_name = residue.get_resname()
            if original_name in RESNAME_MAPPING:
                residue.resname = RESNAME_MAPPING[original_name]

        pdb_model = structure[0]
        chains = list(pdb_model.get_chains())
        if not chains:
            raise ValueError("No chains found in the protein structure.")
        chain_id = chains[0].id  # We'll assume only 1 chain for simplicity

        # 4) Iterate over selected frames
        for i in frame_indices:
            frame_start_time = time.time()

            # Extract the i-th frame from the trajectory
            frame = traj[i]

            # Save the frame to a temporary PDB for ESM encoding
            with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as tmp_pdb:
                frame.save_pdb(tmp_pdb.name)
                pdb_path = tmp_pdb.name

            try:
                # Load structure for this frame
                structure = parser.get_structure('protein', pdb_path)

                # Rename non-standard residues
                for residue in structure.get_residues():
                    original_name = residue.get_resname()
                    if original_name in RESNAME_MAPPING:
                        residue.resname = RESNAME_MAPPING[original_name]

                # Create corrected PDB for token encoding
                with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as corrected_pdb:
                    io = Bio.PDB.PDBIO()
                    io.set_structure(structure)
                    io.save(corrected_pdb.name)
                    corrected_pdb_path = corrected_pdb.name

                # (C) Encode current frame using ESM
                protein_chain = ProteinChain.from_pdb(corrected_pdb_path, chain_id=chain_id)
                protein_esm = ESMProtein.from_protein_chain(protein_chain)
                tokens = esm_model.encode(protein_esm)
                structure_tokens = tokens.structure.tolist()

                # (D) Build a sub-dictionary for this frame
                tokens_dict[i] = {}
                chain_model = structure[0][chain_id]

                # We assume chain_model.get_residues() matches the order of the MDtraj residues
                for r, residue in enumerate(chain_model.get_residues()):
                    # The PDB "res_number"
                    res_number = residue.get_id()[1]

                    tokens_dict[i][res_number] = {
                        "token": structure_tokens[r]
                    }

                    # Print statement to display info for each residue at this frame
                    print(f"Frame {i}, Residue {res_number}, Token: {structure_tokens[r]}")

                frame_end_time = time.time()
                print(f"Processed frame {i} in {frame_end_time - frame_start_time:.3f}s. Collected {len(structure_tokens)} tokens.")

            except Exception as e:
                print(f"Error processing frame {i}: {e}")
            finally:
                os.remove(pdb_path)

        # 5) Pickle the results
        pickle_file = "tokens_data2.pkl"
        with open(pickle_file, 'wb') as f:
            pickle.dump(tokens_dict, f)

        print(f"Saved tokens data to {pickle_file}")

    finally:
        # Clean up
        os.unlink(converted_trajectory)
        script_end_time = time.time()
        print(f"Total script execution time: {script_end_time - script_start_time:.3f}s")
        print("Cleaned up temporary DCD file.")
