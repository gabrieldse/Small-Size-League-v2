# main.py
import time
import threading

from Controle.strategy import strategy
from constants import TEAM_COLOR, LOOP_SLEEP_S
from system_logic import initialize_system
from utils.logger import setup_logger

def start_client_thread(client, name):
    """Inicia o UDPClient em thread separada."""
    thread = threading.Thread(target=client.run, daemon=True, name=name)
    thread.start()
    return thread

def main():
    logger = setup_logger('main', 'logs/main.log')
    logger.info("Starting the Robot Control System...")

    components = initialize_system()
    if not components:
        logger.error("Failed to initialize system components.")
        return

    # Iniciar threads para vision e game controller
    vision_thread = start_client_thread(components['vision_client'], "VisionThread")
    gc_thread = start_client_thread(components['gc_client'], "GCThread")
    strategys = None
    try:
        vision_client = components['vision_client']
        vision_parser = components['vision_parser']
        gc_client = components['gc_client']
        gc_parser = components['gc_parser']
        strategys = components['strategy']

        logger.info("Waiting for first vision data...")
        while vision_client.get_last_data() is None:
            time.sleep(0.01)
        logger.info("First vision data received. Entering main loop.")

        while True:
            # Receber dados do vision
            vision_raw_data = vision_client.get_last_data()
            if vision_raw_data is not None:
                try:
                    vision_parser.parser_loop(vision_raw_data)
                except Exception as e:
                    logger.error(f"Vision parser error: {e}", exc_info=True)

            # Receber dados do GameController
            gc_raw_data = gc_client.get_last_data()
            if gc_raw_data is not None:
                try:
                    gc_parser.parser_loop(gc_raw_data)
                except Exception as e:
                    logger.error(f"GC parser error: {e}", exc_info=True)
            
            detection = vision_parser.get_last_detection()

            strategys.play_game(detection, components)

            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Shutting down system...")
        
        if strategys:
            strategys.stop_all_robots(components['robot_senders'])

        if components.get('vision_client'):
            components['vision_client'].stop()
            components['vision_client'].stop()
        if components.get('gc_client'):
            components['gc_client'].stop()
        logger.info("System shutdown complete.")

if __name__ == '__main__':
    main()
