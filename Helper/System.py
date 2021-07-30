from Helper.Terminal import execute, execute_with_result
from Database.Db import Db
from Model.systemConfiguration import systemConfiguration
from Cache.GlobalVariables import GlobalVariables
import datetime
from HcServices.Mqtt import Mqtt
from HcServices.Http import Http
from sqlalchemy import and_, or_
from HcServices.Http import Http
import aiohttp
import asyncio
import Constant.constant as const
import http
import json
import logging


def time_split(time: datetime.datetime):
    m = str(time.month)
    if int(m) < 10:
        m = "0" + m

    d = str(time.day)
    if int(d) < 10:
        d = "0" + d

    update_day = int(str(time.year) + m + d)
    update_time = 60 * time.hour + time.minute
    return update_day, update_time


def ping_google():
    rel = execute_with_result("ping -c3 www.google.com|grep packet")[1]
    try:
        rel2 = rel.split(", ")
        rel3 = rel2[2].split(" ")
        r = rel3[0] == "0%"
    except:
        r = False
    return r


def eliminate_current_progress():
    s = execute_with_result(f'ps | grep python3')
    dt = s[1].split(" ")
    current_progress_port = ""
    for i in range(len(dt)):
        if dt[i] != "":
            current_progress_port = dt[i]
            break
    execute(f'kill -9 {current_progress_port}')


def check_and_kill_all_repeat_progress():
    s = execute_with_result(f'ps|grep python3')
    current_self_repeat_process_list_info = s[1].split("\n")
    current_self_repeat_process_list_port = []
    for i in range(len(current_self_repeat_process_list_info)):
        p = current_self_repeat_process_list_info[i].split(" ")
        if p[len(p) - 1] != "RDhcPy/main.py":
            continue
        current_self_repeat_process_list_port.append(p[1])

    if len(current_self_repeat_process_list_port) > 1:
        kill_all_cmd = "kill -9"
        for i in range(len(current_self_repeat_process_list_port)):
            kill_all_cmd = kill_all_cmd + " " + current_self_repeat_process_list_port[i]
        execute(kill_all_cmd)


class System:
    __db = Db()
    __globalVariables = GlobalVariables()
    __logger = logging.Logger

    def __init__(self, logger: logging.Logger):
        self.__logger = logger

    async def update_reconnect_status_to_db(self, reconnect_time: datetime.datetime):
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        s = systemConfiguration(IsConnect=True, DisconnectTime=r['DisconnectTime'], ReconnectTime=reconnect_time,
                                IsSync=r['IsSync'])
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        await self.__push_data_to_cloud(r['DisconnectTime'], s)

    def update_disconnect_status_to_db(self, disconnect_time: datetime.datetime):
        s = systemConfiguration(IsConnect=False, DisconnectTime=disconnect_time, ReconnectTime=None, IsSync=False)
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        if r is None:
            self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
        if r is not None and r["IsSync"] != "False":
            self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)

    async def recheck_reconnect_status_of_last_activation(self):
        if not self.__globalVariables.RecheckConnectionStatusInDbFlag:
            rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
            r = rel.first()

            if r is None:
                s = systemConfiguration(IsConnect=True, DisconnectTime=datetime.datetime.now(),
                                        ReconnectTime=datetime.datetime.now(), IsSync=True)
                self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
                self.__globalVariables.RecheckConnectionStatusInDbFlag = True
                return

            s = systemConfiguration(IsConnect=r["IsConnect"], DisconnectTime=r['DisconnectTime'],
                                    ReconnectTime=r['ReconnectTime'], IsSync=r['IsSync'])

            if r["ReconnectTime"] is None:
                await self.update_reconnect_status_to_db(datetime.datetime.now())
                return

            if r["ReconnectTime"] is not None and r["IsSync"] == "False":
                ok = await self.__push_data_to_cloud(r["DisconnectTime"], s)
                if ok:
                    self.__globalVariables.RecheckConnectionStatusInDbFlag = True
                return
        self.__globalVariables.RecheckConnectionStatusInDbFlag = True
        return

    async def send_http_request_to_heartbeat_url(self, h: Http):
        heartbeat_url = const.SERVER_HOST + const.SIGNSLR_HEARDBEAT_URL
        header = h.create_new_http_header(cookie="", domitory_id=self.__globalVariables.DormitoryId)
        req = h.create_new_http_request(url=heartbeat_url, header=header)
        session = aiohttp.ClientSession()
        res = await h.post(session, req)
        await session.close()
        try:
            if (res != "") and (res.status == http.HTTPStatus.OK):
                return True
        except:
            return False

    async def __get_token(self, http: Http):
        refresh_token = self.__globalVariables.RefreshToken
        if refresh_token == "":
            return ""
        token_url = const.SERVER_HOST + const.TOKEN_URL
        cookie = f"RefreshToken={refresh_token}"
        header = http.create_new_http_header(cookie=cookie, domitory_id=self.__globalVariables.DormitoryId)
        req = http.create_new_http_request(url=token_url, header=header)
        session = aiohttp.ClientSession()
        res = await http.post(session, req)
        token = ""
        if res != "":
            try:
                data = await res.json()
                token = data['token']
            except:
                return ""
        await session.close()
        return token

    async def __push_data_to_cloud(self, reference_time: datetime.datetime, dt: systemConfiguration):
        t = time_split(time=reference_time)
        update_day = t[0]
        update_time = t[1]
        print(f"updateDay: {update_day}, updateTime: {update_time}")

        rel = self.__db.Services.DeviceAttributeValueServices.FindDeviceAttributeValueWithCondition(
            or_(and_(self.__db.Table.DeviceAttributeValueTable.c.UpdateDay == update_day,
                     self.__db.Table.DeviceAttributeValueTable.c.UpdateTime >= update_time),
                self.__db.Table.DeviceAttributeValueTable.c.UpdateDay > update_day))
        data = []
        for r in rel:
            if r['DeviceId'] == "" or r['DeviceAttributeId'] is None or r['Value'] is None:
                continue
            d = {
                "deviceId": r['DeviceId'],
                "deviceAttributeId": r['DeviceAttributeId'],
                "value": r['Value']
            }
            data.append(d)
        if not data:
            print("have no data to push")
            self.__logger.info("have no data to push")
            self.__update_sync_data_status_success_to_db(dt)
            return True

        data_send_to_cloud = json.dumps(data)
        print(f"data push to cloud: {data_send_to_cloud}")
        self.__logger.info(f"data push to cloud: {data_send_to_cloud}")
        res = await self.__send_http_request_to_push_url(data=data_send_to_cloud)
        print(f"pull data response: {res}")
        self.__logger.info(f"pull data response: {res}")
        if res == "":
            print("Push data failure")
            self.__logger.info("Push data failure")
            self.__update_sync_data_status_fail_to_db(dt)
            return False

        if (res != "") and (res.status == http.HTTPStatus.OK):
            self.__update_sync_data_status_success_to_db(dt)
            print("Push data successfully")
            self.__logger.info("Push data successfully")
            return True

        print("Push data failure")
        self.__logger.info("Push data failure")
        self.__update_sync_data_status_fail_to_db(dt)
        return False

    async def __send_http_request_to_push_url(self, data: str):
        h = Http()
        token = await self.__get_token(h)
        cookie = f"Token={token}"
        pull_data_url = const.SERVER_HOST + const.CLOUD_PUSH_DATA_URL
        header = h.create_new_http_header(cookie=cookie, domitory_id=self.__globalVariables.DormitoryId)
        req = h.create_new_http_request(url=pull_data_url, body_data=json.loads(data), header=header)
        session = aiohttp.ClientSession()
        res = await h.post(session, req)
        await session.close()
        return res

    def __update_sync_data_status_success_to_db(self, s: systemConfiguration):
        s.IsSync = True
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)

    def __update_sync_data_status_fail_to_db(self, s: systemConfiguration):
        s.IsSync = False
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
