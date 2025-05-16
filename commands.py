from enum import Enum


class CommandEnum(Enum):
    POWER_STATE = ("Состояние питания", "ssap://com.webos.service.tvpower/power/getPowerState", {})
    POWER_OFF = ("Выключить телевизор", "ssap://system/turnOff", {})
    VOLUME_STATUS = ("Получить статус звука", "ssap://audio/getStatus", {})
    VOLUME_SET = ("Установить громкость", "ssap://audio/setVolume", {"volume": None})
    VOLUME_UP = ("Увеличить громкость", "ssap://audio/volumeUp", {})
    VOLUME_DOWN = ("Уменьшить громкость", "ssap://audio/volumeDown", {})
    MUTE_TOGGLE = ("Включить/выключить звук", "ssap://audio/setMute", {"mute": None})
    PLAY = ("Воспроизведение", "ssap://media.controls/play", {})
    PAUSE = ("Пауза", "ssap://media.controls/pause", {})
    STOP = ("Остановить", "ssap://media.controls/stop", {})
    BACK = ("Перемотка назад", "ssap://media.controls/rewind", {})
    SECOND = ("Перемотка вперёд", "ssap://media.controls/fastForward", {})
    SET_CHANNEL = ("Установить канал", "ssap://tv/openChannel", {"channelId": None})

    def __init__(self, name, uri, payload_template):
        self.command_name = name
        self.uri = uri
        self.payload_template = payload_template

    def with_payload(self, **kwargs):
        payload = self.payload_template.copy()
        for k, v in kwargs.items():
            if k in payload or payload == {}:
                payload[k] = v
        return self.command_name, self.uri, payload
