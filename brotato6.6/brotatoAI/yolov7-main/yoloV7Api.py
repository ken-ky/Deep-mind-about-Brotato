import detect
import cv2
import time
import matplotlib.pyplot as plt
optdic={
    'weights':"C:\\Users\\Administrator\\Desktop\\brotato_character\\yolo\\yolov7-main\\brotatobest.pt",#修改pt文件
    'conf':0.7,
    'source':"C:\\Users\\Administrator\\Desktop\\brotato_character\\yolo\\yolov7-main\\test.png"
}

yolo=detect.yolov7API(optdic)
backdic=yolo.run(optdic)
img=backdic["img"]
# print(type(img))
hole_sum=backdic["holesum"]
# print(hole_sum)