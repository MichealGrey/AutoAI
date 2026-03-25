#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试登录修复 - 简化版本
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_login():
    """测试登录流程"""
    print("="*50)
    print("Boss直聘登录测试")
    print("="*50)
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-notifications")
    # 修复：禁用可能导致data:的特性
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-popup-blocking")
    
    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        wait = WebDriverWait(driver, 20)
        
        # 保存主窗口句柄
        main_window = driver.current_window_handle
        print(f"主窗口句柄: {main_window}")
        
        # 打开网站
        print("\n正在打开Boss直聘网站...")
        driver.get("https://www.zhipin.com/")
        time.sleep(3)
        
        # 打印当前URL
        print(f"当前URL: {driver.current_url}")
        print(f"当前窗口句柄: {driver.current_window_handle}")
        print(f"窗口数量: {len(driver.window_handles)}")
        
        print("\n请在浏览器中完成登录操作")
        print("注意：如果打开了新标签页，请关闭它，并确保在主标签页操作")
        print("登录完成后，请回到这里按回车键继续")
        
        # 等待用户输入
        input("\n按回车键确认已登录...")
        
        # 检查当前状态
        print("\n检查当前状态...")
        print(f"当前URL: {driver.current_url}")
        print(f"当前窗口句柄: {driver.current_window_handle}")
        print(f"窗口数量: {len(driver.window_handles)}")
        
        # 确保在主窗口
        if driver.current_window_handle != main_window:
            print("\n发现不在主窗口，切换回去...")
            # 关闭多余窗口
            for handle in driver.window_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(main_window)
            
        print(f"\n最终URL: {driver.current_url}")
        print(f"窗口数量: {len(driver.window_handles)}")
        
        # 验证是否登录成功（检查是否有用户相关元素）
        try:
            user_elements = driver.find_elements(
                By.CSS_SELECTOR, 
                "a.name, div.user-info, a[href*='user'], a[href*='resume']"
            )
            if user_elements:
                print("\n✓ 检测到已登录状态！")
                for elem in user_elements[:2]:
                    try:
                        print(f"  找到元素: {elem.text.strip()[:20]}")
                    except:
                        pass
            else:
                print("\n⚠ 未检测到登录状态，请手动确认")
        except:
            pass
            
        print("\n✓ 登录流程测试完成！")
        print("="*50)
        
        # 等待用户观察
        input("按回车键关闭浏览器...")
        
    except Exception as e:
        print(f"\n❌ 出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
                print("\n浏览器已关闭")
            except:
                pass

if __name__ == "__main__":
    test_login()
