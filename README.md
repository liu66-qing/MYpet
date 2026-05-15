# MYpet - AI桌面宠物

> 让AI陪伴你的每一次编程。一个开源的桌面虚拟宠物，实时显示AI工作状态，支持自定义形象和多平台AI接入。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 功能特性

- **AI状态实时可视化** - 宠物动画随AI状态变化（思考、写代码、搜索等）
- **自定义宠物形象** - PNG序列帧动画，无需写代码即可创建新皮肤
- **多AI平台支持** - 适配器模式，支持OpenAI/Claude/Ollama及任何兼容API
- **丰富交互** - 拖拽、双击对话、右键菜单、系统托盘
- **轻量低占用** - 纯Python实现，内存占用低
- **插件化架构** - 事件总线解耦，易于扩展

## 快速开始

### 环境要求

- Python 3.10+
- Windows 10+ / macOS / Linux

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/liu66-qing/MYpet.git
cd MYpet

# 2. 安装依赖
pip install -r requirements.txt

# 3. 生成默认精灵图（首次运行需要）
python generate_sprites.py

# 4. 配置AI（可选，不配置也能运行）
# 编辑 config.yaml，填入你的API Key
```

### 一键启动

```bash
python run.py
```

启动后，桌面右下角会出现一只像素小猫。你可以：
- **拖拽** - 按住左键移动宠物位置
- **双击** - 打开AI对话窗口
- **右键** - 打开菜单（切换状态、打开对话、退出）
- **托盘图标** - 右键托盘图标可显示/隐藏宠物

## 配置说明

编辑项目根目录的 `config.yaml`：

```yaml
ai:
  provider: "openai"          # AI服务商：openai / claude / ollama
  api_key: "sk-xxx"          # 你的API Key
  base_url: "https://api.openai.com/v1"  # API地址（支持自定义）
  model: "gpt-4o"            # 模型名称

pet:
  sprite_set: "default"       # 使用的形象包
  window:
    size: [128, 128]          # 宠物窗口大小
    start_position: "bottom_right"  # 初始位置
    always_on_top: true       # 是否置顶
```

### 支持的AI平台

| 平台 | provider值 | 说明 |
|------|-----------|------|
| OpenAI | `openai` | GPT-4o等，也支持任何OpenAI兼容API |
| Claude | `claude` | Anthropic Claude系列 |
| Ollama | `ollama` | 本地模型，无需API Key |
| 自定义 | `custom` | 继承AIProvider实现自己的接入 |

**使用国内中转API**：只需修改 `base_url` 为中转地址即可。

## 自定义形象

### 创建新皮肤

1. 在 `assets/sprites/` 下创建新文件夹（如 `my_cat`）
2. 按以下结构放入PNG序列帧：

```
my_cat/
├── manifest.json      # 形象配置文件
├── idle/              # 待机动画
│   ├── idle_001.png
│   ├── idle_002.png
│   └── ...
├── thinking/          # 思考动画
├── coding/            # 写代码动画
├── searching/         # 搜索动画
├── happy/             # 开心动画
└── sleeping/          # 睡觉动画
```

3. 编写 `manifest.json`：

```json
{
  "name": "我的小猫",
  "author": "你的名字",
  "version": "1.0.0",
  "size": [128, 128],
  "animations": {
    "idle": {
      "frames": "idle/idle_{:03d}.png",
      "frame_count": 4,
      "fps": 4,
      "loop": true
    }
  }
}
```

4. 修改 `config.yaml` 中 `pet.sprite_set` 为你的文件夹名

### 动画状态说明

| 状态 | 触发条件 | 建议帧数 |
|------|---------|---------|
| idle | AI空闲 | 4-8帧 |
| thinking | AI思考中 | 4-12帧 |
| coding | AI生成代码 | 4-8帧 |
| searching | AI搜索/调用工具 | 4-8帧 |
| happy | 交互反馈 | 4-10帧 |
| sleeping | 长时间无活动 | 4帧 |

## 项目架构

```
MYpet/
├── run.py                  # 启动入口
├── config.yaml             # 配置文件
├── src/
│   ├── app.py              # 应用初始化
│   ├── core/               # 核心层
│   │   ├── pet_window.py   # 透明悬浮窗口
│   │   ├── state_machine.py # 状态机
│   │   ├── event_bus.py    # 事件总线
│   │   └── config_manager.py # 配置管理
│   ├── ai/                 # AI接入层
│   │   ├── base_provider.py # Provider抽象基类
│   │   ├── openai_provider.py # OpenAI实现
│   │   └── status_monitor.py # 状态监控
│   ├── animation/          # 动画系统
│   │   ├── sprite_engine.py # 帧动画引擎
│   │   └── sprite_loader.py # 资源加载
│   └── interaction/        # 交互系统
│       ├── chat_bubble.py  # 对话气泡
│       └── chat_window.py  # 聊天窗口
├── assets/sprites/         # 精灵图资源
└── generate_sprites.py     # 默认精灵图生成器
```

### 架构设计亮点

- **事件总线（EventBus）** - 模块间零直接依赖，通过发布/订阅模式通信
- **适配器模式** - 新增AI平台只需实现 `AIProvider` 接口
- **数据驱动动画** - `manifest.json` 定义动画配置，自定义形象无需写代码
- **状态机驱动** - 宠物行为由有限状态机统一管理

## 开发指南

### 添加新的AI Provider

```python
from src.ai.base_provider import AIProvider, ChatMessage, AIStatusUpdate

class MyProvider(AIProvider):
    async def send_message(self, message: str, history: list[ChatMessage]) -> str:
        # 实现消息发送
        ...

    async def stream_message(self, message, history):
        # 实现流式输出
        ...

    def get_status(self) -> AIStatusUpdate:
        # 返回当前AI状态
        ...

    @property
    def name(self) -> str:
        return "MyAI"

    @property
    def is_connected(self) -> bool:
        return True
```

## 技术栈

- **Python 3.10+** - 主语言
- **PyQt6** - GUI框架，支持透明窗口和高级绘图
- **asyncio** - 异步AI通信
- **OpenAI SDK** - AI接口调用
- **YAML** - 配置文件格式

## 许可证

MIT License
