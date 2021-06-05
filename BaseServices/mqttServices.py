import paho.mqtt.client as mqtt
import os
import asyncio
import queue
import threading
class MqttConfig():
    host = ""
    port = ""
    sub_topic = ""
    pub_topic = ""
    qos = ""
    keepalive = ""

    def GetMqttConfig(self):
        self.host = os.getenv("MQTT_HOST")
        self.port = os.getenv("MQTT_PORT")
        self.sub_topic = os.getenv("MQTT_SUB_TOPIC")
        self.pub_topic = os.getenv("MQTT_PUB_TOPIC")
        self.qos = os.getenv("MQTT_QOS")
        self.keepalive = os.getenv("MQTT_KEEPALIVE")
        return self



class MqttServices():
    __mqttConfig = MqttConfig()
    __client = mqtt.Client()
    __queue = queue.Queue()
    __lock = threading.Lock()

    def __on_message(self, client, userdata, msg):
        item = msg.payload.decode("utf-8")
        print(item)
        try:
            with self.__lock:
                self.__queue.put_nowait(item)
        except Exception as err:
            print(f"Err when put subcribe data in queue: {err}")
        return
        
    # def __on_public(self, client, userdata, mid):
    #     return
    # def __on_connect(self, client, userdata, flags, rc, properties=None):
    #     return
   
    def MqttConnect(self):
        self.__mqttConfig = MqttConfig().GetMqttConfig()
        self.__client.on_message = self.__on_message
        # self.__client.on_publish = self.__on_public
        # self.__client.on_connect = self.__on_connect
        try:
            self.__client.connect(self.__mqttConfig.host, int(self.__mqttConfig.port))
            self.__client.subscribe(topic=self.__mqttConfig.sub_topic, qos=int(self.__mqttConfig.qos))
        except Exception as err:
            print(f"Exception in connect to mqtt: {err}")
        return self

    def MqttPublish(self, data):
        self.__client.publish(self.__mqttConfig.pub_topic, payload=data, qos=int(self.__mqttConfig.qos))
    
    def MqttSubscribe(self, topic, qos=0):
        self.__client.subscribe(topic, qos)

    def MqttStartLoop(self):
        self.__client.loop_start()

    def MqttStopLoop(self):
        self.__client.loop_stop()

    def MqttLoopForever(self):
        self.__client.loop_forever()

    async def MqttHandlerData(self):
        while True:
            await asyncio.sleep(0.5)
            if self.__queue.empty() == False:
                with self.__lock:
                    item = self.__queue.get()
                    print(item)