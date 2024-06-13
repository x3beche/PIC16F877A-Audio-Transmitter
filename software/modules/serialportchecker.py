from serial.tools.list_ports import comports


def portChecker():
    PORTS = []
    for port in comports():
        # Check if the description contains specific keywords for ESP32 Pico devices
        if "USB" in port.description:
            PORTS.append(port.device)
    return PORTS
