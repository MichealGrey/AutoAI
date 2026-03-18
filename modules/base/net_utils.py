import subprocess
import time

class NetUtils:
    @staticmethod
    def ping(host, count=4, timeout=1000):
        """
        执行ping命令
        :param host: 目标主机
        :param count: ping次数
        :param timeout: 超时时间（毫秒）
        :return: (success, output)
        """
        try:
            result = subprocess.run(
                ["ping", "-n", str(count), "-w", str(timeout), host],
                capture_output=True,
                text=True,
                timeout=10
            )
            success = result.returncode == 0
            return success, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Ping超时"
        except Exception as e:
            return False, f"Ping失败: {e}"

    @staticmethod
    def continuePing(host, interval=60):
        """
        持续执行ping命令
        :param host: 目标主机
        :param interval: 间隔时间（秒）
        """
        while True:
            success, output = NetUtils.ping(host, count=1, timeout=1000)
            if not success:
                print(f"网络连接失败: {host}")
            time.sleep(interval)

    @staticmethod
    def checkInternetConnection():
        """
        检查互联网连接
        :return: True/False
        """
        hosts = ["8.8.8.8", "www.baidu.com", "www.google.com"]
        for host in hosts:
            success, _ = NetUtils.ping(host, count=1, timeout=1000)
            if success:
                return True
        return False