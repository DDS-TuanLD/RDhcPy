class MqttDataHandler():
    pass

class SignalRDataHandler():
    pass

class DataHandlerService():
    __mqttHandler: MqttDataHandler
    __signalrHandler: SignalRDataHandler
    
    def __init__(self):
        self.__mqttHandler = MqttDataHandler()
        self.__signalrHandler = MqttDataHandler()
        
    