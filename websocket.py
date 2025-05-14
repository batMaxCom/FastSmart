import asyncio
import json
import logging
import os

import websockets

TV_IP = os.getenv("TV_IP")
PORT = 3000
CLIENT_KEY_FILE = "client_key.json"

class LGWebOSClient:
    def __init__(self, ip=TV_IP, port=PORT, client_key_file=CLIENT_KEY_FILE):
        self.ip = ip
        self.port = port
        self.client_key_file = client_key_file
        self.websocket = None
        self.connected = False
        self.connecting = False
        self.reconnect_tries = 0
        self.max_retries = 5
        self.lock = asyncio.Lock()

    async def connect(self):
        async with self.lock:
            if self.connected or self.connecting:
                return

            self.connecting = True
            for _ in range(self.max_retries):
                try:
                    uri = f"ws://{self.ip}:{self.port}"
                    logging.info(f"🔌 Подключение к {uri}")
                    self.websocket = await websockets.connect(uri)

                    if os.path.exists(self.client_key_file):
                        with open(self.client_key_file, "r") as f:
                            client_key = json.load(f).get("client-key")
                        register_msg = {
                            "type": "register",
                            "id": "register_0",
                            "payload": {"client-key": client_key}
                        }
                    else:
                        register_msg = {
                            "type": "register",
                            "id": "register_0",
                            "payload": {
                                "forcePairing": False,
                                "pairingType": "PROMPT",
                                "manifest": {
                                    "manifestVersion": 1,
                                    "appVersion": "1.1",
                                    "signed": {
                                        "created": "20140509",
                                        "appId": "com.lge.test",
                                        "vendorId": "com.lge",
                                        "localizedAppNames": {"": "LG Remote App"},
                                        "localizedVendorNames": {"": "LG Electronics"},
                                        "serial": "2f930e2d2cfe083771f68e4fe7bb07"
                                    },
                                    "permissions": ["LAUNCH", "CONTROL_POWER", "CONTROL_AUDIO", "READ_RUNNING_APPS"]
                                }
                            }
                        }

                    await self.websocket.send(json.dumps(register_msg))

                    async for message in self.websocket:
                        data = json.loads(message)
                        logging.info(f"Получено: {data}")

                        # Ответ на ping
                        if data.get("type") == "ping":
                            await self.websocket.send(json.dumps({"type": "pong"}))
                            logging.info("Отправлен pong")
                            continue

                        if data.get("type") == "registered":
                            client_key = data.get("payload", {}).get("client-key")
                            if client_key:
                                with open(self.client_key_file, "w") as f:
                                    json.dump({"client-key": client_key}, f)
                            break
                    self.connected = True
                    logging.info("Успешное подключение к телевизору")
                    break
                except Exception as e:
                    logging.warning(f"Ошибка подключения: {e}")
                    await asyncio.sleep(3)
                    self.reconnect_tries += 1
            self.connecting = False

    async def send_command(self, command_name, uri, payload):
        if not self.connected:
            await self.connect()
        if not self.connected:
            raise ConnectionError("Не удалось подключиться к телевизору")

        command = {
            "type": "request",
            "id": command_name,
            "uri": uri,
            "payload": payload
        }
        await self.websocket.send(json.dumps(command))
        async for message in self.websocket:
            return message


tv_client = LGWebOSClient()
