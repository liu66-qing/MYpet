"""精灵图加载器"""
import json
import os
from dataclasses import dataclass, field
from typing import Optional

from PyQt6.QtGui import QPixmap


@dataclass
class AnimationConfig:
    name: str
    frames: list[QPixmap] = field(default_factory=list)
    fps: int = 8
    loop: bool = True
    next_animation: str = "idle"


class SpriteLoader:
    def __init__(self, base_path: str):
        self._base_path = base_path
        self._animations: dict[str, AnimationConfig] = {}

    @property
    def animations(self) -> dict[str, AnimationConfig]:
        return self._animations

    def load_manifest(self, manifest_path: str) -> dict[str, AnimationConfig]:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        sprite_dir = os.path.dirname(manifest_path)

        for anim_name, anim_data in manifest.get("animations", {}).items():
            frames = []
            pattern = anim_data["frames"]
            count = anim_data["frame_count"]

            for i in range(1, count + 1):
                frame_path = os.path.join(sprite_dir, pattern.format(i))
                if os.path.exists(frame_path):
                    pix = QPixmap(frame_path)
                    if not pix.isNull():
                        frames.append(pix)

            if frames:
                self._animations[anim_name] = AnimationConfig(
                    name=anim_name,
                    frames=frames,
                    fps=anim_data.get("fps", 8),
                    loop=anim_data.get("loop", True),
                    next_animation=anim_data.get("next", "idle"),
                )

        return self._animations

    def get_animation(self, name: str) -> Optional[AnimationConfig]:
        return self._animations.get(name)
