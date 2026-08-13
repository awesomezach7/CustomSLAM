import time
from pathlib import Path
from xmlrpc import server

import numpy as np
import viser
import serial
import serial.tools.list_ports
import viser.transforms as tf

import math

ports = serial.tools.list_ports.comports()
for port in ports:
    if port.device == "/dev/ttyACM0":
        SerialPort = serial.Serial(port=port.device, baudrate = 115200)
    elif port.device == "/dev/ttyACM1":
        SerialPort = serial.Serial(port=port.device, baudrate = 115200)
SerialPort.flushInput()
SerialPort.flushOutput()
time.sleep(1)
scaleUp = 10

def main():
    server = viser.ViserServer()
    pointCloud = server.scene.add_point_cloud(
        "/Points",
        points = np.ndarray((0, 3)),
        colors = (82, 46, 242),
        point_size = 0.1
    )
    allPoints = np.ndarray((0, 3))
    print("Open your browser to http://localhost:8080")
    print("Press Ctrl+C to exit")
    while True:
        Input = SerialPort.readline().decode('utf-8').rstrip()
        Parsed = Input.split(",")
        if Parsed[0] == "NewPts":
            for i in range(1, int((len(Parsed)-1)/3)): # Start at 1 because 0th index is "NewPts"
                allPoints = np.append(allPoints, [float(Parsed[3*i-2])*scaleUp, float(Parsed[3*i-1])*scaleUp, float(Parsed[3*i])*scaleUp])
            pointCloud.points = allPoints

if __name__=="__main__":
    main()