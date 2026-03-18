from abc import ABC, abstractmethod
import importlib
import os

class SkillInterface(ABC):
    """
    技能接口抽象基类
    """
    @abstractmethod
    def getName(self):
        """
        获取技能名称
        """
        pass

    @abstractmethod
    def getDescription(self):
        """
        获取技能描述
        """
        pass

    @abstractmethod
    def execute(self, params):
        """
        执行技能
        :param params: 技能参数
        """
        pass

class SkillManager:
    """
    技能管理器
    """
    def __init__(self):
        self.skills = {}

    def loadSkill(self, skill_path):
        """
        加载技能
        :param skill_path: 技能文件路径
        """
        try:
            module_name = os.path.splitext(os.path.basename(skill_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, skill_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找技能类
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, SkillInterface) and obj != SkillInterface:
                    skill_instance = obj()
                    self.skills[skill_instance.getName()] = skill_instance
                    print(f"已加载技能: {skill_instance.getName()}")
        except Exception as e:
            print(f"加载技能失败: {e}")

    def loadSkillsFromDirectory(self, directory):
        """
        从目录加载所有技能
        :param directory: 技能目录
        """
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                skill_path = os.path.join(directory, filename)
                self.loadSkill(skill_path)

    def getSkill(self, skill_name):
        """
        获取技能
        :param skill_name: 技能名称
        """
        return self.skills.get(skill_name, None)

    def listSkills(self):
        """
        列出所有技能
        """
        return list(self.skills.keys())

class ExampleSkill(SkillInterface):
    """
    示例技能
    """
    def getName(self):
        return "example_skill"

    def getDescription(self):
        return "这是一个示例技能"

    def execute(self, params):
        print(f"执行示例技能，参数: {params}")
        return "示例技能执行成功"