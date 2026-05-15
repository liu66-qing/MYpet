"""
AI动画帧生成器 - 使用通义万相(wan2.6-image)从静态图生成桌宠多帧动画

核心改进：使用图生图模式（image-to-image），直接传入原图作为参考，
确保生成结果与原图角色完全一致，而非仅靠文字描述重建。

使用方法：
    python generate_ai_sprites.py [--image 精灵.jpg] [--output assets/sprites/default]

需要在 .env 中配置：
    LLM_API_KEY=你的阿里云百炼API Key
"""
import os
import sys
import json
import time
import base64
import argparse
import requests
import numpy as np
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY", "")

# wan2.6-image 支持图生图，直接参考原图保持角色一致性
IMAGE_MODEL = "wan2.6-image"
ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

ANIMATION_STATES = {
    "idle": {
        "frames": 4,
        "prompts": [
            "保持这个角色完全不变，正面站立，双手自然下垂，表情放松微笑，白色纯净背景",
            "保持这个角色完全不变，身体微微向左倾斜2度，像在呼吸一样，白色纯净背景",
            "保持这个角色完全不变，身体微微向右倾斜2度，像在呼吸一样，白色纯净背景",
            "保持这个角色完全不变，回到正面站立姿势，表情放松，白色纯净背景",
        ],
    },
    "thinking": {
        "frames": 4,
        "prompts": [
            "保持这个角色完全不变，头微微歪向右边，一只手放在下巴上做思考状，白色纯净背景",
            "保持这个角色完全不变，头歪向右边，头顶画一个小问号气泡，白色纯净背景",
            "保持这个角色完全不变，抬头看向右上方，头顶有省略号...气泡，白色纯净背景",
            "保持这个角色完全不变，点头恍然大悟的表情，头顶有灯泡图标，白色纯净背景",
        ],
    },
    "coding": {
        "frames": 4,
        "prompts": [
            "保持这个角色完全不变，坐在一台小笔记本电脑前，双手放在键盘上，白色纯净背景",
            "保持这个角色完全不变，坐在电脑前打字，左手抬起敲击键盘，白色纯净背景",
            "保持这个角色完全不变，坐在电脑前打字，右手抬起敲击键盘，白色纯净背景",
            "保持这个角色完全不变，坐在电脑前，双手快速打字，屏幕发光，白色纯净背景",
        ],
    },
    "searching": {
        "frames": 4,
        "prompts": [
            "保持这个角色完全不变，手持一个放大镜，看向左边寻找东西，白色纯净背景",
            "保持这个角色完全不变，手持放大镜，看向右边寻找东西，白色纯净背景",
            "保持这个角色完全不变，手持放大镜举高，看向上方寻找，白色纯净背景",
            "保持这个角色完全不变，放下放大镜，开心地找到了目标，白色纯净背景",
        ],
    },
    "happy": {
        "frames": 4,
        "prompts": [
            "保持这个角色完全不变，双腿微曲准备跳起来，开心的表情，白色纯净背景",
            "保持这个角色完全不变，跳到空中最高点，双手举过头顶欢呼，白色纯净背景",
            "保持这个角色完全不变，从空中下落，手臂张开，开心表情，白色纯净背景",
            "保持这个角色完全不变，落地微蹲，满脸笑容，周围有小星星，白色纯净背景",
        ],
    },
    "sleeping": {
        "frames": 4,
        "prompts": [
            "保持这个角色完全不变，闭上眼睛，头微微低下，打瞌睡的样子，白色纯净背景",
            "保持这个角色完全不变，闭眼睡觉，头低得更多，旁边有一个小z字母，白色纯净背景",
            "保持这个角色完全不变，闭眼熟睡，头歪向一边，旁边有Zz字母，白色纯净背景",
            "保持这个角色完全不变，闭眼深度睡眠，旁边有ZZZ字母气泡，白色纯净背景",
        ],
    },
}


def remove_background(image_path: str, threshold: int = 240) -> None:
    """去除白色/浅色背景，转为透明PNG"""
    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)

    # 检测接近白色的像素（RGB各通道 > threshold）
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)

    # 边缘羽化：对接近白色但不完全白色的像素做半透明处理
    soft_threshold = threshold - 20
    soft_mask = (r > soft_threshold) & (g > soft_threshold) & (b > soft_threshold) & ~white_mask

    # 完全白色区域设为全透明
    data[white_mask, 3] = 0

    # 边缘区域设为半透明（羽化）
    if np.any(soft_mask):
        # 根据与白色的距离计算透明度
        avg_channel = (r[soft_mask].astype(int) + g[soft_mask].astype(int) + b[soft_mask].astype(int)) / 3
        alpha_values = ((255 - avg_channel) / (255 - soft_threshold) * 255).clip(0, 255).astype(np.uint8)
        data[soft_mask, 3] = alpha_values

    result = Image.fromarray(data)
    result.save(image_path, "PNG")


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_frame_i2i(image_b64: str, mime: str, prompt: str, state_name: str, frame_idx: int, output_dir: str) -> str | None:
    """使用wan2.6-image图生图模式生成单帧，直接参考原图"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": IMAGE_MODEL,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:{mime};base64,{image_b64}"},
                        {"text": prompt},
                    ],
                }
            ]
        },
        "parameters": {
            "size": "768*768",
            "n": 1,
            "prompt_extend": False,
            "enable_interleave": False,
        },
    }

    try:
        resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=180)
        resp.raise_for_status()
        data = resp.json()

        # wan2.6-image 同步返回，格式: output.choices[0].message.content[{image: url}]
        img_url = None
        output = data.get("output", {})
        choices = output.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", [])
            for item in content:
                if isinstance(item, dict) and "image" in item:
                    img_url = item["image"]
                    break

        if img_url:
            img_resp = requests.get(img_url, timeout=30)
            img_resp.raise_for_status()
            filename = f"{state_name}_{frame_idx:03d}.png"
            filepath = os.path.join(output_dir, state_name, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(img_resp.content)
            # 去除白色背景，转为透明PNG
            remove_background(filepath)
            return filepath
        else:
            print(f"  [警告] 未找到图片: {json.dumps(output, ensure_ascii=False)[:200]}")
            return None

    except Exception as e:
        print(f"  [错误] {e}")
        return None


def generate_all_frames(image_path: str, output_dir: str):
    """生成所有状态的动画帧"""
    print("=" * 50)
    print("MYpet AI动画帧生成器 (图生图模式)")
    print(f"模型: {IMAGE_MODEL}")
    print(f"原图: {image_path}")
    print("=" * 50)

    if not API_KEY:
        print("错误：未配置API Key，请在.env文件中设置 LLM_API_KEY")
        sys.exit(1)

    # 编码原图
    ext = Path(image_path).suffix.lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    print(f"正在编码原图 ({mime})...")
    image_b64 = encode_image_to_base64(image_path)
    print(f"  原图大小: {len(image_b64) * 3 // 4 // 1024} KB")

    # 逐状态生成帧
    generated = {}
    total = sum(s["frames"] for s in ANIMATION_STATES.values())
    done = 0

    for state_name, state_info in ANIMATION_STATES.items():
        print(f"\n生成 [{state_name}] 动画 ({state_info['frames']}帧)...")
        frames_generated = []

        for i, prompt in enumerate(state_info["prompts"]):
            done += 1
            print(f"  帧 {i+1}/{state_info['frames']} ({done}/{total} 总进度)")
            print(f"    提示: {prompt[:50]}...")
            filepath = generate_frame_i2i(image_b64, mime, prompt, state_name, i + 1, output_dir)
            if filepath:
                frames_generated.append(filepath)
                print(f"    -> 已保存: {os.path.basename(filepath)}")
            else:
                print(f"    -> 跳过")
            time.sleep(1)

        generated[state_name] = frames_generated

    # 生成manifest.json
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
