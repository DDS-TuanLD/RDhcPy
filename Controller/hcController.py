from BaseServices.httpServices import HttpServices
from BaseServices.signalrServices import SignalrClient
from ExtraServices.hcRequestServices import HcRequestServices



class HcController:

    def __init__(self):
        self.httpServices = HttpServices()
        self.signalServices = SignalrClient()
        self.hcRequestServices = HcRequestServices()
        
    def RunForever(self):
        while(1):
            return