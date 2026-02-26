arquitetura do HULKs (que usa Rust)
# Architecture

Problem definition:
1. Lack of long-term vision and task decomposition.
2. Lack of an architecture definition.
3. Lack of documentation.
4. Lack of structure in code version management.

Ideally, the solution found should facilitate the transfer of knowledge to new students and allow them to integrate into the workflow quickly. This change should be implementable in the next 5 months, with the main goal of winning the next competition around November.

Some logical principles:
1. Simplicity, aiming to make onboarding and knowledge transfer easier.
2. Reusability.
3. Modularity, so that parts of the strategy can be tested independently. Or even for VSSS, for example.

middle: feedback loop, deliberate practice principles

principles
simplicity and onboarding
reusability (especially with VSSS)



Previous research:
- ROS is a giant hammer for a small nail
- C++ is dangerous for beginners (memory, UB, concurrency)
- Python is insufficient for real-time control
- However, Python has a huge structure for AI and NN.
- Rust solves all this without heavy frameworks


HULKs architecture (which uses Rust)

# Understanding Our Data Flow

For our robots to operate on the field, our software must perceive the game, make decisions, and send motion commands within fractions of a second. This document explains how information flows through our system architecture.

Below is the main data flow of our system:

```bash
## 2. High-Level Data Flow

      +------------------+                +------------------+
      |     Vision       |                |     GameCtrl     |
      | (SSL + GC parse) |                |  (Referee input) |
      +------------------+                +------------------+
                     |                                 |
                     | VisionPacket / RefereeFrame     |
                     v                                 |
            +--------------------------+               |
            |        Strategy          |               |
            |  (GameState + Behaviors) | <-------------
            +--------------------------+
                        |
                        | RobotIntents (desired action)
                        v
             +---------------------------+
             |        Controller         |
             |  (OmniCalc + MotionCtrl)  |
             +---------------------------+
                        |
                        | RobotCommand
                        v
             +---------------------------+
             |           Sender          |
             | (grSim / Serial / UDP)    |
             +---------------------------+
```

The system can be divided into four main stages:

---

## 1. Data Acquisition and Interpretation (Vision & Game Controller)

Before making any decision, we need to know what is happening on the field. We rely on two data sources:

* **SSL-Vision**: Provides positions of the ball and robots.
* **Game Controller**: Acts as the referee, sending the current game state (fouls, stops, restarts, etc.).

### Components

* **UDPClient**
  Responsible for establishing the network connection and receiving raw data via the UDP protocol. At this stage, the data is just a stream of bytes.

* **Protobufs (Protocol Buffers)**
  Used to convert raw bytes into structured data. Protobuf acts as a serializer/deserializer, parsing the binary stream into usable data structures (objects).

* **Parsers (VisionDataParser and GCDataParser)**
  These classes take the raw data received by `UDPClient` and apply the Protobuf parsing logic.

The code responsible for this parsing process in the vision module looks like this:

```python
try:
    packet = wr.SSL_WrapperPacket()
    packet.ParseFromString(data)  # Raw bytes become a Python object!

    with self._lock:
        if packet.HasField("detection"):
            self._detection = packet.detection
        if packet.HasField("geometry"):
            self._geometry = packet.geometry
```

With these four classes instantiated (two clients and two parsers), we obtain clean and structured access to everything happening on the field.

---

## 2. Decision Making (Strategy)

The `Strategy` class is the brain of the team. It receives all translated information from the previous step:

* Our robot positions
* Opponent positions
* Ball position
* Game state from the referee

Based on this data, the strategy layer determines the next action. It generates a target position or desired behavior, encapsulated as `RobotIntents`.

---

## 3. Motion Control (Controller and OmniCalculator)

Knowing *where* to go is different from knowing *how* to go. This is handled by the `Controller`.

The `OmniCalculator` component receives the target defined by the Strategy layer and performs the necessary kinematic calculations. It converts a high-level intention (e.g., “move forward”) into precise wheel velocities (PWM values) for each omnidirectional wheel on the robot.

---

## 4. Command Transmission (Sender)

Finally, the calculated wheel velocities must be sent to either the physical robot or the simulator.

Depending on the execution environment, we instantiate a different sender:

* **UdpSender (RobotSender)**
  Builds and sends motion commands over the network (WiFi/UDP). Typically used with simulators such as `grSim`.

* **RadioSender**
  Builds a data packet and sends it through a serial port to a microcontroller (e.g., STM32), which then transmits the command via radio frequency to the physical robots.

---

### Radio Communication Packet Structure

For radio communication with real robots, we build a byte packet that follows a strict protocol, where each byte has a specific role:

| Order | Name     | Type  | Size   | Description                                     |
| ----- | -------- | ----- | ------ | ----------------------------------------------- |
| 0     | HEADER_1 | uint8 | 1 byte | Fixed value `0xAA`                              |
| 1     | HEADER_2 | uint8 | 1 byte | Fixed value `0x55`                              |
| 2     | ROBOT_ID | uint8 | 1 byte | Robot identifier                                |
| 3     | M1_SPEED | uint8 | 1 byte | Motor 1 speed (0–255)                           |
| 4     | M1_DIR   | uint8 | 1 byte | Direction (0 = clockwise, 1 = counterclockwise) |
| 5     | M2_SPEED | uint8 | 1 byte | Motor 2 speed                                   |
| 6     | M2_DIR   | uint8 | 1 byte | Motor 2 direction                               |
| 7     | M3_SPEED | uint8 | 1 byte | Motor 3 speed                                   |
| 8     | M3_DIR   | uint8 | 1 byte | Motor 3 direction                               |
| 9     | M4_SPEED | uint8 | 1 byte | Motor 4 speed                                   |
| 10    | M4_DIR   | uint8 | 1 byte | Motor 4 direction                               |
| 11    | KICK     | uint8 | 1 byte | `1` = kick, `0` = no kick                       |
| 12    | CHECKSUM | uint8 | 1 byte | Sum modulo 256 of bytes M1..KICK                |
| 13    | TAIL     | uint8 | 1 byte | Fixed value `0xFF`                              |
