import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

HOST = "localhost"
PORT = 3000

tv_state = {
    "power": True,
    "volume": 20,
    "mute": False,
    "channel": 1
}

async def handle_client(websocket):
    logging.info(f"🔌 Клиент подключен: {websocket.remote_address}")

    try:
        async for message in websocket:
            data = json.loads(message)
            logging.info(f"📥 Получено от клиента: {data}")

            msg_type = data.get("type")
            uri = data.get("uri")

            # Ответ на регистрацию
            if msg_type == "register":
                response = {
                    "type": "registered",
                    "payload": {
                        "client-key": "mock-client-key"
                    }
                }
                await websocket.send(json.dumps(response))
                logging.info("✅ Ответ на регистрацию отправлен")

            # Получение состояния питания
            elif uri == "ssap://com.webos.service.tvpower/power/getPowerState":
                await websocket.send(json.dumps({
                    "type": "response",
                    "id": data.get("id"),
                    "payload": {
                        "returnValue": tv_state["power"]
                    }
                }))
                logging.info(f"⚡ Состояние питания: {tv_state['power']}")

            # Выключение телевизора
            elif uri == "ssap://system/turnOff":
                tv_state["power"] = False
                await websocket.send(json.dumps({
                    "type": "response",
                    "id": data.get("id"),
                    "payload": {"returnValue": True}
                }))
                logging.info("📴 Телевизор выключен")

            # Включение телевизора
            elif uri == "ssap://system/turnOn":
                tv_state["power"] = True
                await websocket.send(json.dumps({
                    "type": "response",
                    "id": data.get("id"),
                    "payload": {"returnValue": True}
                }))
                logging.info("📺 Телевизор включен")

            # Получение статуса аудио
            elif uri == "ssap://audio/getStatus":
                await websocket.send(json.dumps({
                    "type": "response",
                    "id": data.get("id"),
                    "payload": {
                        "volume": tv_state["volume"],
                        "mute": tv_state["mute"]
                    }
                }))
                logging.info("🔊 Отправлен статус звука")

            # Установка громкости
            elif uri == "ssap://audio/setVolume":
                new_volume = data.get("payload", {}).get("volume")
                if isinstance(new_volume, int):
                    tv_state["volume"] = new_volume
                    logging.info(f"🔈 Громкость установлена на {new_volume}")
                await websocket.send(json.dumps({
                    "type": "response",
                    "id": data.get("id"),
                    "payload": {"returnValue": True}
                }))

            else:
                logging.warning(f"⚠️ Неизвестная команда: {uri}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "id": data.get("id"),
                    "payload": {"message": "Unknown command"}
                }))
    except websockets.exceptions.ConnectionClosed:
        logging.info("❌ Клиент отключен")

async def start_server():
    server = await websockets.serve(handle_client, HOST, PORT)
    logging.info(f"🌐 Сервер WebSocket запущен на ws://{HOST}:{PORT}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start_server())
