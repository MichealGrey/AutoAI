import time
import threading
import logging
from logging.handlers import RotatingFileHandler
import psutil
from datetime import datetime
import cv2
import pyautogui
import numpy as np

class Logger:
    """
    日志记录器
    """
    def __init__(self, log_file="rpa.log", max_bytes=10*1024*1024, backup_count=5):
        self.logger = logging.getLogger("RPA_Monitor")
        self.logger.setLevel(logging.INFO)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)

        # 格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

class PerformanceMonitor:
    """
    性能监控器
    """
    def __init__(self, interval=10):
        self.interval = interval
        self.running = False
        self.thread = None
        self.logger = Logger().logger

    def start(self):
        """
        启动性能监控
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.monitorLoop)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """
        停止性能监控
        """
        self.running = False
        if self.thread:
            self.thread.join()

    def monitorLoop(self):
        """
        监控循环
        """
        while self.running:
            try:
                # CPU使用率
                cpu_usage = psutil.cpu_percent(interval=1)
                # 内存使用率
                memory_usage = psutil.virtual_memory().percent
                # 磁盘使用率
                disk_usage = psutil.disk_usage("C:\\").percent

                self.logger.info(
                    f"性能监控 - CPU: {cpu_usage}%, 内存: {memory_usage}%, 磁盘: {disk_usage}%"
                )

                # 检查阈值
                if cpu_usage > 90:
                    self.logger.warning("CPU使用率超过90%")
                if memory_usage > 90:
                    self.logger.warning("内存使用率超过90%")
                if disk_usage > 90:
                    self.logger.warning("磁盘使用率超过90%")

                time.sleep(self.interval)
            except Exception as e:
                self.logger.error(f"性能监控失败: {e}")
                time.sleep(self.interval)

class ExceptionMonitor:
    """
    异常监控器
    """
    def __init__(self):
        self.logger = Logger().logger

    def handleException(self, task_id, exception):
        """
        处理异常
        :param task_id: 任务ID
        :param exception: 异常对象
        """
        self.logger.error(f"任务 {task_id} 执行失败: {exception}")
        # 可以添加更多异常处理逻辑，如发送报警邮件、微信等

class VideoRecorder:
    """
    视频记录器
    """
    def __init__(self, output_dir="videos", fps=10):
        self.output_dir = output_dir
        self.fps = fps
        self.running = False
        self.thread = None
        self.writer = None
        os.makedirs(output_dir, exist_ok=True)

    def startRecording(self):
        """
        开始录制视频
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.recordLoop)
            self.thread.daemon = True
            self.thread.start()

    def stopRecording(self):
        """
        停止录制视频
        """
        self.running = False
        if self.thread:
            self.thread.join()
        if self.writer:
            self.writer.release()
            self.writer = None

    def recordLoop(self):
        """
        视频录制循环
        """
        while self.running:
            try:
                # 获取屏幕尺寸
                screen_size = pyautogui.size()
                # 捕获屏幕
                screenshot = pyautogui.screenshot()
                # 转换为OpenCV格式
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # 初始化视频写入器
                if not self.writer:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = os.path.join(self.output_dir, f"recording_{timestamp}.avi")
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    self.writer = cv2.VideoWriter(output_file, fourcc, self.fps, screen_size)

                # 写入帧
                if self.writer:
                    self.writer.write(frame)

                # 控制帧率
                time.sleep(1 / self.fps)
            except Exception as e:
                print(f"视频录制失败: {e}")
                time.sleep(1)

class OperationRecorder:
    """
    操作记录器
    """
    def __init__(self, record_file="operations.log"):
        self.record_file = record_file

    def recordOperation(self, operation_type, params, result):
        """
        记录操作
        :param operation_type: 操作类型
        :param params: 操作参数
        :param result: 操作结果
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = f"{timestamp} - {operation_type} - {params} - {result}\n"
        with open(self.record_file, "a", encoding="utf-8") as f:
            f.write(record)

class MonitorSystem:
    """
    监控系统
    """
    def __init__(self):
        self.logger = Logger()
        self.performance_monitor = PerformanceMonitor()
        self.exception_monitor = ExceptionMonitor()
        self.operation_recorder = OperationRecorder()
        self.video_recorder = VideoRecorder()

    def start(self):
        """
        启动监控系统
        """
        self.performance_monitor.start()
        self.video_recorder.startRecording()

    def stop(self):
        """
        停止监控系统
        """
        self.performance_monitor.stop()
        self.video_recorder.stopRecording()

    def logInfo(self, message):
        self.logger.info(message)

    def logWarning(self, message):
        self.logger.warning(message)

    def logError(self, message):
        self.logger.error(message)

    def logDebug(self, message):
        self.logger.debug(message)

    def handleException(self, task_id, exception):
        self.exception_monitor.handleException(task_id, exception)

    def recordOperation(self, operation_type, params, result):
        self.operation_recorder.recordOperation(operation_type, params, result)