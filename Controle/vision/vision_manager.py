import threading
import time
from utils.logger import setup_logger
from vision.protobuf_messages import wrapper_pb2 as wr
from google.protobuf.message import DecodeError
from vision.clientUDP import UDPClient  # ajuste o path se necessário


class VisionManager:
    """
    Handles SSL-Vision data acquisition, parsing, and access to current state.
    """

    def __init__(self, team_color="blue", ip="224.5.23.2", port=10006):
        self.logger = setup_logger("vision_manager", "logs/vision_manager.log")

        self.team_color = team_color.lower()
        self.client = UDPClient(ip, port, "vision_client")

        self._lock = threading.Lock()
        self._running = threading.Event()

        self._detection = None
        self._geometry = None

        # Thread de recepção
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

        self.logger.info(f"VisionManager initialized for team {self.team_color}")

    def _listen_loop(self):
        """Thread que escuta pacotes do SSL-Vision."""
        self._running.set()
        sock_thread = threading.Thread(target=self.client.run, daemon=True)
        sock_thread.start()

        while self._running.is_set():
            data = self.client.get_last_data()
            if not data:
                time.sleep(0.01)
                continue

            try:
                packet = wr.SSL_WrapperPacket()
                packet.ParseFromString(data)

                with self._lock:
                    if packet.HasField("detection"):
                        self._detection = packet.detection
                    if packet.HasField("geometry"):
                        self._geometry = packet.geometry

            except DecodeError:
                self.logger.error("Failed to parse SSL-Vision packet")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")

            time.sleep(0.01)

        self.logger.info("VisionManager stopped.")

    def stop(self):
        """Parar o VisionManager e o cliente UDP."""
        self._running.clear()
        self.client.stop()

    # -----------------------------
    # Métodos de acesso limpo
    # -----------------------------
    def get_ball(self):
        with self._lock:
            if not self._detection or not self._detection.balls:
                return None
            return self._detection.balls[0]

    def get_robots(self):
        with self._lock:
            if not self._detection:
                return [], []
            if self.team_color == "blue":
                ours = self._detection.robots_blue
                theirs = self._detection.robots_yellow
            else:
                ours = self._detection.robots_yellow
                theirs = self._detection.robots_blue
            return ours, theirs

    def get_field_state(self):
        """Retorna (ball, our_robots, opponent_robots)"""
        ball = self.get_ball()
        ours, theirs = self.get_robots()
        return ball, ours, theirs
