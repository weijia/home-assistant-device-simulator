import json
import time
from random import randint
from os import path
import paho.mqtt.client as mqtt

# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "broker": "127.0.0.1",
    "brokerPort": 1883,
    "brokerUser": "ENTERBROKERUSER",
    "brokerPass": "ENTERBROKERPASS",
    "lastState": "OFF",
    "client_id": "switchSimulator" + str(randint(0, 100000)),
    "configurationTopic": "homeassistant/switch/switchSimulator/config",
    "commandTopic": "home/lab/switchSimulator/set",
    "stateTopic": "home/lab/switchSimulator/state",
    "qos":1
}

CONFIGLOCATION = path.dirname(__file__) + "/config.json"

def load_config():
    try:
        with open(CONFIGLOCATION) as file_:
            config = json.load(file_)
    except (OSError, ValueError):
        print("Couldn't load " + CONFIGLOCATION)
        save_config()
    else:
        CONFIG.update(config)
        print("Loaded config from " + CONFIGLOCATION)


def save_config():
    try:
        with open(CONFIGLOCATION, "w") as file_:
            json.dump(CONFIG, file_)
    except OSError:
        print("Couldn't save " + CONFIGLOCATION)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client_, userdata_, flags_, rc):
    if rc == 0:
        client_.connected_flag = True  # set flag
        print("connected OK - ClientID " + CONFIG["client_id"])

        discoverymsg_ = '{"name": "'+CONFIG["client_id"]+'", "command_topic": "' + \
            CONFIG["commandTopic"] + '", "state_topic": "' + \
            CONFIG["stateTopic"] + '"}'
        print (discoverymsg_)
        send_message(client_,CONFIG["configurationTopic"], discoverymsg_, CONFIG["qos"])

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client_.subscribe(CONFIG["commandTopic"])

        send_message(client_,CONFIG["stateTopic"], CONFIG["lastState"], CONFIG["qos"])
    else:
        print("Bad connection Returned code=", rc)

# The callback for when a PUBLISH message is received from the server.
def on_message(client_, userdata_, msg):
    print ("received menssage: "+str(msg.payload)+ " from topic: " + msg.topic )
    if msg.payload == b'ON':
        alter_state(client_,CONFIG["stateTopic"], "ON", CONFIG["qos"])
    else:
        alter_state(client_,CONFIG["stateTopic"], "OFF", CONFIG["qos"])

def alter_state(client_,state_topic_, state_, qos_):
    send_message(client_,state_topic_, state_, qos_)
    CONFIG["lastState"] = state_
    save_config()

def send_message(client_, topic_, playload_, qos):
    print ("send menssage: " + playload_ + " to topic: " + topic_)
    return_ = client_.publish(topic_, payload=playload_, qos=qos)
    print ("RC:{} Mid{}".format(*return_))

def main():
    load_config()
    print (CONFIG)
    client_ = mqtt.Client(CONFIG["client_id"])

    # create flag in class
    mqtt.Client.connected_flag = False
    client_.on_connect = on_connect
    client_.on_message = on_message
    client_.username_pw_set(CONFIG["brokerUser"],CONFIG["brokerPass"])

    try:
        client_.loop_start()
        # connect to broker
        try:
            client_.connect(CONFIG["broker"], CONFIG["brokerPort"])
        except:
            print("connection failed...")
        
        # wait in loop for connection.
        while not client_.connected_flag:
            print("Waiting to connect...")
            time.sleep(1)

        # infinite loop for mantain the script alive
        while True:
            pass

    except KeyboardInterrupt:
        print ("\nBye...")
    finally:
        client_.loop_stop()
        client_.disconnect()

if __name__ == "__main__":
    main()
