"""生成README展示用的预览拼图，并缩放精灵图到128x128"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SPRITE_DIR = os.path.join(BASE, "assets", "sprites", "default")
PREVIEW_DIR = os.path.join(BASE, "assets", "preview")
os.makedirs(PREVIEW_DIR, exist_ok=True)

STATES = ["idle", "thinking", "coding", "searching", "happy", "sleeping"]
STATE_LABELS = ["待机", "思考", "写代码", "搜索", "开心", "睡觉"]
PET_SIZE = 128


def resize_sprites():
    """将所有生成的精灵图缩放到128x128"""
    print("缩放精灵图到 128x128...")
    for state in STATES:
        state_dir = os.path.join(SPRITE_DIR, state)
        if not os.path.isdir(state_dir):
            continue
        for fname in sorted(os.listdir(state_dir)):
            if not fname.endswith(".png"):
                continue
            path = os.path.join(state_dir, fname)
            img = Image.open(path)
            if img.size != (PET_SIZE, PET_SIZE):
                img = img.resize((PET_SIZE, PET_SIZE), Image.Resampling.LANCZOS)
                img.save(path)
    print("  完成")


def generate_preview():
    """生成6种状态的横向拼图预览"""
    print("生成预览拼图...")
    frame_size = 256
    padding = 10
    cols = 3
    rows = 2
    width = cols * frame_size + (cols + 1) * padding
    height = rows * (frame_size + 30) + (rows + 1) * padding

    canvas = Image.new("RGBA", (width, height), (245, 245, 245, 255))

    for idx, (state, label) in enumerate(zip(STATES, STATE_LABELS)):
        state_dir = os.path.join(SPRITE_DIR, state)
        files = sorted([f for f in os.listdir(state_dir) if f.endswith(".png")]) if os.path.isdir(state_dir) else []
        if not files:
            continue

        img = Image.open(os.path.join(state_dir, files[0]))
        img = img.resize((frame_size, frame_size), Image.Resampling.LANCZOS)

        col = idx % cols
        row = idx // cols
        x = padding + col * (frame_size + padding)
        y = padding + row * (frame_size + 30 + padding)

        canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)

    preview_path = os.path.join(PREVIEW_DIR, "states_preview.png")
    canvas.save(preview_path)
    print(f"  保存到: {preview_path}")

    # 单独保存每个状态的第一帧作为展示
    for state in STATES:
        state_dir = os.path.join(SPRITE_DIR, state)
        files = sorted([f for f in os.listdir(state_dir) if f.endswith(".png")]) if os.path.isdir(state_dir) else []
        if files:
            img = Image.open(os.path.join(state_dir, files[0]))
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            img.save(os.path.join(PREVIEW_DIR, f"{state}.png"))

    print("  各状态预览图已保存")


def generate_gif():
    """为每个状态生成GIF动画预览"""
    print("生成GIF动画预览...")
    for state in STATES:
        state_dir = os.path.join(SPRITE_DIR, state)
        files = sorted([f for f in os.listdir(state_dir) if f.endswith(".png")]) if os.path.isdir(state_dir) else []
        if len(files) < 2:
            continue

        frames = []
        for fname in files:
            img = Image.open(os.path.join(state_dir, fname))
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            # GIF需要转为P模式或RGB
            bg = Image.new("RGBA", (256, 256), (255, 255, 255, 255))
            bg.paste(img, (0, 0), img)
            frames.append(bg.convert("RGB"))

        gif_path = os.path.join(PREVIEW_DIR, f"{state}.gif")
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=250,
            loop=0,
        )
    print("  GIF动画已保存")


if __name__ == "__main__":
    resize_sprites()
    generate_preview()
    generate_gif()
    print("\n全部完成！")
