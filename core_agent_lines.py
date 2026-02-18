#!/usr/bin/env python3
"""
統計 nanobot 核心程式碼行數的跨平台版本。
用法: python core_agent_lines.py
"""

import os
from pathlib import Path

def count_lines(file_path: Path) -> int:
    """計算檔案行數"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def main():
    # 專案根目錄 (假設此腳本放在根目錄)
    root_dir = Path(__file__).parent
    nanobot_dir = root_dir / "nanobot"
    
    if not nanobot_dir.exists():
        print(f"Error: Directory {nanobot_dir} not found.")
        return

    print("nanobot core agent line count")
    print("================================")
    print("")

    # 要統計的特定目錄 (對應原始 Shell Script 的迴圈)
    # 注意: Shell script 中的 find maxdepth 1 僅統計該層目錄下的檔案
    target_rel_paths = [
        "agent",
        "agent/tools",
        "bus",
        "config",
        "cron",
        "heartbeat",
        "session",
        "utils"
    ]
    
    total_lines = 0

    for rel_path in target_rel_paths:
        target_dir = nanobot_dir / rel_path
        dir_count = 0
        
        if target_dir.exists():
            for item in target_dir.iterdir():
                if item.is_file() and item.suffix == ".py":
                    dir_count += count_lines(item)
        
        # 格式化輸出
        print(f"  {rel_path + '/':<16} {dir_count:>5} lines")
        
        # 這裡不累加 total_lines，因為後面會用 os.walk 重新計算總數 (排除特定目錄)

    # 統計根目錄下的 __init__.py 和 __main__.py
    root_files_count = 0
    for f_name in ["__init__.py", "__main__.py"]:
        f_path = nanobot_dir / f_name
        if f_path.exists():
            root_files_count += count_lines(f_path)
    
    print(f"  {'(root)':<16} {root_files_count:>5} lines")
    print("")

    # 計算總行數 (排除 channels, cli, providers)
    core_total = 0
    excludes = {"channels", "cli", "providers", "__pycache__"}
    
    for root, dirs, files in os.walk(nanobot_dir):
        # 排除指定的目錄，避免進入遍歷
        # 修改 dirs 列表會影響 os.walk 的後續遍歷
        dirs[:] = [d for d in dirs if d not in excludes]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix == ".py":
                core_total += count_lines(file_path)

    print(f"  Core total:     {core_total} lines")
    print("")
    print("  (excludes: channels/, cli/, providers/)")

if __name__ == "__main__":
    main()
