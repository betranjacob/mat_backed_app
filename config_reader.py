import os


def read_config_file(f_path):
    """
    Read config parameters from environment variables. 
    :param f_path:
    :return:
    """
    env_map = {}
    try:
        with open(f_path) as f:
            for line in f:
                line = line.strip()
                # Exclude Comments
                if line.startswith('#'):
                    continue
                line = line.split('=')
                env_map[line[0]] = line[1]

    except IOError:
        print ('Failed to read file from path: {}'.format(f_path))
        pass
    return env_map

MQTT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'mqtt.env')
CARS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'cars.env')
SOURCE_GPS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'source_gps.env')
SERVER_UNIQUE_ID = 'car_status_monitor'
CAR_COORDINATES_TOPIC = 'carCoordinates'
EVENT_TOPIC = 'events'
CAR_STATUS_TOPIC = 'carStatus'
CarCount = int(read_config_file(CARS_CONFIG_FILE)['CAR_COUNT'])
LoopDelay = float(read_config_file(SOURCE_GPS_CONFIG_FILE)['LOOP_DELAY'])
broker = read_config_file(MQTT_CONFIG_FILE)['MQTT_URL'].rsplit(':', 1)[0]
port = int(read_config_file(MQTT_CONFIG_FILE)['MQTT_URL'].rsplit(':', 1)[1])
