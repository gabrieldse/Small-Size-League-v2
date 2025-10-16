"""
Don't alter this file directly. Instead, modify the values in config.py.
This file translates those values into constants used throughout the system.
"""

import config

TEAM_COLOR = 'blue' if config.COR_DO_TIME == 1 else 'yellow'
ROBOT_CONFIGS = {
    config.ID_ALVIN: {'ip': config.IP_ALVIN, 'port': config.PORT},
    config.ID_SIMON: {'ip': config.IP_SIMON, 'port': config.PORT},
    config.ID_THEODORE: {'ip': config.IP_THEODORE, 'port': config.PORT},
}

VISION_IP = config.VISION_DATA_SOURCE_IP
VISION_PORT = config.VISION_DATA_SOURCE_PORT

LOOP_SLEEP_S = config.TEMPO_MAXIMO_SEM_COMUNICACAO_S

HALT = 0 
STOP = 1
NORMAL_START = 2
FORCE_START = 3
KICKOF_YELLOW = 4
KICKOF_BLUE = 5
PENALTY_YELLOW = 6
PENALTY_BLUE = 7