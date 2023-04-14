import logging
from rich import print
from rich.logging import RichHandler
import uvc
import cv2

from typing import NamedTuple

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
            listOfCamInfo.append(CameraSpec(
                name=cap.name,
                width=cap.available_modes[10][0],
                height=cap.available_modes[10][1],
                fps=cap.available_modes[10][2],
                bandwidth_factor=1.6,
            )
            )
        else:
            listOfCamInfo.append(CameraSpec(
                name=cap.name,
                width=cap.available_modes[5][0],
                height=cap.available_modes[5][1],
                fps=cap.available_modes[5][2],
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
                    return capture
            else:
                logging.warning(
                    f"None of the available modes matched: {capture.available_modes}"
                )
            capture.close()

def main():
    camInfo = getCameraInfo()
    print(camInfo)
    devices = uvc.device_list()
    cameras = {spec: initCameraFromList(devices, spec) for spec in camInfo}
    print(cameras.items())

    for spec, cam in cameras.items():
        print(spec.name)
        if int(spec.name[-1]) < 2:
            controls_dict = dict([(c.display_name, c) for c in cam.controls])
            controls_dict['Auto Exposure Mode'].value = 1
            controls_dict['Gamma'].value = 200
        else:
            controls_dict = dict([(c.display_name, c) for c in cam.controls])
            controls_dict['Auto Exposure Mode'].value = 1
    print(len(cameras))
    print("\n\n")
    print(type(cameras))
    print(cameras.keys())
    print("\n\n")

    for x in range(200):
        for spec, cam in cameras.items():
            if int(spec.name[-1]) < 2:
                print(spec.name)
                try:
                    frame = cam.get_frame_robust()
                except TimeoutError:
                    print("TimeoutError")
                    pass
                except uvc.InitError as err:
                    logging.debug(f"Failed to init {spec}: {err}")
                    break
                except uvc.StreamError as err:
                    logging.debug(f"Failed to get a frame for {spec}: {err}")
                else:
                    data = frame.bgr if hasattr(frame, "bgr") else frame.gray
                    if frame.data_fully_received:
                        cv2.imshow(spec.name, data)
                        cv2.waitKey(1)
    for cam in cameras.values():
        cam.close()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
