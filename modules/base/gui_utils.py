import pyautogui
import pyperclip
from datetime import datetime
from PIL import ImageGrab
import time

pyautogui.FAILSAFE = False

class GUIUtils:
    @staticmethod
    def clickByImg(logger, img_path, offsetx=0, offsety=0, confidence=0.9):
        target_position = pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
        if target_position is not None:
            click_x = target_position.x + offsetx
            click_y = target_position.y + offsety
            pyautogui.click(click_x, click_y)
            return True
        else:
            logger.info(f"未找到指定图片: {img_path}")
            return False

    @staticmethod
    def doubleClickByImg(logger, img_path, offsetx=0, offsety=0, confidence=0.9):
        target_position = pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
        if target_position is not None:
            click_x = target_position.x + offsetx
            click_y = target_position.y + offsety
            pyautogui.doubleClick(click_x, click_y)
            return True
        else:
            logger.info(f"未找到指定图片: {img_path}")
            return False

    @staticmethod
    def rightClickByImg(logger, img_path, offsetx=0, offsety=0, confidence=0.9):
        target_position = pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
        if target_position is not None:
            click_x = target_position.x + offsetx
            click_y = target_position.y + offsety
            pyautogui.rightClick(click_x, click_y)
            return True
        else:
            logger.info(f"未找到指定图片: {img_path}")
            return False

    @staticmethod
    def waitUntilShow(logger, imgPath, timeout=20, shoot=True):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                position = pyautogui.locateOnScreen(image=imgPath, grayscale=False, confidence=0.9)
                if position:
                    logger.info(f"找到图片: {imgPath} at ({position.left}, {position.top})")
                    return pyautogui.center(position)
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.info(f"未找到图片: {imgPath}, 异常: {e}")
                time.sleep(0.1)
        else:
            if shoot:
                GUIUtils.screenShoot(imgPath)
            logger.info(f"超时未找到图片: {imgPath}")
            return None

    @staticmethod
    def waitForImageToDisappear(logger, image_path, confidence=0.9, interval=0.01):
        while True:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location is None:
                logger.info(f"图片已消失: {image_path}")
                break
            time.sleep(interval)

    @staticmethod
    def clickUntilShow(logger, img_path, offsetx=0, offsety=0, confidence=0.9, wait_imgPath=None, timeout=20):
        if wait_imgPath:
            position = GUIUtils.waitUntilShow(logger, wait_imgPath, timeout)
            if position:
                return GUIUtils.clickByImg(logger, img_path, offsetx, offsety, confidence)
            else:
                return False
        else:
            return GUIUtils.clickByImg(logger, img_path, offsetx, offsety, confidence)

    @staticmethod
    def enterUntilShow(logger, wait_imgPath, timeout=20):
        position = GUIUtils.waitUntilShow(logger, wait_imgPath, timeout)
        if position:
            pyautogui.press("enter")
            return True
        else:
            return False

    @staticmethod
    def maxWindowUntilShow(logger, wait_imgPath, timeout=20):
        position = GUIUtils.waitUntilShow(logger, wait_imgPath, timeout)
        if position:
            pyautogui.hotkey('winleft', 'up')
            return True
        else:
            return False

    @staticmethod
    def screenShoot(imgPath):
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(f"screenshot_{imgPath.replace('/', '_').replace('\\', '_')}.png")
        except Exception as e:
            print(f"截图失败: {e}")

    @staticmethod
    def showMessageBox(title='RPA程序', message='请选择操作', buttons=['确定', '取消']):
        return pyautogui.confirm(text=message, title=title, buttons=buttons)

    @staticmethod
    def showAlert(title='RPA程序', message='操作提示'):
        return pyautogui.alert(text=message, title=title, button='确定')

    @staticmethod
    def promptInput(title='RPA程序', message='请输入内容', default=''):
        return pyautogui.prompt(text=message, title=title, default=default)

    @staticmethod
    def isDateFormat(string, format='%Y-%m-%d %H:%M:%S'):
        try:
            datetime.strptime(string, format)
            return True
        except Exception as e:
            return False