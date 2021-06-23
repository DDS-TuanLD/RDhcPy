import paho.mqtt.client as mqtt
import asyncio
import queue
import Constant.constant as const
import time
from Cache.HcCache import HcCache
import socket
import logging
import threading
class MqttConfig():
    host: str
    port: int
    qos: int
    keepalive: int
    username: str
    password: str
    
    def __init__(self, host:str, port: int, qos: int, keepalive: int, username: str, password: str):
        self.host = host
        self.port = port
        self.qos = qos
        self.keepalive = keepalive
        self.username = username
        self.password = password
    
class MqttServices():
    __mqttConfig: MqttConfig
    __client: mqtt.Client
    mqttDataQueue: queue.Queue
    __cache: HcCache
    __logger: logging.Logger
    __lock: threading.Lock
    
    def __init__(self, log: logging.Logger, mqttConfig: MqttConfig):
        self.__logger = log
        self.__mqttConfig = mqttConfig
        self.__client = mqtt.Client()
        self.mqttDataQueue = queue.Queue()
        self.__cache = HcCache()
        self.__lock = threading.Lock()
    
    def __on_message(self, client, userdata, msg):
        """[summary]

        Args:
            client ([type]): [description]
            userdata ([type]): [description]
            msg ([type]): [description]
        """
        message = msg.payload.decode("utf-8")
        topic = msg.topic
        item = {"topic": topic, "msg": message}
        with self.__lock:
            self.mqttDataQueue.put(item)
        return
    
    def __on_connect(self, client, userdata, flags, rc):
            self.__client.subscribe(topic=const.MQTT_SUB_RESPONSE_TOPIC, qos=self.__mqttConfig.qos)

    async def Connect(self):
        """  Connect to mqtt broker

        Returns:
            [bool]: [connect status: false/true]
        """
      
        connectSuccess = False
        self.__client.on_message = self.__on_message
        self.__client.on_connect = self.__on_connect
        #self.__client.username_pw_set(username=self.__mqttConfig.username, password=self.__mqttConfig.password)
        try:
            self.__client.connect_async("broker.mqttdashboard.com", self.__mqttConfig.port)
            self.__client.reconnect()
            self.__client.loop_start()
            connectSuccess = True
        except Exception as err:
            self.__logger.error(f"Exception in connect to mqtt: {err}")
            print(f"Exception in connect to mqtt: {err}")
        return connectSuccess

    def Publish(
        self, topic:str, send_data:str, qos: int):
        """ Public data to mqtt server

        Args:
            send_data ([type]): [description]
            qos (int, optional): [description]. Defaults to 0.
        """
        
        self.__client.publish(topic, payload=send_data, qos=qos)
        

    def StartLoop(self):
        self.__client.loop_start()

    def StopLoop(self):
        self.__client.loop_stop()
        
    def Disconnect(self):
        self.__client.disconnect()
        
    # def MqttLoopForever(self):
    #     self.__client.loop_forever()

    async def Init(self):
        connectSuccess = False
        while connectSuccess == False:
            connectSuccess =await self.Connect()
            time.sleep(2)

        
   
