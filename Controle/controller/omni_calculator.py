import math


class OmniCalculator:
    def __init__(self, wheel_radius_mm=30, robot_radius_mm=75):
        """
        Inicializa o OmniCalculator.

        Args:
            wheel_radius_mm (float): Raio da roda omnidirecional em mm.
            robot_radius_mm (float): Distância do centro do robô ao centro da roda em mm.
        """
        self.wheel_radius_m = wheel_radius_mm / 1000.0
        self.robot_radius_m = robot_radius_mm / 1000.0
        self.max_motor_pwm = 255

        # Ângulos das rodas em relação ao eixo X positivo do robô (em radianos)
        self.angle_fl = math.radians(60)
        self.angle_bl = math.radians(45)
        self.angle_fr = math.radians(60)
        self.angle_br = math.radians(45)

        # Calibre este valor! Velocidade angular máxima que um motor pode atingir em rad/s para PWM 255.
        self.MAX_ANGULAR_VEL_RAD_S = 10  # Exemplo: 20 rad/s (ajuste)

        print(
            f"OmniCalculator init. Raio Roda: {self.wheel_radius_m:.3f}m, Raio Robô: {self.robot_radius_m:.3f}m"
        )

    def calculate_wheel_speeds(self, vx_global, vy_global, w, robot_data):
        """
        Calcula PWM e direção para rodas omni.

        vx_global, vy_global: velocidades desejadas no frame global (m/s)
        w: velocidade angular do robô (rad/s)
        robot_data: dicionário com posição e orientação do robô
        """
        # print (f"Velocidade x{vx}, Velo Y: {vy} Velo Anglular{w}")
        if robot_data is None:
            # Se não houver os dados, retorna velocidade zero
            return {"v_fl": 0.0, "v_bl": 0.0, "v_fr": 0.0, "v_br": 0.0}

        # O print foi movido para depois da verificação de 'robot_data' para evitar erros
        # Também, os nomes das variáveis foram ajustados para corresponder aos argumentos da função
        print(f"Vel Vx global: {vx_global}")
        print(f"Vel Vy global: {vy_global}")
        print(f"W :{w}")

        # Never used
        # Xr = robot_data["robot_current_x"]
        # Yr = robot_data["robot_current_y"]
        # ThetaR = robot_data["robot_current_orientation"]
        # Tx = robot_data["robot_target_x"]
        # Ty = robot_data["robot_target_y"]

        # ------------------- MUDANÇA PRINCIPAL AQUI -------------------
        # O bloco de código que recalculava vx_global e vy_global foi removido.
        # Agora, a função confia e usa os valores calculados pelo MotionController
        # que são passados como argumento.
        # -------------------------------------------------------------

        # Transformar velocidades globais para o frame do robô
        # vx = math.cos(ThetaR) * vx_global + math.sin(ThetaR) * vy_global
        # vy = -math.sin(ThetaR) * vx_global + math.cos(ThetaR) * vy_global

        # r = self.robot_radius_m  # Raio do robô
        # R = self.wheel_radius_m  # Raio da roda

        # Cinemática omni (considerando rodas mecanum ou omni)
        # ESTA FÓRMULA É A PADRÃO E MAIS ESTÁVEL. A sua anterior com números
        # mágicos como 529/1919 foi substituída.
        # v_fl = (vx - vy - r * w) / R
        # v_bl = (vx + vy - r * w) / R
        # v_fr = (vx + vy + r * w) / R
        # v_br = (vx - vy + r * w) / R

        # ----------- Impressão formatada -----------
        # (Seus prints de depuração detalhados foram mantidos, mas comentados como no original)

        # print("== Velocidades das Rodas (Detalhadas) ==")
        # print_wheel_velocity("FL", term_w, term_vx_fl, term_vy_fl, v_fl)
        # print_wheel_velocity("BL", term_w, term_vx_bl, term_vy_bl, v_bl)
        # print_wheel_velocity("FR", term_w, term_vx_fr, term_vy_fr, v_fr)
        # print_wheel_velocity("BR", term_w, term_vx_br, term_vy_br, v_br)
        # print("Wheel Velocities:")
        # print(f"{'Wheel':<10} {'Velocity':<20}")
        # print("-" * 30)
        # print(f"{'FL':<10} {v_fl:<20.6f}")
        # print(f"{'BL':<10} {v_bl:<20.6f}")
        # print(f"{'FR':<10} {v_fr:<20.6f}")
        # print(f"{'BR':<10} {v_br:<20.6f}")

        # Encontrar a velocidade angular máxima entre todas as rodas para normalização
        # max_abs_omega = max(abs(v_fl), abs(v_bl), abs(v_fr), abs(v_br))

        # Normaliza as velocidades se alguma exceder a capacidade máxima do motor
        # scale_factor = 1.0
        # if max_abs_omega > self.MAX_ANGULAR_VEL_RAD_S:
        #     scale_factor = self.MAX_ANGULAR_VEL_RAD_S / max_abs_omega
        #     v_fl *= scale_factor
        #     v_bl *= scale_factor
        #     v_fr *= scale_factor
        #     v_br *= scale_factor

        # Converte a velocidade angular (rad/s) para PWM (0-255)
        # pwm_fl = int(abs(v_fl / self.MAX_ANGULAR_VEL_RAD_S * self.max_motor_pwm))
        # pwm_bl = int(abs(v_bl / self.MAX_ANGULAR_VEL_RAD_S * self.max_motor_pwm))
        # pwm_fr = int(abs(v_fr / self.MAX_ANGULAR_VEL_RAD_S * self.max_motor_pwm))
        # pwm_br = int(abs(v_br / self.MAX_ANGULAR_VEL_RAD_S * self.max_motor_pwm))

        # Determina a direção (0 ou 1).
        # dir_fl = 0 if v_fl >= 0 else 1
        # dir_bl = 0 if v_bl >= 0 else 1
        # dir_fr = 0 if v_fr >= 0 else 1
        # dir_br = 0 if v_br >= 0 else 1

        # Garante que os valores PWM estão dentro do limite (0-255)
        # pwm_fl = min(self.max_motor_pwm, pwm_fl)
        # pwm_bl = min(self.max_motor_pwm, pwm_bl)
        # pwm_fr = min(self.max_motor_pwm, pwm_fr)
        # pwm_br = min(self.max_motor_pwm, pwm_br)

        # output = {
        #     "fl_speed": pwm_fl,
        #     "fl_direction": dir_fl,
        #     "bl_speed": pwm_bl,
        #     "bl_direction": dir_bl,
        #     "fr_speed": pwm_fr,
        #     "fr_direction": dir_fr,
        #     "br_speed": pwm_br,
        #     "br_direction": dir_br,
        # }

        # print("Output:")
        # print(f"{'Wheel':<10} {'Speed':<10} {'Direction':<10}")
        # print("-" * 30)
        # print(f"{'FL':<10} {output['fl_speed']:<10} {output['fl_direction']:<10}")
        # print(f"{'BL':<10} {output['bl_speed']:<10} {output['bl_direction']:<10}")
        # print(f"{'FR':<10} {output['fr_speed']:<10} {output['fr_direction']:<10}")
        # print(f"{'BR':<10} {output['br_speed']:<10} {output['br_direction']:<10}")
        # print(output)

        # return {
        #     "fl_speed": pwm_fl,
        #     "fl_direction": dir_fl,
        #     "bl_speed": pwm_bl,
        #     "bl_direction": dir_bl,
        #     "fr_speed": pwm_fr,
        #     "fr_direction": dir_fr,
        #     "br_speed": pwm_br,
        #     "br_direction": dir_br,
        # }
