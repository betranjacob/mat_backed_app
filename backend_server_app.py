import time
import paho.mqtt.client as paho
import json
import mpu
import traceback
from config_reader import SERVER_UNIQUE_ID, CAR_COORDINATES_TOPIC, EVENT_TOPIC, CAR_STATUS_TOPIC, CarCount, \
                          broker, port

SECONDS_IN_HOUR = 60 * 60
mqtt_client = None
all_cars_data = dict()
position_map = dict.fromkeys(range(1, CarCount+1), None)


class Car:

    def __init__(self, index, timestamp, lat, lon):
        self.index = index
        self.latitude = lat
        self.longitude = lon
        self.timestamp = timestamp
        self.total_distance_covered = 0.0
        self.distance_covered = 0.0
        self.position = None
        self.speed = 0.0

    def _update_speed(self, timestamp):
        """
        Update the speed to KMs/Hour based on the timestamp difference and distance covered.
        :param timestamp:
        :return:
        """
        if timestamp != self.timestamp:
            # print 'T1:{}, T2:{}'.format(timestamp, self.timestamp)
            time_diff = float(timestamp - self.timestamp) / 1000  # Assuming timestamp is in millisecond granularity.
            self.speed = float(SECONDS_IN_HOUR / time_diff) * self.distance_covered  # KMs/Hour

    def update_status(self, timestamp, lat, lon):
        """
        Compute the distance covered in Kms from the lat/log pairs of concecutive updates.
        Update the total distance covered.
        Update the current parameters.
        :param timestamp:
        :param lat:
        :param lon:
        :return:
        """
        self.distance_covered = abs(float(mpu.haversine_distance((self.latitude, self.longitude), (lat, lon))))
        self.total_distance_covered += self.distance_covered
        self._update_speed(timestamp)
        self.latitude = lat
        self.longitude = lon
        self.timestamp = timestamp

    def __repr__(self):
        return 'Car(index:{}, lat:{}, lon:{}, pos:{}, speed={}, t_dc:{}, dc:{} t:{})'.format(self.index,
                                                                                             self.latitude,
                                                                                             self.longitude,
                                                                                             self.position,
                                                                                             self.speed,
                                                                                             self.total_distance_covered,
                                                                                             self.distance_covered,
                                                                                             self.timestamp)


def publish_event(car1, car2, timestamp):
    """
    Publish the event topic.
    :param car1:
    :param car2:
    :param timestamp:
    :return:
    """
    event_data = dict()
    event_data['timestamp'] = timestamp
    event_data['text'] = 'Car' + str(car1) + 'races ahead of Car' + str(car2) + 'in a dramatic overtake'
    print('Publishing Dramatic event:{}'.format(event_data['text']))
    mqtt_client.publish(EVENT_TOPIC, json.dumps(event_data))


def publish_speed_position(index, position=True):
    """
    Publish the speed/position topic.
    :param index:
    :param position:
    :return:
    """
    event_data = dict()
    car = all_cars_data[index]
    event_data['timestamp'] = car.timestamp
    event_data['carIndex'] = index
    event_data['type'] = 'POSITION' if position else 'SPEED'
    event_data['value'] = car.position if position else car.speed
    mqtt_client.publish(CAR_STATUS_TOPIC, json.dumps(event_data))
    print('Published {} event - {}'.format(event_data['type'], event_data['value']))


def check_position(index):
    """
    Check if the current event has advanced any of the car position.
    If yes, notify downstream.
    :param index:
    :return:
    """
    current_car = all_cars_data[index]
    current_car_previous_distance = current_car.total_distance_covered - current_car.total_distance_covered
    #  Compare the current car progress with other cars.
    for idx in [_idx for _idx in range(1, CarCount+1) if _idx != index]:
        car = all_cars_data.get(idx, None)
        if car and current_car_previous_distance < car.total_distance_covered and \
          current_car.total_distance_covered > car.total_distance_covered:
            publish_event(index, idx, current_car.timestamp)
            publish_speed_position(index)


def update_position():
    """
    Update the position of cars based on the total distance covered.
    :return:
    """
    dist_map = []
    for _, car in all_cars_data.items():
        dist_map.append((car.index, car.total_distance_covered))
    dist_map_sorted = sorted(dist_map, key=lambda c: c[1], reverse=True)

    cur_car_pos = 1
    prev_car_dist = -1
    for car in dist_map_sorted:
        if prev_car_dist > car[1]:
            cur_car_pos += 1
        all_cars_data[car[0]].position = cur_car_pos
        prev_car_dist = car[1]


def update_status(car_coordinates_dict):
    lat = car_coordinates_dict['location']['lat']
    long = car_coordinates_dict['location']['long']
    index = car_coordinates_dict['carIndex']
    timestamp = car_coordinates_dict['timestamp']
    car = all_cars_data.setdefault(index, Car(index, timestamp, lat, long))
    try:
        car.update_status(timestamp, lat, long)
        update_position()
        check_position(index)
        publish_speed_position(index, position=False)
    except:
        print(traceback.print_exc())
        exit(1)
    print('Finished update status for {} \n'.format(car))


def on_message(_, __, message):
    """
    Call back function to handle message subscriptions.
    :param _:
    :param __:
    :param message:
    :return:
    """
    if str(message.topic) == CAR_COORDINATES_TOPIC:
        car_coordinates_dict = json.loads(str(message.payload.decode("utf-8")))
    print("Received message on topic:{} = {}".format(str(message.topic), car_coordinates_dict))
    update_status(car_coordinates_dict)


def subscribe_to_topic(topic=CAR_COORDINATES_TOPIC):
    mqtt_client.on_message = on_message
    print("Connecting to broker {} on port {}".format(broker, port))
    mqtt_client.connect(broker, port=port)
    print("Subscribing on carCoordinates - ")
    mqtt_client.subscribe(topic)


def main():
    """
    Main entry function.
    Create a client and subscribe to carCoordinates topic.
    Update status, aggregate data and notify downstream as messages arrive.
    Run in an infinite loop until instructed to exit.
    :return:
    """
    global mqtt_client
    mqtt_client = paho.Client(SERVER_UNIQUE_ID)
    subscribe_to_topic()
    mqtt_client.loop_start()
    while True:
        time.sleep(1)
        #ip = input("Enter 'x' to exit the application")
        #if ip == 'x':
        #    print('Exiting Server')
        #    break
    mqtt_client.disconnect()
    mqtt_client.loop_stop()


if __name__ == '__main__':
    main()
