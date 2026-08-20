from pymavlink import mavutil

# Connect to flight controller / telemetry radio
master = mavutil.mavlink_connection(
    'COM24',
    baud=57600
)

print("Waiting for heartbeat...")

master.wait_heartbeat()

print("Connected!")
print("System:", master.target_system)
print("Component:", master.target_component)

# while True:

#     msg = master.recv_match(blocking=True)

#     if msg is not None:
#         print(msg)