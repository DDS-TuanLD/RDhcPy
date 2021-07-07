HttpStatusCodeOk = 200
#Cloud generic infomation
SERVER_HOST = "https://iot-dev.truesight.asia"

#SignalR connection option
SIGNALR_SERVER_URL = "/rpc/iot-ebe/signalr/sync"
SIGNSLR_HEARDBEAT_URL = "/rpc/iot-ebe/sync/time"
SIGNALR_COMMAND_ENTITY = "Command"
SIGNALR_RESPONSE_ENTITY = "HC-DeviceAttributeValue"

#pull,push data url
CLOUD_PUSH_DATA_URL = "/rpc/iot-ebe/sync/hc/merge-device-attribute-value"

#Server connection option
TOKEN_URL = "/rpc/iot-ebe/account/renew-token"

#Mqtt connection option
MQTT_PORT = 1883
MQTT_QOS = 2
MQTT_KEEPALIVE = 60
MQTT_PUB_CONTROL_TOPIC = "HC.CONTROL"
MQTT_SUB_RESPONSE_TOPIC = "HC.CONTROL.RESPONSE"
MQTT_USER = "RD"
MQTT_PASS = "1"

#Sqlite connection option
DB_NAME = "rd.Sqlite"

#
