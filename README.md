# Real-Time Aerial Target Geolocation Using Computer Vision and MAVLink

A real-time UAV target geolocation system that combines a live FPV camera feed with MAVLink telemetry to estimate the geographic coordinates of a point or ground target visible in the camera frame.

The system uses **OpenCV** for live video processing and **PyMAVLink** for receiving UAV telemetry, including GPS coordinates, relative altitude, roll, pitch, and yaw. Using the camera's field of view and mounting angle, the system projects the selected image point toward the ground and estimates its latitude and longitude.

---

## Features

- Live FPV/HDMI camera feed using OpenCV
- MAVLink telemetry integration using PyMAVLink
- Real-time drone GPS coordinate acquisition
- Relative altitude monitoring
- Roll, pitch, and yaw compensation
- Forward-facing camera support
- Fixed camera downward mounting angle
- Image pixel to ground-coordinate projection
- Estimated target latitude and longitude calculation
- Target coordinates displayed directly above the target box
- Real-time terminal telemetry output

---

## System Overview

```text
                  ┌─────────────────┐
                  │   FPV Camera    │
                  │   Live Video    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     OpenCV      │
                  │ Image Processing│
                  └────────┬────────┘
                           │
                    Target Pixel
                           │
                           ▼
┌─────────────────┐   ┌─────────────────┐
│ Drone Telemetry │──►│ Geolocation      │
│                 │   │ Engine           │
│ GPS             │   │                  │
│ Altitude        │   │ Camera FOV       │
│ Roll            │   │ Camera Tilt      │
│ Pitch           │   │ Ray Projection   │
│ Yaw             │   │ N/E Conversion   │
└─────────────────┘   └────────┬────────┘
                               │
                               ▼
                     Estimated Target GPS
                     Latitude / Longitude
```

---

## How It Works

The system performs the following steps:

1. Captures the live video feed from an HDMI capture device.
2. Receives UAV telemetry through a MAVLink connection.
3. Extracts:
   - Latitude
   - Longitude
   - Relative altitude
   - Roll
   - Pitch
   - Yaw
4. Defines a target point in the camera frame.
5. Converts the target pixel position into a camera viewing ray using the camera field of view.
6. Applies the fixed camera mounting angle.
7. Compensates for UAV orientation using roll, pitch, and yaw.
8. Projects the viewing ray toward the ground.
9. Calculates the target's displacement relative to the UAV.
10. Converts the North/East displacement into estimated latitude and longitude.
11. Displays the estimated coordinates on the live video feed.

---

## Camera Configuration

The current system assumes a forward-facing camera mounted with a fixed downward angle.

```python
HFOV = 90.0
VFOV = 60.0

CAMERA_TILT = 30.0
```

### Camera Tilt Convention

The camera tilt is measured relative to the drone's forward horizontal axis:

```text
Drone Forward
──────────────────────────────►
                 \
                  \
                   \ 30°
                    \
                     ▼
                  Camera View
```

Therefore:

- `0°` → Camera points straight forward
- `30°` → Camera points 30° downward from horizontal
- `90°` → Camera points directly downward

> The field-of-view values are initial estimates and should be calibrated for improved accuracy.

---

## Technologies Used

- Python
- OpenCV
- PyMAVLink
- MAVLink Protocol
- GPS Coordinate Systems
- Computer Vision
- UAV Telemetry
- Geometric Ray Projection

---

## Hardware Requirements

- UAV with MAVLink-compatible flight controller
- GPS module
- Telemetry connection
- Forward-facing FPV/HD camera
- HDMI capture card
- Computer or ground control station

---

## Software Requirements

- Python 3.x
- OpenCV
- PyMAVLink

Install the required dependencies:

```bash
pip install opencv-python pymavlink
```

---

## MAVLink Configuration

Update the MAVLink connection according to your telemetry setup.

### Windows Serial Connection

```python
MAVLINK_CONNECTION = "COM24"
BAUD_RATE = 57600
```

### Linux Serial Connection

```python
MAVLINK_CONNECTION = "/dev/ttyUSB0"
BAUD_RATE = 57600
```

### UDP Connection

```python
MAVLINK_CONNECTION = "udp:127.0.0.1:14550"
```

---

## Camera Configuration

Select the appropriate camera index:

```python
CAMERA_INDEX = 1
```

If the camera does not open, try:

```python
CAMERA_INDEX = 0
```

or another available camera index.

---

## Running the Project

Clone the repository:

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

Press `ESC` to close the application.

---

## Expected Output

The application displays a live FPV camera feed with a target box in the center.

```text
       Lat: 30.1234567
       Lon: 77.1234567

             ┌──────┐
             │   •  │
             │TARGET│
             │      │
             └──────┘
```

The terminal displays real-time telemetry:

```text
DRONE:
Lat = 30.xxxxxxx
Lon = 77.xxxxxxx
Altitude = 50.00 m

ATTITUDE:
Roll = 2.50°
Pitch = -3.20°
Yaw = 125.40°

TARGET:
Lat = 30.xxxxxxx
Lon = 77.xxxxxxx

North Offset = XX.XX m
East Offset = XX.XX m
```

---

## Coordinate Estimation

The target position is estimated by combining:

```text
Camera Target Pixel
        +
Camera Field of View
        +
Camera Mounting Angle
        +
Drone Roll
        +
Drone Pitch
        +
Drone Yaw
        +
Drone GPS Position
        +
Relative Altitude
        │
        ▼
Estimated Ground Position
        │
        ▼
Target Latitude / Longitude
```

The local North/East displacement is converted into geographic coordinates using an approximate local Earth model.

---

## Project Structure

```text
Aerial-Target-Geolocation/
│
├── mainv2.py
├── README.md
└── requirements.txt
```

Example `requirements.txt`:

```text
opencv-python
pymavlink
```

---

## Current Limitations

The calculated target coordinates are estimates and can be affected by:

- GPS accuracy
- Compass/yaw accuracy
- Relative altitude accuracy
- Camera mounting angle error
- Camera field-of-view estimation
- Camera lens distortion
- UAV vibration
- Telemetry latency
- Non-flat terrain
- Camera-to-GPS physical offset

The current implementation assumes that the target lies on an approximately flat ground plane.

---

## Future Improvements

- [ ] Automatic object detection using YOLO
- [ ] Dynamic target bounding boxes
- [ ] Camera calibration using intrinsic parameters
- [ ] Lens distortion correction
- [ ] Digital Elevation Model (DEM) integration
- [ ] Terrain-aware ray intersection
- [ ] RTK GPS support
- [ ] Gimbal angle integration
- [ ] Target tracking across frames
- [ ] Kalman filtering for smoother target coordinates
- [ ] Click-to-select target coordinates
- [ ] Map-based target visualization
- [ ] Target coordinate logging
- [ ] Multiple target support

---

## Disclaimer

This project is intended for educational, research, and civilian UAV/computer vision applications. The estimated coordinates should be independently validated before use in any situation requiring high positional accuracy or safety-critical decision-making.

---

## Author

**Shaurya Thareja**
