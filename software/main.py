from collections import deque
from modules.models import AudioAnalytics, UartDevice
from modules.serialportchecker import portChecker
from modules.graphical_interface import *
from modules.sensor import sensorHandler
import sys, time, threading


class GUI_Interface(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("modules/favicon.ico"))
        self.setWindowTitle("Radiochatter Control")

        self.prev_msg_len = 0
        self.refreshRate = 30
        self.dataWindow = 12000
        self._neg = 0
        self._pos = 1024

        self.audioDataDeque = deque(
            [512 for i in range(0, self.dataWindow)], maxlen=self.dataWindow
        )
        self.device = UartDevice(
            port="",
            baudrate=0,
            status=False,
            recording_status=False,
            prev_rx=0,
            prev_tx=0,
            volume=0,
            tx_buffer=[],
        )
        self.dataCounter = 0

        self.initUI()

    def terminal(self, status, msg):

        if status == "INFO":
            self.ui.console.insertHtml(
                f'<font color={self.chat_user_color}><strong>INFO :: </strong></font><font color="white">{msg}</font><br>'
            )
        elif status == "WARNING":
            self.ui.console.insertHtml(
                f'<font color={self.warning_color  }><strong>WARNING :: </strong></font><font color="white">{msg}</font><br>'
            )
        elif status == "SUCCESS":
            self.ui.console.insertHtml(
                f'<font color={self.success_color  }><strong>SUCCESS :: </strong></font><font color="white">{msg}</font><br>'
            )
        self.ui.console.verticalScrollBar().setValue(
            self.ui.console.verticalScrollBar().maximum()
        )

    def recording_status(self, toggle: bool = None, status: bool = None):

        if status == False:
            self.ui.Rec_c.setEnabled(True)
        elif toggle:
            if self.ui.Rec_c.isEnabled():
                self.ui.Rec_c.setEnabled(False)
            else:
                self.ui.Rec_c.setEnabled(True)

    def initUI(self):

        self.info_color = "#FFD801"
        self.warning_color = "#ff0f0f"
        self.success_color = "#FF4CAF50"
        self.chat_time_color = "#D3D3D3"
        self.chat_user_color = "#F6F6F6"
        self.chat_root_color = "#5B9EFE"
        self.setFixedSize(self.size())

        self.ui.TX_c.setProperty("color", "txrx")
        self.ui.RX_c.setProperty("color", "txrx")
        self.ui.Rec_c.setProperty("color", "txrx")
        self.recording_status(status=False)

        self.ui.audio_graph.setRange(yRange=[self._neg, self._pos])
        self.ui.audio_graph.setBackground("black")
        self.ui.audio_graph.hideAxis("bottom")
        self.ui.audio_graph.hideAxis("left")

        self.ui.console.setReadOnly(True)
        self.terminal("SUCCESS", "The interface is initialized.")

        self.portLister()
        self.baudrateLister()
        self.initButtons()

        self.ui.volume_slider.setValue(0)
        self.ui.time_range_slider.setValue(3)
        self.ui.regtesh_reate_sider.setValue(30)

        self.rxtx_control = True
        self.rxtx_control_thread = threading.Thread(target=self.rxtx_control_func)
        self.rxtx_control_thread.daemon = True
        self.rxtx_control_thread.start()

    def rxtx_control_func(self):
        while self.rxtx_control:
            current_time = time.time()

            if self.device.prev_rx + 0.1 > current_time:
                self.ui.RX_c.setChecked(True)
            else:
                self.ui.RX_c.setChecked(False)
            if self.device.prev_tx + 0.1 > current_time:
                self.ui.TX_c.setChecked(True)
            else:
                self.ui.TX_c.setChecked(False)

            time.sleep(0.1)

    def audioDataHandle(self, value: int):
        self.dataCounter += 1
        self.audioDataDeque.append(value)
        if self.dataCounter == self.refreshRate:
            self.dataCounter = 0
            self.ui.audio_graph.clear()
            self.ui.audio_graph.plot(
                [i for i in range(0, len(self.audioDataDeque))],
                self.audioDataDeque,
                pen="lightGray",
            )

    def volumeUpdate(self):
        self.ui.volume_slider_lcd.display(self.ui.volume_slider.value())

    def startRecording(self):
        self.device.recording_status = True
        self.ui.record_b.setText("Recording...")
        self.ui.record_b.setEnabled(False)
        self.ui.save_b.setEnabled(True)

    def stopRecording(self):
        self.recording_status(status=False)
        if self.device.recording_status:
            self.device.recording_status = False
            self.ui.record_b.setText("Record")
            self.ui.record_b.setEnabled(True)
            self.ui.save_b.setEnabled(False)

    def refreshPorts(self):
        self.portLister()

    def volumeChangeHandler(self):
        self.device.volume = self.ui.volume_slider.value() / 100

    def initButtons(self):
        self.ui.disconnect_b.setEnabled(False)
        self.ui.record_b.setEnabled(False)
        self.ui.save_b.setEnabled(False)

        self.ui.connect_b.clicked.connect(self.startSensorCommunication)
        self.ui.disconnect_b.clicked.connect(self.stopSensorCommunication)
        self.ui.volume_slider.valueChanged.connect(self.volumeUpdate)
        self.ui.record_b.clicked.connect(self.startRecording)
        self.ui.save_b.clicked.connect(self.stopRecording)
        self.ui.refresh_b.clicked.connect(self.refreshPorts)
        self.ui.volume_slider.valueChanged.connect(self.volumeChangeHandler)
        self.ui.sendmessage_b.clicked.connect(self.sendMessage)
        self.ui.message_text.returnPressed.connect(self.sendMessage)

    def sendMessage(self):
        msg = self.ui.message_text.text()
        self.ui.message_text.setText("")
        self.device.tx_buffer.append("MSG " + " " * (self.prev_msg_len + 1))
        self.device.tx_buffer.append(f"MSG {msg}")
        self.prev_msg_len = len(msg)

    def sampleRateHandler(self, value: int):
        print(value)

    def analyticsHandler(self, analytics: AudioAnalytics):
        self.ui.samplerate_text.setText(f"Sample Rate = {analytics.samplerate} hz")
        self.ui.speed_text.setText(f"Speed = {analytics.speed} bps")
        self.ui.rssi_text.setText(f"RSSI = {analytics.rssi} dB")
        self.ui.loss_text.setText(f"Loss = {analytics.loss} byte/s")

    def startSensorCommunication(self):

        self.ui.open_b.setEnabled(False)

        self.device.port = self.ui.port_selection.currentText()
        self.device.baudrate = int(self.ui.baudrate_selection.currentText())
        self.device.status = True
        self.ui.connect_b.setEnabled(False)
        self.ui.disconnect_b.setEnabled(True)

        self.ui.record_b.setEnabled(True)
        self.ui.save_b.setEnabled(False)

        self.sensorThread = sensorHandler(self.device)
        self.sensorThread.sensor_verileri.connect(self.audioDataHandle)
        self.sensorThread.recording_status.connect(self.recordingIndicatorHandler)
        self.sensorThread.analytics.connect(self.analyticsHandler)
        self.sensorThread.terminal_msg.connect(self.terminalMsgHandler)
        self.sensorThread.start()

        self.terminal("SUCCESS", f"Connection on {self.device.port} started.")

    def terminalMsgHandler(self, msg: str):
        self.terminal("SUCCESS", msg)

    def stopSensorCommunication(self):
        self.ui.open_b.setEnabled(True)
        self.ui.connect_b.setEnabled(True)
        self.ui.disconnect_b.setEnabled(False)
        self.device.status = False
        self.ui.record_b.setEnabled(False)
        self.ui.save_b.setEnabled(False)
        self.terminal("SUCCESS", f"Connection on {self.device.port} terminated.")

    def portLister(self):
        self.ui.port_selection.clear()
        for i, port in enumerate(portChecker()):
            self.ui.port_selection.addItem("")
            self.ui.port_selection.setItemText(i, port)

    def baudrateLister(self):
        self.ui.baudrate_selection.clear()
        baudrates = [
            9600,
            14400,
            19200,
            33600,
            38400,
            56000,
            57600,
            76800,
            115200,
            125000,
        ]
        for i, baudrate in enumerate(baudrates):
            self.ui.baudrate_selection.addItem("")
            self.ui.baudrate_selection.setItemText(i, str(baudrate))

        default_baudrate_index = baudrates.index(115200)
        self.ui.baudrate_selection.setCurrentIndex(default_baudrate_index)

    def recordingIndicatorHandler(self, value: bool):
        if value:
            self.recording_status(toggle=True)
        else:
            self.recording_status(status=False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GUI_Interface()
    ui.show()
    sys.exit(app.exec())
