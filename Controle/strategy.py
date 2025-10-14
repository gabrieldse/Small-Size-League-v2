# strategy.py
import math

class Strategy:
    def __init__(self):
        print("Estrategia inicializada: Selecionando alvo (bola) para o robo.")
        self.KICK_DISTANCE_THRESHOLD = 150 # Distância em mm

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