"""终端输出监听器 - 包裹用户命令，捕获stdout/stderr并分析"""
import subprocess
import sys
import threading

from src.monitor.keyword_rules import match_line, DEFAULT_RULES
from src.monitor.socket_server import send_to_pet


def watch_command(command: list[str], verbose: bool = True):
    """包裹用户命令，实时监听输出并通知桌宠

    用法：mypet watch python train.py
    """
    print(f"[MYpet] 监听命令: {' '.join(command)}")
    print(f"[MYpet] 桌宠将实时响应终端输出")
    print("-" * 40)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # 通知桌宠进入coding状态
    send_to_pet({"type": "state", "state": "coding", "message": f"运行: {' '.join(command)}"})

    try:
        for line in process.stdout:
            line = line.rstrip("\n")
            # 原样输出到终端
            print(line)

            # 匹配关键词
            result = match_line(line)
            if result:
                category, keyword = result
                msg = {
                    "type": "terminal",
                    "category": category,
                    "keyword": keyword,
                    "line": line[:200],  # 截断过长的行
                }
                send_to_pet(msg)
                if verbose:
                    print(f"[MYpet] 检测到 [{category}]: {keyword}")

    except KeyboardInterrupt:
        process.terminate()
        print("\n[MYpet] 已终止")

    process.wait()
    exit_code = process.returncode

    # 通知桌宠命令结束
    if exit_code == 0:
        send_to_pet({"type": "terminal", "category": "success", "keyword": "done", "line": f"命令执行完成 (exit 0)"})
    else:
        send_to_pet({"type": "terminal", "category": "error", "keyword": "failed", "line": f"命令失败 (exit {exit_code})"})

    return exit_code


def notify_pet(message: str, category: str = "info"):
    """手动发送通知给桌宠

    用法：mypet notify "训练完成！"
    """
    msg = {
        "type": "notify",
        "category": category,
        "message": message,
    }
    success = send_to_pet(msg)
    if success:
        print(f"[MYpet] 已通知桌宠: {message}")
    else:
        print(f"[MYpet] 无法连接桌宠（桌宠是否在运行？）")
    return success
