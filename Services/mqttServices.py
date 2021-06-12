import paho.mqtt.client as mqtt
import asyncio
import queue
import Constant.constant as const
class MqttConfig():
    host = ""
    port: int
    sub_topic = ""
    pub_topic = ""
    qos: int
    keepalive: int

    def GetMqttConfig(self):
        """ Get mqtt server params from env file

        Returns:
            [MqttConfig]: [Instance of MqttConfig
        """
        self.host = const.MQTT_HOST
        self.port = const.MQTT_PORT
        self.sub_topic = const.MQTT_SUB_TOPIC
        self.pub_topic = const.MQTT_PUB_TOPIC
        self.qos = const.MQTT_QOS
        self.keepalive = const.MQTT_KEEPALIVE
        return self



class MqttServices():
    __mqttConfig = MqttConfig()
    __client = mqtt.Client()
    __queue = queue.Queue()

    def __on_message(self, client, userdata, msg):
        """[summary]

        Args:
            client ([type]): [description]
            userdata ([type]): [description]
            msg ([type]): [description]
        """
        
        item = msg.payload.decode("utf-8")
        try:
            self.__queue.put_nowait(item)
        except Exception as err:
            print(f"Error when put subcribe data in queue: {err}")
        return
    
    # def __on_connect(self, client, userdata, flags, rc):
    #         self.__client.subscribe(topic=self.__mqttConfig.sub_topic, qos=self.__mqttConfig.qos)
            
    # def __on_public(self, client, userdata, mid):
    #     return

   
    def MqttConnect(self):
        """  Connect to mqtt broker

        Returns:
            [bool]: [connect status: false/true]
        """
        
        connectSuccess = False
        self.__mqttConfig.GetMqttConfig()
        self.__client.on_message = self.__on_message
        # self.__client.on_publish = self.__on_public
        # self.__client.on_connect = self.__on_connect
        try:
            self.__client.connect(self.__mqttConfig.host, self.__mqttConfig.port)
            self.__client.subscribe(topic=self.__mqttConfig.sub_topic, qos=int(self.__mqttConfig.qos))
            self.__client.loop_start()
            connectSuccess = True
        except Exception as err:
            print(f"Exception in connect to mqtt: {err}")
        return connectSuccess

    def MqttPublish(
        self, send_data, qos: int = 0):
        """ Public data to mqtt server

        Args:
            send_data ([type]): [description]
            qos (int, optional): [description]. Defaults to 0.
        """
        
        self.__client.publish(self.__mqttConfig.pub_topic, payload=send_data, qos=qos)
    
    # def MqttSubscribe(
    #     self, topic, qos):
    #     self.__client.subscribe(topic, qos)

    def MqttStartLoop(self):
        self.__client.loop_start()

    def MqttStopLoop(self):
        self.__client.loop_stop()

    # def MqttLoopForever(self):
    #     self.__client.loop_forever()

    async def MqttServicesInit(self):
        startSuccess = False
        while startSuccess == False:
            startSuccess =  self.MqttConnect()
            await asyncio.sleep(5)
        
    async def MqttHandlerData(self):
        """ This function handler data received in queue
        """
        while True:
            await asyncio.sleep(0.5)
            if self.__queue.empty() == False:
                item = self.__queue.get()
                print(item)
