import threading
import pyautogui as pag
import PyHook3 as ph
import pythoncom
import win32api
import detect
import numpy as np
from PIL import ImageGrab
from PIL import Image
import cv2
optdic={
    'weights':"C:\\Users\\Administrator\\Desktop\\brotato_character\\yolo\\yolov7-main\\brotatobest.pt",#修改pt文件
    'conf':0.7,
    'source':"C:\\Users\\Administrator\\Desktop\\brotato_character\\yolo\\yolov7-main\\dected.png"
}


# 定义全局变量 服务于F2键
x, y = None, None
pre_x, pre_y = None, None
stop_flag = False  # 控制 show_mouse_position() 函数是否执行的全局变量

screen_xyxy=[None,None,None,None] #窗口坐标
game_flag,game_flag_detect = False,False#是否玩游戏的标记符,检测F3是否被按下
yolo = detect.yolov7API(optdic)

# 写一个获取坐标的工具函数
def get_position(event):
    global x, y, stop_flag,game_flag,game_flag_detect  # 在函数内部使用全局变量
    if event.Key == 'F2':  # 设置截取坐标方式
        x, y = pag.position()
        x,y=int(x),int(y)
        # print('({},{})'.format(x, y))
    if event.Key=='F3':
        game_flag=True
        print('游戏进行')
    if event.Key == 'F4':
        game_flag = False
        print('游戏终止')
    if event.Key == 'F12':  # 按下F12键结束监听并终止显示线程
        hm.UnhookKeyboard()
        stop_flag = ~stop_flag
        if stop_flag:
            print('监听关闭')
        else:
            print('监听打开')
        win32api.PostQuitMessage()

    return True


# 进行键盘监听的函数
def listen_keyboard():
    global hm
    hm = ph.HookManager()  # 创建一个“钩子”管理对象
    hm.KeyAll = get_position  # 监听所有键盘事件
    hm.HookKeyboard()  # 设置键盘钩子
    pythoncom.PumpMessages()  # 进入循环，如不手动关闭，程序将一直处于监听状态


# 进行显示鼠标位置的函数
def show_mouse_position():
    global x, y, stop_flag, pre_x, pre_y,screen_xyxy,game_flag
    while not stop_flag:
        if x != pre_x or y != pre_y:  # 只有在坐标值发生改变时才打印坐标信息
            print('鼠标位置：({},{})'.format(x, y))
            pre_x, pre_y = x, y
            screen_xyxy[0],screen_xyxy[1],screen_xyxy[2],screen_xyxy[3]=screen_xyxy[2],screen_xyxy[3],x,y
            if screen_xyxy[0]!=None and screen_xyxy[1]!=None and screen_xyxy[2]!=None and screen_xyxy[3]!=None:
                if screen_xyxy[0]>screen_xyxy[2]:
                    screen_xyxy[0],screen_xyxy[2]=screen_xyxy[2],screen_xyxy[0]
                if screen_xyxy[1]>screen_xyxy[3]:
                    screen_xyxy[1],screen_xyxy[3]=screen_xyxy[3],screen_xyxy[1]
        if game_flag:
            print("thinking")
            walk_one_step()

def walk_one_step():
    global screen_xyxy
    if screen_xyxy[0]==None or screen_xyxy[0]==None or screen_xyxy[0]==None or screen_xyxy[0]==None:
        print("窗口坐标还没有锁定，请先关闭游戏模式（F3），设置窗口坐标")
        return
    #截图
    allscreen_PIL = ImageGrab.grab()  # PIL截屏
    box=(screen_xyxy[0],screen_xyxy[1],screen_xyxy[2],screen_xyxy[3])
    screen_PIL=allscreen_PIL.crop(box)
    screen_PIL.save("dected.png")
    img = Image.open("dected.png")
    #img.size[0]=x img.size[1]=y
    na = np.asarray(img)  # 将图片转换为数组 xy,变成[y][x]
    backdic = yolo.run(optdic)
    if backdic["holesum"]!=1:
        pag.press(['a'])
        print("miss")
    else:
        bodylen=2*int(pow(pow(backdic["x1"]-backdic['x2'],2)+pow(backdic['y1']-backdic['y2'],2),0.5))
        xx0=max(backdic["x1"]-bodylen,0)
        yy0=max(backdic["y2"]-bodylen,0)
        x=backdic["x2"]-backdic['x1']
        y = backdic["y2"] - backdic['y1']
        dangerli = [getpercent(na,xx0, yy0, min(xx0 + bodylen,img.size[0]), min(yy0 + bodylen,img.size[1])),  # 0
              getpercent(na,xx0, yy0 + bodylen, min(xx0 + bodylen,img.size[0]), min(yy0 + bodylen,img.size[1])),  # 1
              getpercent(na,xx0, yy0 + bodylen + y,min(xx0 + bodylen,img.size[0]) , min(yy0 + 2 * bodylen + y,img.size[1])),  # 2
              getpercent(na,xx0 + bodylen, yy0, min(xx0 + bodylen + x,img.size[0]), min(yy0 + bodylen,img.size[1])),  # 3
              getpercent(na,xx0 + bodylen, yy0 + bodylen, min(xx0 + x + bodylen,img.size[0]), min(yy0 + bodylen + y,img.size[1])),  # 4
              getpercent(na,xx0 + bodylen, yy0 + bodylen + y, min(xx0 + bodylen + x,img.size[0]), min(yy0 + 2 * bodylen + y,img.size[1])),  # 5
              getpercent(na,xx0 + bodylen + x, yy0, min(xx0 + 2 * bodylen + x,img.size[0]), min(yy0 + bodylen,img.size[1])),  # 6
              getpercent(na,xx0 + bodylen + x, yy0 + bodylen, min(xx0 + 2 * bodylen + x,img.size[0]), min(yy0 + bodylen + y,img.size[1])),  # 7
              getpercent(na,xx0 + bodylen + x, yy0 + bodylen + y, min(xx0 + 2 * bodylen + x,img.size[0]), min(yy0 + 2 * bodylen + y,img.size[1]))] # 8
        valueli = [value_area(na, 0, 0, backdic["x1"], backdic["y1"]),  # 0
                    value_area(na, 0, backdic["y1"], backdic["x1"], backdic["y2"]),  # 1
                    value_area(na, 0, backdic["y2"], backdic["x1"], img.size[1]),  # 2
                    value_area(na, backdic["x1"],0, backdic["x2"], backdic["y1"]),  # 3
                    value_area(na, backdic["x1"], backdic["y1"], backdic["x2"], backdic["y2"]),  # 4
                    value_area(na, backdic["x1"], backdic["y2"], backdic["x2"], img.size[1]),  # 5
                    value_area(na, backdic["x2"], 0, img.size[0], backdic["y1"]),  # 6
                    value_area(na, backdic["x2"], backdic["y1"], img.size[0], backdic["y2"]),  # 7
                    value_area(na, backdic["x2"], backdic["y2"], img.size[0],img.size[1])]  # 8
        if dangerli[0]>0.5 or dangerli[2]>0.5 or dangerli[6]>0.5 or dangerli[8]>0.5:
            print(dangerli[0],dangerli[2],dangerli[6],dangerli[8])
            max_vi,max_val=0,dangerli[0]
            for i in [2,6,8]:
                if max_val>dangerli[i]:
                    max_vi=i
                    max_val=dangerli[i]
            if max_vi==0:
                pag.keyDown('D','S')
                pag.PAUSE=0.1
                pag.keyUp('D', 'S')
            elif max_vi==2:
                pag.keyDown('D', 'W')
                pag.PAUSE=0.1
                pag.keyUp('D', 'W')
            elif max_vi==6:
                pag.keyDown('a', 'S')
                pag.PAUSE=0.1
                pag.keyUp('a', 'S')
            elif max_vi ==8:
                pag.keyDown('a', 'w')
                pag.PAUSE=0.1
                pag.keyUp('a', 'w')
            print("danger1")
        elif dangerli[1]>0.5 or dangerli[3]>0.5 or dangerli[5]>0.5 or dangerli[7]>0.5:
            if dangerli[1]>0.5:
                pag.keyDown('D')
                pag.PAUSE=0.1
                pag.keyUp('D')
                if dangerli[3] < 0.5:
                    pag.keyDown('w')
                    pag.PAUSE=0.1
                    pag.keyUp('w')
                elif dangerli[5] < 0.5:
                    pag.keyDown('S')
                    pag.PAUSE=0.1
                    pag.keyUp('S')
            if dangerli[3]>0.5:
                pag.keyDown('S')
                pag.PAUSE=0.1
                pag.keyUp('S')
                if dangerli[1] < 0.5:
                    pag.keyDown('a')
                    pag.PAUSE=0.1
                    pag.keyUp('a')
                elif dangerli[7] < 0.5:
                    pag.keyDown('D')
                    pag.PAUSE=0.1
                    pag.keyUp('D')
            if dangerli[5]>0.5:
                pag.keyDown('w')
                pag.PAUSE=0.1
                pag.keyUp('w')
                if dangerli[1] < 0.5:
                    pag.keyDown('a')
                    pag.PAUSE=0.1
                    pag.keyUp('a')
                elif dangerli[7] < 0.5:
                    pag.keyDown('D')
                    pag.PAUSE=0.1
                    pag.keyUp('D')
            if dangerli[7]>0.5:
                pag.keyDown('a')
                pag.PAUSE=0.1
                pag.keyUp('a')
                if dangerli[3] < 0.5:
                    pag.keyDown('w')
                    pag.PAUSE=0.1
                    pag.keyUp('w')
                elif dangerli[5] < 0.5:
                    pag.keyDown('S')
                    pag.PAUSE=0.1
                    pag.keyUp('S')
            print("danger2")
        else:
            max_vi, max_val = 0, valueli[0]
            for i in range(9):
                if max_val > valueli[i]:
                    max_vi = i
                    max_val = valueli[i]
            if max_vi == 0:
                pag.keyDown('a', 'w')
                pag.PAUSE=0.1
                pag.keyUp('a', 'w')
            elif max_vi == 1:
                pag.keyDown('a')
                pag.PAUSE=0.1
                pag.keyUp('a')
            elif max_vi == 2:
                pag.keyDown('a', 's')
                pag.PAUSE=0.1
                pag.keyUp('a', 's')
            elif max_vi == 3:
                pag.keyDown('w')
                pag.PAUSE=0.1
                pag.keyUp('w')
            elif max_vi == 5:
                pag.keyDown('s')
                pag.PAUSE=0.1
                pag.keyUp('s')
            elif max_vi == 6:
                pag.keyDown('w','d')
                pag.PAUSE=0.1
                pag.keyUp('w','d')
            elif max_vi == 7:
                pag.keyDown('d')
                pag.PAUSE=0.1
                pag.keyUp('d')
            elif max_vi == 8:
                pag.keyDown('s','d')
                pag.PAUSE=0.1
                pag.keyUp('s','d')
            print("value1")

def getpercent(na, x0, y0, x1, y1):  # 判断每一块的百分比
    area = (x1 - x0 + 1) * (y1 - y0 + 1)
    num = 0
    for i in range(int(x0), int(x1-1)):
        for j in range(int(y0), int(y1-1)):
            # print(j, i)
            if judgedanger(na[j][i]):
                num += 1
    return num / area


def value_area(na, x0, y0, x1, y1):
    sum = 0
    for i in range(int(x0), int(x1-1 )):
        for j in range(int(y0), int(y1-1 )):
            # print(j,i)
            if jungevalue(na[j][i]):
                sum += 1
    return sum
# def value_area(na, x0, y0, x1, y1):
#     sub_na = na[y0:y1 + 1, x0:x1 + 1, :]
#     mask = jungevalue(sub_na)
#     sum = np.sum(mask)
#     return sum
#
# def getpercent(na, x0, y0, x1, y1):
#     # 判断每一块的百分比
#     area = (x1 - x0 + 1) * (y1 - y0 + 1)
#     danger_pixels = np.logical_not(
#         np.all(na[y0:y1 + 1, x0:x1 + 1] >= np.array([[90, 150, 110], [80, 130, 50], [120, 170, 45]]), axis=-1) &
#         np.all(na[y0:y1 + 1, x0:x1 + 1] <= np.array([[100, 190, 130], [90, 170, 70], [140, 240, 60]]), axis=-1))
#     return danger_pixels.sum() / area
def judgedanger(pixlist):  # 判断每个像素点是不是危险
    R_low = [90, 150, 110]
    R_high = [100, 190, 130]
    G_low = [80, 130, 50]
    G_high = [90, 170, 70]
    B_low = [120, 170, 45]
    B_high = [140, 240, 60]
    r, g, b = pixlist
    if R_low[0] <= r <= R_high[0] and G_low[0] <= g <= G_high[0] and B_low[0] <= b <= B_high[0]:
        return True
    elif R_low[1] <= r <= R_high[1] and G_low[1] <= g <= G_high[1] and B_low[1] <= b <= B_high[1]:
        return True
    elif R_low[2] <= r <= R_high[2] and G_low[2] <= g <= G_high[2] and B_low[2] <= b <= B_high[2]:
        return True
    else:
        return False


def jungevalue(pixlist):  # 判断价值量的多少
    R = [99, 146]
    G = [142, 218]
    B = [90, 151]
    r, g, b = pixlist
    if R[0] <= r <= R[1] and G[0] <= g <= G[1] and B[0] <= b <= B[1]:
        return True
    return False
# def judgedanger(pixlist):
#     R_low = [90, 150, 110]
#     R_high = [100, 190, 130]
#     G_low = [80, 130, 50]
#     G_high = [90, 170, 70]
#     B_low = [120, 170, 45]
#     B_high = [140, 240, 60]
#     mask_R = np.all((R_low[0] <= pixlist[:, 0]) & (pixlist[:, 0] <= R_high[0]) |
#                     (R_low[1] <= pixlist[:, 0]) & (pixlist[:, 0] <= R_high[1]) |
#                     (R_low[2] <= pixlist[:, 0]) & (pixlist[:, 0] <= R_high[2]), axis=1)
#     mask_G = np.all((G_low[0] <= pixlist[:, 1]) & (pixlist[:, 1] <= G_high[0]) |
#                     (G_low[1] <= pixlist[:, 1]) & (pixlist[:, 1] <= G_high[1]) |
#                     (G_low[2] <= pixlist[:, 1]) & (pixlist[:, 1] <= G_high[2]), axis=1)
#     mask_B = np.all((B_low[0] <= pixlist[:, 2]) & (pixlist[:, 2] <= B_high[0]) |
#                     (B_low[1] <= pixlist[:, 2]) & (pixlist[:, 2] <= B_high[1]) |
#                     (B_low[2] <= pixlist[:, 2]) & (pixlist[:, 2] <= B_high[2]), axis=1)
#     return np.logical_not(mask_R & mask_G & mask_B)
#
# def jungevalue(pixlist):  # 判断价值量的多少
#     R = [99, 146]
#     G = [142, 218]
#     B = [90, 151]
#     mask = np.all((R[0] <= pixlist[:, 0]) & (pixlist[:, 0] <= R[1]) &
#                   (G[0] <= pixlist[:, 1]) & (pixlist[:, 1] <= G[1]) &
#                   (B[0] <= pixlist[:, 2]) & (pixlist[:, 2] <= B[1]), axis=1)
#     return mask
#
# def getpercent(na,x0,y0,x1,y1): #判断每一块的百分比
#     area= (x1-x0+1)*(y1-y0+1)
#     num=0
#     for i in range(x0,x1+1):
#         for j in range(y0,y1+1):
#             if judgedanger(na[j][i]):
#                 num+=1
#     return num/area
#
# def judgedanger(pixlist):  #判断每个像素点是不是危险
#     R_low = [90, 150, 110]
#     R_high = [100, 190, 130]
#     G_low = [80, 130, 50]
#     G_high = [90, 170, 70]
#     B_low = [120, 170, 45]
#     B_high = [140, 240, 60]
#     r,g,b=pixlist
#     if R_low[0] <= r <= R_high[0] and G_low[0] <= g <= G_high[0] and B_low[0] <= b <= B_high[0]:
#         return False
#     elif R_low[1] <= r <= R_high[1] and G_low[1] <= g <= G_high[1] and B_low[1] <= b <= B_high[1]:
#         return False
#     elif R_low[2] <= r <= R_high[2] and G_low[2] <= g <= G_high[2] and B_low[2] <= b <= B_high[2]:
#         return False
#     else:
#         return True

if __name__ == '__main__':
    # 创建并启动两个线程
    t1 = threading.Thread(target=listen_keyboard)
    t2 = threading.Thread(target=show_mouse_position)
    t1.start()
    t2.start()
    # backdic = yolo.run(optdic)
    # img = backdic["img"]
    # print(type(img))
    # hole_sum = backdic["holesum"]