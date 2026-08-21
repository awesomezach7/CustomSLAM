import time
from pathlib import Path

import numpy as np
import viser
import serial
import serial.tools.list_ports
import viser.transforms as tf
import trimesh
from collections import deque

import math

ports = serial.tools.list_ports.comports()
for port in ports:
    if port.device == "/dev/ttyACM0" or port.device == "/dev/ttyACM1" or port.device == "/dev/ttyACM2":
        SerialPort = serial.Serial(port=port.device, baudrate = 115200)
SerialPort.flushInput()
SerialPort.flushOutput()
time.sleep(1)

def step(inputQueue, breadboard, pointCloud, newCloud):
    cloudUpdated = False
    while cloudUpdated == False:
        identifier = inputQueue.popleft()
        if identifier == 0:
            pointCloudPoints = inputQueue.popleft()
            print("Main point cloud updated")
            pointCloud.points = np.append(pointCloud.points, pointCloudPoints)
            cloudUpdated = True
        elif identifier == 1:
            newCloudPoints = inputQueue.popleft()
            print("Iteration begun")
            newCloud.points = newCloudPoints
            cloudUpdated = True
        elif identifier == 2:
            poseData = inputQueue.popleft()
            print("pose data: ")
            print(poseData)
            breadboard.wxyz = poseData[0]
            breadboard.position = poseData[1]
        else:
            inputQueue.popleft()
            print("identifier failure")

def main():
    server = viser.ViserServer()
    mesh = trimesh.load_mesh(str(Path(__file__).parent / "breadboard.obj"))
    assert isinstance(mesh, trimesh.Trimesh)
    mesh.apply_scale(0.01)
    inputQueue = deque()
    breadboard = server.scene.add_mesh_simple(
        "/Breadboard",
        vertices = mesh.vertices,
        faces = mesh.faces,
        wxyz = tf.SO3.from_quaternion_xyzw(xyzw = np.array([0.0, 0.0, 0.0, 1.0])).wxyz,
        position = (0, 0, 0)
    )
    pointCloud = server.scene.add_point_cloud(
        "/Points",
        points = np.ndarray((0, 3)),
        colors = (82, 46, 242),
        point_size = 0.01
    )
    newCloud = server.scene.add_point_cloud(
        "/NewCloud",
        points = np.ndarray((0,3)),
        colors = (255, 96, 19),
        point_size = 0.01
    )
    print("Open your browser to http://localhost:8080")
    print("Press Ctrl+C to exit")
    button = server.gui.add_button(label="Step", color="indigo")
    button.on_click(lambda _:(step(inputQueue, breadboard, pointCloud, newCloud)))
    while True:
        try:
            Input = SerialPort.readline().decode('utf-8').rstrip()
        except serial.serialutil.SerialException:
            while True:
                time.sleep(1)
        Parsed = Input.split(",")
        if Parsed[0] == "NewPts":
            pointCloudPoints = np.ndarray((0,3))
            for i in range(1, int((len(Parsed)-1)/3)): # Start at 1 because 0th index is "NewPts"
                try:
                    pointCloudPoints = np.append(pointCloudPoints, [float(Parsed[3*i-2])*scaleUp, float(Parsed[3*i-1])*scaleUp, float(Parsed[3*i])*scaleUp])
                except ValueError, IndexError:
                    print("bad input")
            inputQueue.append(0)
            inputQueue.append(pointCloudPoints)
        if Parsed[0] == "OldPts":
            newCloudPoints = np.ndarray((0,3))
            for i in range(1, int((len(Parsed)-1)/3)): # Start at 1 because 0th index is "NewPts"
                try:
                    newCloudPoints = np.append(newCloudPoints, [float(Parsed[3*i-2]), float(Parsed[3*i-1]), float(Parsed[3*i])])
                except ValueError, IndexError:
                    print("bad input")
            inputQueue.append(1)
            inputQueue.append(newCloudPoints)
        elif Parsed[0] == "Orient":
            try:
                breadboardWxyz = tf.SO3.from_quaternion_xyzw(xyzw = np.array([float(Parsed[2]), float(Parsed[3]), float(Parsed[4]), float(Parsed[1])])).wxyz
                breadboardPosition = (float(Parsed[6]), float(Parsed[7]), float(Parsed[8]))
                inputQueue.append(2)
                inputQueue.append([breadboardWxyz, breadboardPosition])
            except ValueError, IndexError:
                print("bad input")

if __name__=="__main__":
    main()