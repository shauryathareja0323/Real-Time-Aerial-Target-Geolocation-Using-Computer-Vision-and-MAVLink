import cv2

# Try 0 first. If your capture card is not detected,
# try 1, 2, 3, etc.
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Could not open the HDMI capture device.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not receive video frame.")
        break

    # Get current frame dimensions
    height, width = frame.shape[:2]

    # Square size
    square_size = 30

    # Calculate center of screen
    center_x = width // 2
    center_y = height // 2

    # Calculate square corners
    x1 = center_x - square_size // 2
    y1 = center_y - square_size // 2
    x2 = center_x + square_size // 2
    y2 = center_y + square_size // 2

    # Draw square
    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    # Draw center point
    cv2.circle(
        frame,
        (center_x, center_y),
        4,
        (0, 0, 255),
        -1
    )

    # Display coordinates for debugging
    cv2.putText(
        frame,
        f"TL: ({x1}, {y1})",
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    cv2.imshow("FPV Camera", frame)

    # Press ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()