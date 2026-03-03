import socket
import time
import sys
import os
import traceback

# Add the proto_generated directory to the path so internal imports work
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "proto_generated"))
)

try:
    from control.vision.proto_generated import grSim_Packet_pb2 as grSim_Packet
    from control.vision.proto_generated import ssl_vision_wrapper_pb2 as ssl_wrapper

    print("Protobuf modules loaded successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure all _pb2.py files are in controle/vision/proto_generated/")
    sys.exit(1)

# --- Configuration ---
VISION_PORT = 10020  # SSL-Vision multicast port
COMMAND_PORT = 20011  # Your specific grSim Command port
GRSIM_IP = "127.0.0.1"
VISION_IP = "224.5.23.2"  # Standard SSL-Vision Multicast IP


def send_robot_command(robot_id, vx=0.0, vy=0.0, vw=0.0, is_yellow=False):
    """Sends a velocity command (m/s) to grSim."""
    server_address = (GRSIM_IP, COMMAND_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    packet = grSim_Packet.grSim_Packet()
    packet.commands.isteamyellow = is_yellow
    packet.commands.timestamp = time.time()

    robot_cmd = packet.commands.robot_commands.add()
    robot_cmd.id = robot_id
    robot_cmd.kickspeedx = 0
    robot_cmd.kickspeedz = 0
    robot_cmd.veltangent = vx
    robot_cmd.velnormal = vy
    robot_cmd.velangular = vw
    robot_cmd.spinner = False
    robot_cmd.wheelsspeed = False

    sock.sendto(packet.SerializeToString(), server_address)


def listen_to_vision():
    """Listens to SSL-Vision and controls the robot."""
    # Create the UDP socket for multicast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("", VISION_PORT))
    except Exception as e:
        print(f"Failed to bind to port {VISION_PORT}: {e}")
        return

    # Join the multicast group
    mreq = socket.inet_aton(VISION_IP) + socket.inet_aton("0.0.0.0")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening for vision data on {VISION_IP}:{VISION_PORT}...")

    # Instantiate the wrapper object ONCE outside the loop
    wrapper = ssl_wrapper.SSL_WrapperPacket()

    last_command_time = 0

    try:
        while True:
            # Set a timeout so we know if we aren't receiving anything
            sock.settimeout(2.0)
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                print("Warning: No vision packets received for 2 seconds.")
                continue

            # Parse the incoming bytes
            wrapper.ParseFromString(data)

            if wrapper.HasField("detection"):
                frame = wrapper.detection

                # --- Ball Info ---
                for ball in frame.balls:
                    # Print ball position (converted to meters)
                    print(f"[Ball] X: {ball.x/1000:.2f}m | Y: {ball.y/1000:.2f}m")

                # --- Blue Team Info ---
                for robot in frame.robots_blue:
                    print(
                        f"[Blue {robot.robot_id}] X: {robot.x/1000:.2f}m | Y: {robot.y/1000:.2f}m"
                    )
                    if robot.robot_id == 0:
                        send_robot_command(0, vx=0.5, is_yellow=False)

                # --- Yellow Team Info ---
                for robot in frame.robots_yellow:
                    print(
                        f"[Yellow {robot.robot_id}] X: {robot.x/1000:.2f}m | Y: {robot.y/1000:.2f}m"
                    )
                    if robot.robot_id == 0:
                        # If you see a yellow robot in grSim, this will move it
                        send_robot_command(0, vx=0.5, is_yellow=True)

            # Maintain frequency to avoid simulator watchdog timeout
            # time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error during execution: {e}")
        traceback.print_exc()
    finally:
        sock.close()


if __name__ == "__main__":
    listen_to_vision()
