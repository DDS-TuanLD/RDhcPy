from BaseServices.httpServices import HttpServices
from BaseServices.signalrServices import SignalrClient
from ExtraServices.hcRequestServices import HcRequestServices
from BaseServices.mqttServices import MqttServices


class HcController:

    def __init__(self):
        self.httpServices = HttpServices()
        self.signalServices = SignalrClient()
        self.hcRequestServices = HcRequestServices()
        self.mqttServices = MqttServices()
        
    def RunForever(self):
        while(1):
            return