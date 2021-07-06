from Helper.Terminal import Terminal
from Database.Db import Db
from Model.systemConfiguration import systemConfiguration
from Cache.Cache import Cache
import datetime

class System():
    __db=Db()
    __cache=Cache()
    
    def EliminateCurrentProgess(self):
        t = Terminal()
        s = t.ExecuteWithResult(f'ps | grep python3')
        dt = s[1].split(" ")
        for i in range(len(dt)):
            if dt[i] != "":
                print(dt[i])
                break
        s = t.Execute(f'kill -9 {dt[i]}')
    
    def UpdateReconnectStatusToDb(self, reconnectTime: datetime.datetime):
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        s =systemConfiguration(isConnect= True, DisconnectTime= r['DisconnectTime'], ReconnectTime= reconnectTime, isSync=False)
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        self.__cache.SignalrDisconnectStatusUpdate = False 
        self.__cache.SignalrDisconnectCount = 0
    
    def UpdateDisconnectStatusToDb(self, DisconnectTime: datetime.datetime):
        s =systemConfiguration(isConnect= False, DisconnectTime= DisconnectTime, ReconnectTime= None, isSync=False)
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        if r == None:
            self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
        if r!=None and r["IsSync"]!="False":
            self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        self.__cache.SignalrDisconnectStatusUpdate = True
        self.__cache.SignalrDisconnectCount = 0  
    
    def RecheckReconnectStatusOfLastActiveInDb(self):
        if self.__cache.RecheckConnectionStatusInDb == False:
            rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
            r = rel.first()
            if r["ReconnectTime"] == None:
                s = System()
                s.UpdateReconnectStatusToDb(reconnectTime=datetime.datetime.now())
            self.__cache.RecheckConnectionStatusInDb = True    