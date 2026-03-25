#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Boss直聘职位搜索自动化 - 主运行脚本

使用方法:
    python run_boss_zhipin.py
"""

import sys
import os

# 添加技能路径
sys.path.insert(0, os.path.dirname(__file__))

from .trae.skills.boss_zhipin_job_search.boss_zhipin_skill import BossZhipinSkill

def main():
    """主函数"""
    print("=" * 60)
    print("Boss直聘职位搜索自动化工具")
    print("=" * 60)
    print()
    
    # 获取用户输入
    city = input("请输入目标城市（默认: 苏州）: ").strip() or "苏州"
    keyword = input("请输入搜索关键词（默认: 开发者）: ").strip() or "开发者"
    
    # 薪资输入
    while True:
        try:
            min_salary_input = input("请输入最低薪资（元，默认: 10000）: ").strip() or "10000"
            min_salary = int(min_salary_input)
            break
        except ValueError:
            print("请输入有效数字！")
    
    while True:
        try:
            max_salary_input = input("请输入最高薪资（元，默认: 13000）: ").strip() or "13000"
            max_salary = int(max_salary_input)
            break
        except ValueError:
            print("请输入有效数字！")
    
    while True:
        try:
            pages_input = input("请输入最多搜索页数（默认: 3）: ").strip() or "3"
            max_pages = int(pages_input)
            break
        except ValueError:
            print("请输入有效数字！")
            
    print()
    print("=" * 60)
    print("搜索配置确认:")
    print(f"  城市: {city}")
    print(f"  关键词: {keyword}")
    print(f"  薪资范围: {min_salary} - {max_salary} 元")
    print(f"  最多页数: {max_pages}")
    print("=" * 60)
    print()
    
    input("按回车键开始执行...")
    
    # 执行搜索
    skill = BossZhipinSkill(headless=False)
    result = skill.run(
        keyword=keyword,
        city=city,
        min_salary=min_salary,
        max_salary=max_salary,
        max_pages=max_pages
    )
    
    print()
    print("=" * 60)
    print("执行结果:")
    if result["success"]:
        print(f"✅ 成功! 收集到 {result['count']} 个职位")
        if result["file"]:
            print(f"📁 结果文件: {os.path.abspath(result['file'])}")
    else:
        print(f"❌ 失败: {result['message']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
