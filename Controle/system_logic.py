import gc
import time
import threading
from sender.radio_sender import RadioSender
from sender.udp_sender import UdpSender
from vision.clientUDP import UDPClient
from vision.parser import VisionDataParser
from vision.gcparser import GCDataParser
from strategy import Strategy
from controller.pid import OmniCalculator
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

def on_halt(robot_info, ball_info, components):
    robot_id = robot_info.robot_id
    if robot_id not in ROBOT_CONFIGS:
        return

    sender = components['robot_senders'].get(robot_id)
    if sender:
        sender.stop_all_motors()

def move_robot_to_position(robot_info, target_pos, components):
    """
    Move o robô até uma posição alvo sem chutar a bola.
    Usa o OmniCalculator existente para gerar velocidades.
    """
    target_data = {
        'target_x': target_pos.get('x', robot_info.x),
        'target_y': target_pos.get('y', robot_info.y),
        'target_theta': target_pos.get('orientation', 0),
        'kick_command': False
    }

    wheel_speeds = components['omni_calculator'].calculate_wheel_speeds(target_data)

    sender = components['robot_senders'].get(robot_info.robot_id)
    if sender:
        sender.send_command(
            wheel_speeds['fl_speed'], wheel_speeds['fl_direction'],
            wheel_speeds['fr_speed'], wheel_speeds['fr_direction'],
            wheel_speeds['bl_speed'], wheel_speeds['bl_direction'],
            wheel_speeds['br_speed'], wheel_speeds['br_direction'],
            False
        )


def enforce_game_rules(robot_info, ball_info, components, gc_parser):

    gc_data = gc_parser.get_last_data() 
    if gc_data is None:
        return True  
    
    gc_state = getattr(gc_data, "game_state", None)
    if gc_state is None:
        print(gc_state)
        return True

    if gc_state in ["HALT", "STOP"]:
        stop_all_robots(components["robot_senders"])
        return False
    
    if gc_state in ["FORCE_START", "NORMAL_START"]:
        return True

    return True


def get_speed_scale(gc_parser):
    """
    Retorna uma escala de velocidade entre 0.0 e 1.0 dependendo do estado do jogo.
    """
    gc_data = gc_parser.get_last_data()
    if gc_data is None:
        return 1.0  # Se não tiver dados, joga normalmente

    gc_state = getattr(gc_data, "game_state", None)
    if gc_state is None:
        return 1.0

    if gc_state in ["HALT", "STOP"]:
        return 0.0
    elif gc_state.startswith("PREPARE"):
        # Movimento lento durante preparação
        return 0.3
    elif gc_state.startswith("FORCE_START") or gc_state == "NORMAL_START":
        return 1.0

    # Default
    return 1.0

def stop_all_robots(robot_senders):
    for sender in robot_senders.values():
        sender.send_command(0,0,0,0,0,0,0,0,False)
