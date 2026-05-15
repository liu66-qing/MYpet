# MYpet - AI桌面宠物

> 让AI陪伴你的每一次编程。一个开源的桌面虚拟宠物，实时显示AI工作状态，支持上传任意形象照片自动生成动态桌宠。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 效果展示

### 动画状态预览

| 待机 | 思考 | 写代码 |
|:---:|:---:|:---:|
| ![idle](assets/preview/idle.gif) | ![thinking](assets/preview/thinking.gif) | ![coding](assets/preview/coding.gif) |

| 搜索 | 开心 | 睡觉 |
|:---:|:---:|:---:|
| ![searching](assets/preview/searching.gif) | ![happy](assets/preview/happy.gif) | ![sleeping](assets/preview/sleeping.gif) |

> 以上动画由AI根据一张静态角色图自动生成，支持用户上传自己的形象照片生成专属桌宠！

## 功能特性

- **AI生成动画** - 上传一张角色图片，AI自动生成6种状态的动画帧
- **AI状态实时可视化** - 宠物动画随AI工作状态变化（思考、写代码、搜索等）
- **自定义宠物形象** - 支持上传任意图片生成桌宠，也可手动制作PNG序列帧
- **多AI平台支持** - 适配器模式，支持OpenAI/Claude/Ollama及任何兼容API
- **丰富交互** - 拖拽、双击对话、右键菜单、系统托盘
- **轻量低占用** - 纯Python实现，内存占用低
- **插件化架构** - 事件总线解耦，易于扩展

## 快速开始

### 环境要求

- Python 3.10+
- Windows 10+ / macOS / Linux
- 通义万相API Key（用于AI生成动画，[免费申请](https://dashscope.console.aliyun.com/)）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/liu66-qing/MYpet.git
cd MYpet

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API Key
# 复制 .env.example 为 .env，填入你的API Key
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY

# 4. 生成桌宠动画（从你的角色图片）
python generate_ai_sprites.py --image 你的角色图.jpg

# 5. 启动桌宠
python run.py
```

### 一键启动（使用默认形象）

```bash
python run.py
```

启动后，桌面右下角会出现你的桌宠。你可以：
- **拖拽** - 按住左键移动宠物位置
- **双击** - 打开AI对话窗口
- **右键** - 打开菜单（切换状态、打开对话、退出）
- **托盘图标** - 右键托盘图标可显示/隐藏宠物

## 上传自定义形象生成桌宠

这是本项目的核心特色功能：**一张图片 → 完整动态桌宠**。

```bash
# 用你自己的角色图片生成动画
python generate_ai_sprites.py --image 我的角色.png --output assets/sprites/my_pet
```

生成过程：
1. AI视觉模型（qwen-vl-max）分析你的角色外观特征
2. AI图像生成模型（wanx2.1-t2i-turbo）为每种状态生成4帧动画
3. 自动生成manifest.json配置文件
4. 自动缩放到128x128适配桌宠窗口

然后修改 `config.yaml` 中的 `pet.sprite_set` 为你的文件夹名即可使用。

### 支持的输入格式
- JPG / PNG / WEBP
- 建议使用清晰的角色全身图，白色或简单背景效果最佳

## 配置说明

### .env（API密钥，不会被推送）

```bash
# 通义万相/阿里云百炼 API Key
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### config.yaml（桌宠配置）

```yaml
ai:
  provider: "openai"          # AI对话服务商：openai / claude / ollama
  api_key: ""                 # 对话AI的API Key
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"

pet:
  sprite_set: "default"       # 使用的形象包名
  window:
    size: [128, 128]          # 宠物窗口大小
    start_position: "bottom_right"
    always_on_top: true
```

### 支持的AI对话平台

| 平台 | provider值 | 说明 |
|------|-----------|------|
| OpenAI | `openai` | GPT-4o等，也支持任何OpenAI兼容API |
| Claude | `claude` | Anthropic Claude系列 |
| Ollama | `ollama` | 本地模型，无需API Key |
| 自定义 | `custom` | 继承AIProvider实现自己的接入 |

## 项目架构

```
MYpet/
├── run.py                      # 启动入口
├── generate_ai_sprites.py      # AI动画生成器（核心）
├── generate_preview.py         # 预览图/GIF生成
├── config.yaml                 # 桌宠配置
├── .env                        # API密钥（不推送）
├── src/
│   ├── app.py                  # 应用初始化
│   ├── core/                   # 核心层
│   │   ├── pet_window.py       # 透明悬浮窗口
│   │   ├── state_machine.py    # 有限状态机
│   │   ├── event_bus.py        # 事件总线（发布/订阅）
│   │   └── config_manager.py   # 配置管理
│   ├── ai/                     # AI接入层（适配器模式）
│   │   ├── base_provider.py    # Provider抽象基类
│   │   ├── openai_provider.py  # OpenAI兼容实现
│   │   └── status_monitor.py   # AI状态监控
│   ├── animation/              # 动画系统
│   │   ├── sprite_engine.py    # 帧动画引擎
│   │   └── sprite_loader.py    # 资源加载器
│   └── interaction/            # 交互系统
│       ├── chat_bubble.py      # 对话气泡
│       └── chat_window.py      # 聊天窗口
└── assets/
    ├── sprites/default/        # 默认精灵图（AI生成）
    └── preview/                # README展示用预览图
```

### 架构设计亮点

- **事件总线（EventBus）** - 单例模式，模块间零直接依赖，通过发布/订阅通信
- **适配器模式** - 新增AI平台只需实现 `AIProvider` 接口，不改动现有代码
- **数据驱动动画** - `manifest.json` 定义动画配置，自定义形象无需写代码
- **状态机驱动** - 宠物行为由有限状态机统一管理，状态转换有明确规则
- **AI生成管线** - 视觉理解 → 特征提取 → 多帧生成 → 自动配置

## 自定义形象（手动方式）

除了AI生成，你也可以手动制作精灵图：

1. 在 `assets/sprites/` 下创建新文件夹
2. 按状态分目录放入PNG序列帧（128x128，透明背景）
3. 编写 `manifest.json`：

```json
{
  "name": "我的桌宠",
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

## 开发指南

### 添加新的AI Provider

```python
from src.ai.base_provider import AIProvider, ChatMessage, AIStatusUpdate

class MyProvider(AIProvider):
    async def send_message(self, message: str, history: list[ChatMessage]) -> str:
        ...
    async def stream_message(self, message, history):
        ...
    def get_status(self) -> AIStatusUpdate:
        ...
    @property
    def name(self) -> str:
        return "MyAI"
    @property
    def is_connected(self) -> bool:
        return True
```

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 主语言 |
| PyQt6 | GUI框架，透明窗口 |
| 通义万相 (wanx2.1) | AI图像生成 |
| Qwen-VL-Max | 角色视觉分析 |
| asyncio | 异步AI通信 |
| OpenAI SDK | AI对话接口 |

## 许可证

MIT License
