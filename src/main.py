# This code was written by Beau Hobba and Julia Tan on the 7/2/2022 (Julia on frontend, Beau on embedded/backend)
# Purpose - show simple computer vision of a shuffle board match

from camera import * 
from cv_util import * 
import requests 
import imutils

def get_json_payload(score, title):
    json_payload = []
    json_payload = {"player": title, "score": score}
    return json_payload



def main():
    Cam = Camera(); 
    # frame, hsv_img = Cam.get_picture_from_file("./sample_data/example1.png") 
    frame, hsv_img = Cam.get_picture()
    table_mask, table_img, colour_img  = mask_table(hsv_img, frame)
    
    region_1 = None 
    while(region_1 == None):
        try:
            region_5, region_4, region_3, region_2, region_1, lines = find_region_lines(colour_img.copy())
        except:
            pass
    height, width, c = hsv_img.shape 
    
    while(True):
        try: 
            frame, hsv_img = Cam.get_picture()
            # frame, hsv_img = Cam.get_picture_from_file("./sample_data/example1.png") 
            # FIRST FIND THE EDGE OF THE BOARD 
            table_mask, table_img, colour_img  = mask_table(hsv_img, frame)

            blue_mask, res_img, blue_centroid_locations  = mask_blue_puck(table_img, colour_img.copy())
            red_mask, red_res_img, red_centroid_locations  = mask_red_puck(table_img, colour_img.copy())
            
            # find the scores 
            blue_score = find_score_range(blue_centroid_locations, [region_1, region_2, region_3, region_4, region_5], height, colour='b')
            red_score = find_score_range(red_centroid_locations, [region_1, region_2, region_3, region_4, region_5], height, colour='r')
            
            red_final_score, blue_final_score = find_actual_score(blue_score, red_score, lines[0])


            red_payload = get_json_payload(red_final_score, "red")
            blue_payload = get_json_payload(blue_final_score, "blue")
            try:
                r = requests.put('http://'+"192.168.43.196:5000"+'/update-score', json=red_payload)
                print(r)
            except Exception as E:
                print(E)
            try:
                r = requests.put('http://'+"192.168.43.196:5000"+'/update-score', json=blue_payload)
                print(r)
            except Exception as E:
                print(E)           
                
            print("Red %s, Blue %s" %( red_final_score, blue_final_score))
            
            
            cv2.imshow('frame',table_img)
            cv2.imshow('mask',table_mask+blue_mask+red_mask)
            cv2.imshow('regular',frame)
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
            
            
        except:
            red_payload = get_json_payload(0, "red")
            blue_payload = get_json_payload(0, "blue")
            try:
                r = requests.put('http://'+"192.168.43.196:5000"+'/update-score', json=red_payload)
                print(r)
            except Exception as E:
                print(E)
            try:
                r = requests.put('http://'+"192.168.43.196:5000"+'/update-score', json=blue_payload)
                print(r)
            except Exception as E:
                print(E)         
        time.sleep(1)
        
    cv2.destroyAllWindows()





if __name__ == "__main__":
    print("\n|=*=*======**==&==|")
    print("|*===*&=*===*===  |")
    print("|=====&==*===     |")
    print("|  SHUFFLEBOTZ68  |")
    print("|     =====&==*===|")
    print("| *===*&=*===*=== |")
    print("|=*=*======**==&==|\n")
    main()