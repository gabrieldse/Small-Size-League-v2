import math
import time


class MotionController:
    def __init__(self):
        """
        Inicializa o controlador de movimento.
        """
        print("Controlador de Movimento inicializado.")

        self.KP = 1.5  # Ganho proporcional para velocidade linear
        self.KI = 0.5  # Ganho integral
        self.KD = 0.5  # Ganho derivativo

        self._interror_phi = 0.0  # Erro integral acumulado para o ângulo
        self.Integral_part = 0.0  # Parte integral do PID
        self._fant_phi = 0.0  # Valor anterior do ângulo para o filtro

        self._angulo_anterior_phid = 0.0  # Ângulo anterior desejado (phid)
        self._angulo_anterior_phi = 0.0  # Ângulo anterior (phi)
        self._last_update_time = time.time()

        # Velocidades máximas (para limitar o output do controlador)
        self.MAX_V = 1.5  # m/s
        self.MAX_W = 5.0  # rad/s

    def calculate_robot_velocities(self, robot_data):
        """
        Calcula as velocidades lineares ('v_linear_x', 'v_linear_y') e angular ('w') para o robô
        no seu próprio referencial, com base na posição atual e alvo.
        """

        if robot_data is None:
            # Se não houver dados, retorna velocidades zero
            return {"v_linear": 0.0, "w": 0.0, "kick": False}

        current_x = robot_data["robot_current_x"]
        current_y = robot_data["robot_current_y"]
        current_orientation = robot_data["robot_current_orientation"]
        target_x = robot_data["robot_target_x"]
        target_y = robot_data["robot_target_y"]
        kick_command = robot_data["kick_command"]

        # Calcular o phid (ângulo desejado) para o robô se alinhar com o alvo (bola)
        phid = math.atan2((target_y - current_y), (target_x - current_x))
        # Normalização do ângulo para o intervalo [-pi, pi]
        if phid > math.pi:
            phid -= 2 * math.pi
        elif phid < -math.pi:
            phid += 2 * math.pi

        # Normaliza o phid (ângulo desejado)
        diferencia_phid = phid - self._angulo_anterior_phid
        # Normaliza a diferença para o intervalo [-pi, pi]
        if diferencia_phid > math.pi:
            phid -= 2 * math.pi
        elif diferencia_phid < -math.pi:
            phid += 2 * math.pi

        # Normaliza a orientação do robô
        diferencia_phi = current_orientation - self._angulo_anterior_phi
        # Normaliza a diferença para o intervalo [-pi, pi]
        if diferencia_phi > math.pi:
            current_orientation -= 2 * math.pi
        elif diferencia_phi < -math.pi:
            current_orientation += 2 * math.pi

        # Atualiza os ângulos anteriores para a próxima iteração
        self._angulo_anterior_phid = phid
        self._angulo_anterior_phi = current_orientation

        # Calcular o erro angular (phi) entre o ângulo desejado (phid) e a orientação atual do robô
        error_phi = phid - current_orientation
        # Normaliza o erro para o intervalo [-pi, pi]
        if error_phi > math.pi:
            error_phi -= 2 * math.pi
        elif error_phi < -math.pi:
            error_phi += 2 * math.pi

        # Calcula o deltaT (tempo entre atualizações)
        current_time = time.time()
        deltaT = current_time - self._last_update_time
        self._last_update_time = current_time

        # Chama o controlador PID para obter o omega (velocidade angular do robô)
        omega = self._pid_controller(deltaT, error_phi)

        # Calcular a distância até o alvo
        error_distance = math.sqrt(
            (target_x - current_x) ** 2 + (target_y - current_y) ** 2
        )

        # Calcular as velocidades lineares (v_linear_x, v_linear_y) do robô
        v_linear = self.KP * error_distance
        # v_linear = 1.4

        # Limitar a velocidade linear ao máximo permitido
        v_linear = max(min(v_linear, self.MAX_V), -self.MAX_V)
        # Limitar a velocidade angular (omega) ao máximo permitido
        omega = max(min(omega, self.MAX_W), -self.MAX_W)

        return {
            "vx": v_linear * math.cos(current_orientation),
            "vy": v_linear * math.sin(current_orientation),
            "w": omega,
            "kick": kick_command,
        }

    def _pid_controller(self, deltaT, error_phi):
        """
        Controlador PID para calcular a velocidade angular (omega) do robô.

        Parâmetros:
            deltaT (float): Intervalo de tempo entre as atualizações.
            error_phi (float): Erro angular entre o ângulo desejado e a orientação atual do robô.

        Retorna:
            float: Velocidade angular (omega) calculada pelo PID.
        """
        integral_saturation = 1
        sqrt_gains = math.sqrt(self.KD), math.sqrt(self.KP), math.sqrt(self.KI)
        filter_constant = 1 / (max(sqrt_gains) * 10)
        exp_decay = math.exp(-(deltaT / filter_constant))
        filter_weight = 1 - exp_decay
        self._interror_phi += error_phi
        self._filtered_error = exp_decay * self._fant_phi + filter_weight * error_phi
        derivative_error = (
            (self._filtered_error - self._fant_phi) / deltaT
            if self._fant_phi != 0
            else self._filtered_error / deltaT
        )
        self.Integral_part = min(
            max(
                self.Integral_part + self.KI * self._interror_phi * deltaT,
                -integral_saturation,
            ),
            integral_saturation,
        )
        omega = self.KP * error_phi + self.Integral_part + derivative_error * self.KD

        return omega
