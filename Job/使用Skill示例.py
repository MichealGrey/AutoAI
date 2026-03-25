#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用示例：Boss直聘职位搜索Skill
"""

# 导入Skill
from .trae.skills.boss_zhipin_job_search import BossZhipinSkill

def main():
    """
    示例1：使用自定义参数搜索
    """
    print("=" * 60)
    print("Boss直聘职位搜索Skill使用示例")
    print("=" * 60)
    
    # 创建Skill实例
    # headless=True 表示后台运行（不显示浏览器窗口）
    # headless=False 表示显示浏览器窗口（默认，推荐首次使用）
    skill = BossZhipinSkill(headless=False)
    
    # 运行搜索
    result = skill.run(
        keyword="开发者",           # 搜索关键词
        city="苏州",                # 目标城市
        min_salary=10000,          # 最低薪资（元）
        max_salary=13000,          # 最高薪资（元）
        max_pages=3                # 最多搜索页数
    )
    
    # 输出结果
    if result["success"]:
        print(f"\n✅ 任务完成！")
        print(f"📊 收集到 {result['count']} 个职位")
        print(f"📁 Excel文件: {result['file']}")
    else:
        print(f"\n❌ 任务失败: {result['message']}")


def quick_demo():
    """
    示例2：快速开始模式
    """
    print("\n" + "=" * 60)
    print("快速开始模式")
    print("=" * 60)
    
    skill = BossZhipinSkill()
    
    # 使用快速开始方法（搜索苏州的开发者职位，薪资10k-13k）
    result = skill.quick_start(job_type="Python开发")
    
    if result["success"]:
        # 打印前3个职位信息
        print("\n📋 职位预览:")
        for i, job in enumerate(result["jobs"][:3], 1):
            print(f"\n{i}. {job['职位名称']} - {job['公司名称']}")
            print(f"   薪资: {job['薪资范围']}")
            print(f"   地点: {job['工作地点']}")


if __name__ == "__main__":
    # 选择运行哪个示例
    print("请选择运行模式:")
    print("1. 自定义参数搜索（示例1）")
    print("2. 快速开始模式（示例2）")
    
    choice = input("请输入选项 (1/2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        quick_demo()
    else:
        print("无效选项，运行默认模式（示例1）")
        main()
