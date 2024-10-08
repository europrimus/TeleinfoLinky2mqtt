#!/usr/bin/python3
"""
    Generic MQTT module to publish or subscribe to a MQTT broker
    with logging
"""

import datetime
import logging
from paho.mqtt import client as mqtt_client

log_file = "mqtt.log"

print(f"logging to {log_file}. follow execution using 'tail -f {log_file}'")
logging.basicConfig(filename=log_file, level=logging.DEBUG)

class myMqtt():
    """
        contains basic MQTT resources
    """
    client_id = ""
    broker = ""
    port = 1883

    def __init__(self, client_id):
        self.client_id = client_id
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
        # print(self.client)
        self.log = logging.getLogger(client_id)
        #self.log.basic(filename=f"{log_client_id}.txt", encoding='utf-8', level=logging.DEBUG)
        self.client.enable_logger(self.log)
        self.log.info(f"init complete")

    def on_connect(self, mqtt_client_id, userdata, flags, rc):
        ymdhms = self.yyyymmddhhmmss()
        if rc == 0:
            self.log.info(f"{ymdhms}: {self.client_id} Connected to MQTT Broker {self.broker}")
        else:
            self.log.info(f"{ymdhms}: {self.client_id} Failed to connect to MQTT Broker {self.broker}, return code %d\n", rc)

    def on_socket_open(self):
        self.log.info(f"socket open")

    def on_socket_close(self):
        self.log.info(f"socket close")
        self.client.connect(self.broker, self.port, self.keepalive)

    def connect_to(self, broker, port=1883, keepalive=60, publisher=False):
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        ymdhms = self.yyyymmddhhmmss()
        self.port = port
        try:
            self.client.connect(broker, port, keepalive)
        except Exception as e:
            logging.error(f"{e}")
        if publisher:
            """
            With paho.mqtt, publishers need to call loop_start() to send regular PINGs
            """
            self.client.loop_start()
        self.publish(topic=f"time/{self.client_id}/start", msg=ymdhms)
        self.client.will_set(topic="will/msg", payload=f"{self.client_id}: This is my last will, I'm disconnected without asking for it. I started at {ymdhms}")

    def disconnect(self):
        self.client.disconnect()

    def on_message(self, c, userdata, msg):
        ymdhms = self.yyyymmddhhmmss()
        if "last will" in msg.topic:
            self.log.info(f"{ymdhms} < {msg.topic}: {msg.payload.decode()}")
        else:
            self.log.info(f"{ymdhms} < {msg.topic}: {msg.payload.decode()}")

    def yyyymmddhhmmss(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def on_log(self, userdata, level, buf):
        self.log.info("log: {buf}")

    def subscribe(self, topics, qos=1):
        self.client.subscribe(topics, qos)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.onlog = self.on_log

    def publish(self, topic, msg, qos=1, retain=True):
        result = self.client.publish(topic, msg, retain)
        status = result[0]
        if status == 0:
            self.log.info(f"{self.client_id} > {topic}: {msg}")
        else:
            self.log.info(f"Failed to send message to topic {topic}: result {str(result)}")
            """
            In case of publishing errors, reconnect
            """
            self.client.reconnect()
            self.client.publish(topic, msg, retain)

    def listen(self):
        """
        Listeners need to call loop_forever()
        """
        self.client.loop_forever()

