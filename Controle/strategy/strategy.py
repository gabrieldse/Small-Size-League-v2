# strategy.py
import math

from cv2 import normalize
from Controle.constants import *
import time
import copy
from utils.logger import setup_logger
from strategy.vectors import sum_vectors, norm_vector, multi_vector, angle_diff

GOALIE_CLEARANCE_DISTANCE = 600.0 # Distância (mm) para o goleiro "atacar" a bola

# Posições do Nosso Gol
GOAL_X_POSITION = 2100.0 # Linha do nosso gol (Exemplo)
GOAL_TOP_Y = 500.0       # Trave superior (Exemplo)
GOAL_BOTTOM_Y = -500.0   # Trave inferior (Exemplo)

# Posições do Gol Adversário
OPPONENT_GOAL = {'x': -1700.0, 'y': 0.0}            # Centro do gol adversário (Exemplo)
OPPONENT_AREA_X_LINE = 1200.0                     # Linha da área adversária (Exemplo)

# --- ESTAS SÃO AS NOVAS VARIÁVEIS ---
# Alvos nos cantos do campo adversário
OPPONENT_CORNER_TOP = {'x': -1700.0, 'y': 1000.0}    # Canto superior adversário (Ajuste o Y)
OPPONENT_CORNER_BOTTOM = {'x': -1700.0, 'y': -1000.0} # Canto inferior adversário (Ajuste o Y)

# Distâncias de Estratégia
POSITION_OFFSET_BEHIND_BALL = 100.0  # Distância para se posicionar atrás da bola (mm)
GOALIE_CLEARANCE_DISTANCE = 250.0     # Distância (mm) para o goleiro "atacar" a bola
ATTACK_POSITIONING_THRESHOLD = 250.0   # Margem de erro (mm) para considerar "em posição"
ATTACK_ORIENTATION_THRESHOLD = 0.2    # Margem de erro (radianos, ~5.7 graus)
CENTER = {'x': 0, 'y':0 }
KICK_YELLOW = {'x': 1000, 'y':111 }
KICK_BLUE = {'x': 1100, 'y':0 }
GOAL = {'x': -1700, 'y':0 }
GOAL_A = {'x': 2000, 'y': 400}
GOAL_B = {'x': 2000, 'y': -400}

PENALTY_BLUE = {'x': -750, 'y':0}
class Strategy:
    def __init__(self):
        print("Estrategia inicializada: Selecionando alvo (bola) para o robo.")
        self.logger = setup_logger('strategy', 'logs/strategy.log')
        self.KICK_DISTANCE_THRESHOLD = 150 # Distância em mm

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
        Esta função usa PID para parar suavemente no alvo.
        """
        robot_id = robot_info.robot_id
        if robot_id not in ROBOT_CONFIGS:
            return

        omni_calc = components['omni_calculator']
        sender = components['robot_senders'].get(robot_id)

        # Extrai valores do target
        robot_target_x = target_pos.get('x')
        robot_target_y = target_pos.get('y')
        robot_target_orientation = target_pos.get('orientation', 0.0) # Padrão é 0 se não fornecido

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
                kick  
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
        """
        Segue a bola usando velocidade constante (go_direction)
        para conduzi-la ou chutá-la.
        """
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
            # Correto: Usa go_direction para movimento contínuo
            wheel_speeds = components['omni_calculator'].go_direction(target_data)
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
        #game_state = -1
        # ... (Sua definição de constantes de jogo) ...
        target = {'x': -1000.0, 'y': 0}
        CENTER = {'x': 0, 'y':0 }
        KICK_YELLOW = {'x': 1100, 'y':0 }
        KICK_BLUE = {'x': 1100, 'y':0 }
        GOAL = {'x': -1700, 'y':0 }
        PENAL_BLUE = {'x': -750, 'y':0}
        PENAL_YELLOW = {'x': 750, 'y':0}

        if game_state == -1:
            print("testando funçoes")
            #self.move_to_target(robot_info, OPPONENT_CORNER_TOP, components)
            self.move_to_target(robot_info, KICK_YELLOW, components)

        if game_state == HALT:
            print(f"halt, Parando robos state: {game_state}")
            self.stop_all_robots(components['robot_senders']) 

        if game_state == STOP:
            print(f"Stop: {game_state}")
            self.stop_all_robots(components['robot_senders']) 

        if game_state == NORMAL_START:
            print('saida normal')
            # Correto: usa follow_ball para atacar
            self.attack(robot_info, ball_info, components)

        if game_state == FORCE_START:
            print("ataque")
            # Correto: usa follow_ball para atacar
            self.attack(robot_info, ball_info, components)

        if game_state == KICKOF_YELLOW:
            print("mantenha a distancia")
            self.move_to_target(robot_info, KICK_YELLOW, components)

        if game_state == KICKOF_BLUE:
            self.move_to_target(robot_info, KICK_BLUE, components)
            
        if game_state == PENALTY_YELLOW:
            self.move_to_target(robot_info, PENAL_BLUE, components)            
        if game_state == PENALTY_BLUE:
             # Correto: usa move_to_target para posicionar
            self.move_to_target(robot_info, PENAL_YELLOW, components)            

    def get_speed_scale(self, gc_parser):
        gc_data = gc_parser.get_last_data()
        if gc_data is None:
            return 1.0  # Se não tiver dados, joga normalmente
        gc_state = getattr(gc_data, "game_state", None)
        if gc_state is None:
            return 1.0
        if gc_state in ["HALT", "STOP"]:
            return 0.0
        elif gc_state.startswith("PREPARE"):
            return 0.3
        elif gc_state.startswith("FORCE_START") or gc_state == "NORMAL_START":
            return 1.0
        return 1.0
    
    def play_game(self, detection, components):
        vision_client = components['vision_client']
        vision_parser = components['vision_parser']
        gc_client = components['gc_client']
        gc_parser = components['gc_parser']
        strategys = components['strategy']
        
        detection = vision_parser.get_last_detection()
        if detection:
            our_robots = detection.robots_blue #if TEAM_COLOR == "blue" else detection.robots_yellow
            opponent_robots = detection.robots_yellow if TEAM_COLOR == "blue" else detection.robots_blue
            balls = detection.balls
            print("Meu robo")
            print(our_robots)
            gc_data = gc_parser.get_last_data()
            # print("data")
            #print(gc_data)

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
            try:
                ball_info = balls[0]
                print(f"Ball detected at x={ball_info.x:.1f}, y={ball_info.y:.1f}")                   
                #print(f"Detected {len(our_robots)} of our robots.")
            except Exception as e:
                print(f"\nOcorreu um erro durante o teste: {e}")

            ## LOGICS PARA OS ROBOS
            for robot_info in our_robots:
                robot_id = robot_info.robot_id
                x, y, orientation = robot_info.x, robot_info.y, robot_info.orientation

                print(f"Robot {robot_id}: x={x:.1f}, y={y:.1f}, θ={orientation:.2f}")
                try:
                    #game_state = 2
                    strategys.enforce_game_rules(robot_info, ball_info, components, game_state) # type: ignore

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
    
    def attack(self, robot_info, ball_info, components):
        """
        Estratégia de ataque: 
        1. Decide para qual CANTO do gol adversário mirar.
        2. Posiciona-se atrás da bola, alinhado com esse canto.
        3. Quando em posição, avança para conduzir a bola.
        """
        print("Função de ataque (Mirar no Canto)")

        # --- ETAPA 1: Decidir qual canto atacar ---
        # Se a bola está na metade de cima (y > 0), mira no canto de cima.
        # Se não, mira no canto de baixo.
        if ball_info.y > 0:
            target_corner = OPPONENT_CORNER_TOP
            print("Atacante: Mirando no canto SUPERIOR.")
        else:
            target_corner = OPPONENT_CORNER_BOTTOM
            print("Atacante: Mirando no canto INFERIOR.")
        
        # --- ETAPA 2: Calcular o alvo de posicionamento ---
        
        # 1. Calcula o vetor da bola para o CANTO
        vec_ball_to_target = {
            'x': target_corner['x'] - ball_info.x,
            'y': target_corner['y'] - ball_info.y
        }
        
        # 2. Normaliza o vetor
        dir_ball_to_target = norm_vector(vec_ball_to_target)
        
        # 3. Cria um vetor de offset "para trás"
        offset_vector = multi_vector(dir_ball_to_target, POSITION_OFFSET_BEHIND_BALL)
        
        # 4. Posição alvo (atrás da bola)
        ball_pos_dict = {'x': ball_info.x, 'y': ball_info.y}
        target_pos = sum_vectors(ball_pos_dict, offset_vector) 

        # 5. Orientação alvo (olhando para o canto)
        target_orientation = math.atan2(vec_ball_to_target['y'], vec_ball_to_target['x'])

        # --- ETAPA 3: Decidir entre Posicionar ou Conduzir ---

        # Calcula o erro de posição e orientação
        dist_to_target = math.hypot(target_pos['x'] - robot_info.x, target_pos['y'] - robot_info.y)
        orientation_error = angle_diff(target_orientation, robot_info.orientation)

        is_in_position = (dist_to_target < ATTACK_POSITIONING_THRESHOLD) and \
                         (orientation_error) < ATTACK_ORIENTATION_THRESHOLD

        if is_in_position:
            # 3.A. ESTÁ EM POSIÇÃO: Mudar para modo "CONDUZIR"
            # (Implementando seu comentário: "quando chegar no target, conduza a bola")
            print("Atacante: Em posição, conduzindo bola!")

            # Cria uma cópia da bola para não modificar a original
            clipped_ball = copy.copy(ball_info)
            
            # Aplica a restrição "não invadir a área"
            if clipped_ball.x > OPPONENT_AREA_X_LINE:
                clipped_ball.x = OPPONENT_AREA_X_LINE
            
            # Usa follow_ball para atacar o alvo (bola ou linha da área)
            self.follow_ball(robot_info, clipped_ball, components)
            
        else:
            # 3.B. FORA DE POSIÇÃO: Mudar para modo "POSICIONAR"
            print(f"Atacante: Posicionando (Dist: {dist_to_target:.0f}mm, AngErr: {math.degrees(orientation_error):.0f}deg)")
            
            # Adiciona a orientação desejada ao alvo
            target_pos['orientation'] = target_orientation
            
            # Usa move_to_target para ir até o alvo (usará PID)
            self.move_to_target(robot_info, target_pos, components)

    def defender(self, robot_info, ball_info, components):
        """
        Estratégia de goleiro: Fica na linha do gol (GOAL_X_POSITION).
        Se a bola chegar muito perto, chama a função de ataque para afastar.
        """
        print("Função defender (Goleiro)")

        # Calcula a distância do goleiro até a bola
        dist_to_ball = math.hypot(ball_info.x - robot_info.x, ball_info.y - robot_info.y)

        # --- LÓGICA DE DECISÃO ---
        if dist_to_ball < GOALIE_CLEARANCE_DISTANCE:
            # 1. BOLA ESTÁ PERTO: Mudar para modo "ATACAR"
            # (Como pedido, ele agora chama a função 'attack' principal)
            print("Goleiro: Bola próxima, chamando ATTACH!")
            self.attack(robot_info, ball_info, components)
        
        else:
            # 2. BOLA ESTÁ LONGE: Mudar para modo "POSICIONAR"
            # (Esta é a sua lógica original de seguir na linha do gol)
            
            target_x = GOAL_X_POSITION
            target_y = ball_info.y
            
            if target_y > GOAL_TOP_Y:
                target_y = GOAL_TOP_Y
            elif target_y < GOAL_BOTTOM_Y:
                target_y = GOAL_BOTTOM_Y

            target_orientation = math.atan2(
                (ball_info.y - robot_info.y),
                (ball_info.x - robot_info.x)
            )
            target_pos = {
                'x': target_x, 
                'y': target_y, 
                'orientation': target_orientation
            }

            self.move_to_target(robot_info, target_pos, components)
 
    def move_fwd(self, robot_senders):
        # ... (Função original, sem mudanças) ...
        for sender in robot_senders.values():
            sender.send_command(250, 0, 250, 0, 250, 0, 250, 0, 0)

    def stop_all_robots(self, robot_senders):
        # ... (Função original, sem mudanças) ...
        for sender in robot_senders.values():
            sender.send_command(0,0,0,0,0,0,0,0,False)