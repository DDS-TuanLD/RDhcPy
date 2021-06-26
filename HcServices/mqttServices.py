import paho.mqtt.client as mqtt
import asyncio
import queue
import Constant.constant as const
from Cache.HcCache import HcCache
import logging
import threading
import socket
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
    
class MqttServices():
    __mqttConfig: MqttConfig
    __client: mqtt.Client
    mqttDataQueue: queue.Queue
    __cache: HcCache
    __logger: logging.Logger
    __lock: threading.Lock
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
        self.__mqttConfig = MqttConfig()
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
            self.__client.subscribe(topic=const.MQTT_PUB_CONTROL_TOPIC, qos=self.__mqttConfig.qos)

    async def Connect(self):
        """  Connect to mqtt broker

        Returns:
            [bool]: [connect status: false/true]
        """
      
        connectSuccess = False
        self.__client.on_message = self.__on_message
        self.__client.on_connect = self.__on_connect
        self.__client.username_pw_set(username=self.__mqttConfig.username, password=self.__mqttConfig.password)
        try:
            self.__client.connect_async(self.__mqttConfig.host, self.__mqttConfig.port)
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

    async def Init(self):
        connectSuccess = False
        while connectSuccess == False:
            connectSuccess =await self.Connect()
            await asyncio.sleep(5)

        
   
