# https://github.com/brean/python-pathfinding
# pip install pathfinding
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

import cv2
import numpy as np
import matplotlib.pyplot as plt

# Define range for red color
lower_red = np.array([0, 0, 100]) # this may vary
upper_red = np.array([50, 50, 255]) # this may vary
lower_blue = np.array([100, 0, 0]) # this may vary
upper_blue = np.array([255, 50, 50]) # this may vary

def get_red_px(image):
    # Create a mask to filter only red pixels
    mask = cv2.inRange(image, lower_red, upper_red)

    # Bitwise-AND mask and with your image 
    red_pixels = cv2.bitwise_and(image, image, mask=mask)
    return red_pixels

def identify_target_from_top_down(image):
    red_pixels = get_red_px(image)

    # All the red pixels will be in the red_pixels image 
    # Non-red pixels will be black.

    # Source: https://www.tutorialspoint.com/how-to-detect-a-rectangle-and-square-in-an-image-using-opencv-python
    image = image # the top down view
    img = red_pixels # only red pixels
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret,thresh = cv2.threshold(gray,50,255,0)
    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    print("Number of contours detected:", len(contours), hierarchy)

    largest_area = 0
    target_point = []
    for cnt in contours:
        x1,y1 = cnt[0][0]
        approx = cv2.approxPolyDP(cnt, 0.05*cv2.arcLength(cnt, True), True) # 0.05 is the tolerance, increase to make more tolerant
        if len(approx) == 4:
            print("square")
            x, y, w, h = cv2.boundingRect(cnt)
            current_area = w * h
            if current_area > largest_area:  # only keep the largest square to not select the gun
                largest_area = current_area
            target_point = (x+w//2, y+h//2)

        
    img = cv2.drawContours(image, [cnt], -1, (0,255,255), 3)
    cv2.putText(img, 'Target', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    return target_point, img


def get_path(target_point, image):
    red_pixels = get_red_px(image)
    red_pixels[red_pixels <= lower_red[2]] = 1
    matrix=red_pixels[:,:,2]

    # Create a mask to filter only blue pixels
    mask = cv2.inRange(image, lower_blue, upper_blue)
    # Bitwise-AND mask and with your image 
    blue_pixels = cv2.bitwise_and(image, image, mask=mask)
    blue_pixels_1_d = blue_pixels[:,:,0]

    matrix[blue_pixels_1_d > 0] = 0 # make blue pixels = obstacle
    
    grid = Grid(matrix=matrix)
    # start = grid.node(red_pixels.shape[1]//2-1,red_pixels.shape[0]-1) # BOTTOM MIDDLE
    start = grid.node(red_pixels.shape[1]//2,red_pixels.shape[0]//2) # CENTER MIDDLE
    end = grid.node(*target_point)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start, end, grid)

    for step in path: # draw the path
        image[step.y][step.x] = [0,200,0]

    return path






