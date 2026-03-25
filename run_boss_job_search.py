#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘职位搜索 - 运行脚本
使用Skill方式运行自动化职位搜索
"""

import sys
import json
import argparse
from boss_zhipin_automation import BossZhipinAutomation


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Boss直聘自动化职位搜索工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用默认配置运行
  python run_boss_job_search.py
  
  # 指定城市和关键词
  python run_boss_job_search.py --city 上海 --keyword Python开发
  
  # 指定薪资范围和公司规模
  python run_boss_job_search.py --salary "15-25K" --size "500-1000人"
  
  # 从配置文件加载
  python run_boss_job_search.py --config config_boss.json
        """
    )
    
    parser.add_argument('--city', type=str, default='苏州',
                       help='目标城市 (默认: 苏州)')
    parser.add_argument('--keyword', type=str, default='开发者',
                       help='搜索关键词 (默认: 开发者)')
    parser.add_argument('--salary', type=str, default='10-13K',
                       help='薪资范围 (默认: 10-13K)')
    parser.add_argument('--size', type=str, default='100-10000人',
                       help='公司规模 (默认: 100-10000人)')
    parser.add_argument('--pages', type=int, default=3,
                       help='最大翻页数 (默认: 3)')
    parser.add_argument('--headless', action='store_true',
                       help='无头模式运行（不显示浏览器窗口）')
    parser.add_argument('--config', type=str,
                       help='从JSON配置文件加载设置')
    
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """从配置文件加载设置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        sys.exit(1)


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           Boss直聘自动化职位搜索工具                         ║
║           Boss Zhipin Job Automation Tool                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_config(city: str, keyword: str, salary: str, size: str, pages: int):
    """打印当前配置"""
    print("📋 搜索配置:")
    print(f"   城市: {city}")
    print(f"   关键词: {keyword}")
    print(f"   薪资范围: {salary}")
    print(f"   公司规模: {size}")
    print(f"   最大页数: {pages}")
    print()


def main():
    """主函数"""
    print_banner()
    
    # 解析参数
    args = parse_arguments()
    
    # 如果指定了配置文件，从配置文件加载
    if args.config:
        print(f"📂 正在加载配置文件: {args.config}")
        config = load_config(args.config)
        search_config = config.get('search_config', {})
        
        city = search_config.get('city', '苏州')
        keyword = search_config.get('keyword', '开发者')
        salary = search_config.get('salary_range', '10-13K')
        size = search_config.get('company_size', '100-10000人')
        pages = search_config.get('max_pages', 3)
    else:
        city = args.city
        keyword = args.keyword
        salary = args.salary
        size = args.size
        pages = args.pages
    
    # 打印配置
    print_config(city, keyword, salary, size, pages)
    
    # 创建自动化实例
    automation = BossZhipinAutomation(headless=args.headless)
    
    try:
        print("🚀 启动自动化流程...")
        print("⚠️  请在浏览器打开后手动完成登录和验证\n")
        
        # 运行自动化流程
        excel_file = automation.run(
            city=city,
            keyword=keyword,
            salary_range=salary,
            company_size=size,
            max_pages=pages
        )
        
        if excel_file:
            print("\n" + "=" * 60)
            print("✅ 任务完成！")
            print("=" * 60)
            print(f"📊 Excel文件: {excel_file}")
            print(f"📋 共收集 {len(automation.jobs_collected)} 个职位")
            print("\n📁 职位列表:")
            for idx, job in enumerate(automation.jobs_collected, 1):
                print(f"   {idx}. {job.job_title} | {job.company_name} | {job.salary}")
            print("=" * 60)
        else:
            print("\n⚠️ 未收集到任何职位信息")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        automation.close()
        print("\n👋 程序已退出")


if __name__ == "__main__":
    main()
