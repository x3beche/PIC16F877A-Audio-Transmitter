import datetime
import random
from modules.models import AudioAnalytics, UartDevice
from modules.graphical_interface import *
import serial, time, threading
import numpy as np
from scipy.io.wavfile import write
import pygame


class sensorHandler(QtCore.QThread):
    sensor_verileri = QtCore.pyqtSignal(float)
    recording_status = QtCore.pyqtSignal(bool)
    analytics = QtCore.pyqtSignal(AudioAnalytics)
    terminal_msg = QtCore.pyqtSignal(str)

    def __init__(self, uartDevice: UartDevice, parent=None):
        super(sensorHandler, self).__init__(parent)
        self.uartDevice = uartDevice
        self.ser = serial.Serial(uartDevice.port, uartDevice.baudrate, timeout=1)
        self.sample_rate = 0
        self.rssi = 0
        self.loss = 0
        self.buffer = []
        self.bufferlen = 1000
        self.i = 0
        pygame.mixer.init(frequency=5650, size=-16, channels=1)
        self.buf = np.zeros((self.bufferlen, 2), dtype=np.int16)
        self.sound = pygame.sndarray.make_sound(self.buf)
        self.buf = pygame.sndarray.samples(self.sound)
        self.sound.play(loops=-1, fade_ms=0)
        self.prev_msg_len = 0
        self.recording_buffer = np.array([])
        self.prev_recording_status = False

        self.recording_blink_thread_status = True
        self.recording_blink_thread = threading.Thread(target=self.recording_blink)
        self.recording_blink_thread.daemon = True
        self.recording_blink_thread.start()

        self.audio_analytics_thread_status = True
        self.audio_analytics_thread = threading.Thread(target=self.audio_analytics)
        self.audio_analytics_thread.daemon = True
        self.audio_analytics_thread.start()

        self.tx_handler_thread_status = True
        self.tx_handler_thread = threading.Thread(target=self.tx_handler)
        self.tx_handler_thread.daemon = True
        self.tx_handler_thread.start()

    def tx_handler(self):
        while self.tx_handler_thread_status:
            if len(self.uartDevice.tx_buffer) > 0:
                self.uartDevice.prev_tx = time.time()
                msg = self.uartDevice.tx_buffer[0] + "\n"
                self.uartDevice.tx_buffer.pop(0)
                self.ser.write(msg.encode("utf-8"))
                self.uartDevice.prev_tx = time.time()
                time.sleep(0.1)

            time.sleep(0.1)

    def save_recording(self):
        self.recording_buffer = (self.recording_buffer / 1024) - 0.512
        rate = 5750
        num = random.randint(0, 10**3)
        scaled = np.int16(self.recording_buffer / 0.50 * 32767)
        write(f"recording{num}.wav", rate, scaled)
        self.recording_buffer = np.array([])
        self.terminal_msg.emit(f"Recording saved to recording{num}.wav")

    def run(self):
        while self.uartDevice.status:
            while self.uartDevice.status:

                try:

                    data0 = self.ser.read()[0]
                    if data0 & 0b10000000:  # 0b01000000 is 64 in decimal
                        self.rssi = -int(data0 - 0b10000000)
                    if int(data0) % 2 == 1:
                        self.loss += 1
                        break
                    low = int(int(data0) / 2)
                    data1 = self.ser.read()[0]
                    if data1 & 0b10000000:  # 0b01000000 is 64 in decimal
                        self.rssi = -int(data1 - 0b10000000)
                    if int(data1) % 2 == 0:
                        self.loss += 1
                        break
                    high = int(int(data1) / 2)
                    data = high * 32 + low

                    if data > 1024:
                        break

                    self.buffer.append(data)
                except:
                    break

                # realtime audio conversion
                if len(self.buffer) == self.bufferlen:
                    array = (np.array(self.buffer) / 1024) - 0.512
                    scaled = np.int16(array / 0.50 * 32767)
                    scaled = np.repeat(scaled.reshape(len(scaled), 1), 2, axis=1)
                    self.buf[: -self.bufferlen] = self.buf[self.bufferlen :]
                    self.buf[-self.bufferlen :] = scaled
                    self.buffer = []

                if self.uartDevice.recording_status:
                    self.recording_buffer = np.append(self.recording_buffer, data)
                else:
                    if self.prev_recording_status == True:
                        self.record_save_thread = threading.Thread(
                            target=self.save_recording
                        )
                        self.record_save_thread.daemon = True
                        self.record_save_thread.start()

                self.prev_recording_status = self.uartDevice.recording_status

                try:
                    self.sensor_verileri.emit(float(data))
                    self.sample_rate += 1
                    self.uartDevice.prev_rx = time.time()
                except:
                    pass

        self.ser.close()
        self.recording_blink_thread_status = False
        self.audio_analytics_thread_status = False
        pygame.mixer.quit()
        self.analytics.emit(AudioAnalytics(rssi=0, speed=0, samplerate=0, loss=0))
        self.recording_status.emit(False)

    def get_formatted_date(self):
        # Get the current date and time
        now = datetime.datetime.now()

        # Format the date and time according to the required format
        formatted_date = now.strftime("%y.%m.%d %H.%M")

        return formatted_date

    def audio_analytics(self):
        self.start_time = time.time()
        while self.audio_analytics_thread_status:
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            if elapsed_time >= 1:
                self.i += 1

                if (self.i % 2) == 0:
                    self.uartDevice.tx_buffer.append(f"RSSI {self.rssi}dB")
                if (int(time.time()) % 60) == 0:
                    self.uartDevice.tx_buffer.append(f"RTC {self.get_formatted_date()}")

                self.analytics.emit(
                    AudioAnalytics(
                        rssi=self.rssi,
                        speed=self.sample_rate * 16,
                        samplerate=self.sample_rate,
                        loss=self.loss,
                    )
                )
                self.start_time = current_time
                self.sample_rate = 0
                self.loss = 0

            self.sound.set_volume(self.uartDevice.volume)

            time.sleep(0.05)

    def recording_blink(self):
        while self.recording_blink_thread_status:
            if self.uartDevice.recording_status:
                self.recording_status.emit(True)
            time.sleep(0.5)
