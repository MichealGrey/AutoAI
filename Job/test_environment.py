"""
测试环境是否能正常运行自动化脚本
"""
import sys
import importlib

def test_imports():
    """测试依赖包是否能正常导入"""
    required_packages = [
        'selenium',
        'pandas',
        'openpyxl',
        'webdriver_manager',
        'pyautogui'
    ]
    
    print("测试依赖包导入...")
    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
            print(f"✓ {pkg} 导入成功")
        except ImportError as e:
            print(f"✗ {pkg} 导入失败: {e}")
            return False
    return True

def test_selenium():
    """测试Selenium能否启动浏览器"""
    print("\n测试Selenium浏览器启动...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")  # 无头模式
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # 访问一个简单的网页测试
        driver.get("https://www.baidu.com")
        title = driver.title
        driver.quit()
        
        if "百度" in title:
            print("✓ Selenium 浏览器测试成功")
            return True
        else:
            print("✗ Selenium 页面访问异常")
            return False
            
    except Exception as e:
        print(f"✗ Selenium 测试失败: {e}")
        return False

def test_pandas():
    """测试Pandas和Excel导出"""
    print("\n测试Pandas和Excel导出...")
    try:
        import pandas as pd
        
        # 创建测试数据
        test_data = [
            {"职位名称": "测试工程师", "公司名称": "测试公司", "薪资": "10-15K", "工作地点": "苏州"},
            {"职位名称": "Python开发", "公司名称": "科技公司", "薪资": "12-18K", "工作地点": "苏州"}
        ]
        
        df = pd.DataFrame(test_data)
        df.to_excel("test_output.xlsx", index=False, engine="openpyxl")
        print("✓ Pandas Excel 导出成功")
        return True
    except Exception as e:
        print(f"✗ Pandas Excel 导出失败: {e}")
        return False

def main():
    print("=" * 50)
    print("环境测试开始")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_selenium())
    results.append(test_pandas())
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    if all(results):
        print("✓ 所有测试通过，环境准备就绪！")
        print("\n你现在可以运行 boss_zhipin_automation.py 来执行自动化任务")
        print("注意：运行时需要手动登录Boss直聘账号")
    else:
        print("✗ 部分测试失败，请检查环境配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
