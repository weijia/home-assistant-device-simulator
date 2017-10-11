import paho.mqtt.client as mqtt
import json
import time
from random import randint
from os import path

# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "broker": "127.0.0.1",
    "brokerPort": 1883,
    "lastState": 0, 
    "client_id": "switchSimulator"+str(randint(0, 100000)),
    "configurationTopic": "homeassistant/switch/switchSimulator/config",
    "commandTopic": "home/lab/switchSimulator/set",
    "stateTopic": "home/lab/switchSimulator/state"
}

def load_config(configLocatcion):
    try:
        with open(configLocation) as f:
            config = json.load(f)
    except (OSError, ValueError):
        print("Couldn't load "+configLocation)
        save_config(configLocation)
    else:
        CONFIG.update(config)
        print("Loaded config from "+configLocation)

def save_config(configLocatcion):
    try:
        with open(configLocatcion, "w") as f:
            json.dump(CONFIG,f)
    except OSError:
        print("Couldn't save "+configLocation)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK - ClientID " + CONFIG["client_id"])
        
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")
    else:
        print("Bad connection Returned code=",rc)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

configLocation = path.dirname(__file__)+"/config.json"
load_config(configLocation)
#create flag in class
mqtt.Client.connected_flag=False 
client = mqtt.Client(CONFIG["client_id"])
client.on_connect = on_connect
client.on_message = on_message

try:
    client.loop_start()
    #connect to broker  
    try:
        client.connect(CONFIG["broker"],CONFIG["brokerPort"])
    except:
        print("connection failed...")
    
    #wait in loop for connection.
    while not client.connected_flag: 
        print("Waiting to connect...")
        time.sleep(1)

    s = "RC:{} Mid{}"
    r=client.publish(CONFIG["configurationTopic"],payload="teste2",qos=2)
    print (s.format(*r))
    
    #infinite loop for mantain the script alive
    while True:
        pass
except KeyboardInterrupt:
    print ("\nBye...")
finally:
    client.loop_stop()
    client.disconnect()