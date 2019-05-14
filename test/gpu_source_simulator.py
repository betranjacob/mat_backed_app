"""
This program simulates the messages from CarCoordinates Topic.
Randomly selects cars from carCount and updates their location and timestamp based on the defined message protocol.
"""

import time
import paho.mqtt.client as paho
import sys
import random
import traceback
from numpy import arange
sys.path.append("..")
from config_reader import broker, port, CarCount, CAR_COORDINATES_TOPIC, LoopDelay

GPS_SOURCE_SIMULATOR = 'gps_source_simulator'
RACE_DURATION_IN_SECONDS = 15
STARTING_LATITUDE = 23.5
STARTING_LONGITUDE = 67.5


class Car:

    def __init__(self, idx):
        self.index = idx
        self.latitude = STARTING_LATITUDE
        self.longitude = STARTING_LONGITUDE

    def __repr__(self):
        return 'Car(' + str(self.index) + ')'


def get_current_timestamp_in_ms():
    return str(int(time.time() * 1000))


def generate_car_coordinates(car_list):
    coordinates_list = []
    for car in car_list:
        car.longitude += round(random.sample(list(arange(0.0001, 0.0005, 0.00002)), 1)[0], 5)
        data = '{"timestamp": ' + get_current_timestamp_in_ms() + ', "carIndex": ' + str(car.index) + \
               ', "location": {"lat": ' + str(car.latitude) + ', "long": ' + str(car.longitude) + '}}'
        coordinates_list.append(data)
        print (data)
    return coordinates_list


def publish_coordinates(coordinates_list, mqtt_client):
    print('CCL: ', len(coordinates_list))
    for c in coordinates_list:
        print('Publishing: ', c)
        mqtt_client.publish(CAR_COORDINATES_TOPIC, c)


def run_race(car_map, mqtt_client):
    for i in range(RACE_DURATION_IN_SECONDS * 5):
        car_list = []
        for i in random.sample(range(1, CarCount + 1), 2):
            car_list.append(car_map[i])
        print('Generating Coordinates for ', [c.index for c in car_list])
        coordinates = generate_car_coordinates(car_list)
        publish_coordinates(coordinates, mqtt_client)
        time.sleep(LoopDelay / 1000)


def main():
    try:
        mqtt_client = paho.Client(GPS_SOURCE_SIMULATOR)
        mqtt_client.connect(broker, port=port)
        mqtt_client.loop_start()

        car_map = {}
        for i in range(1, CarCount + 1):
            car_map[i] = Car(i)

        # Publish the starting location
        publish_coordinates(generate_car_coordinates([car_map[c] for c in car_map]), mqtt_client)
        time.sleep(LoopDelay / 1000)

        # Start the race.
        run_race(car_map, mqtt_client)

        mqtt_client.disconnect()
        mqtt_client.loop_stop()
    except:
        print('Simulation failed with Error', (traceback.print_exc()))
        exit(1)


if __name__ == '__main__':
    main()