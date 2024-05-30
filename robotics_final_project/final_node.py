import camera
import pathing
import move

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
    print("ok v2.5")
    ep_robot.initialize(conn_type="sta")
    print("ok v3")
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
    print("ok4")


    # create map TODO

    # calculate path
    # TODO rm hardcoded img
    top_down_map = cv2.imread("/home/robotics23/dev_ws/robotics_final_project/img/font_top.png")
    target_point, img = pathing.identify_target_from_top_down(top_down_map)
    path = pathing.get_path(target_point, top_down_map)

    # drive TODO
    # for step in path:
    # check in which direction, use odometry to move 1 px ?!
    # optionally, only do the first step and then take a picture again
    print("start to move")
    remaining_path = path
    while len(remaining_path)>0:
        remaining_path = move.move_along_path(ep_robot, path) # moves into one direction and returns remaining path
    print("finished moving")

main()