# main.py
import time
import threading
from constants import TEAM_COLOR, LOOP_SLEEP_S
from system_logic import (
    initialize_system,
    process_robot_logic,
    stop_all_robots,
    enforce_game_rules
)
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

    try:
        vision_client = components['vision_client']
        vision_parser = components['vision_parser']
        gc_client = components['gc_client']
        gc_parser = components['gc_parser']

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

            # Processar dados de detecção
            detection = vision_parser.get_last_detection()
            print(detection)
            if detection:
                our_robots = detection.robots_blue if TEAM_COLOR == "blue" else detection.robots_yellow
                opponent_robots = detection.robots_yellow if TEAM_COLOR == "blue" else detection.robots_blue
                balls = detection.balls

                gc_data = gc_parser.get_last_data()
                print(gc_data)
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
                    logger.warning("No ball detected. Stopping robots.")
                    stop_all_robots(components['robot_senders'])
                    time.sleep(0.05)
                    continue

                ball_info = balls[0]
                print(f"Ball detected at x={ball_info.x:.1f}, y={ball_info.y:.1f}")

                if not our_robots:
                    logger.warning("No robots detected for our team!")
                    stop_all_robots(components['robot_senders'])
                    time.sleep(0.01)
                    continue

                print(f"Detected {len(our_robots)} of our robots.")
                for robot_info in our_robots:
                    robot_id = robot_info.robot_id
                    x, y, orientation = robot_info.x, robot_info.y, robot_info.orientation

                    print(f"Robot {robot_id}: x={x:.1f}, y={y:.1f}, θ={orientation:.2f}")
                    try:
                        can_play = enforce_game_rules(robot_info, ball_info, components, gc_parser)

                        if can_play:
                            print('robo vai jogar')
                            gc_data = gc_parser.get_last_data() 
                            process_robot_logic(robot_info, ball_info, components)
                        else:
                            print('pararei de jogar')
                            # Para o robô se não puder jogar
                            components['robot_senders'][robot_id].stop()

                    except Exception as e:
                        logger.error(f"Error processing robot {robot_id}: {e}", exc_info=True)

            else:
                print("No vision data received. Stopping all robots.")
                stop_all_robots(components['robot_senders'])

            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Shutting down system...")
        stop_all_robots(components['robot_senders'])
        if components.get('vision_client'):
            components['vision_client'].stop()
        if components.get('gc_client'):
            components['gc_client'].stop()
        logger.info("System shutdown complete.")

if __name__ == '__main__':
    main()
