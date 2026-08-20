import cv2
from pymavlink import mavutil
import time
import math

# ============================================================
# CONFIGURATION
# ============================================================

# HDMI capture card
CAMERA_INDEX = 1

# MAVLink connection
MAVLINK_CONNECTION = "COM24"
BAUD_RATE = 57600

# Fixed red box size
SQUARE_SIZE = 30

# ============================================================
# CAMERA PARAMETERS
# ============================================================

# Initial estimated camera FOV
# We can calibrate these later
HFOV = 90.0
VFOV = 60.0

# Camera is tilted 30 degrees downward
CAMERA_TILT = 30.0


# ============================================================
# FUNCTION:
# CALCULATE TARGET GPS
# ============================================================

def calculate_target_gps(
    drone_lat,
    drone_lon,
    altitude,
    roll,
    pitch,
    yaw,
    frame_width,
    frame_height,
    target_x,
    target_y
):

    # --------------------------------------------------------
    # Convert angles to radians
    # --------------------------------------------------------

    roll_rad = math.radians(roll)
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)

    hfov_rad = math.radians(HFOV)
    vfov_rad = math.radians(VFOV)

    camera_tilt_rad = math.radians(CAMERA_TILT)

    # --------------------------------------------------------
    # Pixel position relative to image center
    # --------------------------------------------------------

    pixel_x = target_x - frame_width / 2
    pixel_y = target_y - frame_height / 2

    # --------------------------------------------------------
    # Convert pixel displacement to angular displacement
    # --------------------------------------------------------

    horizontal_angle = (
        pixel_x / frame_width
    ) * hfov_rad

    vertical_angle = (
        pixel_y / frame_height
    ) * vfov_rad

    # --------------------------------------------------------
    # Camera coordinate system
    #
    # X = forward
    # Y = right
    # Z = down
    #
    # Camera is looking forward.
    # --------------------------------------------------------

    ray_x = 1.0
    ray_y = math.tan(horizontal_angle)
    ray_z = math.tan(vertical_angle)

    # --------------------------------------------------------
    # Normalize ray
    # --------------------------------------------------------

    magnitude = math.sqrt(
        ray_x**2 +
        ray_y**2 +
        ray_z**2
    )

    ray_x /= magnitude
    ray_y /= magnitude
    ray_z /= magnitude

    # --------------------------------------------------------
    # Apply camera downward tilt
    #
    # Positive CAMERA_TILT means camera points downward.
    # --------------------------------------------------------

    forward = (
        ray_x * math.cos(camera_tilt_rad)
        - ray_z * math.sin(camera_tilt_rad)
    )

    down = (
        ray_x * math.sin(camera_tilt_rad)
        + ray_z * math.cos(camera_tilt_rad)
    )

    right = ray_y

    # --------------------------------------------------------
    # Convert camera coordinates to BODY coordinates
    #
    # BODY:
    # X = forward
    # Y = right
    # Z = down
    # --------------------------------------------------------

    body_x = forward
    body_y = right
    body_z = down

    # --------------------------------------------------------
    # Apply aircraft roll
    # --------------------------------------------------------

    y1 = (
        body_y * math.cos(roll_rad)
        - body_z * math.sin(roll_rad)
    )

    z1 = (
        body_y * math.sin(roll_rad)
        + body_z * math.cos(roll_rad)
    )

    x1 = body_x

    # --------------------------------------------------------
    # Apply aircraft pitch
    # --------------------------------------------------------

    x2 = (
        x1 * math.cos(pitch_rad)
        + z1 * math.sin(pitch_rad)
    )

    z2 = (
        -x1 * math.sin(pitch_rad)
        + z1 * math.cos(pitch_rad)
    )

    y2 = y1

    # --------------------------------------------------------
    # z2 must point DOWN toward the ground
    # --------------------------------------------------------

    if z2 <= 0:

        return None

    # --------------------------------------------------------
    # Find intersection with ground
    #
    # altitude = vertical distance to ground
    #
    # distance along ray:
    #
    # distance = altitude / z_component
    # --------------------------------------------------------

    ground_distance = altitude / z2

    # --------------------------------------------------------
    # Calculate displacement in aircraft frame
    # --------------------------------------------------------

    forward_distance = x2 * ground_distance
    right_distance = y2 * ground_distance

    # --------------------------------------------------------
    # Convert aircraft-relative coordinates
    # to North/East coordinates using yaw
    # --------------------------------------------------------

    north = (
        forward_distance * math.cos(yaw_rad)
        - right_distance * math.sin(yaw_rad)
    )

    east = (
        forward_distance * math.sin(yaw_rad)
        + right_distance * math.cos(yaw_rad)
    )

    # --------------------------------------------------------
    # Convert meters to latitude / longitude
    # --------------------------------------------------------

    meters_per_degree_lat = 111320.0

    meters_per_degree_lon = (
        111320.0 *
        math.cos(math.radians(drone_lat))
    )

    target_lat = (
        drone_lat +
        north / meters_per_degree_lat
    )

    target_lon = (
        drone_lon +
        east / meters_per_degree_lon
    )

    # --------------------------------------------------------
    # Return everything
    # --------------------------------------------------------

    return (
        target_lat,
        target_lon,
        north,
        east,
        forward_distance,
        right_distance,
        ground_distance
    )


# ============================================================
# CONNECT TO CAMERA
# ============================================================

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)

if not cap.isOpened():

    print(
        "ERROR: Could not open HDMI capture card."
    )

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
# VARIABLES
# ============================================================

latitude = None
longitude = None
relative_altitude = None

roll = 0.0
pitch = 0.0
yaw = 0.0


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # READ CAMERA FRAME
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print(
            "ERROR: Failed to receive video frame."
        )

        break

    height, width = frame.shape[:2]


    # ========================================================
    # CALCULATE CENTER OF IMAGE
    # ========================================================

    center_x = width // 2
    center_y = height // 2


    # ========================================================
    # CALCULATE RED SQUARE
    # ========================================================

    x1 = (
        center_x -
        SQUARE_SIZE // 2
    )

    y1 = (
        center_y -
        SQUARE_SIZE // 2
    )

    x2 = (
        center_x +
        SQUARE_SIZE // 2
    )

    y2 = (
        center_y +
        SQUARE_SIZE // 2
    )


    # ========================================================
    # DRAW RED SQUARE
    # ========================================================

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


    # ========================================================
    # READ MAVLINK
    # ========================================================

    while True:

        msg = master.recv_match(
            type=[
                'GLOBAL_POSITION_INT',
                'ATTITUDE'
            ],
            blocking=False
        )

        if msg is None:
            break

        msg_type = msg.get_type()


        # ====================================================
        # GPS
        # ====================================================

        if msg_type == "GLOBAL_POSITION_INT":

            latitude = msg.lat / 1e7

            longitude = msg.lon / 1e7

            relative_altitude = (
                msg.relative_alt / 1000.0
            )


        # ====================================================
        # ATTITUDE
        # ====================================================

        elif msg_type == "ATTITUDE":

            roll = (
                msg.roll *
                180.0 /
                math.pi
            )

            pitch = (
                msg.pitch *
                180.0 /
                math.pi
            )

            yaw = (
                msg.yaw *
                180.0 /
                math.pi
            )

            # Convert yaw from -180..180
            # to 0..360

            if yaw < 0:
                yaw += 360


    # ========================================================
    # CALCULATE TARGET GPS
    # ========================================================

    if (
        latitude is not None
        and longitude is not None
        and relative_altitude is not None
        and relative_altitude > 0
    ):

        result = calculate_target_gps(

            latitude,
            longitude,
            relative_altitude,

            roll,
            pitch,
            yaw,

            width,
            height,

            center_x,
            center_y
        )


        # ====================================================
        # CHECK RESULT
        # ====================================================

        if result is not None:

            (
                target_lat,
                target_lon,
                north,
                east,
                forward_distance,
                right_distance,
                ground_distance
            ) = result


            # =================================================
            # PRINT TELEMETRY
            # =================================================

            print(
                f"\r"
                f"DRONE: "
                f"Lat={latitude:.7f} "
                f"Lon={longitude:.7f} "
                f"Alt={relative_altitude:.2f}m | "

                f"R={roll:.2f}° "
                f"P={pitch:.2f}° "
                f"Y={yaw:.2f}° | "

                f"TARGET: "
                f"Lat={target_lat:.7f} "
                f"Lon={target_lon:.7f} | "

                f"N={north:.2f}m "
                f"E={east:.2f}m | "

                f"D={ground_distance:.2f}m",
                end=""
            )


            # =================================================
            # DISPLAY TARGET GPS ON VIDEO
            # =================================================

            cv2.putText(
                frame,
                f"Target Lat: {target_lat:.7f}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Target Lon: {target_lon:.7f}",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Distance: {ground_distance:.2f} m",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Alt: {relative_altitude:.2f} m",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )


    # ========================================================
    # SHOW VIDEO
    # ========================================================

    cv2.imshow(
        "FPV Camera",
        frame
    )


    # ========================================================
    # ESC TO EXIT
    # ========================================================

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

print("\nProgram stopped.")