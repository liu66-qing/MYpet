"""
AI动画帧生成器 - 使用通义万相从静态图生成桌宠多帧动画

使用方法：
    python generate_ai_sprites.py [--image 精灵.jpg] [--output assets/sprites/default]

需要在 .env 中配置：
    LLM_API_KEY=你的阿里云百炼API Key
    LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
"""
import os
import sys
import json
import time
import base64
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

IMAGE_MODEL = "wanx2.1-t2i-turbo"
VISION_MODEL = "qwen-vl-max"

ANIMATION_STATES = {
    "idle": {
        "description": "待机状态，角色放松站立，轻微呼吸起伏",
        "frames": 4,
        "variations": ["正常站立", "微微向左倾斜", "微微向右倾斜", "回到正常站立"],
    },
    "thinking": {
        "description": "思考状态，角色歪头思考，头顶有问号或省略号",
        "frames": 4,
        "variations": ["歪头看向左上方", "头顶出现一个小问号", "头顶问号变大", "恢复正常并点头"],
    },
    "coding": {
        "description": "写代码状态，角色面前有虚拟键盘在打字",
        "frames": 4,
        "variations": ["双手放在键盘上", "左手敲击", "右手敲击", "双手同时敲击"],
    },
    "searching": {
        "description": "搜索状态，角色手持放大镜四处查看",
        "frames": 4,
        "variations": ["举起放大镜看向左边", "看向右边", "看向上方", "找到目标开心"],
    },
    "happy": {
        "description": "开心状态，角色跳跃欢呼",
        "frames": 4,
        "variations": ["准备起跳", "跳到最高点双手举起", "开始下落", "落地微蹲"],
    },
    "sleeping": {
        "description": "睡觉状态，角色闭眼打盹，有Zzz气泡",
        "frames": 4,
        "variations": ["闭眼低头", "头更低一些出现小z", "出现中等z", "出现大Z然后循环"],
    },
}


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_character(image_path: str) -> str:
    """用qwen-vl-max分析角色特征，生成描述"""
    print("正在分析角色特征...")
    img_b64 = encode_image_to_base64(image_path)
    ext = Path(image_path).suffix.lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}.get(ext, "image/jpeg")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                    {"type": "text", "text": (
                        "请详细描述这个角色的外观特征，包括：颜色、体型、服装、配饰、表情等。"
                        "用简洁的英文描述，适合作为AI绘图的prompt。不超过100词。"
                    )},
                ],
            }
        ],
    }

    resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    description = result["choices"][0]["message"]["content"]
    print(f"角色描述: {description}")
    return description


def generate_frame(character_desc: str, state_name: str, variation: str, frame_idx: int, output_dir: str) -> str | None:
    """用通义万相生成单帧图像"""
    prompt = (
        f"A cute desktop pet character sprite, {character_desc}, "
        f"in {state_name} pose: {variation}. "
        f"Chibi style, transparent background, centered composition, "
        f"128x128 pixel art style, clean lines, vibrant colors, "
        f"single character only, no text, white background."
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": IMAGE_MODEL,
        "input": {"prompt": prompt},
        "parameters": {
            "size": "512*512",
            "n": 1,
        },
    }

    # 通义万相使用异步任务模式
    task_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    task_headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    }
    task_payload = {
        "model": IMAGE_MODEL,
        "input": {"prompt": prompt},
        "parameters": {
            "size": "512*512",
            "n": 1,
        },
    }

    try:
        resp = requests.post(task_url, headers=task_headers, json=task_payload, timeout=30)
        resp.raise_for_status()
        task_data = resp.json()

        task_id = task_data.get("output", {}).get("task_id")
        if not task_id:
            print(f"  [错误] 未获取到task_id: {task_data}")
            return None

        # 轮询等待结果
        status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        status_headers = {"Authorization": f"Bearer {API_KEY}"}

        for _ in range(60):
            time.sleep(3)
            status_resp = requests.get(status_url, headers=status_headers, timeout=15)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            task_status = status_data.get("output", {}).get("task_status")

            if task_status == "SUCCEEDED":
                results = status_data["output"].get("results", [])
                if results and results[0].get("url"):
                    img_url = results[0]["url"]
                    img_resp = requests.get(img_url, timeout=30)
                    img_resp.raise_for_status()

                    filename = f"{state_name}_{frame_idx:03d}.png"
                    filepath = os.path.join(output_dir, state_name, filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, "wb") as f:
                        f.write(img_resp.content)
                    return filepath
                return None
            elif task_status == "FAILED":
                print(f"  [失败] {status_data.get('output', {}).get('message', '未知错误')}")
                return None

        print(f"  [超时] 任务未在180秒内完成")
        return None

    except Exception as e:
        print(f"  [错误] {e}")
        return None


def generate_all_frames(image_path: str, output_dir: str):
    """生成所有状态的动画帧"""
    print("=" * 50)
    print("MYpet AI动画帧生成器")
    print("=" * 50)

    if not API_KEY:
        print("错误：未配置API Key，请在.env文件中设置 LLM_API_KEY")
        sys.exit(1)

    # 1. 分析角色
    character_desc = analyze_character(image_path)

    # 2. 逐状态生成帧
    generated = {}
    total = sum(s["frames"] for s in ANIMATION_STATES.values())
    done = 0

    for state_name, state_info in ANIMATION_STATES.items():
        print(f"\n生成 [{state_name}] 动画 ({state_info['frames']}帧)...")
        state_dir = os.path.join(output_dir, state_name)
        os.makedirs(state_dir, exist_ok=True)
        frames_generated = []

        for i, variation in enumerate(state_info["variations"]):
            done += 1
            print(f"  帧 {i+1}/{state_info['frames']} ({done}/{total} 总进度) - {variation}")
            filepath = generate_frame(character_desc, state_name, variation, i + 1, output_dir)
            if filepath:
                frames_generated.append(filepath)
                print(f"    -> 已保存: {filepath}")
            else:
                print(f"    -> 跳过")
            time.sleep(1)

        generated[state_name] = frames_generated

    # 3. 生成manifest.json
    manifest = {
        "name": "AI生成精灵",
        "author": "MYpet AI Generator",
        "version": "1.0.0",
        "size": [128, 128],
        "animations": {},
    }
    for state_name, state_info in ANIMATION_STATES.items():
        actual_count = len(generated.get(state_name, []))
        if actual_count > 0:
            manifest["animations"][state_name] = {
                "frames": f"{state_name}/{state_name}_{{:03d}}.png",
                "frame_count": actual_count,
                "fps": 4 if state_name in ("idle", "sleeping") else 6,
                "loop": state_name != "happy",
            }
            if state_name == "happy":
                manifest["animations"][state_name]["next"] = "idle"

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"生成完成！")
    print(f"成功生成: {sum(len(v) for v in generated.values())}/{total} 帧")
    print(f"输出目录: {output_dir}")
    print(f"配置文件: {manifest_path}")
    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(description="MYpet AI动画帧生成器")
    parser.add_argument("--image", default="精灵.jpg", help="输入角色图片路径")
    parser.add_argument("--output", default="assets/sprites/default", help="输出目录")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(project_root, args.image) if not os.path.isabs(args.image) else args.image
    output_dir = os.path.join(project_root, args.output) if not os.path.isabs(args.output) else args.output

    if not os.path.exists(image_path):
        print(f"错误：找不到图片 {image_path}")
        sys.exit(1)

    generate_all_frames(image_path, output_dir)


if __name__ == "__main__":
    main()
