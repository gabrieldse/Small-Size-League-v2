import math
import time


class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, output_limits=(None, None)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = None

    def reset(self):
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = None

    def update(self, error, current_time=None):
        if current_time is None:
            current_time = time.time()
        dt = 0.0
        if self._last_time is not None:
            dt = current_time - self._last_time
        p = self.kp * error
        self._integral += error * dt
        i = self.ki * self._integral
        d = 0.0
        if dt > 0:
            d = self.kd * (error - self._last_error) / dt
        output = p + i + d
        min_out, max_out = self.output_limits
        if min_out is not None:
            output = max(min_out, output)
        if max_out is not None:
            output = min(max_out, output)
        self._last_error = error
        self._last_time = current_time
        return output


def angle_diff(target, current):
    diff = target - current
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff


class OmniCalculator:
    def __init__(self, wheel_radius_mm=30, robot_radius_mm=75):
        self.wheel_radius_m = wheel_radius_mm / 1000.0
        self.robot_radius_m = robot_radius_mm / 1000.0
        self.max_motor_pwm = 255
        self.MAX_ANGULAR_VEL_RAD_S = 10.0
        self.pid_x = PIDController(kp=1.5, ki=0.2, kd=0.2, output_limits=(-0.8, 0.8))
        self.pid_y = PIDController(kp=1.5, ki=0.2, kd=0.2, output_limits=(-0.8, 0.8))
        self.pid_theta = PIDController(kp=3.0, ki=0.2, kd=5, output_limits=(-7.0, 7.0))
        print("OmniCalculator (VERSÃO HÍBRIDA FINAL) inicializado.")

    def calculate_wheel_speeds(self, robot_data):
        self.pid_x.reset()
        self.pid_y.reset()
        self.pid_theta.reset()

        target_x = robot_data["robot_target_x"] / 1000.0
        target_y = robot_data["robot_target_y"] / 1000.0
        target_theta = robot_data["robot_target_orientation"]
        x_m = robot_data["robot_current_x"] / 1000.0
        y_m = robot_data["robot_current_y"] / 1000.0
        theta = robot_data["robot_current_orientation"]

        error_x = target_x - x_m
        error_y = target_y - y_m
        error_theta = angle_diff(target_theta, theta)

        vx_global = self.pid_x.update(error_x)
        vy_global = self.pid_y.update(error_y)
        w = self.pid_theta.update(error_theta)
        # --- LÓGICA DE PRIORIZAÇÃO DE GIRO (O SEGREDO DA FLUIDEZ) ---
        # Se o robô estiver muito desalinhado, ele reduz a velocidade de avanço.
        ANGULO_MAX_PENALIDADE = math.radians(
            90
        )  # A partir de 90°, a velocidade frontal é zero
        if abs(error_theta) < ANGULO_MAX_PENALIDADE:
            scale = 1.0 - (abs(error_theta) / ANGULO_MAX_PENALIDADE)
            vx_global *= scale
            vy_global *= scale
        else:
            vx_global = 0
            vy_global = 0

        vx_local = math.cos(theta) * vx_global + math.sin(theta) * vy_global
        vy_local = -math.sin(theta) * vx_global + math.cos(theta) * vy_global

        r = self.robot_radius_m
        R = self.wheel_radius_m

        v_fl = (vx_local - vy_local - r * w) / R
        v_bl = (vx_local + vy_local - r * w) / R
        v_fr = (vx_local + vy_local + r * w) / R
        v_br = (vx_local - vy_local + r * w) / R

        speeds = [v_fl, v_bl, v_fr, v_br]
        max_speed = max(abs(s) for s in speeds) if speeds else 0
        if max_speed > self.MAX_ANGULAR_VEL_RAD_S:
            scale = self.MAX_ANGULAR_VEL_RAD_S / max_speed
            v_fl, v_bl, v_fr, v_br = [s * scale for s in speeds]

        def to_pwm(speed):
            return int(
                min(
                    self.max_motor_pwm,
                    abs(speed / self.MAX_ANGULAR_VEL_RAD_S * self.max_motor_pwm),
                )
            )

        return {
            "fl_speed": to_pwm(v_fl),
            "fl_direction": 0 if v_fl >= 0 else 1,
            "bl_speed": to_pwm(v_bl),
            "bl_direction": 0 if v_bl >= 0 else 1,
            "fr_speed": to_pwm(v_fr),
            "fr_direction": 0 if v_fr >= 0 else 1,
            "br_speed": to_pwm(v_br),
            "br_direction": 0 if v_br >= 0 else 1,
        }

    def go_direction(self, robot_data, constant_speed=True, linear_speed=10.0):
        """
        Calcula as velocidades das rodas do robô com movimento constante.
        Usado para "atacar" a bola sem frear.
        """

        def to_pwm(speed):
            return int(
                min(
                    self.max_motor_pwm,
                    abs(speed / self.MAX_ANGULAR_VEL_RAD_S * self.max_motor_pwm),
                )
            )

        # Resetar PID de rotação
        self.pid_theta.reset()

        # --- Dados do robô ---
        target_x = robot_data["robot_target_x"] / 1000.0
        target_y = robot_data["robot_target_y"] / 1000.0
        target_theta = robot_data["robot_target_orientation"]
        x_m = robot_data["robot_current_x"] / 1000.0
        y_m = robot_data["robot_current_y"] / 1000.0
        theta = robot_data["robot_current_orientation"]

        # --- Cálculo de erros ---
        error_x = target_x - x_m
        error_y = target_y - y_m
        error_theta = angle_diff(target_theta, theta)

        # --- Movimento linear (Velocidade constante) ---
        if constant_speed:
            norm = math.hypot(error_x, error_y)
            if norm > 1e-3:  # evita divisão por zero
                vx_global = (error_x / norm) * linear_speed
                vy_global = (error_y / norm) * linear_speed
            else:
                vx_global, vy_global = 0.0, 0.0
        else:
            # Opção de usar PID de posição (mas não é o padrão desta função)
            self.pid_x.reset()
            self.pid_y.reset()
            vx_global = self.pid_x.update(error_x)
            vy_global = self.pid_y.update(error_y)

        # --- Controle de rotação (Sempre PID) ---
        w = self.pid_theta.update(error_theta)

        # --- Conversão para referencial local ---
        vx_local = math.cos(theta) * vx_global + math.sin(theta) * vy_global
        vy_local = -math.sin(theta) * vx_global + math.cos(theta) * vy_global

        # --- Cinemática inversa ---
        r = self.robot_radius_m
        R = self.wheel_radius_m
        v_fl = (vx_local - vy_local - r * w) / R
        v_bl = (vx_local + vy_local - r * w) / R
        v_fr = (vx_local + vy_local + r * w) / R
        v_br = (vx_local - vy_local + r * w) / R

        # --- Normaliza se ultrapassar limite físico ---
        speeds = [v_fl, v_bl, v_fr, v_br]
        max_speed = max(abs(s) for s in speeds) if speeds else 0
        if max_speed > self.MAX_ANGULAR_VEL_RAD_S:
            scale = self.MAX_ANGULAR_VEL_RAD_S / max_speed
            v_fl, v_bl, v_fr, v_br = [s * scale for s in speeds]

        return {
            "fl_speed": to_pwm(v_fl),
            "fl_direction": 0 if v_fl >= 0 else 1,
            "bl_speed": to_pwm(v_bl),
            "bl_direction": 0 if v_bl >= 0 else 1,
            "fr_speed": to_pwm(v_fr),
            "fr_direction": 0 if v_fr >= 0 else 1,
            "br_speed": to_pwm(v_br),
            "br_direction": 0 if v_br >= 0 else 1,
        }
