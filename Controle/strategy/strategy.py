# strategy.py
import math
from Controle.constants import *
import time
from utils.logger import setup_logger

class Strategy:
    def __init__(self):
        print("Estrategia inicializada: Selecionando alvo (bola) para o robo.")
        self.logger = setup_logger('strategy', 'logs/strategy.log')
        self.KICK_DISTANCE_THRESHOLD = 150 # DistâControle/strategy/strategy.pyncia em mm

    def find_robot(self, robot_state, robot_id):
        robot_current_x = robot_state.get('robot_current_x')
        robot_current_y = robot_state.get('robot_current_y')
        robot_orientation = robot_state.get('robot_current_orientation')

        return {
            'robot_current_x': robot_current_x,
            'robot_current_y': robot_current_y,
            'robot_current_orientation': robot_orientation,
        }

    def move_to_target(self, robot_info, target_pos, components, kick=False):
        """
        Move o robô até uma posição-alvo genérica (target_pos = {'x': ..., 'y': ...})
        """
        robot_id = robot_info.robot_id
        if robot_id not in ROBOT_CONFIGS:
            return

        omni_calc = components['omni_calculator']
        sender = components['robot_senders'].get(robot_id)

        # Extrai valores do target
        robot_target_x = target_pos.get('x')
        robot_target_y = target_pos.get('y')
        robot_target_orientation = target_pos.get('orientation', 0.0)

        context = {
            'robot_current_x': robot_info.x,
            'robot_current_y': robot_info.y,
            'robot_current_orientation': robot_info.orientation,
            'robot_target_x': robot_target_x,
            'robot_target_y': robot_target_y,
            'robot_target_orientation': robot_target_orientation
        }

        if context:
            wheel_speeds = omni_calc.calculate_wheel_speeds(context)
        else:
            wheel_speeds = {k: 0 for k in [
                'fl_speed', 'bl_speed', 'fr_speed', 'br_speed',
                'fl_direction', 'bl_direction', 'fr_direction', 'br_direction'
            ]}

        if sender:
            sender.send_command(
                wheel_speeds['fl_speed'], wheel_speeds['fl_direction'],
                wheel_speeds['fr_speed'], wheel_speeds['fr_direction'],
                wheel_speeds['bl_speed'], wheel_speeds['bl_direction'],
                wheel_speeds['br_speed'], wheel_speeds['br_direction'],
                False
            )

    def decide_action(self, robot_state, robot_id):
        robot_current_x = robot_state.get('robot_current_x')
        robot_current_y = robot_state.get('robot_current_y')
        ball_pos = robot_state.get('ball_pos')

        if robot_current_x is None or ball_pos is None:
            print("Posição do robô ou da bola ausente.")
            return None

        # O alvo de posição é a bola
        robot_target_x = ball_pos.x
        robot_target_y = ball_pos.y

        # O alvo de orientação é o ângulo direto para a bola
        target_orientation = math.atan2(
            (robot_target_y - robot_current_y),
            (robot_target_x - robot_current_x)
        )
        
        distance_to_ball = math.sqrt((robot_target_x - robot_current_x)**2 + (robot_target_y - robot_current_y)**2)
        kick_command = distance_to_ball < self.KICK_DISTANCE_THRESHOLD

        return {
            'robot_current_x': robot_current_x,
            'robot_current_y': robot_current_y,
            'robot_current_orientation': robot_state.get('robot_current_orientation'),
            'robot_target_x': robot_target_x,
            'robot_target_y': robot_target_y,
            'robot_target_orientation': target_orientation,
            'kick_command': kick_command
        }
    
    def follow_ball(self, robot_info, ball_info, components):
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

    def keep_distance(self, robot_info, ball_info, components):
        robot_id = robot_info.robot_id
        if robot_id not in ROBOT_CONFIGS:
            return
        
        ball_info.x = ball_info.x - 1000
        ball_info.y = ball_info.y - 1000
        print('bola info')
        print(ball_info)

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

    def enforce_game_rules(self, robot_info, ball_info, components, game_state):
        game_state = -1

        if game_state == -1:
            print("testando funçoes")
            target = {'x': 3000.0, 'y': 0.0}  # unidades em mm, por exemplo
            self.move_to_target(robot_info, target, components)
        if game_state == HALT:
            print(f"halt, Parando robos state: {game_state}")
            self.stop_all_robots(components['robot_senders']) 

        if game_state == STOP:
            print(f"Stop: {game_state}")
            self.stop_all_robots(components['robot_senders'])

        if game_state == NORMAL_START:
            print('seguindo a bola')
            self.follow_ball(robot_info, ball_info, components)

        if game_state == FORCE_START:
            print('Force start:')
            self.follow_ball(robot_info, ball_info, components)

        if game_state == KICKOF_YELLOW:
            print("mantenha a distancia")
            self.keep_distance(robot_info, ball_info, components)

        if game_state == KICKOF_BLUE:
            self.keep_distance(robot_info, ball_info, components)
            
        if game_state == PENALTY_YELLOW:
            self.penalty(robot_info, ball_info, components)
        if game_state == PENALTY_BLUE:
            pass

    def get_speed_scale(self, gc_parser):
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
    
    def play_game(self, detection, components):
        vision_client = components['vision_client']
        vision_parser = components['vision_parser']
        gc_client = components['gc_client']
        gc_parser = components['gc_parser']
        strategys = components['strategy']
        
        detection = vision_parser.get_last_detection()
        if detection:
            our_robots = detection.robots_blue if TEAM_COLOR == "blue" else detection.robots_yellow
            opponent_robots = detection.robots_yellow if TEAM_COLOR == "blue" else detection.robots_blue
            balls = detection.balls
            print(our_robots)
            gc_data = gc_parser.get_last_data()
            # print("data")
            #print(gc_data)
            game_state = 3

            if gc_data is not None:
                # O comando atual indica o "game state"
                game_state = gc_data.command  # Ex: HALT, NORMAL_START, etc.
                next_command = getattr(gc_data, "next_command", None)
                stage = getattr(gc_data, "stage", None)
                time_left = getattr(gc_data, "current_action_time_remaining", None)

                print(f"[GC] Command: {game_state}, Next: {next_command}, Stage: {stage}, Time left: {time_left}")
            else:
                print("[GC] No data received yet") 

            if not balls:
                print("No ball detected. Stopping robots.")
                # stop_all_robots(components['robot_senders'])
                time.sleep(0.05)

            ball_info = balls[0]
            print(f"Ball detected at x={ball_info.x:.1f}, y={ball_info.y:.1f}")                   
            print(f"Detected {len(our_robots)} of our robots.")

            ## LOGICS PARA OS ROBOS
            for robot_info in our_robots:
                robot_id = robot_info.robot_id
                x, y, orientation = robot_info.x, robot_info.y, robot_info.orientation

                print(f"Robot {robot_id}: x={x:.1f}, y={y:.1f}, θ={orientation:.2f}")
                try:
                    game_state = 2
                    strategys.enforce_game_rules(robot_info, ball_info, components, game_state)

                except Exception as e:
                    self.logger.error(f"Error processing robot {robot_id}: {e}", exc_info=True)

            if not our_robots:
                self.logger.warning("No robots detected for our team!")
                self.stop_all_robots(components['robot_senders'])
                time.sleep(0.01)

            print(f"Detected {len(our_robots)} of our robots.")
        else:
            print("No vision data received. Stopping all robots.")
            strategys.stop_all_robots(components['robot_senders'])

    def move_fwd(self, robot_senders):
        for sender in robot_senders.values():
            sender.send_command(250, 0, 250, 0, 250, 0, 250, 0, 0)

    def stop_all_robots(self, robot_senders):
        for sender in robot_senders.values():
            sender.send_command(0,0,0,0,0,0,0,0,False)