#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动Boss直聘自动化脚本
"""
import subprocess
import sys

print("=" * 60)
print("Boss直聘职位搜索自动化")
print("=" * 60)
print()
print("选择运行模式:")
print("1. 标准模式（推荐）- 搜索苏州10k-13k开发者职位")
print("2. 自定义模式 - 手动输入搜索条件")
print()

choice = input("请输入选项 (1/2，默认: 1): ").strip() or "1"

if choice == "1":
    # 标准模式
    print("\n启动标准模式...")
    subprocess.run([sys.executable, "boss_zhipin_automation_v2.py"], cwd=sys.path[0])
elif choice == "2":
    # 自定义模式
    print("\n启动自定义模式...")
    subprocess.run([sys.executable, "run_boss_zhipin.py"], cwd=sys.path[0])
else:
    print("无效选项，启动标准模式...")
    subprocess.run([sys.executable, "boss_zhipin_automation_v2.py"], cwd=sys.path[0])
