import requests
import json
import time
import datetime

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

# https://developers.home-assistant.io/docs/api/rest/
key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJlNjllN2VkMWIxOWI0NTZjOTA4MDQzYjI0ZTQwMzM4ZCIsImlhdCI6MTY2NTUzMDYzNywiZXhwIjoxOTgwODkwNjM3fQ.UrzKrM8mqPzMCHLyWc5lplu__Ec0YCw7zk51oJFokDo"
headers = {"Authorization" : "Bearer " + key,
            "content-type": "application/json"
    }
ip = "192.168.99.15"
states = "http://" + ip + ":8123/api/states/"
remoteSend = "http://" + ip + ":8123/api/services/remote/send_command"
switchOn = "http://" + ip + ":8123/api/services/switch/turn_on"
switchOff = "http://" + ip + ":8123/api/services/switch/turn_off"
indoor_sensor = "sensor.indoor_temperature"
outdoor_sensor = "sensor.outdoor_temperature"
bm_fanout = "switch.bm_fanout"
universal_remote = "remote.universal_remote_remote"
mb_fan = "switch.mb_fan"
ent_fireplace = "switch.ent_fireplace"
livingroom = "climate.living_room"
mb_door_fan = True


while True:
    try:
        response = requests.get(states + indoor_sensor, headers=headers)
        indoor_temp = float(response.json()['state'])
        response = requests.get(states + outdoor_sensor, headers=headers)
        outdoor_temp = float(response.json()['state'])
        response = requests.get(states + livingroom, headers=headers)
        heater = response.json()['attributes']['hvac_action']
        print(heater)

        now = datetime.datetime.now()
        if heater == "cooling" and is_time_between(datetime.time(7, 0), datetime.time(20, 0), now.time()):
            print(f"{now} turning fans on")
            post = {"entity_id": bm_fanout}
            response = requests.post(switchOn, json=post, headers=headers)
            post = {"entity_id": mb_fan}
            response = requests.post(switchOn, json=post, headers=headers)
            if mb_door_fan == False:
                post = {"entity_id": universal_remote, "device": "mb_door_fan", "command":"on", "hold_secs": 1.5}
                response = requests.post(remoteSend, json=post, headers=headers)
                mb_door_fan = True
            pass
        else:
            print(f"{now} turning fans off")
            post = {"entity_id": bm_fanout}
            response = requests.post(switchOff, json=post, headers=headers)
            post = {"entity_id": mb_fan}
            response = requests.post(switchOff, json=post, headers=headers)
            if mb_door_fan == True:
                post = {"entity_id": universal_remote, "device": "mb_door_fan", "command":"off", "hold_secs": 1.5}
                response = requests.post(remoteSend, json=post, headers=headers)
                mb_door_fan = False
            pass
        if heater == "heating":
            print(f"{now} turning heater on")
            post = {"entity_id": ent_fireplace}
            response = requests.post(switchOn, json=post, headers=headers)
        else:
            post = {"entity_id": ent_fireplace}
            response = requests.post(switchOff, json=post, headers=headers)

    except Exception as ex:
        print(ex)
    time.sleep(15)
