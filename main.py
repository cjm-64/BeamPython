import logging
from rich import print
from rich.logging import RichHandler
import uvc
import cv2

from typing import NamedTuple
import time

import os

class CameraSpec(NamedTuple):
    name: str
    width: int
    height: int
    fps: int
    bandwidth_factor: float = 2.0

def getCameraInfo():
    listOfCamInfo = []
    for device in uvc.device_list():
        cap = uvc.Capture(device["uid"])
        print(cap.name)
        if int(cap.name[-1]) > 1:
            print("World Cam")
            # Uncomment to include world cam
            # listOfCamInfo.append(CameraSpec(
            #     name=cap.name,
            #     width=cap.available_modes[10][0],
            #     height=cap.available_modes[10][1],
            #     fps=cap.available_modes[10][2],
            #     bandwidth_factor=1.6,
            # )
            # )
        else:
            capmode = 3
            listOfCamInfo.append(CameraSpec(
                name=cap.name,
                width=cap.available_modes[capmode][0],
                height=cap.available_modes[capmode][1],
                fps=cap.available_modes[capmode][2],
                bandwidth_factor=1.6,
            )
            )
    # print(listOfCamInfo)
    return listOfCamInfo

def initCameraFromList(devices, camera: CameraSpec):
    logging.debug(f"Searching {camera}...")
    for device in devices:
        if device["name"] == camera.name:
            capture = uvc.Capture(device["uid"])
            capture.bandwidth_factor = camera.bandwidth_factor
            for mode in capture.available_modes:
                if mode[:3] == camera[1:4]:  # compare width, height, fps
                    capture.frame_mode = mode
                    setCamAttrs(capture)
                    return capture
            else:
                logging.warning(
                    f"None of the available modes matched: {capture.available_modes}"
                )
            capture.close()
            print("Cap Closed")

def setCamAttrs(cam):
    print(cam.name)
    controls_dict = dict([(c.display_name, c) for c in cam.controls])
    controls_dict['Gamma'].value = 200
    controls_dict['Brightness'].value = 0
    controls_dict['Auto Exposure Mode'].value = 1
    return cam
def openStream(streamTime, camDict):
    # camDict = updateCamSettings(camDict)
    initTime = time.perf_counter()
    currTime = 0
    while currTime < streamTime:
        print(currTime)
        for spec, cam in camDict.items():
            if int(spec.name[-1]) < 2:
                print(spec.name)
                try:
                    frame = cam.get_frame(timeout=0.1)
                except TimeoutError:
                    print("TimeoutError")
                    pass
                except uvc.InitError as err:
                    logging.debug(f"Failed to init {spec}: {err}")
                    break
                except uvc.StreamError as err:
                    logging.debug(f"Failed to get a frame for {spec}: {err}")
                else:
                    cv2.imshow(spec.name, cv2.flip(frame.bgr, 0))
                    cv2.waitKey(1)
        currTime = time.perf_counter() - initTime

    for cam in camDict.values():
        cam.close()

def main():
    camInfo = getCameraInfo()
    print(camInfo)
    devices = uvc.device_list()
    camDict = {spec: initCameraFromList(devices, spec) for spec in camInfo}
    print(camDict.items())

    print(len(camDict))
    print("\n\n")
    print(type(camDict))
    print(camDict.keys())
    print(camDict.values())
    print("\n\n")

    openStream(5, camDict)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
