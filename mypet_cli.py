"""MYpet CLI - 统一命令行入口

用法：
    mypet run                    启动桌宠
    mypet generate [--image X]   从图片生成动画帧
    mypet watch <command>        监听命令输出，实时通知桌宠
    mypet notify <message>       手动发送通知给桌宠
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]

    if command == "run":
        from src.app import main as app_main
        app_main()

    elif command == "generate":
        from generate_ai_sprites import main as gen_main
        # 转发剩余参数
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        gen_main()

    elif command == "watch":
        if len(sys.argv) < 3:
            print("用法: mypet watch <command> [args...]")
            print("示例: mypet watch python train.py")
            sys.exit(1)
        from src.monitor.terminal_monitor import watch_command
        exit_code = watch_command(sys.argv[2:])
        sys.exit(exit_code)

    elif command == "notify":
        if len(sys.argv) < 3:
            print("用法: mypet notify <message> [--category error|success|info]")
            sys.exit(1)
        message = sys.argv[2]
        category = "info"
        if "--category" in sys.argv:
            idx = sys.argv.index("--category")
            if idx + 1 < len(sys.argv):
                category = sys.argv[idx + 1]
        from src.monitor.terminal_monitor import notify_pet
        notify_pet(message, category)

    elif command in ("--help", "-h", "help"):
        print(__doc__)

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
