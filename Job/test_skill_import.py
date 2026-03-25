"""
测试Skill是否能正常导入
"""
import sys
import os

# 将Skill目录添加到Python路径
skill_path = os.path.join(os.path.dirname(__file__), '.trae', 'skills')
sys.path.insert(0, skill_path)

print("测试Skill导入...")
print(f"Skill路径: {skill_path}")

try:
    from boss_zhipin_job_search import BossZhipinSkill
    print("✓ Skill 模块导入成功")
    
    # 创建实例测试
    skill = BossZhipinSkill()
    print("✓ Skill 实例创建成功")
    
    print("\n✅ Skill 准备就绪！")
    print("\n使用方法:")
    print("1. 运行 'python boss_zhipin_automation_v2.py' 直接使用自动化脚本")
    print("2. 或参考 '使用Skill示例.py' 使用Skill接口")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ 创建实例失败: {e}")
    sys.exit(1)
