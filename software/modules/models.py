from typing import List
from pydantic import BaseModel


class UartDevice(BaseModel):
    port: str
    baudrate: int
    status: bool
    recording_status: bool
    prev_rx: float
    prev_tx: float
    volume: float
    tx_buffer: List[str]


class AudioAnalytics(BaseModel):
    rssi: int
    speed: int
    samplerate: int
    loss: int
