import json
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from commands import CommandEnum
from websocket import tv_client

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

app = FastAPI()


async def execute_command(command_enum: CommandEnum, **payload_kwargs):
    try:
        command_name, uri, payload = command_enum.with_payload(**payload_kwargs)
        response_raw = await tv_client.send_command(command_name, uri, payload)
        return json.loads(response_raw)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/power")
async def get_power():
    result = await execute_command(CommandEnum.POWER_STATE)
    return {"value": result["payload"].get("returnValue", False)}


@app.get("/power/off")
async def power_off():
    await execute_command(CommandEnum.POWER_OFF)
    return {"power": False}


@app.get("/volume")
async def get_volume():
    result = await execute_command(CommandEnum.VOLUME_STATUS)
    return {"value": result["payload"].get("volume", 0)}


@app.get("/volume/up")
async def volume_up():
    await execute_command(CommandEnum.VOLUME_UP)
    result = await execute_command(CommandEnum.VOLUME_STATUS)
    return {"value": result["payload"].get("volume", 0)}


@app.get("/volume/down")
async def volume_down():
    await execute_command(CommandEnum.VOLUME_DOWN)
    result = await execute_command(CommandEnum.VOLUME_STATUS)
    return {"value": result["payload"].get("volume", 0)}


@app.get("/volume/set/{value}")
async def set_volume(value: int):
    await execute_command(CommandEnum.VOLUME_SET, volume=value)
    return {"volume": value}


@app.get("/mute/toggle")
async def mute_toggle():
    current = await execute_command(CommandEnum.VOLUME_STATUS)
    is_muted = current["payload"].get("mute", False)
    await execute_command(CommandEnum.MUTE_TOGGLE, mute=not is_muted)
    return {"value": not is_muted}


if __name__ == "__main__":
    # Запуск FastAPI приложения через uvicorn в асинхронном режиме
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
