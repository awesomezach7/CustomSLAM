"""import time
from pathlib import Path
from xmlrpc import server

import numpy as np
import viser
import serial
import viser.transforms as tf

import math

ports = serial.tools.list_ports.comports()
SerialPort = serial.Serial(port=ports[0].device"""'/dev/ttyACM0'""", baudrate = 115200)
SerialPort.flushInput()
SerialPort.flushOutput()
time.sleep(1)

def main():
    server = viser.ViserServer()
    pointCloud = server.scene.add_point_cloud(
        "/Points",
        points = np.ndarray((0, 3)),
        colors = (82, 46, 242),
        point_size = 0.5
    )
    allPoints = np.ndarray((0, 3))
    print("Open your browser to http://localhost:8080")
    print("Press Ctrl+C to exit")
    while True:
        Input = SerialPort.readline().decode('utf-8').rstrip()
        Parsed = Input.split(",")
        if Parsed[0] == "NewPts":
            for i in range(1, int((len(Parsed)-1)/3)): # Start at 1 because 0th index is "NewPts"
                allPoints.append([Parsed[3*i-2], Parsed[3*i-1], Parsed[3*i]])
            pointCloud.points = allPoints

if __name__=="__main__":
    main()"""