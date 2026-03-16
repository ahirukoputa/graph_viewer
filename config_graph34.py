# config.py
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

# ── 表示関連 ──
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 660
OFFSET_WIDTH = 7
OFFSET_HEIGHT = 8

# グリッド構成
GRID_ROWS = 5
GRID_COLS = 7
N_GRAPHS = GRID_ROWS * GRID_COLS  # 34 or 35でも自動対応可

MAX_POINTS = 330

# 見た目
BACKGROUND_COLOR = "#002632"
GRAPH_TITLE_FONT_SIZE = "6pt"
AXIS_TICK_FONT_SIZE = 6

# 表示位置
SHOW_WINDOW_X = 0
SHOW_WINDOW_Y = 338

# データ関連
DATA_FILE_PATH = Path("./tmp/graph34.csv")
REFERENCE_FILE_PATH = Path("./tmp/graph_reference.csv")

# ── グラフごとの設定（名前・中心値） ──
GRAPH_CONFIG: List[Dict[str, Any]] = [
    {"title": "Test-1", "center": 800},
    {"title": "Test-2", "center": 1100},
    {"title": "Test-3", "center": 3100},
    {"title": "Test-4", "center": 2600},
    {"title": "Test-5", "center": 970},
    {"title": "Test-6", "center": 670},
    {"title": "Test-7", "center": 2800},
    {"title": "Test-8", "center": 4000},
    {"title": "Test-9", "center": 3000},
    {"title": "Test-10", "center": 6000},
    {"title": "Test-11", "center": 2000},
    {"title": "Test-12", "center": 850},
    {"title": "Test-13", "center": 4800},
    {"title": "Test-14", "center": 1750},
    {"title": "Test-15", "center": 5300},
    {"title": "Test-16", "center": 6800},
    {"title": "Test-17", "center": 5600},
    {"title": "Test-18", "center": 14000},
    {"title": "Test-19", "center": 6000},
    {"title": "Test-20", "center": 720},
    {"title": "Test-21", "center": 2400},
    {"title": "Test-22", "center": 1800},
    {"title": "Test-23", "center": 260},
    {"title": "Test-24", "center": 4700},
    {"title": "Test-25", "center": 7000},
    {"title": "Test-26", "center": 5900},
    {"title": "Test-27", "center": 2370},
    {"title": "Test-28", "center": 630},
    {"title": "Test-29", "center": 900},
    {"title": "Test-30", "center": 3300},
    {"title": "Test-31", "center": 1350},
    {"title": "Test-32", "center": 3050},
    {"title": "Test-33", "center": 2960},
    {"title": "Test-34", "center": 3800},
]

# ── 便利な計算プロパティ（必要に応じて使う） ──
Y_RANGE_MARGIN_FACTOR = 0.1  # 中心値の±10%


# 読み込みデータを適切に変換する
def format(file_path: str) -> pd.DataFrame:
    """
    必要なデータのみ抽出しグラフに適したデータに変換する。

    """
    return pd.read_csv(file_path)
