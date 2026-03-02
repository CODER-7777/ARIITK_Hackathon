import cv2
import numpy as np
import sys

# Fixed camera constants
FOCAL_LENGTH_MM    = 3.04
SENSOR_WIDTH_MM    = 3.68
RESOLUTION_PX      = 1920
MARKER_REAL_SIZE_M = 1.0


def get_pixels_at_altitude(altitude_m):
    pixels = (FOCAL_LENGTH_MM * MARKER_REAL_SIZE_M * RESOLUTION_PX) / \
             (altitude_m * SENSOR_WIDTH_MM)
    return max(int(pixels), 10)


def simulate(image_path, altitude_m):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"ERROR: Cannot load {image_path}")
        sys.exit(1)

    original_size = (img.shape[1], img.shape[0])
    marker_pixels = get_pixels_at_altitude(altitude_m)

    print(f"\nAltitude    : {altitude_m} metres")
    print(f"Sensor size : {marker_pixels} × {marker_pixels} pixels")

    # Shrink to simulate distance
    drone_view = cv2.resize(img, (marker_pixels, marker_pixels),
                            interpolation=cv2.INTER_AREA)

    # Atmospheric blur above 10m
    if altitude_m > 10:
        drone_view = cv2.GaussianBlur(drone_view, (3, 3), 0)
        print(f"Blur        : applied (altitude > 10m)")
    else:
        print(f"Blur        : none")

    # Scale back up for human viewing
    display = cv2.resize(drone_view, original_size,
                         interpolation=cv2.INTER_NEAREST)

    cv2.imshow(f"Drone View @ {altitude_m}m  ({marker_pixels}px on sensor)", display)
    print(f"Press any key to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage  : python simulator.py <image> <altitude_metres>")
        print("Example: python simulator.py hybrid_marker.png 30")
        print("")
        print("Suggested altitudes to test:")
        print("  python simulator.py hybrid_marker.png 100")
        print("  python simulator.py hybrid_marker.png 30")
        print("  python simulator.py hybrid_marker.png 15")
        print("  python simulator.py hybrid_marker.png 5")
        print("  python simulator.py hybrid_marker.png 2")
        sys.exit(1)

    simulate(sys.argv[1], float(sys.argv[2]))