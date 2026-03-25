#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简测试 - 诊断data:问题
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_minimal():
    print("="*50)
    print("极简测试 - 诊断data:问题")
    print("="*50)
    
    # 最基础的选项
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # 关键修复：使用旧的ChromeDriver协议
    # 这是解决Chrome 111+ 版本中data:问题的关键
    options.add_argument("--remote-debugging-port=9222")
    
    # 禁用一些可能导致问题的特性
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    
    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        print(f"\nChrome启动成功，版本: {driver.capabilities['browserVersion']}")
        print(f"ChromeDriver版本: {driver.capabilities['chrome']['chromedriverVersion'].split()[0]}")
        
        # 先检查当前URL
        print(f"\n初始URL: {driver.current_url}")
        
        # 方式1：直接访问
        print("\n尝试直接访问网站...")
        driver.get("https://www.zhipin.com/")
        time.sleep(3)
        print(f"get()后URL: {driver.current_url}")
        
        if "data:" in driver.current_url:
            print("检测到data:问题，尝试补救措施...")
            
            # 措施1：刷新
            driver.refresh()
            time.sleep(2)
            print(f"刷新后URL: {driver.current_url}")
            
            # 措施2：执行JS跳转
            if "data:" in driver.current_url:
                print("尝试JS跳转...")
                driver.execute_script("window.location.href = 'https://www.zhipin.com/';")
                time.sleep(3)
                print(f"JS跳转后URL: {driver.current_url}")
                
                # 措施3：再次调用get()
                if "data:" in driver.current_url:
                    print("再次调用get()...")
                    driver.get("https://www.zhipin.com/")
                    time.sleep(3)
                    print(f"第二次get()后URL: {driver.current_url}")
        
        print(f"\n最终URL: {driver.current_url}")
        print(f"页面标题: {driver.title}")
        
        if "zhipin" in driver.current_url or "BOSS直聘" in driver.title:
            print("\n✓ 网站加载成功！")
        else:
            print("\n✗ 网站未能正确加载")
            
        print("\n请在浏览器中完成登录操作")
        input("按回车键退出...")
        
    except Exception as e:
        print(f"\n出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n浏览器已关闭")

if __name__ == "__main__":
    test_minimal()
