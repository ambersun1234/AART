import os
import cv2
import glob

from darknet import *

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def overlap(leftTopX1, leftTopY1, rightBottomX1, rightBottomY1,
                  leftTopX2, leftTopY2, rightBottomX2, rightBottomY2):
    x0 = max(leftTopX1, leftTopX2)
    x1 = min(rightBottomX1, rightBottomX2)
    y0 = max(leftTopY1, leftTopY2)
    y1 = min(rightBottomY1, rightBottomY2)
    if x0 >= x1 or y0 >= y1:
        return 0.0
    areaInt = (x1 - x0) * (y1 - y0)
    return areaInt / ((rightBottomX1-leftTopX1)*(rightBottomY1-leftTopY1) +\
                        (rightBottomX2-leftTopX2)*(rightBottomY2-leftTopY2) - areaInt)

# obj_names = ['4', '5', '2', '1', '11', 'hoop', 'ball']
with open('/home/aart/library/darknet/trainData/cfg/obj.names', 'r') as file:
    obj_names = file.readlines()

for i in range(len(obj_names)):
    obj_names[i] = obj_names[i][:-1]

net = load_net(
    '/home/aart/library/darknet/trainData/cfg/yolov3_.cfg'.encode('utf-8'),
    '/home/aart/library/darknet/trainData/cfg/backup/yolov3_170000.weights'.encode('utf-8'),
    0
)
meta = load_meta('/home/aart/library/darknet/trainData/cfg/obj.data'.encode('utf-8'))
cap = cv2.VideoCapture('/home/aart/Documents/20191122_163120.mp4')
yolos = '/home/aart/Pictures/yolos'
jpgs = glob.glob(os.path.join(yolos, '*.jpg'))

allDict = {'4': 0, '5': 0, '2': 0, '1': 0, '11': 0, 'hoop': 0, 'ball': 0}
yesDict = {'4': 0, '5': 0, '2': 0, '1': 0, '11': 0, 'hoop': 0, 'ball': 0}
for picName in jpgs:
    txtName = picName.split('.')[0] + '.txt'
    with open(txtName, 'r') as file:
        lines = file.readlines()
    img = cv2.imread(picName)
    result = detect(net, meta, img)
    w, h, c = img.shape
    x, y, x2, y2 = 0, 0, 0, 0
    x3, y3, x4, y4 = 0, 0, 0, 0
    for i in result:
        label = i[0].decode()
        allDict[label] += 1
        x, y, x2, y2 = convertBack(float(i[2][0]), float(i[2][1]), float(i[2][2]), float(i[2][3]))
        tmpOverlap = 0
        overlaped = 0
        for line in lines:
            row = line[:-1]
            spli = row.split(' ')
            if label == obj_names[int(spli[0])]:
                a, b, c, d = int(w*float(spli[2])), int(h*float(spli[1])), int(w*float(spli[4])), int(h*float(spli[3]))
                y3, x3, y4, x4 = convertBack(a, b, c, d)
                cv2.rectangle(img, (x3, y3), (x4, y4), (0, 255, 0), 2)
                img = cv2.resize(img, (int(h/3), int(w/3)), interpolation=cv2.INTER_CUBIC)
                print(label)
                if label == '4':
                    tmpOverlap = overlap(x, y, x2, y2, x3, y3, x4, y4)
                    if tmpOverlap > overlaped:
                        overlaped = tmpOverlap
                else:
                    overlaped = overlap(x, y, x2, y2, x3, y3, x4, y4)
                cv2.imshow('show', img)
                cv2.waitKey(1)
                # print(spli[1], float(spli[2]), float(spli[3]), float(spli[4]))
                x3, y3, x4, y4 = convertBack(float(spli[1]), float(spli[2]), float(spli[3]), float(spli[4]))
                break
        # print(x, y, x2, y2, x3, y3, x4, y4)
        # overlap = overlap(x, y, x2, y2, x3, y3, x4, y4)
        if overlaped > 0.7:
            yesDict[label] += 1
print(allDict, yesDict)
