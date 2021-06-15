import paho.mqtt.client as mqtt
import asyncio
import queue
import Constant.constant as const
import time
from Cache.HcCache import HcCache
from Database.Db import Db
from Model.systemConfiguration import systemConfiguration
import socket
import logging
class MqttConfig():
    host = ""
    port: int
    sub_topic = ""
    pub_topic = ""
    qos: int
    keepalive: int
    username: str
    password: str

    def GetMqttConfig(self):
        """ Get mqtt server params from env file

        Returns:
            [MqttConfig]: [Instance of MqttConfig
            
        """
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        
        self.host = ip
        self.port = const.MQTT_PORT
        self.sub_topic = const.MQTT_SUB_TOPIC
        self.pub_topic = const.MQTT_PUB_TOPIC
        self.qos = const.MQTT_QOS
        self.keepalive = const.MQTT_KEEPALIVE
        self.username = const.MQTT_USER
        self.password = const.MQTT_PASS
        return self
    
class MqttServices():
    __mqttConfig = MqttConfig()
    __client = mqtt.Client()
    mqttDataQueue = queue.Queue()
    __cache = HcCache()
    __logger: logging.Logger
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
    
    def __on_message(self, client, userdata, msg):
        """[summary]

        Args:
            client ([type]): [description]
            userdata ([type]): [description]
            msg ([type]): [description]
        """
        item = msg.payload.decode("utf-8")
        try:
            self.mqttDataQueue.put_nowait(item)
        except Exception as err:
            pass
        return
    
    def __on_connect(self, client, userdata, flags, rc):
            self.__client.subscribe(topic=self.__mqttConfig.sub_topic, qos=self.__mqttConfig.qos)
            
    # def __on_public(self, client, userdata, mid):
    #     return
   
    async def MqttConnect(self):
        """  Connect to mqtt broker

        Returns:
            [bool]: [connect status: false/true]
        """
      
        connectSuccess = False
        
        self.__mqttConfig.GetMqttConfig()
        self.__client.on_message = self.__on_message
        # self.__client.on_publish = self.__on_public
        self.__client.on_connect = self.__on_connect
        #self.__client.username_pw_set(username=self.__mqttConfig.username, password=self.__mqttConfig.password)
        try:
            self.__client.connect_async(self.__mqttConfig.host, self.__mqttConfig.port)
            self.__client.reconnect()
            self.__client.loop_start()
            connectSuccess = True
        except Exception as err:
            self.__logger.error(f"Exception in connect to mqtt: {err}")
        return connectSuccess

    def MqttPublish(
        self, send_data, qos: int = 0):
        """ Public data to mqtt server

        Args:
            send_data ([type]): [description]
            qos (int, optional): [description]. Defaults to 0.
        """
        
        self.__client.publish(self.__mqttConfig.pub_topic, payload=send_data, qos=qos)

    def MqttStartLoop(self):
        self.__client.loop_start()

    def MqttStopLoop(self):
        self.__client.loop_stop()
        
    def MqttDisconnect(self):
        self.__client.disconnect()
        
    # def MqttLoopForever(self):
    #     self.__client.loop_forever()

    async def MqttServicesInit(self):
        connectSuccess = False
        while connectSuccess == False:
            connectSuccess =await self.MqttConnect()
            time.sleep(5)
        self.__logger.debug("Connect to mqtt status: " + str(connectSuccess))

        
   
