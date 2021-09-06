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
    __disconnectFlag: int
    __disconnectRetryCount: int

    def __init__(self, log: logging.Logger):
        super().__init__()
        self.__logger = log
        self.__globalVariables = GlobalVariables()
        self.__lock = threading.Lock()
        self.__disconnectFlag = 1
        self.__disconnectRetryCount = 0

    def __build_connection(self):
        self.__hub = HubConnectionBuilder() \
            .with_url(const.SERVER_HOST + const.SIGNALR_SERVER_URL,
                      options={
                          "access_token_factory": get_token,
                          "headers": {
                          }
                      }) \
            .with_automatic_reconnect({
                "type": "raw",
                "keep_alive_interval": 5,
                "reconnect_interval": 5,
                "max_attempts": 40
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
        self.__disconnectFlag = 0
        self.__disconnectRetryCount = 0

    def __on_connect_event(self):
        self.__hub.on_open(self.__connect_event_callback())

    def __connect_event_callback(self):
        print("Connect to signalr server")
        self.__logger.debug("Connect to signalr server")

    async def disconnect(self):
        self.__disconnectFlag = 1
        try:
            self.__hub.stop()
        except Exception as err:
            self.__logger.error(f"Exception when disconnect with signalr server: {err}")
        await asyncio.sleep(1)
        if self.__disconnectFlag == 1:
            if self.__disconnectRetryCount == 15:
                self.__disconnectRetryCount = 0
                print("Disconnect signalr server timeout")
                self.__logger.error("Disconnect signalr timeout")
                t = datetime.datetime.now().timestamp() - 30
                s = System(self.__logger)
                s.update_disconnect_status_to_db(datetime.datetime.fromtimestamp(t))
                eliminate_current_progress()

            self.__disconnectRetryCount = self.__disconnectRetryCount + 1
            print(f"Retry to disconnect signalr server {self.__disconnectRetryCount} times")
            await self.disconnect()

    def send(self, destination, data_send):
        entity = data_send[0]
        message = data_send[1]
        self.__hub.send("Send", [destination, entity, message])

    async def connect(self):
        run_only_one = False
        while self.__globalVariables.RefreshToken == "":
            await asyncio.sleep(1)
        self.__build_connection()
        self.__on_connect_event()
        self.__on_disconnect_event()
        self.__on_receive_event()
        while True:
            if self.__globalVariables.ResetSignalrConnectFlag:
                await self.disconnect()
                self.__hub.start()
                self.__globalVariables.ResetSignalrConnectFlag = False
                  
            try:
                if not self.__globalVariables.SignalrConnectSuccessFlag and not run_only_one:
                    self.__hub.start()
                    self.__globalVariables.SignalrConnectSuccessFlag = True
                    run_only_one = True
            except Exception as err:
                self.__logger.error(f"Exception when connect with signalr server: {err}")
                print(f"Exception when connect with signalr server: {err}")
                self.__globalVariables.SignalrConnectSuccessFlag = False
            await asyncio.sleep(3)

    def reconnect(self):
        try:
            self.__hub.start()
        except Exception as err:
            self.__logger.error(f"Exception when connect with signalr server: {err}")

    def receive(self):
        pass
