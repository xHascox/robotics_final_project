# type: ignore

import time
import patch_ftp
import robomaster.config  # noqa
from robomaster import robot, logger, logging  # noqa

def get_directions_from_path(path):
    directions = []
    current_position = path[0]

    for next_position in path[1:]:
        dx = next_position.x - current_position.x
        dy = next_position.y - current_position.y
        if dx > 0:
            directions.append('x')
        elif dx < 0:
            directions.append('-x')
        elif dy > 0:
            directions.append('y')
        elif dy < 0:
            directions.append('-y')
        current_position = next_position
    
    return directions

def count_consecutive_steps(directions):
    first_step = directions[0]
    count = 0

    for step in directions:
        if step == first_step:
            count += 1
        else:
            break
    return count


def move_along_path(ep_robot, path):
    # Move into the next direction (for as many steps as there are consequtive in the path)

    # one square in the scene is 0.5m
    # we use 1 square = 100px in rectification
    # so we have 1m = 200px
    # and each step in our path is one pixel
    # so one step is 0.005 meters

    directions = get_directions_from_path(path)
    n_steps = count_consecutive_steps(directions)

    # move n_steps * 0.005 meters in direction directions[0]
    if directions[0] == "x":
        ep_robot.chassis.move(x = 0.005 * n_steps, y=0, z=0, xy_speed=1.0, z_speed=90).wait_for_completed()
        ep_robot.chassis.stop()
        print(f"moved {n_steps} in {directions[0]}")
    elif directions[0] == "-x":
        ep_robot.chassis.move(x = -0.005 * n_steps, y=0, z=0, xy_speed=1.0, z_speed=90).wait_for_completed()
        ep_robot.chassis.stop()
        print(f"moved {n_steps} in {directions[0]}")
    elif directions[0] == "y":
        ep_robot.chassis.move(x = 0, y= 0.005 * n_steps, z=0, xy_speed=1.0, z_speed=90).wait_for_completed()
        ep_robot.chassis.stop()
        print(f"moved {n_steps} in {directions[0]}")
    elif directions[0] == "-y":
        ep_robot.chassis.move(x = 0, y= -0.005 * n_steps, z=0, xy_speed=1.0, z_speed=90).wait_for_completed()
        ep_robot.chassis.stop()
        print(f"moved {n_steps} in {directions[0]}")

    return path[n_steps:] # returns the remaining path


    




def main():
    logger.setLevel(logging.ERROR)
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")
    ep_robot.set_robot_mode('chassis_lead')
    print('Drive in circle for 5 second')
    ep_robot.chassis.drive_speed(0.3, 0, 45)
    time.sleep(5)
    print('Move forward 1 meter and turn by 90 degrees')
    time.sleep(1)
    ep_robot.chassis.move(x=1, y=0, z=90, xy_speed=1.0, z_speed=90).wait_for_completed()
    print('Arrived')
    ep_robot.chassis.stop()
    ep_robot.close()


if __name__ == '__main__':
    main()
