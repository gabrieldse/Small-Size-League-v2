from vision.protobuf_messages import ssl_gc_referee_message_pb2 as gc
from google.protobuf.message import DecodeError
from utils.logger import setup_logger
import threading


class GCDataParser:
    def __init__(self):
        self.data = None
        self.logger = setup_logger("gc_parser", "logs/parser.log")

        self.last_data = None
        self.last_frame_number = -1
        self._is_running = threading.Event()
        self._lock = threading.Lock()

    def parser_loop(self, data):
        self.data = data
        try:
            frame = gc.Referee()
            frame.ParseFromString(self.data)

            with self._lock:
                self.last_data = frame

        except DecodeError:
            self.logger.error("Failed to decode the received data.")
        except Exception as e:
            self.logger.error(f"Error processing received data: {e}")

    def get_last_data(self):
        with self._lock:
            return self.last_data
