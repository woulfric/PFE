from dronekit import VehicleMode, connect, Command
from pymavlink import mavutil
import time
import csv
import random

# connect to sitl
connection_string = "tcp:127.0.0.1:5760"
print(f">> connecting to vehicle at {connection_string}")
vehicle = connect(connection_string, wait_ready=True)
print(">> vehicle connected")

# do pre-arm checks
print(">> basic pre-arm checks")
waiting = False
while not vehicle.is_armable:
    print(">> waiting for vehicle to initialize...")
    time.sleep(1)
print(">> vehicle is armable")

# upload mission commands to vehicle
commands = vehicle.commands
commands.download()
commands.wait_ready()
commands.clear()

error_threshold_x = random.uniform(-0.000010, 0.000010)
error_threshold_y = random.uniform(-0.000010, 0.000010)
error_threshold_z = random.uniform(-3, 3)

mission = [
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.71570587158203, 3.1848137378692627, 20),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.715606689453125, 3.1846301555633545, 20),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.71611404418945, 3.184183120727539, 20),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.71492004394531, 3.181950330734253, 60),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.7148323059082, 3.1817564964294434, 60),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.71457290649414, 3.181494951248169, 20),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.71440124511719, 3.181600332260132, 20),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.7140998840332, 3.1810216903686523, 20),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 36.71393585205078, 3.180666923522949, 20),
    Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 36.71421432495117, 3.1803975105285645, 0),
]

for command in mission:
    command.x += error_threshold_x
    command.y += error_threshold_y
    command.z += error_threshold_z
    commands.add(command)
commands.upload()

print(">> Commands uploaded successfully")

# takeoff
print(">> Preparing takeoff")
print(">> Arming motors")
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True

while not vehicle.armed:
    print(">> Waiting for arming...")
    time.sleep(1)

# setup logging
f = open("data.csv", "a")
field_names = [
    "timestamp",
    "pitch",
    "yaw",
    "roll",
    "lat",
    "lon",
    "alt",
    "velocity_x",
    "velocity_y",
    "velocity_z",
    "battery",
    "heading",
    "airspeed",
    "groundspeed",
]

writer = csv.DictWriter(f, fieldnames=field_names)
writer.writeheader()

print(">> Mission started")
print(">> Taking off")
cmds = vehicle.commands
target_altitude = 20 + error_threshold_z
vehicle.simple_takeoff(target_altitude)

while True:
    if vehicle.location.global_frame.alt >= target_altitude * 0.95:
        print(">> Reached target altitude")
        break
    time.sleep(1)

vehicle.mode = VehicleMode("AUTO")

timestamp = 0
while True:
    writer.writerow(
        {
            "timestamp": timestamp,
            "pitch": vehicle.attitude.pitch,
            "yaw": vehicle.attitude.yaw,
            "roll": vehicle.attitude.roll,
            "lat": vehicle.location.global_frame.lat,
            "lon": vehicle.location.global_frame.lon,
            "alt": vehicle.location.global_frame.alt,
            "velocity_x": vehicle.velocity[0],
            "velocity_y": vehicle.velocity[1],
            "velocity_z": vehicle.velocity[2],
            "battery": vehicle.battery.level,
            "heading": vehicle.heading,
            "airspeed": vehicle.airspeed,
            "groundspeed": vehicle.groundspeed,
        }
    )

    if(vehicle.commands.next == vehicle.commands.count):
        print("done")
        break

    time.sleep(0.2)
    timestamp += 1

f.close()
vehicle.close()


