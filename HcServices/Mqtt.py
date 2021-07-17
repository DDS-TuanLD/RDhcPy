import paho.mqtt.client as mqtt
import asyncio
import queue
import Constant.constant as const
from Cache.GlobalVariables import GlobalVariables
import logging
import threading
import socket
from Contracts.Itransport import Itransport


class MqttConfig():
    host: str
    port: int
    qos: int
    keepalive: int
    username: str
    password: str
    
    def __init__(self): 
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        self.host = ip
        self.port = const.MQTT_PORT
        self.qos = const.MQTT_QOS
        self.keepalive = const.MQTT_KEEPALIVE
        self.username = const.MQTT_USER
        self.password = const.MQTT_PASS
    
class Mqtt(Itransport):
    __mqttConfig: MqttConfig
    __client: mqtt.Client
    mqttDataQueue: queue.Queue
    __globalVariables: GlobalVariables
    __logger: logging.Logger
    __lock: threading.Lock
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
        self.__mqttConfig = MqttConfig()
        self.__client = mqtt.Client()
        self.mqttDataQueue = queue.Queue()
        self.__globalVariables = GlobalVariables()
        self.__lock = threading.Lock()
    
    def __on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        topic = msg.topic
        item = {"topic": topic, "msg": message}
        with self.__lock:
            self.mqttDataQueue.put(item)
        return
    
    def __on_connect(self, client, userdata, flags, rc):
            self.__client.subscribe(topic=const.MQTT_RESPONSE_TOPIC, qos=self.__mqttConfig.qos)
            self.__client.subscribe(topic=const.MQTT_CONTROL_TOPIC, qos=self.__mqttConfig.qos)
            self.__client.subscribe(topic="test", qos=self.__mqttConfig.qos)

    def _connect(self):
        self.__client.on_message = self.__on_message
        self.__client.on_connect = self.__on_connect
        self.__client.username_pw_set(username=self.__mqttConfig.username, password=self.__mqttConfig.password)
        try:
            self.__client.connect(self.__mqttConfig.host, self.__mqttConfig.port)
            self.__client.loop_start()
        except Exception as err:
            self.__logger.error(f"Exception in connect to mqtt: {err}")
            print(f"Exception in connect to mqtt: {err}")

    def Send(self, topic:str, send_data:str, qos: int):
        self.__client.publish(topic, payload=send_data, qos=qos)
             
    def DisConnect(self):
        self.__client.disconnect()

    def Init(self):
        self._connect()

    def ReConnect(self):
        pass
    
    def Receive(self):
        pass
