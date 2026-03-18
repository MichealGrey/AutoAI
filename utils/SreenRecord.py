import numpy as np
from PIL import ImageGrab,ImageDraw
import cv2
import config.appConfig as appConfig
import datetime
import pyautogui

def Record(queue):
    
    # 设置录制参数
    SCREEN_SIZE = (1920, 1080)
    FILENAME = appConfig.VideoPath + datetime.datetime.strftime(datetime.datetime.today(),'%Y%m%d%H%M%S') + '.mp4'
    FPS = 20.0

    # 开始录制
    
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(FILENAME, fourcc, FPS, SCREEN_SIZE)
    out.set(cv2.CAP_PROP_POS_FRAMES,0)#设置帧索引

    while True:
        # 获取屏幕截图
        # img = pyautogui.screenshot()
        img = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
        center_x, center_y = pyautogui.position()  # 圆心坐标
        radius = 5                   # 半径
        draw = ImageDraw.Draw(img)
        draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], fill='blue')
        # 转换为OpenCV格式
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        # 写入视频文件
        out.write(frame)

        if not queue.empty():
            break

    # 停止录制
    out.release()
    cv2.destroyAllWindows()
