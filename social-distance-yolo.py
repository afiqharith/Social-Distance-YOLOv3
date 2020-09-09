__author__ = "Afiq Harith"
__email__ = "afiqharith05@gmail.com"
__date__ = "09 Sep 2020"
__status__ = "Development"

import cv2
import numpy as np
import math
from setup import config, load_model


colors = config.COLORS
GREEN = colors.get('GREEN')
RED = colors.get('RED')
YELLOW = colors.get('YELLOW')
WHITE = colors.get('WHITE')
ORANGE = colors.get('ORANGE')

# Load video
videosrc = "TownCentre.mp4"
video = cv2.VideoCapture(videosrc)

#config for different datasets
if videosrc == 'TownCentre.mp4':
    configuration = config.TOWNCENTRE

if videosrc == 'PETS2009.mp4':
    configuration = config.PETS2009

if videosrc == 'VIRAT.mp4':
    configuration = config.VIRAT

distance = configuration.get('distance')
h = configuration.get('height')
w = configuration.get('width')

# Load Yolo
net, output_layers, classes = load_model.loading_dependencies()

def calculateCentroid(xmin,ymin,xmax,ymax):

    xmid = ((xmax+xmin)/2)
    ymid = ((ymax+ymin)/2)
    centroid = (xmid,ymid)

    return xmid,ymid,centroid

def get_distance(x1,x2,y1,y2):

    distance = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    
    return distance

def draw_detection_box(frame,x1,y1,x2,y2,color):

    cv2.rectangle(frame,(x1,y1),(x2,y2), color, 2)

def main():

    while True:

        centroids = []
        box_colors = []
        detectedBox = []
        ret, frame = video.read() 

        if ret:
            frame_resized = cv2.resize(frame, (416,416)) # resize frame for prediction       
        else:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        height, width, channels = frame.shape

        # Detecting objects
        blob = cv2.dnn.blobFromImage(frame_resized, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                #if prediction is 50% and class id is 0 which is 'person'
                if confidence > 0.5 and class_id == 0:
                    
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # apply non-max suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]

                xmin = x
                ymin = y
                xmax = (x + w)
                ymax = (y + h)

                '''use when to select person based on class label's name instead of object's class id'''
                # label = str(classes[class_ids[i]])
                # if label == 'person':

                #calculate centroid point for bounding boxes
                xmid, ymid, centroid = calculateCentroid(xmin,ymin,xmax,ymax)
                detectedBox.append([xmin,ymin,xmax,ymax,centroid])

                my_color = 0
                for k in range (len(centroids)):
                    c = centroids[k]
                    
                    if get_distance(c[0],centroid[0],c[1],centroid[1]) <= distance:
                        box_colors[k] = 1
                        my_color = 1
                        cv2.line(frame, (int(c[0]),int(c[1])), (int(centroid[0]),int(centroid[1])), YELLOW, 1,cv2.LINE_AA)
                        cv2.circle(frame, (int(c[0]),int(c[1])), 3, ORANGE, -1,cv2.LINE_AA)
                        cv2.circle(frame, (int(centroid[0]),int(centroid[1])), 3, ORANGE, -1,cv2.LINE_AA)
                        break
                centroids.append(centroid)
                box_colors.append(my_color)        

        for i in range (len(detectedBox)):
            x1 = detectedBox[i][0]
            y1 = detectedBox[i][1]
            x2 = detectedBox[i][2]
            y2 = detectedBox[i][3]
            
            #for ellipse output
            xc = ((x2+x1)/2)
            yc = y2-5
            centroide = (int(xc),int(yc))

            if box_colors[i] == 0:
                color = WHITE
                draw_detection_box(frame,x1,y1,x2,y2,color)
                label = "safe"
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                y1label = max(y1, labelSize[1])
                cv2.rectangle(frame, (x1, y1label - labelSize[1]),(x1 + labelSize[0], y1 + baseLine), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 1,cv2.LINE_AA)

            else:
                color = RED
                draw_detection_box(frame,x1,y1,x2,y2,color)
                # cv2.ellipse(frame, centroide, (35, 19), 0.0, 0.0, 360.0, RED, 2)
                label = "unsafe"
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                y1label = max(y1, labelSize[1])
                cv2.rectangle(frame, (x1, y1label - labelSize[1]),(x1 + labelSize[0], y1 + baseLine), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ORANGE, 1,cv2.LINE_AA)

        cv2.imshow("Social Distance System", frame)

        if cv2.waitKey(1) >= 0:  
            break

    video.release()

if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()
