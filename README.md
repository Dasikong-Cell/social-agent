# 吉吉朋友圈文案 🎉

> 一句话生成专业文案 · AI 驱动的朋友圈/小红书/短视频文案助手

## ✨ 功能特性

- 🎨 **多场景覆盖**：朋友圈、小红书、短视频标题、通知公告、节日祝福
- 🎭 **多种风格**：简约、文艺、搞笑、正式、可爱，一键切换
- 🤖 **大模型驱动**：支持阿里云百炼（通义千问 qwen-plus）、DeepSeek，可切换
- ⏰ **定时发布**：内置 APScheduler，定时生成并推送文案
- 🔒 **敏感词过滤**：18 条敏感词规则，自动拦截违规内容
- 📊 **调用计数**：后端自动记录每日生成次数
- 💬 **QQ 频道推送**：可对接 QQ 官方频道机器人一键推送
- 📱 **微信小程序**：现代化 UI，支持收藏/历史记录持久化

## 🏗️ 项目结构

```
social-agent/
├── main_server.py          # Flask 后端主服务（含 Web UI）
├── deepseek_agent.py       # 多模型 AI 客户端
├── qq_bot_service.py       # QQ 频道推送
├── scheduler_task.py       # 定时任务调度
├── requirements.txt        # Python 依赖
├── start.bat               # Windows 一键启动
├── build_exe.bat           # PyInstaller 打包脚本
├── sensitive_words.txt     # 敏感词库
├── .env                    # ⚠️ 请勿提交此文件（含 API Key）
│
├── utils/                  # 工具模块
│   ├── log_utils.py        # 日志（按日期）
│   ├── sensitive_filter.py # 敏感词过滤
│   └── count_utils.py      # 调用计数
│
└── mini_program/           # 微信小程序
    ├── app.json / app.js / app.wxss
    ├── project.config.json
    └── pages/index/
        ├── index.wxml      # 渐变 Hero + 卡片布局
        ├── index.wxss      # 主题色紫蓝渐变
        └── index.js        # 生成/收藏/历史逻辑
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone git@gitee.com:grand-minister-of-works/social-agent.git
cd social-agent
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入真实密钥：

```ini
# AI 提供商：dashscope | deepseek | siliconflow | ollama | zhipu
AI_PROVIDER=dashscope

# 阿里云百炼（推荐）
DASHSCOPE_API_KEY=sk-xxxxxx
DASHSCOPE_MODEL=qwen-plus
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DeepSeek（备用）
DEEPSEEK_API_KEY=sk-xxxxxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 服务端口
SERVER_PORT=8000

# QQ 频道机器人（可选）
QQ_BOT_APPID=
QQ_BOT_SECRET=
QQ_TARGET_CHANNEL_ID=
```

### 3. 启动后端

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python main_server.py
```

启动成功后：
- Web UI: http://127.0.0.1:8000
- 局域网访问: `http://<你的IP>:8000`

### 4. 打开小程序

用微信开发者工具导入 `mini_program/` 目录，AppID 填入你的真实小程序 AppID。

如需真机调试，在开发者工具 → 详情 → 本地设置中勾选：
- ✅ 不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书

## 📡 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/generate` | POST | 生成 AI 文案 |
| `/api/count` | GET | 获取今日调用次数 |
| `/api/send_qq` | POST | 推送到 QQ 频道 |
| `/api/task` | POST | 添加定时发布任务 |

### 请求示例

```bash
curl -X POST http://127.0.0.1:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"scene":"朋友圈","style":"文艺","require":"秋天的第一杯奶茶"}'
```

### 返回格式

```json
{
  "code": 0,
  "data": "秋风送爽，奶茶飘香🍂...",
  "todayCount": 42
}
```

## 🎨 界面预览

**Web 端**（内置 Web UI）：浏览器访问 `http://127.0.0.1:8000`

**小程序端**：
- 紫蓝渐变 Hero 顶栏
- 胶囊选择器（场景 / 风格 / 字数）
- 大胶囊生成按钮 + Loading 动画
- 结果卡片 + 四宫格操作栏（复制 / 收藏 / 推QQ / 定时）
- 历史记录本地持久化

## 🔒 安全说明

- `.env` 文件已在 `.gitignore` 中，**API Key 不会被上传**
- 敏感词库可自行扩充 `sensitive_words.txt`，每行一个词
- 生产环境部署建议使用 HTTPS + 反向代理（Nginx）

## 👥 贡献者

<table>
  <tr>
    <td align="center">
      <b>杨欣宇</b>
    </td>
  </tr>
</table>

## 📜 License

MIT License
