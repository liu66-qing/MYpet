---
name: mypet
description: AI桌面宠物 - 生成、启动、监听终端
triggers:
  - "启动桌宠"
  - "生成桌宠"
  - "桌宠"
  - "mypet"
  - "desktop pet"
---

# MYpet - AI桌面宠物 Skill

## 功能

MYpet 是一个AI桌面宠物工具，支持：
1. 从一张图片自动生成6种状态的动画桌宠
2. 桌宠实时反映终端/AI工作状态
3. 监听终端输出，检测错误/完成/进度等关键词时桌宠做出反应

## 命令

### 启动桌宠
```bash
cd <project_root> && python mypet_cli.py run
```

### 从图片生成桌宠动画
```bash
cd <project_root> && python mypet_cli.py generate --image <图片路径> --output assets/sprites/<名称>
```
生成后修改 `config.yaml` 中 `pet.sprite_set` 为对应名称。

### 监听终端命令
```bash
cd <project_root> && python mypet_cli.py watch <要监听的命令>
```
示例：`python mypet_cli.py watch python train.py`

桌宠会在检测到以下关键词时做出反应：
- error/failed/exception → 错误状态 + 红色提示
- completed/done/finished/success → 开心状态 + 绿色提示
- epoch/step/training → 编码状态 + 进度提示

### 手动通知桌宠
```bash
cd <project_root> && python mypet_cli.py notify "训练完成！"
```

## 环境要求

- Python 3.10+
- 依赖：`pip install -r requirements.txt`
- AI生成需要在 `.env` 中配置 `LLM_API_KEY`（通义万相API Key）

## 项目路径

此skill对应的项目位于当前工作目录。如果用户提到桌宠相关需求，先确认项目路径再执行命令。
