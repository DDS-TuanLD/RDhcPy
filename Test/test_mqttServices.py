import unittest
from HcServices.mqttServices import MqttServices
import aiohttp
import asyncio
from unittest.async_case import IsolatedAsyncioTestCase
import http

class TestHttpService(IsolatedAsyncioTestCase):
    mqtt = MqttServices()
    
    async def test_mqttConnect(self):
        with self.assertRaises(TypeError):
            await self.mqtt.MqttConnect()
        
