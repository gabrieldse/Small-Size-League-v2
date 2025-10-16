import gc
import time
import threading
from sender.radio_sender import RadioSender
from sender.udp_sender import UdpSender
from vision.clientUDP import UDPClient
from vision.parser import VisionDataParser
from vision.gcparser import GCDataParser
from controller.pid import OmniCalculator
from strategy.strategy import Strategy
import config
from utils.logger import setup_logger
from constants import ROBOT_CONFIGS

logger = setup_logger('system_logic', 'logs/main.log')

USE_RADIO = True

def create_sender(robot_id, cfg):
    if USE_RADIO:
        return RadioSender(robot_id=robot_id)
    else:
        return UdpSender(robot_ip=cfg['ip'], robot_port=cfg['port'])

def initialize_system():
    logger.info("Initializing system...")

    vision_client = UDPClient('224.5.23.2', 10006, 'vision')
    threading.Thread(target=vision_client.run, daemon=True).start()
    vision_parser = VisionDataParser()

    gc_client = UDPClient('224.5.23.1', 10003, 'gc_referee')
    threading.Thread(target=gc_client.run, daemon=True).start()
    gc_parser = GCDataParser()
    
    robot_senders = {}
    for robot_id, cfg in ROBOT_CONFIGS.items():
        robot_senders[robot_id] = create_sender(robot_id, cfg)
        logger.info(f"Sender for Robot {robot_id} -> {robot_senders[robot_id].__class__.__name__}")

    return {
        'vision_client': vision_client,
        'vision_parser': vision_parser,
        'gc_client': gc_client,
        'gc_parser': gc_parser,
        'strategy': Strategy(),
        'omni_calculator': OmniCalculator(
            wheel_radius_mm=config.WHEEL_RADIUS_MM,
            robot_radius_mm=config.ROBOT_RADIUS_MM
        ),
        'robot_senders': robot_senders
    }

def process_robot_logic(robot_info, ball_info, components):
    robot_id = robot_info.robot_id
    if robot_id not in ROBOT_CONFIGS:
        return

    target_data = components['strategy'].decide_action({
        'robot_current_x': robot_info.x,
        'robot_current_y': robot_info.y,
        'robot_current_orientation': robot_info.orientation,
        'ball_pos': ball_info
    }, robot_id)

    if target_data:
        wheel_speeds = components['omni_calculator'].calculate_wheel_speeds(target_data)
        should_kick = target_data.get('kick_command', False)
    else:
        wheel_speeds = {'fl_speed': 0, 'bl_speed': 0, 'fr_speed': 0, 'br_speed': 0,
                        'fl_direction': 0, 'bl_direction': 0, 'fr_direction': 0, 'br_direction': 0}
        should_kick = False

    sender = components['robot_senders'].get(robot_id)
    if sender:
        sender.send_command(
            wheel_speeds['fl_speed'], wheel_speeds['fl_direction'],
            wheel_speeds['fr_speed'], wheel_speeds['fr_direction'],
            wheel_speeds['bl_speed'], wheel_speeds['bl_direction'],
            wheel_speeds['br_speed'], wheel_speeds['br_direction'],
            should_kick
        )
