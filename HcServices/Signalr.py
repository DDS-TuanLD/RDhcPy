from signalrcore.hub_connection_builder import HubConnectionBuilder
import asyncio
import queue
import requests
from Cache.GlobalVariables import GlobalVariables
import Constant.constant as const
import logging
import threading
from Contracts.ITransport import ITransport
from Helper.System import System, eliminate_current_progress
import datetime
import time

def get_token():
    cache = GlobalVariables()
    try:
        renew_token = "https://iot-dev.truesight.asia/rpc/iot-ebe/account/renew-token"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'X-DormitoryId': cache.DormitoryId,
                   'Cookie': "RefreshToken={refresh_token}".format(refresh_token=cache.RefreshToken)}
        response = requests.post(renew_token, json=None, headers=headers).json()
        token = response['token']
        headers['Cookie'] = "Token={token}".format(token=token)
        return token
    except Exception as e:
        return None


class Signalr(ITransport):
    __hub: HubConnectionBuilder
    __globalVariables: GlobalVariables
    __logger: logging.Logger
    __lock: threading.Lock
  

    def __init__(self, log: logging.Logger):
        super().__init__()
        self.__logger = log
        self.__globalVariables = GlobalVariables()
        self.__lock = threading.Lock()
      
    def __build_connection(self):
        self.__hub = HubConnectionBuilder() \
            .with_url(const.SERVER_HOST + const.SIGNALR_SERVER_URL,
                      options={
                          "access_token_factory": get_token,
                          "headers": {
                          }
                      }) \
            .build()
        return self

    def __on_receive_event(self):
        self.__hub.on("Receive", self.__receive_event_callback)
        
    def __receive_event_callback(self, data):
        with self.__lock:
            self.receive_data_queue.put(data)

    def __on_disconnect_event(self):
        self.__hub.on_close(self.__disconnect_event_callback)

    def __disconnect_event_callback(self):
        print("disconnect to signalr server")
        self.__logger.debug("Disconnect to signalr server")
        self.reconnect()

    def __on_connect_event(self):
        self.__hub.on_open(self.__connect_event_callback())

    def __connect_event_callback(self):
        print("Connect to signalr server successfully")
        self.__logger.debug("Connect to signalr server successfully")

    async def disconnect(self):
        self.__hub.stop()
      
    def send(self, destination, data_send):
        entity = data_send[0]
        message = data_send[1]
        self.__hub.send("Send", [destination, entity, message])

    async def connect(self):
        connect_success = False
        while self.__globalVariables.RefreshToken == "":
            await asyncio.sleep(1)
        self.__build_connection()
        self.__on_connect_event()
        self.__on_disconnect_event()
        self.__on_receive_event()
        while not connect_success:
            try:
                self.__hub.start()
                self.__globalVariables.SignalrConnectSuccessFlag = True
                connect_success = True
            except Exception as err:
                self.__logger.error(f"Exception when connect with signalr server: {err}")
                print(f"Exception when connect with signalr server: {err}")
                self.__globalVariables.SignalrConnectSuccessFlag = False
            await asyncio.sleep(3)

    def reconnect(self):
        try:
            time.sleep(20)
            self.__hub.start()
            print("reconnect to signalr server successfully")
            self.__logger.debug("reconnect to signalr server successfully")
        except:
            print("fail to reconnect to signalr server")
            self.__logger.error("fail to reconnect to signalr server")
            eliminate_current_progress()
        
    def receive(self):
        pass
