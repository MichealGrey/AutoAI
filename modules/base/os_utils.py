import psutil
import time

class OSUtils:
    @staticmethod
    def killAPPS(app_names):
        """
        关闭指定名称的应用程序
        :param app_names: 应用程序名称列表，如["notepad.exe", "chrome.exe"]
        """
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in [name.lower() for name in app_names]:
                    proc.kill()
                    print(f"已关闭应用程序: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    @staticmethod
    def secondsToHms(seconds):
        """
        将秒数转换为时分秒格式
        :param seconds: 秒数
        :return: (hours, minutes, seconds)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return hours, minutes, seconds

    @staticmethod
    def getProcessesByName(name):
        """
        根据进程名称获取进程列表
        :param name: 进程名称
        :return: 进程列表
        """
        processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == name.lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    @staticmethod
    def isProcessRunning(name):
        """
        检查进程是否在运行
        :param name: 进程名称
        :return: True/False
        """
        return len(OSUtils.getProcessesByName(name)) > 0

    @staticmethod
    def getCPUUsage():
        """
        获取CPU使用率
        :return: CPU使用率百分比
        """
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def getMemoryUsage():
        """
        获取内存使用情况
        :return: 内存使用百分比
        """
        return psutil.virtual_memory().percent

    @staticmethod
    def getDiskUsage(path='C:\\'):
        """
        获取磁盘使用情况
        :param path: 磁盘路径
        :return: 磁盘使用百分比
        """
        return psutil.disk_usage(path).percent