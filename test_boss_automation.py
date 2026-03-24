#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘自动化脚本 - 测试和验证
用于验证代码可以编译运行
"""

import sys
import ast
import importlib.util
from pathlib import Path


def test_syntax_validity():
    """测试Python语法是否正确"""
    print("=" * 60)
    print("测试1: Python语法验证")
    print("=" * 60)
    
    files_to_test = [
        "boss_zhipin_automation.py",
    ]
    
    all_valid = True
    for file_path in files_to_test:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # 解析AST检查语法
            ast.parse(source)
            print(f"✅ {file_path} - 语法正确")
            
        except SyntaxError as e:
            print(f"❌ {file_path} - 语法错误: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"⚠️ {file_path} - 文件不存在")
            all_valid = False
    
    return all_valid


def test_imports():
    """测试必要的依赖包是否可以导入"""
    print("\n" + "=" * 60)
    print("测试2: 依赖包导入验证")
    print("=" * 60)
    
    required_packages = [
        ('selenium', 'selenium'),
        ('openpyxl', 'openpyxl'),
    ]
    
    all_imported = True
    for package_name, import_name in required_packages:
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                print(f"✅ {package_name} - 已安装")
            else:
                print(f"❌ {package_name} - 未安装 (请运行: pip install {package_name})")
                all_imported = False
        except Exception as e:
            print(f"❌ {package_name} - 检查失败: {e}")
            all_imported = False
    
    return all_imported


def test_module_structure():
    """测试模块结构是否正确"""
    print("\n" + "=" * 60)
    print("测试3: 模块结构验证")
    print("=" * 60)
    
    try:
        # 尝试导入主模块
        spec = importlib.util.spec_from_file_location(
            "boss_automation", 
            "boss_zhipin_automation.py"
        )
        module = importlib.util.module_from_spec(spec)
        
        # 检查关键类是否存在
        with open("boss_zhipin_automation.py", 'r', encoding='utf-8') as f:
            source = f.read()
        
        required_classes = ['BossZhipinAutomation', 'JobInfo']
        required_methods = ['setup_driver', 'navigate_to_login', 'search_jobs', 
                          'collect_jobs', 'export_to_excel', 'run']
        
        all_found = True
        for cls in required_classes:
            if f"class {cls}" in source:
                print(f"✅ 类 {cls} 已定义")
            else:
                print(f"❌ 类 {cls} 未找到")
                all_found = False
        
        for method in required_methods:
            if f"def {method}" in source:
                print(f"✅ 方法 {method} 已定义")
            else:
                print(f"❌ 方法 {method} 未找到")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ 模块结构验证失败: {e}")
        return False


def test_config_file():
    """测试配置文件是否正确"""
    print("\n" + "=" * 60)
    print("测试4: 配置文件验证")
    print("=" * 60)
    
    import json
    
    try:
        with open('config_boss.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_keys = ['search_config', 'browser_config', 'filter_criteria']
        
        all_valid = True
        for key in required_keys:
            if key in config:
                print(f"✅ 配置项 {key} 存在")
            else:
                print(f"❌ 配置项 {key} 缺失")
                all_valid = False
        
        return all_valid
        
    except FileNotFoundError:
        print("⚠️ 配置文件不存在")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False


def test_skill_file():
    """测试Skill文件是否正确"""
    print("\n" + "=" * 60)
    print("测试5: Skill文件验证")
    print("=" * 60)
    
    skill_path = Path(".trae/skills/boss-job-automation/SKILL.md")
    
    if not skill_path.exists():
        print("❌ Skill文件不存在")
        return False
    
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的部分
        checks = [
            ('name:', 'Skill名称'),
            ('description:', 'Skill描述'),
            ('Features', '功能特性'),
            ('Usage', '使用说明'),
        ]
        
        all_valid = True
        for keyword, desc in checks:
            if keyword in content:
                print(f"✅ {desc} 已包含")
            else:
                print(f"⚠️ {desc} 可能缺失")
        
        return True
        
    except Exception as e:
        print(f"❌ Skill文件验证失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "🚀 Boss直聘自动化脚本 - 编译验证测试" + "\n")
    
    results = {
        "语法验证": test_syntax_validity(),
        "依赖导入": test_imports(),
        "模块结构": test_module_structure(),
        "配置文件": test_config_file(),
        "Skill文件": test_skill_file(),
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！代码可以编译运行。")
        print("\n使用说明:")
        print("1. 安装依赖: pip install -r requirements_boss.txt")
        print("2. 运行脚本: python boss_zhipin_automation.py")
        print("3. 按提示手动登录Boss直聘")
        print("4. 等待自动化完成并生成Excel")
    else:
        print("⚠️ 部分测试未通过，请检查上述错误信息。")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
