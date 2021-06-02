import signalrcore.hub_connection_builder as SignalrBuilder
from signalrcore.hub.auth_hub_connection import AuthHubConnection
class ISignalrBaseServices:
    hub= AuthHubConnection
    
    def __init__(self):
        self.hub = SignalrBuilder.HubConnectionBuilder().build()
        pass

    def StartConnectToServer(self):
        pass

    def DisConnectWithServer(self):
        pass
