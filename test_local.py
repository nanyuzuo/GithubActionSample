#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试脚本 - 用于调试综合日报功能
使用方法：
1. 设置环境变量
2. 运行 python test_local.py
"""

import os
import sys

def check_environment():
    """检查环境变量配置"""
    required_vars = {
        'APP_ID': '微信测试号AppID',
        'APP_SECRET': '微信测试号AppSecret', 
        'OPEN_ID': '微信接收者OpenID',
        'TEMPLATE_ID': '微信模板ID',
        'HEFENG_KEY': '和风天气API Key',
        'TUSHARE_TOKEN': 'Tushare Token (可选)'
    }
    
    optional_vars = {
        'HEFENG_HOST': '和风天气API主机 (默认: devapi.qweather.com)',
        'HEFENG_PROJECT_ID': '和风天气项目ID (可选)'
    }
    
    print("🔍 环境变量检查:")
    missing_vars = []
    
    for var, desc in required_vars.items():
        value = os.environ.get(var)
        if value:
            # 只显示前几位字符，保护隐私
            masked_value = value[:6] + "..." if len(value) > 6 else value
            print(f"  ✅ {var}: {masked_value} ({desc})")
        else:
            print(f"  ❌ {var}: 未设置 ({desc})")
            if var != 'TUSHARE_TOKEN':  # Tushare是可选的
                missing_vars.append(var)
    
    # 检查可选变量
    print(f"\n🔍 可选环境变量:")
    for var, desc in optional_vars.items():
        value = os.environ.get(var)
        if value:
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {var}: {masked_value} ({desc})")
        else:
            print(f"  ➖ {var}: 未设置 ({desc})")
    
    if missing_vars:
        print(f"\n❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("\n请设置环境变量，例如:")
        for var in missing_vars:
            print(f'export {var}="your_{var.lower()}_value"')
        print("\n💡 和风天气API说明:")
        print("  1. 注册和风天气开发者账户: https://dev.qweather.com/")
        print("  2. 获取API Key后设置 HEFENG_KEY")
        print("  3. 如果使用专用API Host，请设置 HEFENG_HOST")
        print("  4. 免费版默认使用: devapi.qweather.com")
        return False
    
    print("\n✅ 环境变量检查通过!")
    return True

def test_weather_only():
    """只测试天气获取功能"""
    try:
        from comprehensive_report import get_weather
        print("\n🌤️ 测试和风天气API...")
        weather_data = get_weather("惠州")
        print(f"✅ 天气数据获取成功: {weather_data}")
        return True
    except Exception as e:
        print(f"❌ 天气数据获取失败: {e}")
        return False

def test_wechat_only():
    """只测试微信推送功能"""
    try:
        from comprehensive_report import get_access_token
        print("\n🔑 测试微信Access Token获取...")
        access_token = get_access_token()
        if access_token:
            print(f"✅ Access Token获取成功: {access_token[:20]}...")
            return True
        else:
            print("❌ Access Token获取失败")
            return False
    except Exception as e:
        print(f"❌ 微信测试失败: {e}")
        return False

def test_pe_only():
    """只测试PE值获取功能"""
    try:
        from comprehensive_report import get_hs300_pe_ratio
        print("\n📊 测试沪深300 PE值获取...")
        pe_value = get_hs300_pe_ratio()
        print(f"✅ PE值获取成功: {pe_value}")
        return True
    except Exception as e:
        print(f"❌ PE值获取失败: {e}")
        return False

def test_bond_only():
    """只测试中国10年期国债收益率获取功能"""
    try:
        from comprehensive_report import get_bond_data
        print("\n📊 测试中国10年期国债收益率获取...")
        bond_yield = get_bond_data()
        print(f"✅ 债券收益率获取成功: {bond_yield}")
        
        # 解析数值并提供建议
        try:
            yield_value = float(bond_yield.replace('%', ''))
            if yield_value == 1.799:
                print("💡 数据与主流金融软件一致！")
            elif 1.7 < yield_value < 1.9:
                print(f"💡 数据在合理范围内，与期望值1.799%较接近")
            else:
                print(f"⚠️ 数据({yield_value}%)与期望值(1.799%)差异较大")
        except:
            pass
            
        return True
    except Exception as e:
        print(f"❌ 债券收益率获取失败: {e}")
        return False

def run_full_test():
    """运行完整测试"""
    try:
        print("\n🚀 开始完整功能测试...")
        from comprehensive_report import main
        main()
        print("✅ 完整测试执行完成!")
        return True
    except Exception as e:
        print(f"❌ 完整测试失败: {e}")
        import traceback
        print(f"🔍 详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 综合日报本地测试工具")
    print("=" * 60)
    
    # 1. 检查环境变量
    if not check_environment():
        return 1
    
    # 2. 提供测试选项
    print("\n请选择测试模式:")
    print("1. 只测试天气获取")
    print("2. 只测试微信推送") 
    print("3. 只测试PE值获取")
    print("4. 只测试债券收益率获取")
    print("5. 运行完整测试")
    print("6. 退出")
    
    try:
        choice = input("\n请输入选择 (1-6): ").strip()
        
        if choice == '1':
            success = test_weather_only()
        elif choice == '2':
            success = test_wechat_only()
        elif choice == '3':
            success = test_pe_only()
        elif choice == '4':
            success = test_bond_only()
        elif choice == '5':
            success = run_full_test()
        elif choice == '6':
            print("👋 测试结束")
            return 0
        else:
            print("❌ 无效选择")
            return 1
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
        return 0
    except Exception as e:
        print(f"\n❌ 测试执行异常: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())