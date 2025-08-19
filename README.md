# Github Action功能样例

原理：使用Github Action功能，运行python程序，实现无服务器的免费任务，包括：
- 🌤️ 天气推送
- 💰 签到薅羊毛
- ❤️ 爱心动画构建
- 📊 **综合每日金融报告（NEW!）**

### 视频教程

https://www.bilibili.com/video/BV11e411i7Xx/

作者 **技术爬爬虾** 全网同名，转载请注明作者

## Part1 构建画爱心为可执行程序
Fork本项目

构架Windows 可执行程序:
Actions-->画爱心Windows版-->run work flow-->结束后查看结果
-->Artifacts-->下载love_heart

构架Ubuntu 可执行程序:
Actions-->画爱心Ubuntu版-->run work flow-->结束后查看结果
-->Artifacts-->下载love_heart

构架MacOS 可执行程序:
Actions-->画爱心MacOS版-->run work flow-->结束后查看结果
-->Artifacts-->下载love_heart


## Part2 天气推送

### 申请公众号测试账户

使用微信扫码即可
https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login

进入页面以后我们来获取到这四个值 
#### appID  appSecret openId template_id
![image](https://github.com/tech-shrimp/FreeWechatPush/assets/154193368/bdb27abd-39cb-4e77-9b89-299afabc7330)

想让谁收消息，谁就用微信扫二维码，然后出现在用户列表，获取微信号（openId）
 ![image](https://github.com/tech-shrimp/FreeWechatPush/assets/154193368/1327c6f5-5c92-4310-a10b-6f2956c1dd75)

新增测试模板获得  template_id（模板ID）
 ![image](https://github.com/tech-shrimp/FreeWechatPush/assets/154193368/ec689f4d-6c0b-44c4-915a-6fd7ada17028)

模板标题随便填，模板内容如下，可以根据需求自己定制

模板内容：
```copy
今天：{{date.DATA}} 
地区：{{region.DATA}} 
天气：{{weather.DATA}} 
气温：{{temp.DATA}} 
风向：{{wind_dir.DATA}} 
对你说的话：{{today_note.DATA}}
```

### 项目配置 
Fork本项目
进入自己项目的Settings  ----> Secrets and variables ---> Actions --> New repository secret
配置好以下四个值（见上文）

<img width="590" alt="image" src="https://github.com/tech-shrimp/GithubActionSample/assets/154193368/9e6b799d-9230-4d3e-8966-6c6f49e9b89f">

进入自己项目的Action  ----> 天气预报推送 ---> weather_report.yml --> 修改cron表达式的执行时间
<img width="503" alt="image" src="https://github.com/tech-shrimp/GithubActionSample/assets/154193368/badcc0fa-def5-428f-9238-fa6b549baefc">

## Part3 签到薅羊毛
Fork本项目
网页上打开：www.jd.com/ 再按F12打开控制台，再点击切换模式，切换到手机模式，刷新一下页面。如图所示
![image](https://github.com/tech-shrimp/GithubActionSample/assets/154193368/44d01795-8c1e-4a56-bb0e-a36f74062dcb)
在网络->m.jd.com找到Cookie

<img width="935" alt="image" src="https://github.com/tech-shrimp/GithubActionSample/assets/154193368/97139add-a410-4e73-82d3-055c8136ed57">

将其填入  Settings  ----> Secrets and variables ---> Actions --> New repository secret -->新增JD_COOKIE
<img width="685" alt="image" src="https://github.com/tech-shrimp/GithubActionSample/assets/154193368/e28ee156-642a-4c25-94ff-d42af072aa15">

进入自己项目的Action  ----> 签到薅羊毛 ---> daily_sign.yml --> 修改cron表达式的执行时间

---

## Part4 📊 每日金融报告 (NEW!)

### 🚀 功能介绍

全新的综合每日报告功能，整合了天气信息和完整的金融市场数据，每天早上7点（北京时间）自动推送：

#### 📋 报告内容包括：

**🌤️ 天气信息**
- 当日天气情况（默认广东惠州，可以自行在源码修改）

**📈 中国股市数据**

- 上证综合指数及其涨跌幅  
- 沪深300指数及其涨跌幅
- 沪深300风险溢价（自动计算）

**💰 债券及汇率市场**

- 中国10年期国债收益率及变化

- 沪深300风险溢价（自动计算）

- 人民币兑美元汇率

  ### 💡 风险溢价说明

  风险溢价 = 股票盈利收益率 - 无风险利率

  - **盈利收益率** = 1 / 沪深300市盈率
  - **无风险利率** = 10年期国债收益率
  - **数值含义**: 正值越大表示股票相对债券越有吸引力

  该指标帮助判断当前股市的投资价值和风险水平。

**🌍 国际市场**

- 道琼斯工业指数及其涨跌幅
- 纳斯达克综合指数及其涨跌幅
- 标普500指数及其涨跌幅

**₿ 加密货币**
- 比特币实时价格
- 以太坊实时价格

### ⚡ 技术特点

- **权威数据源**: 
  - 中国数据：AKShare 
  - 国际数据：Yahoo Finance

### 📱 微信模板配置

#### 需要在微信公众号测试平台创建新的消息模板

模板内容：

```
📅{{date.DATA}}
🌤️惠州天气：{{weather.DATA}}
📈A股市场（前一交易日）
上证指数：{{sh_index.DATA}}
沪深300：{{hs300.DATA}}
💰债券汇率
10年期国债：{{bond_10y.DATA}}
风险溢价：{{risk_premium.DATA}}
USD/CNY：{{usd_cny.DATA}}
🌍美股指数（前一交易日）
道琼斯：{{dji.DATA}}
纳斯达克：{{nasdaq.DATA}}
标普500：{{sp500.DATA}}
₿加密货币（实时）
比特币：{{bitcoin.DATA}}
以太坊：{{ethereum.DATA}}
```

### ⚙️ 环境变量配置

在 **Settings** → **Secrets and variables** → **Actions** 中添加：

**必需变量：**
- `APP_ID`: 微信测试号AppID
- `APP_SECRET`: 微信测试号AppSecret
- `OPEN_ID`: 接收消息的微信OpenID
- `TEMPLATE_ID`: 新创建的综合报告模板ID

### 🔧 启用步骤

1. **Fork本项目**
2. **配置微信模板**（见上方模板内容）
3. **设置环境变量**（见上方配置说明）
4. **启用GitHub Action**：
   - 进入 Actions 页面
   - 启用 "综合每日报告推送" 工作流
   - 可手动运行测试

### 📊 执行时间

- **运行时间**: 每天北京时间早上7:00自动执行
- **数据更新**: 
  - 股市数据：前一交易日收盘数据
  - 加密货币：7点实时价格
  - 汇率：实时汇率

### 🛠️ 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export APP_ID="your_app_id"
export APP_SECRET="your_app_secret"
export OPEN_ID="your_open_id" 
export TEMPLATE_ID="your_template_id"

# 测试功能
python comprehensive_report.py
```



---
