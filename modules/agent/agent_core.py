import time
import threading
from queue import Queue
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, task_id, task_type, params, priority=1):
        self.task_id = task_id
        self.task_type = task_type
        self.params = params
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.create_time = time.time()
        self.start_time = None
        self.end_time = None

class AgentCore:
    def __init__(self, max_workers=5):
        self.task_queue = Queue()
        self.workers = []
        self.max_workers = max_workers
        self.running = False
        self.task_registry = {}
        self.skill_registry = {}
        self.lock = threading.Lock()

    def registerSkill(self, skill_name, skill_class):
        """
        注册技能
        :param skill_name: 技能名称
        :param skill_class: 技能类
        """
        with self.lock:
            self.skill_registry[skill_name] = skill_class

    def submitTask(self, task):
        """
        提交任务
        :param task: 任务对象
        """
        with self.lock:
            self.task_registry[task.task_id] = task
        self.task_queue.put(task)

    def getTaskStatus(self, task_id):
        """
        获取任务状态
        :param task_id: 任务ID
        """
        with self.lock:
            return self.task_registry.get(task_id, None)

    def workerLoop(self):
        """
        工作线程循环
        """
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                with self.lock:
                    task.status = TaskStatus.RUNNING
                    task.start_time = time.time()

                try:
                    # 执行任务
                    if task.task_type in self.skill_registry:
                        skill_class = self.skill_registry[task.task_type]
                        skill_instance = skill_class()
                        result = skill_instance.execute(task.params)
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                    else:
                        task.error = f"未知任务类型: {task.task_type}"
                        task.status = TaskStatus.FAILED
                except Exception as e:
                    task.error = f"任务执行失败: {e}"
                    task.status = TaskStatus.FAILED
                finally:
                    task.end_time = time.time()
                    self.task_queue.task_done()
            except:
                pass

    def start(self):
        """
        启动Agent
        """
        if not self.running:
            self.running = True
            for _ in range(self.max_workers):
                worker = threading.Thread(target=self.workerLoop)
                worker.daemon = True
                worker.start()
                self.workers.append(worker)

    def stop(self):
        """
        停止Agent
        """
        self.running = False
        for worker in self.workers:
            worker.join()

class TaskScheduler:
    """
    任务调度器
    """
    @staticmethod
    def scheduleTask(agent, task_type, params, priority=1):
        """
        调度任务
        :param agent: Agent实例
        :param task_type: 任务类型
        :param params: 任务参数
        :param priority: 任务优先级
        """
        task_id = f"task_{int(time.time())}_{int(time.time() * 1000) % 1000}"
        task = Task(task_id, task_type, params, priority)
        agent.submitTask(task)
        return task_id

class ExceptionHandler:
    """
    异常处理器
    """
    @staticmethod
    def handleException(task, exception):
        """
        处理异常
        :param task: 任务对象
        :param exception: 异常对象
        """
        task.error = str(exception)
        task.status = TaskStatus.FAILED
        # 可以添加更多异常处理逻辑，如重试、报警等

class ResourceManager:
    """
    资源管理器
    """
    def __init__(self):
        self.resources = {}

    def allocateResource(self, resource_name, resource):
        """
        分配资源
        """
        self.resources[resource_name] = resource

    def getResource(self, resource_name):
        """
        获取资源
        """
        return self.resources.get(resource_name, None)

    def releaseResource(self, resource_name):
        """
        释放资源
        """
        if resource_name in self.resources:
            del self.resources[resource_name]