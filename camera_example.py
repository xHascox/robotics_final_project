# type: ignore

import time
import patch_ftp
import robomaster.config  # noqa
from robomaster import robot, logger, logging  # noqa
import robomaster.conn
import robomaster.camera
import cv2
import argparse

# IP = "127.0.0.1"
IP = ""
if IP:
    robomaster.config.LOCAL_IP_STR = IP
    robomaster.config.ROBOT_IP_STR = IP

def get_image(robot, filename="testimage", resolution="720"):
    robot.camera.start_video_stream(display=False, resolution=f"{resolution}p")
    try:
        frame = robot.camera.read_cv2_image()
        print('Frames have shape', frame.shape)
        cv2.imwrite(filename+".png", frame)
        print(f"image {filename} written")
        #cv2.imshow('image', frame)
        
        #cv2.waitKey(1)
        robot.camera.stop_video_stream()
        return True, frame
    except Exception as e:
        print(f"failed {e}")
        return [False]

def get_images(resolution=720, log_level="WARN", ):
    # max resolution is 720p for video?

    logger.setLevel(log_level)
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")
    time.sleep(1)

    print('Camera version', ep_robot.camera.get_version())
    print('Camera configuration', vars(ep_robot.camera.conf))
    print('Camera address', ep_robot.camera.video_stream_addr)
    print('Camera resolution', f"{resolution}p")
    

    while not get_image(ep_robot, "straight", 720)[0]:
        time.sleep(1)
    print("move gimbal")
    ep_robot.gimbal.moveto(yaw=45, pitch=0, yaw_speed=90, pitch_speed=30).wait_for_completed()
    print("moved gimbal")
    #time.sleep(1)


    while not get_image(ep_robot, "right_gimbal", 720)[0]:
        time.sleep(1)
    print("finished")

    
    #print("closed video")
    #ep_robot.close()
    print("closed robot")


if __name__ == '__main__':
    get_images()
    