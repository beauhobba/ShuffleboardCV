import numpy as np 
import cv2
import imutils
import math
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt
import requests 


def find_score_range(locations, score_ranges, height, colour):
    score = 0
    saved_score = []
    # fig, ax = plt.subplots()
    for location in locations:
        score = 0
        point = Point(location[0], location[1])
        region = 1
        print(score_ranges)
        for range in score_ranges:
            
            polygon = Polygon([(range[0], range[1]), (range[2], range[3]), (range[4], range[5]), (range[6], range[7]), (range[0], range[1]) ])
            # ax.plot(*polygon.exterior.xy)
            # ax.set_ylim(1200, -1200)
            # ax.grid(True)
            
            if(polygon.contains(point)):
                score += region 
                break
            else:
                region += 1
        saved_score.append([score, location, colour])
    print("saved score :"+str(saved_score))
    # plt.show()
    return saved_score 


def find_actual_score(red_scores, blue_scores, fin_line):
    red_score = 0
    blue_score = 0
    
    scores = red_scores+blue_scores
    p2 = np.asarray([fin_line[2], fin_line[3]])
    p1 = np.asarray([fin_line[0], fin_line[1]])
    for i, score in enumerate(scores):
        p3 = np.asarray(score[1])
        print(p1)
        print(p2)
        print(p3)
        d = np.abs(np.cross(p2-p1, p1-p3))/np.linalg.norm(p2-p1)
        scores[i].append(d)
    
    # sort by width value
    new_scores = sorted(scores, key=lambda var: var[3])
    leading_val = new_scores[0][2]
    print(new_scores)
    print(leading_val)
    for score in new_scores:
        if(score[2] == leading_val):
            if(leading_val == 'r'):
                red_score += score[0]
            else:
                blue_score += score[0]
        else:
            break
            
                
    return red_score, blue_score
        
    
    

def mask_blue_puck(hsv_img, image):
    centroid_locations = [] 
    
    # Define the blue mask
    lower_blue = np.array([60,150,50])
    upper_blue = np.array([160,230,200])
    
    # Mask blue from the image 
    mask = cv2.inRange(hsv_img, lower_blue, upper_blue)
    
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20,20))
    # Smooth the image out 
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    res_img = cv2.bitwise_and(hsv_img,hsv_img, mask= mask)
    
    # Apply to the colour image to allow gray 
    new_img = cv2.bitwise_and(image,image, mask= mask)
     
    gray = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)

    
    cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
    	# compute the center of the contour
        M = cv2.moments(c)
        # Shift to the left
        left_point = tuple(c[c[:, :, 0].argmin()][0])
        centroid_locations.append(left_point)
        cv2.circle(image, (left_point), 2, (0, 255, 0), 2)
        
    cv2.imshow("es", image)
        
    
    return mask, res_img, centroid_locations 


def mask_red_puck(hsv_img, image):
    centroid_locations = [] 
    # Define the red mask
    lower = np.array([150,80,50])
    upper = np.array([360,255,255])
    
    # Mask red from the image 
    mask = cv2.inRange(hsv_img, lower, upper)
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20,20))
    # Smooth the image out 
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    res_img = cv2.bitwise_and(hsv_img,hsv_img, mask= mask)
    
    # Apply to the colour image to allow gray 
    new_img = cv2.bitwise_and(image,image, mask= mask)
     
    gray = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)
    
    cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
    	# compute the center of the contour
        M = cv2.moments(c)
        left_point = tuple(c[c[:, :, 0].argmin()][0])
        centroid_locations.append(left_point)
        cv2.circle(image, (left_point), 2, (0, 255, 0), 2)
        
    cv2.imshow("ds", image)
    
    
    return mask, res_img, centroid_locations 


def mask_table(hsv_img, rgb_img):
    # Define the table mask
    lower = np.array([0,0,0])
    upper = np.array([80,210,210])
    
    new_m = np.zeros(hsv_img.shape[:2], np.uint8)
    
    # Mask the table from the region
    mask_ = cv2.inRange(hsv_img, lower, upper)
    kernel=cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))

    # Smooth the image out 
    mask_ = cv2.morphologyEx(mask_, cv2.MORPH_CLOSE, kernel)
    mask_ = cv2.morphologyEx(mask_, cv2.MORPH_CLOSE, kernel)
    mask_ = cv2.morphologyEx(mask_, cv2.MORPH_CLOSE, kernel)
    mask_ = cv2.morphologyEx(mask_, cv2.MORPH_CLOSE, kernel)
    mask_ = cv2.dilate(mask_, kernel)
    
    # Apply the mask and get rid of the junk 
    res = cv2.bitwise_and(rgb_img,rgb_img,mask = mask_)
    # Revert back to a colour image, as it contains more details for blob detection 
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    
    # perform blob detection and then find the largest blob via area 
    cnts,_ =  cv2.findContours(~thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:1]
    new_mm = new_m.copy()
    cv2.fillPoly(new_mm, cnts, 255)
    
    # Apply to the main image 
    mask_c = cv2.merge([new_mm,new_mm,new_mm])
    masked_colour  = cv2.bitwise_and(rgb_img, mask_c)
    hsv_img_2 =  cv2.cvtColor(masked_colour, cv2.COLOR_BGR2HSV)

    
    return new_mm, hsv_img_2, masked_colour  


def find_region_lines(image):
    height, width, _ = image.shape 
    
    new_m = np.zeros(image.shape[:2], np.uint8)
    new_mm = new_m.copy() 
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,30,300,apertureSize =3)
    kernel=cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    lines = cv2.HoughLines(edges,1,np.pi/180,100, np.array([]), 0, 0)
    a,b,c = lines.shape
    
    stored_lines = [] 
    first_line = True  
    count = 0 
    insert = False 
 
    for i in range(a):
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        a = np.cos(theta)
        b = np.sin(theta)
        # Check if the line is vertical 
        if(math.degrees(theta) > 20):
            continue
        else:
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            insert = True 
            
            # Do not add duplicate lines 
            if(first_line == True):
                stored_lines.append([x1, y1, x2, y2])
                print(x1)
                if(x1 < 0):
                    cv2.line(image,(x1,y1),(x2,y2),(255, 0, 0),5)
                else:
                    cv2.line(image,(x1,y1),(x2,y2),(255, 255, 255),3)
                count += 1
                first_line = False
            else:
                for values in stored_lines:
                    if((x1 >values[0]-50) and (x1 <values[0]+50)):
                        insert = False
                        break 
                if(insert == True):
                    stored_lines.append([x1, y1, x2, y2])
                    if(x1 < 0):
                        cv2.line(image,(x1,y1),(x2,y2),(255, 0, 0),5)
                    else:
                        cv2.line(image,(x1,y1),(x2,y2),(255, 255, 255),3)
                    count += 1
                 
                 
    cv2.imshow('lines',image)
            # now make the regions 
    new_stored_lines = sorted(stored_lines)
    
    print(new_stored_lines)
    
    region_5 = [new_stored_lines[0][0],  new_stored_lines[0][1], new_stored_lines[0][2], new_stored_lines[0][3], new_stored_lines[1][2], new_stored_lines[1][3], new_stored_lines[1][0], new_stored_lines[1][1]]
    region_4 = [new_stored_lines[1][0],  new_stored_lines[1][1], new_stored_lines[1][2], new_stored_lines[1][3], new_stored_lines[2][2], new_stored_lines[2][3], new_stored_lines[2][0], new_stored_lines[2][1]] 
    region_3 = [new_stored_lines[2][0],  new_stored_lines[2][1], new_stored_lines[2][2], new_stored_lines[2][3], new_stored_lines[3][2], new_stored_lines[3][3], new_stored_lines[3][0], new_stored_lines[3][1]]            
    region_2 = [new_stored_lines[3][0],  new_stored_lines[3][1], new_stored_lines[3][2], new_stored_lines[3][3], new_stored_lines[4][2], new_stored_lines[4][3], new_stored_lines[4][0], new_stored_lines[4][1]] 
    region_1 = [new_stored_lines[4][0],  new_stored_lines[4][1], new_stored_lines[4][2], new_stored_lines[4][3], width, 0, width, height]    
     
    return region_5, region_4, region_3, region_2, region_1, new_stored_lines
            
