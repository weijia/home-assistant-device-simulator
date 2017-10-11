import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK")
        
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")
    else:
        print("Bad connection Returned code=",rc)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

#create flag in class
mqtt.Client.connected_flag=False 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.loop_start()
    #connect to broker   
    try:
        client.connect("localhost")
    except:
        print("connection failed...")

    #wait in loop for connection.
    while not client.connected_flag: 
        print("Waiting to connect...")
        time.sleep(1)

    #infinite loop for mantain the script alive
    while True:
        pass
except KeyboardInterrupt:
    print ("\nBye...")
finally:
    client.loop_stop()
    client.disconnect()