# teste_reto.py
import time
import math
from controller.pid import OmniCalculator # Importa sua classe
from sender.radio_sender import RadioSender   # Importa sua classe

# --- CONFIGURAÇÕES DO TESTE ---
# Vamos simular que a bola está 1 metro (1000mm) à frente do robô
POSICAO_BOLA_FALSA = {'x': 0, 'y':-110}

# ID do robô e porta do rádio
ROBOT_ID_TESTE = 3
RADIO_PORT = "/dev/ttyACM0" # Verifique se esta é a porta correta
# ---------------------------------

def main():
    print("--- INICIANDO TESTE DE MOVIMENTO RETO ---")
    
    # 1. Inicializa os componentes necessários
    try:
        sender = RadioSender(robot_id=ROBOT_ID_TESTE, port=RADIO_PORT)
        omni_calc = OmniCalculator(wheel_radius_mm=30, robot_radius_mm=75)
        print("Componentes inicializados. O robô deve começar a se mover.")
    except Exception as e:
        print(f"ERRO: Não foi possível inicializar os componentes. Verifique a porta do rádio.")
        print(f"Detalhe: {e}")
        return

    # Loop de controle
    try:
        while True:
            # 2. Simula os dados da visão
            # O robô está "parado" na origem (0,0) e olhando para frente (ângulo 0)
            # O alvo é a bola falsa, 1m à frente
            robot_data = {
                'robot_current_x': 0,
                'robot_current_y': 0,
                'robot_current_orientation': 0,
                'robot_target_x': POSICAO_BOLA_FALSA['x'],
                'robot_target_y': POSICAO_BOLA_FALSA['y'],
                # O ângulo alvo também é para frente (0 graus)
                'robot_target_orientation': math.atan2(POSICAO_BOLA_FALSA['y'], POSICAO_BOLA_FALSA['x'])
            }

            # 3. Calcula as velocidades das rodas
            wheel_speeds = omni_calc.calculate_wheel_speeds(robot_data)

            # 4. Envia o comando para o rádio
            # ATENÇÃO: Verifique se esta ordem de rodas é a correta que definimos!
            sender.send_command(
                wheel_speeds['fl_speed'], wheel_speeds['fl_direction'],
                wheel_speeds['fr_speed'], wheel_speeds['fr_direction'],
                wheel_speeds['bl_speed'], wheel_speeds['bl_direction'], # M3 -> BR
                wheel_speeds['br_speed'], wheel_speeds['br_direction'], # M4 -> BL
                False # Kicker
            )
            
            time.sleep(0.01) # Loop rápido

    except KeyboardInterrupt:
        print("\nTeste interrompido.")
    finally:
        # Envia comando de parada para todos os motores
        print("Parando o robô...")
        sender.send_command(0,0,0,0,0,0,0,0,False)
        print("FIM.")


if __name__ == '__main__':
    main()