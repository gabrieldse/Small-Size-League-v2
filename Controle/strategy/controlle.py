#!/usr/bin/env python3
"""
test_ssl_simulator.py

Simulador fake de SSL-Vision + GameController (multicast).
Preenche todos campos obrigatórios dos protos e envia via multicast
para os endereços padrão da RoboCup SSL.

Uso:
  source venv/bin/activate
  python3 test_ssl_simulator.py
"""

import socket
import struct
import time
import sys
from typing import Tuple

# Ajuste de import se necessário (assume que PYTHONPATH já aponta para vision/protobuf_messages)
from Controle.vision.protobuf_messages import ssl_gc_referee_message_pb2 as gc
from Controle.vision.protobuf_messages import wrapper_pb2 as wr

# ====== CONFIG ======
GC_ADDR = ("224.5.23.1", 10003)
VISION_ADDR = ("224.5.23.2", 10006)
SLEEP_TIME = 0.25  # segundos entre frames
STATE_CYCLE = ["NORMAL_START"]
# ====================


def detect_local_ip() -> str:
    """
    Detecta o IP local que seria usado para acessar a internet.
    Método clássico: abre UDP socket para 8.8.8.8 e lê o socket name.
    Não envia pacotes para a rede.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def make_multicast_sock(
    bind_addr: Tuple[str, int] = None, ttl: int = 1
) -> socket.socket:
    """Cria socket UDP para multicast (envio)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # permitir reuso de porta (opcional)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # set TTL
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", ttl))
    # on some systems, also set IP_MULTICAST_LOOP if you want local loopback
    return sock


def safe_send(sock: socket.socket, data: bytes, addr: Tuple[str, int]):
    try:
        sock.sendto(data, addr)
    except Exception as e:
        print(f"[ERR] sendto {addr}: {e}", file=sys.stderr)


def build_gc_message(frame_number: int, state: str) -> gc.Referee:
    msg = gc.Referee()
    now_us = int(time.time() * 1e6)
    msg.packet_timestamp = now_us
    msg.stage = gc.Referee.Stage.NORMAL_FIRST_HALF
    msg.command_counter = frame_number
    msg.command_timestamp = now_us

    # use a command that exists in the proto
    try:
        msg.command = getattr(gc.Referee.Command, state)
    except Exception:
        msg.command = gc.Referee.Command.NORMAL_START

    # blue team
    blue = msg.blue
    blue.name = "Blue"
    blue.score = 0
    blue.goalkeeper = 0
    blue.yellow_cards = 0
    blue.red_cards = 0
    blue.timeouts = 0
    blue.timeout_time = 0

    # yellow team
    yellow = msg.yellow
    yellow.name = "Yellow"
    yellow.score = 0
    yellow.goalkeeper = 0
    yellow.yellow_cards = 0
    yellow.red_cards = 0
    yellow.timeouts = 0
    yellow.timeout_time = 0

    return msg


def build_vision_packet(frame_number: int) -> wr.SSL_WrapperPacket:
    packet = wr.SSL_WrapperPacket()
    detection = packet.detection
    detection.camera_id = 1
    detection.frame_number = frame_number
    detection.t_capture = time.time()
    detection.t_sent = time.time()

    # ball (center)
    ball = detection.balls.add()
    ball.confidence = 1.0
    ball.x = 0.0
    ball.y = 0.0
    ball.z = 0.0
    # required pixel coordinates (reasonable defaults)
    ball.pixel_x = 320
    ball.pixel_y = 240

    # blue robots (3)
    for i in range(3):
        rb = detection.robots_blue.add()
        rb.robot_id = i
        rb.x = 1000.0 * i
        rb.y = 200.0 * i
        rb.orientation = 0.1 * i
        rb.confidence = 1.0
        rb.pixel_x = 100 + i * 50
        rb.pixel_y = 200 + i * 50

    # yellow robots (2)
    for i in range(2):
        rb = detection.robots_yellow.add()
        rb.robot_id = 3
        rb.x = 1000.0 * i
        rb.y = 1000.0 * i
        rb.orientation = -0.1 * i
        rb.confidence = 1.0
        rb.pixel_x = 400 + i * 50
        rb.pixel_y = 300 + i * 50

    return packet


def main():
    iface_ip = detect_local_ip()
    if iface_ip == "127.0.0.1":
        print(
            "[WARN] Detected loopback IP (127.0.0.1). If your controller "
            "expects multicast on a real interface, set INTERFACE_IP manually."
        )
    print(f"[INFO] Using local interface IP: {iface_ip}")

    gc_sock = make_multicast_sock()
    vision_sock = make_multicast_sock()

    # Force multicast to use this interface for sending
    try:
        gc_sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(iface_ip)
        )
        vision_sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(iface_ip)
        )
    except Exception as e:
        print(f"[WARN] Cannot set IP_MULTICAST_IF to {iface_ip}: {e}")

    frame = 0
    try:
        print(
            "✅ Fake SSL Simulator started. Sending GC ->",
            GC_ADDR,
            "and Vision ->",
            VISION_ADDR,
        )
        while True:
            state = STATE_CYCLE[frame % len(STATE_CYCLE)]

            # GameController
            gc_msg = build_gc_message(frame, state)
            safe_send(gc_sock, gc_msg.SerializeToString(), GC_ADDR)
            print(f"[GC] Frame {frame}: {state}")

            # Vision
            vision_pkt = build_vision_packet(frame)
            safe_send(vision_sock, vision_pkt.SerializeToString(), VISION_ADDR)
            print(f"[VISION] Frame {frame}: 3 blue, 2 yellow, 1 ball")

            frame += 1
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[INFO] Simulator stopped by user")
    finally:
        try:
            gc_sock.close()
            vision_sock.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
