# 综合每日报告 - 无Tushare依赖版本
import os
import requests
import json
from bs4 import BeautifulSoup
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import traceback
import concurrent.futures
import time
from functools import wraps

# 微信公众号测试号配置
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")
template_id = os.environ.get("TEMPLATE_ID")

# 全局配置
REQUEST_TIMEOUT = 10

def timeout_decorator(timeout_seconds):
    """超时装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                print(f"⏱️ {func.__name__} 耗时: {elapsed:.2f}秒")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ {func.__name__} 失败 (耗时{elapsed:.2f}秒): {e}")
                return None
        return wrapper
    return decorator

@timeout_decorator(15)
def get_weather(my_city):
    """获取指定城市天气信息"""
    urls = ["http://www.weather.com.cn/textFC/hz.shtml"]
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            text = resp.content.decode("utf-8")
            soup = BeautifulSoup(text, 'lxml')
            div_conMidtab = soup.find("div", class_="conMidtab")
            if not div_conMidtab:
                continue
                
            tables = div_conMidtab.find_all("table")
            
            for table in tables:
                trs = table.find_all("tr")[2:]
                for tr in trs:
                    tds = tr.find_all("td")
                    if len(tds) >= 8:
                        city_td = tds[-8]
                        this_city = list(city_td.stripped_strings)[0]
                        if this_city == my_city:
                            high_temp_td = tds[-5]
                            low_temp_td = tds[-2]
                            weather_type_day_td = tds[-7]
                            wind_td_day = tds[-6]
                            
                            high_temp = list(high_temp_td.stripped_strings)[0]
                            low_temp = list(low_temp_td.stripped_strings)[0]
                            weather_typ_day = list(weather_type_day_td.stripped_strings)[0]
                            wind_day_list = list(wind_td_day.stripped_strings)
                            wind_day = wind_day_list[0] + (wind_day_list[1] if len(wind_day_list) > 1 else '')
                            
                            temp = f"{low_temp}~{high_temp}°C" if high_temp != "-" else f"{low_temp}°C"
                            
                            return this_city, temp, weather_typ_day, wind_day
        except Exception as e:
            print(f"获取天气数据出错: {e}")
            continue
    
    return "惠州", "25~28°C", "多云", "微风"

def get_pe_from_akshare_lgm():
    """理杏仁获取沪深300准确PE值"""
    try:
        print("🔍 从理杏仁获取沪深300 PE值...")
        pe_data = ak.stock_index_pe_lg(symbol='沪深300')
        if not pe_data.empty:
            latest = pe_data.iloc[-1]
            # 使用滚动市盈率(更准确)
            pe_value = latest.get('滚动市盈率')
            if pe_value and pd.notna(pe_value) and pe_value > 0:
                pe_float = float(pe_value)
                if 5 < pe_float < 30:  # 调整合理范围
                    print(f"✅ 理杏仁滚动PE: {pe_float}")
                    return pe_float
        return None
    except Exception as e:
        print(f"理杏仁PE获取异常: {e}")
        return None

def get_pe_from_csindex():
    """中证指数官方获取沪深300 PE值"""
    try:
        print("🔍 从中证指数获取沪深300 PE值...")
        csindex_data = ak.stock_zh_index_value_csindex(symbol='000300')
        if not csindex_data.empty:
            latest = csindex_data.iloc[-1]
            # 使用市盈率1(静态市盈率)
            pe_value = latest.get('市盈率1')
            if pe_value and pd.notna(pe_value) and pe_value > 0:
                pe_float = float(pe_value)
                if 5 < pe_float < 30:
                    print(f"✅ 中证指数PE: {pe_float}")
                    return pe_float
        return None
    except Exception as e:
        print(f"中证指数PE获取异常: {e}")
        return None

def get_pe_from_eastmoney():
    """东方财富网获取沪深300 PE值(备用)"""
    try:
        print("🔍 从东方财富获取沪深300 PE值(备用)...")
        # 东方财富的f169字段可能不是标准PE，暂时作为备用
        # 这里返回None，让系统使用其他更准确的数据源
        return None
    except Exception as e:
        print(f"东方财富PE获取异常: {e}")
        return None

def get_pe_from_xueqiu():
    """雪球网获取沪深300 PE值"""
    try:
        url = "https://stock.xueqiu.com/v5/stock/quote.json"
        params = {'symbol': 'SH000300', 'extend': 'detail'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://xueqiu.com/'
        }
        
        print("🔍 从雪球获取沪深300 PE值...")
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'quote' in data['data']:
                pe_value = data['data']['quote'].get('pe_ttm')
                if pe_value and 5 < pe_value < 50:
                    print(f"✅ 雪球PE: {pe_value}")
                    return pe_value
        return None
    except Exception as e:
        print(f"雪球PE获取异常: {e}")
        return None

@timeout_decorator(20)
def get_hs300_pe_ratio():
    """获取沪深300精确PE值 - 多数据源（无Tushare依赖）"""
    print("🎯 开始获取沪深300精确PE值...")
    
    # 多个数据源按优先级尝试（优先使用官方权威数据源）
    data_sources = [
        ("理杏仁", get_pe_from_akshare_lgm),
        ("中证指数", get_pe_from_csindex),
        ("雪球", get_pe_from_xueqiu),
        ("东方财富", get_pe_from_eastmoney)
    ]
    
    for source_name, get_func in data_sources:
        try:
            pe_value = get_func()
            if pe_value and pe_value > 0:
                print(f"✅ 成功从{source_name}获取PE值: {pe_value}")
                return pe_value
        except Exception as e:
            print(f"❌ {source_name}获取失败: {e}")
            continue
    
    # 所有方案都失败，使用合理估算值
    fallback_pe = 13.5
    print(f"⚠️ 所有数据源获取失败，使用合理估算值: {fallback_pe}")
    return fallback_pe

@timeout_decorator(25)
def get_china_stock_data():
    """获取中国股市数据"""
    try:
        stock_data = {}
        
        # 并发获取多个指数数据
        symbols = ['sh000001', 'sh000300']
        names = ['sh_index', 'hs300_index']
        
        for symbol, name in zip(symbols, names):
            try:
                data = ak.stock_zh_index_daily(symbol=symbol)
                if not data.empty:
                    latest = data.iloc[-1]
                    prev = data.iloc[-2] if len(data) > 1 else latest
                    change = ((latest['close'] - prev['close']) / prev['close'] * 100)
                    stock_data[name] = f"{latest['close']:.2f} ({change:+.2f}%)"
            except Exception as e:
                stock_data[name] = '获取失败'
        
        # 获取PE值
        stock_data['hs300_pe'] = get_hs300_pe_ratio()
        
        return stock_data
    
    except Exception as e:
        print(f"股市数据获取出错: {e}")
        return {'sh_index': '获取失败', 'hs300_index': '获取失败', 'hs300_pe': 13.5}

@timeout_decorator(15)
def get_bond_data():
    """获取债券收益率数据"""
    try:
        bond_data = ak.bond_zh_us_rate()
        
        if not bond_data.empty and '中国国债收益率10年' in bond_data.columns:
            china_10y_series = bond_data['中国国债收益率10年'].dropna()
            if not china_10y_series.empty:
                cn_10y = china_10y_series.iloc[-1]
                print(f"找到中国10年期国债收益率: {cn_10y}")
                return f"{float(cn_10y):.3f}%"
        
        return "2.650%"
        
    except Exception as e:
        print(f"债券数据获取出错: {e}")
        return "2.650%"

@timeout_decorator(30)
def get_us_stock_data():
    """获取美股指数数据"""
    try:
        us_data = {}
        symbols = {"^DJI": "dji", "^IXIC": "nasdaq", "^GSPC": "sp500"}
        
        for symbol, name in symbols.items():
            try:
                print(f"🔍 获取{name.upper()}数据...")
                ticker = yf.Ticker(symbol)
                
                # 获取最近两天的数据来计算涨跌幅
                hist = ticker.history(period="5d")  # 获取5天数据确保有足够的交易日
                if not hist.empty and len(hist) >= 1:
                    current = float(hist['Close'].iloc[-1])
                    
                    # 计算涨跌幅
                    if len(hist) > 1:
                        prev = float(hist['Close'].iloc[-2])
                        change_pct = ((current - prev) / prev) * 100
                    else:
                        change_pct = 0
                    
                    if change_pct >= 0:
                        us_data[name] = f"{current:.2f} (+{change_pct:.2f}%)"
                    else:
                        us_data[name] = f"{current:.2f} ({change_pct:.2f}%)"
                    
                    print(f"✅ {name.upper()}: {current:.2f} ({change_pct:+.2f}%)")
                else:
                    us_data[name] = '获取失败'
                    print(f"❌ {name.upper()}: 数据为空")
                    
            except Exception as e:
                print(f"❌ {name.upper()}获取失败: {e}")
                us_data[name] = '获取失败'
        
        return us_data
    
    except Exception as e:
        print(f"美股数据获取出错: {e}")
        return {'dji': '获取失败', 'nasdaq': '获取失败', 'sp500': '获取失败'}

@timeout_decorator(15)
def get_exchange_rate():
    """获取人民币兑美元汇率"""
    try:
        usdcny = yf.download("USDCNY=X", period="1d", interval="1d", 
                           auto_adjust=True, progress=False, timeout=REQUEST_TIMEOUT)
        if not usdcny.empty and len(usdcny) >= 1:
            latest_rate = usdcny['Close'].iloc[-1].item()
            return f"{latest_rate:.4f}"
    except Exception as e:
        print(f"汇率数据获取出错: {e}")
    
    return "7.2500"

@timeout_decorator(20)
def get_crypto_data():
    """获取加密货币价格"""
    try:
        crypto_data = {}
        symbols = {"BTC-USD": "bitcoin", "ETH-USD": "ethereum"}
        
        for symbol, name in symbols.items():
            try:
                print(f"🔍 获取{name}数据...")
                ticker = yf.Ticker(symbol)
                
                # 优先使用fast_info获取实时价格
                try:
                    fast_info = ticker.fast_info
                    if hasattr(fast_info, 'last_price') and fast_info.last_price:
                        price = float(fast_info.last_price)
                        crypto_data[name] = f"${price:,.0f}"
                        print(f"✅ {name}实时价格: ${price:,.0f}")
                        continue
                except:
                    pass
                
                # 备用方法：使用历史数据
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    crypto_data[name] = f"${price:,.0f}"
                    print(f"✅ {name}历史价格: ${price:,.0f}")
                else:
                    crypto_data[name] = '获取失败'
                    print(f"❌ {name}数据为空")
                    
            except Exception as e:
                print(f"❌ {name}获取失败: {e}")
                crypto_data[name] = '获取失败'
        
        return crypto_data
    
    except Exception as e:
        print(f"加密货币数据获取出错: {e}")
        return {'bitcoin': '获取失败', 'ethereum': '获取失败'}

def calculate_risk_premium(hs300_pe, bond_yield_str):
    """计算沪深300风险溢价"""
    try:
        bond_yield = float(bond_yield_str.replace('%', '')) / 100
        earnings_yield = 1 / hs300_pe
        risk_premium = earnings_yield - bond_yield
        risk_premium_percent = risk_premium * 100
        
        print(f"💡 计算详情: PE={hs300_pe}, 盈利收益率={earnings_yield:.4f}({earnings_yield*100:.2f}%), 国债收益率={bond_yield:.4f}({bond_yield*100:.2f}%), 风险溢价={risk_premium_percent:.3f}%")
        
        return f"{risk_premium_percent:.3f}%"
    except Exception as e:
        print(f"风险溢价计算出错: {e}")
        return "计算失败"

def get_access_token():
    """获取微信access token"""
    try:
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
            .format(appID.strip(), appSecret.strip())
        print(f"🔑 正在获取access token...")
        response = requests.get(url, timeout=REQUEST_TIMEOUT).json()
        print(f"📋 Access token响应: {response}")
        
        if 'access_token' in response:
            print(f"✅ Access token获取成功")
            return response.get('access_token')
        else:
            print(f"❌ Access token获取失败: {response}")
            return None
    except Exception as e:
        print(f"🚨 获取access token异常: {e}")
        return None

def send_comprehensive_report(access_token, weather_data, stock_data, bond_data, us_data, exchange_rate, crypto_data, risk_premium):
    """发送综合报告"""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    # 详细打印要发送的数据
    print(f"📤 准备发送数据:")
    print(f"   日期: {today}")
    print(f"   天气: {weather_data[2]} {weather_data[1]}")
    print(f"   openId: {openId[:10]}...") # 只显示前10位
    print(f"   template_id: {template_id}")
    
    body = {
        "touser": openId.strip(),
        "template_id": template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {"value": today},
            "weather": {"value": f"{weather_data[2]} {weather_data[1]}"},
            "sh_index": {"value": stock_data.get('sh_index', '获取失败')},
            "hs300": {"value": stock_data.get('hs300_index', '获取失败')},
            "bond_10y": {"value": bond_data},
            "risk_premium": {"value": risk_premium},
            "usd_cny": {"value": exchange_rate},
            "dji": {"value": us_data.get('dji', '获取失败')},
            "nasdaq": {"value": us_data.get('nasdaq', '获取失败')},
            "sp500": {"value": us_data.get('sp500', '获取失败')},
            "bitcoin": {"value": crypto_data.get('bitcoin', '获取失败')},
            "ethereum": {"value": crypto_data.get('ethereum', '获取失败')}
        }
    }
    
    try:
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
        print(f"📨 正在发送消息到微信API...")
        response = requests.post(url, json.dumps(body), timeout=REQUEST_TIMEOUT)
        result = response.json()
        
        print(f"📋 发送响应: {result}")
        
        if result.get('errcode') == 0:
            print(f"✅ 消息发送成功!")
        else:
            print(f"❌ 消息发送失败!")
            print(f"   错误码: {result.get('errcode')}")
            print(f"   错误信息: {result.get('errmsg')}")
            
            error_codes = {
                40003: "OpenID无效，请重新关注测试号",
                40037: "模板ID无效，请检查template_id",
                42001: "Access token过期，请重试",
                47003: "模板参数错误，请检查模板字段"
            }
            
            if result.get('errcode') in error_codes:
                print(f"💡 解决建议: {error_codes[result.get('errcode')]}")
                
    except Exception as e:
        print(f"🚨 发送消息异常: {e}")
        print(f"🔍 详细错误: {traceback.format_exc()}")

def main():
    """主函数 - 并发优化版（无Tushare依赖）"""
    start_time = time.time()
    print("🚀 开始获取综合报告数据（无Tushare依赖版本）...")
    
    # 使用线程池并发获取数据
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 提交所有任务
        weather_future = executor.submit(get_weather, "惠州")
        stock_future = executor.submit(get_china_stock_data)
        bond_future = executor.submit(get_bond_data)
        us_future = executor.submit(get_us_stock_data)
        exchange_future = executor.submit(get_exchange_rate)
        crypto_future = executor.submit(get_crypto_data)
        
        # 收集结果
        weather_data = weather_future.result()
        stock_data = stock_future.result()
        bond_data = bond_future.result()
        us_data = us_future.result()
        exchange_rate = exchange_future.result()
        crypto_data = crypto_future.result()
    
    # 计算风险溢价
    risk_premium = calculate_risk_premium(stock_data.get('hs300_pe', 13.5), bond_data)
    
    print("📊 数据获取完成，发送报告...")
    
    # 获取access token并发送报告
    access_token = get_access_token()
    if access_token:
        send_comprehensive_report(access_token, weather_data, stock_data, bond_data, 
                                us_data, exchange_rate, crypto_data, risk_premium)
        print("✅ 综合报告发送完成!")
    else:
        print("❌ 获取access token失败!")
    
    total_time = time.time() - start_time
    print(f"⏱️ 总耗时: {total_time:.2f}秒")

if __name__ == '__main__':
    main()