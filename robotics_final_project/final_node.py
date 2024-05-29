import camera

import time
import patch_ftp
import robomaster.config  # noqa
from robomaster import robot, logger, logging  # noqa
import robomaster.conn
import robomaster.camera
import cv2




def main():
    print("ok v2")


    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")
    time.sleep(1)

    # get front view
    success, frame = camera.get_image(ep_robot)
    while not success:
        time.sleep(1)
        success, frame = camera.get_image(ep_robot)
    #cv2.imshow(frame)
    

    # get right view
    ep_robot.gimbal.moveto(yaw=45, pitch=0, yaw_speed=90, pitch_speed=30).wait_for_completed()
    print("moved gimbal")
    success2, frame2 = camera.get_image(ep_robot)
    while not success:
        time.sleep(1)
        success2, frame2 = camera.get_image(ep_robot)
    


    # create map

    # calculate path

    # drive

    print("finished")

main()