"""
Download MEC recording data from Dryad repository.
Data: Gardner et al. (2021), https://doi.org/10.5061/dryad.9s4mw6mh0
"""

import os, sys, json, hashlib, urllib.request

DATA_DIR = 'tier2_data'
os.makedirs(DATA_DIR, exist_ok=True)

DRYAD_BASE = 'https://datadryad.org/stash/downloads/file_stream/'

MANIFEST = {
    'Goa_1207_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_1',
    'Goa_1209_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_2',
    'Goa_1210_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_3',
    'Goa_1211_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_4',
    'Kerala_1207_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_5',
    'Kerala_1208_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_6',
    'Kerala_1209_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_7',
    'Kerala_1210_2_MEC_FRtensor.npy': 'DRYAD_FILE_ID_8',
    'Kerala_1211_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_9',
    'Kerala_1213_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_10',
    'Mumbai_1125_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_11',
    'Mumbai_1129_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_12',
    'Mumbai_1130_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_13',
    'Mumbai_1201_1_MEC_FRtensor.npy': 'DRYAD_FILE_ID_14',
    'Calais_0713_2_MEC_FRtensor.npy': 'DRYAD_FILE_ID_15',
    'Hanover_0615_2_MEC_FRtensor.npy': 'DRYAD_FILE_ID_16',
}

def main():
    print("Download MEC recordings from Dryad.")
    print(f"Target directory: {DATA_DIR}/")
    print()

    # In a real deployment, fetch the Dryad file listing first.
    # For now, instruct the user to download manually or populate
    # the manifest with actual Dryad file stream IDs.
    print("ERROR: Dryad file stream IDs must be populated in the MANIFEST.")
    print()
    print("To obtain the data manually:")
    print(f"  1. Visit https://doi.org/10.5061/dryad.9s4mw6mh0")
    print(f"  2. Download the MEC FRtensor .npy files")
    print(f"  3. Place them in {DATA_DIR}/")
    print()
    print("Required files (14 recordings):")
    for fname in sorted(MANIFEST):
        print(f"  - {fname}")
    print()
    print("Alternative: Contact the corresponding author of")
    print("Gardner et al. (2021) for data access instructions.")

    download = input("Enter Dryad file stream IDs to populate manifest, or press Enter to skip: ")
    if download.strip():
        print("Automatic download not yet implemented for this manifest format.")
        print("See download_low2021.py in the original project for reference.")


if __name__ == '__main__':
    main()
