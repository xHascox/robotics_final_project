import camera
import pathing

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
    ep_robot.gimbal.moveto(yaw=0, pitch=0, yaw_speed=90, pitch_speed=30).wait_for_completed()


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
    


    # create map TODO

    # calculate path
    target_point, img = pathing.identify_target_from_top_down(frame)
    path = get_path(target_point, image)

    # drive TODO
    # for step in path:
    # check in which direction, use odometry to move 1 px ?!
    # optionally, only do the first step and then take a picture again
    print("finished")

main()