from vision.protobuf_messages import wrapper_pb2 as wr
from google.protobuf.message import DecodeError
from utils.logger import setup_logger
import threading


class VisionDataParser:
    def __init__(self):
        self.data = None
        self.logger = setup_logger("vision_parser", "logs/parser.log")

        self.last_detection_data = None
        self.last_geometry_data = None
        self.last_frame_number = -1
        self._is_running = threading.Event()
        self._lock = threading.Lock()

    def parser_loop(self, data):
        self.data = data
        try:
            frame = wr.SSL_WrapperPacket()
            frame.ParseFromString(self.data)

            if frame.HasField("detection"):
                detection = frame.detection
                self.logger.debug(f"Detection frame number: {detection.frame_number}")
                with self._lock:
                    self.last_detection_data = detection

            if frame.HasField("geometry"):
                geometry = frame.geometry
                self.logger.debug("Geometry data received.")
                with self._lock:
                    self.last_geometry_data = geometry

        except DecodeError:
            self.logger.error("Failed to decode the received data.")
        except Exception as e:
            self.logger.error(f"Error processing received data: {e}")

    def get_last_detection(self):
        with self._lock:
            if not self.last_detection_data:
                return None
            # if self.last_detection_data.get('frame_number') < self.last_frame_number:
            #    return None

            self.last_frame_number = self.last_detection_data

            return self.last_detection_data

    def get_last_geometry(self):
        with self._lock:
            if not self.last_geometry_data:
                return None
            return self.last_geometry_data
