import cv2
from pymavlink import mavutil
import time

# ============================================================
# CONFIGURATION
# ============================================================

# HDMI capture card
CAMERA_INDEX = 1

# MAVLink connection
# Change this according to your telemetry connection.
#
# Examples:
# Windows COM port:
# "COM5"
#
# Linux:
# "/dev/ttyUSB0"
#
# UDP:
# "udp:127.0.0.1:14550"

MAVLINK_CONNECTION = "COM24"
BAUD_RATE = 57600

# Fixed box size
SQUARE_SIZE = 30

# ============================================================
# CONNECT TO CAMERA
# ============================================================

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Could not open HDMI capture card.")
    exit()

print("Camera connected.")

# ============================================================
# CONNECT TO MAVLINK
# ============================================================

print("Connecting to MAVLink...")

master = mavutil.mavlink_connection(
    MAVLINK_CONNECTION,
    baud=BAUD_RATE
)

print("Waiting for heartbeat...")

master.wait_heartbeat()

print(
    f"MAVLink connected - "
    f"System: {master.target_system}, "
    f"Component: {master.target_component}"
)

# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # READ CAMERA FRAME
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Failed to receive video frame.")
        break

    # Get frame dimensions
    height, width = frame.shape[:2]

    # --------------------------------------------------------
    # CALCULATE CENTER
    # --------------------------------------------------------

    center_x = width // 2
    center_y = height // 2

    # --------------------------------------------------------
    # CALCULATE FIXED SQUARE
    # --------------------------------------------------------

    x1 = center_x - SQUARE_SIZE // 2
    y1 = center_y - SQUARE_SIZE // 2

    x2 = center_x + SQUARE_SIZE // 2
    y2 = center_y + SQUARE_SIZE // 2

    # --------------------------------------------------------
    # DRAW RED SQUARE
    # OpenCV uses BGR
    # Red = (0, 0, 255)
    # --------------------------------------------------------

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 0, 255),
        2
    )

    # Draw center point
    cv2.circle(
        frame,
        (center_x, center_y),
        2,
        (0, 0, 255),
        -1
    )

    # --------------------------------------------------------
    # READ MAVLINK MESSAGES
    # --------------------------------------------------------

    msg = master.recv_match(
        type=[
            'GLOBAL_POSITION_INT',
            'ATTITUDE'
        ],
        blocking=False
    )

    if msg is not None:

        msg_type = msg.get_type()

        # ====================================================
        # GPS + ALTITUDE
        # ====================================================

        if msg_type == "GLOBAL_POSITION_INT":

            latitude = msg.lat / 1e7
            longitude = msg.lon / 1e7

            # Relative altitude in millimeters
            relative_altitude = msg.relative_alt / 1000.0

            # Absolute altitude in millimeters
            altitude = msg.alt / 1000.0

            print(
                f"GPS: "
                f"Lat={latitude:.7f}, "
                f"Lon={longitude:.7f} | "
                f"Relative Alt={relative_altitude:.2f} m | "
                f"Alt={altitude:.2f} m"
            )

        # ====================================================
        # ATTITUDE
        # ====================================================

        elif msg_type == "ATTITUDE":

            roll = msg.roll * 180.0 / 3.141592653589793
            pitch = msg.pitch * 180.0 / 3.141592653589793
            yaw = msg.yaw * 180.0 / 3.141592653589793

            print(
                f"ATTITUDE: "
                f"Roll={roll:.2f}° | "
                f"Pitch={pitch:.2f}° | "
                f"Yaw={yaw:.2f}°"
            )

    # --------------------------------------------------------
    # SHOW VIDEO
    # --------------------------------------------------------

    cv2.imshow("FPV Camera", frame)

    # ESC to exit
    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()

print("Program stopped.")