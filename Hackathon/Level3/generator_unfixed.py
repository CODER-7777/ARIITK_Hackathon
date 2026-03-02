# This is the unfixed version of the generator.py code
# Hybrid Marker Generator — IT IS DELIBERATELY POORLY TUNED
# Your job is to fix the sigma values using the Pinhole Camera Model math
#
# Usage  : python generator.py <far_img> <near_img> <aruco_id> <output>
# Example: python generator.py far_target_decoy.png aruco_markers/aruco_id_37.png 37 hybrid_marker.png

import cv2
import numpy as np
import sys


def create_hybrid_marker(far_path, near_path, aruco_id, output_path,
                          sigma_low=5, sigma_high=4):
    """
    Creates a Hybrid Marker by combining a far (decoy) image and a near (ArUco) image
    using spatial frequency filtering.

    ┌─────────────────────────────────────────────────────────────┐
    │  WARNING — sigma_low=5 and sigma_high=4 are             |
    │  INTENTIONALLY WRONG.                                       │
    │                                                             │
    │  These values are too close together. This causes heavy     │
    │  ghosting — the ArUco grid will bleed through into the      │
    │  high-altitude decoy view and you will fail the visual      │
    │  quality criterion.                                         │
    │                                                             │
    │  YOUR JOB:                                                  │
    │  Calculate the correct sigma values using the Pinhole       │
    │  Camera Model. Show your working in report.pdf.             │
    │  Guessed values without math proof get zero marks.          │
    │                                                             │
    │  HINT:                                                      │
    │  Start by calculating how many pixels one ArUco grid        │
    │  bit occupies in the 512×512 source image.                  │
    │  sigma_low should be significantly larger than sigma_high.  │
    └─────────────────────────────────────────────────────────────┘

    Parameters:
        far_path   : Path to the decoy image (H helipad symbol)
        near_path  : Path to the ArUco marker image
        aruco_id   : The ArUco ID being encoded (for reporting only)
        output_path: Output filename for the hybrid marker
        sigma_low  : Gaussian sigma for low-pass filter on decoy  ← FIX THIS
        sigma_high : Gaussian sigma for high-pass filter on ArUco ← FIX THIS
    """

    print(f"\n--- Hybrid Marker Generator ---")
    print(f"Far image  (decoy)  : {far_path}")
    print(f"Near image (ArUco)  : {near_path}")
    print(f"ArUco ID            : {aruco_id}")
    print(f"sigma_low           : {sigma_low}  ← fix this")
    print(f"sigma_high          : {sigma_high}  ← fix this")
    print(f"")

    #Load both images as grayscale
    far_img  = cv2.imread(far_path,  cv2.IMREAD_GRAYSCALE)
    near_img = cv2.imread(near_path, cv2.IMREAD_GRAYSCALE)

    if far_img is None:
        print(f"ERROR: Cannot load {far_path}")
        sys.exit(1)
    if near_img is None:
        print(f"ERROR: Cannot load {near_path}")
        sys.exit(1)

    #Resize both to 512×512, convert to float32 for precision
    far_img  = cv2.resize(far_img,  (512, 512)).astype(np.float32)
    near_img = cv2.resize(near_img, (512, 512)).astype(np.float32)

    #STEP 1: Low-pass filter on the FAR image (decoy)
    # Keeps only blurry general shape — removes all fine detail
    # sigma_low controls how aggressively fine detail is removed
    low_pass = cv2.GaussianBlur(far_img, (0, 0), sigmaX=sigma_low)

    #STEP 2: High-pass filter on the NEAR image (ArUco)
    # Extracts only sharp edges: Original minus Blurred version
    # sigma_high controls how much edge detail is preserved
    blurred_near = cv2.GaussianBlur(near_img, (0, 0), sigmaX=sigma_high)
    high_pass    = near_img - blurred_near

    #STEP 3: Combine both filtered images
    hybrid = low_pass + high_pass

    #STEP 4: Clip to valid 0–255 pixel range
    hybrid = np.clip(hybrid, 0, 255).astype(np.uint8)

    cv2.imwrite(output_path, hybrid)
    print(f"Hybrid marker saved → {output_path}")
    print(f"")
    print(f"Next steps:")
    print(f"  python simulator.py {output_path} 30   ← should show H symbol, no ArUco")
    print(f"  python simulator.py {output_path} 2    ← should show ArUco clearly")
    print(f"  python visual_check.py {output_path} {far_path}   ← check ghosting score")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage  : python generator.py <far_img> <near_img> <aruco_id> <output>")
        print("Example: python generator.py far_target_decoy.png aruco_markers/aruco_id_37.png 37 hybrid_marker.png")
        sys.exit(1)

    create_hybrid_marker(
        far_path    = sys.argv[1],
        near_path   = sys.argv[2],
        aruco_id    = int(sys.argv[3]),
        output_path = sys.argv[4]
    )