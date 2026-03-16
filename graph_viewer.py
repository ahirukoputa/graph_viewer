# graph_viewer.py
import sys
import argparse
import os
from pathlib import Path
import importlib.util
import importlib
import threading
import time

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer


def parse_args():
    parser = argparse.ArgumentParser(description="複数系列時系列グラフビューワ")
    parser.add_argument(
        "--config",
        "-c",
        default="config_graph33.py",
        help="設定ファイルを指定(デフォルト: config_graph33.py)",
    )
    return parser.parse_args()


args = parse_args()


# ── 動的に設定モジュールをインポート ──
def load_config_module(config_path_str: str):
    """コマンドライン引数の設定ファイル"""
    config_path = Path(config_path_str).resolve()

    if not config_path.exists():
        print(f"エラー: 設定ファイルが見つかりません → {config_path}")
        sys.exit(1)

    # 拡張子が .py でなくても動かすことも可能だが、今回は .py を前提
    module_name = config_path.stem  # ファイル名（拡張子なし）

    spec = importlib.util.spec_from_file_location(module_name, str(config_path))
    if spec is None or spec.loader is None:
        print(f"エラー: 設定ファイルをモジュールとして読み込めません → {config_path}")
        sys.exit(1)

    config_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = config_module
    spec.loader.exec_module(config_module)

    return config_module


# ここで設定を読み込み
config = load_config_module(args.config)
sys.modules["config"] = config

# 設定をインポート
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    OFFSET_WIDTH,
    OFFSET_HEIGHT,
    GRID_ROWS,
    GRID_COLS,
    N_GRAPHS,
    MAX_POINTS,
    BACKGROUND_COLOR,
    GRAPH_TITLE_FONT_SIZE,
    AXIS_TICK_FONT_SIZE,
    SHOW_WINDOW_X,
    SHOW_WINDOW_Y,
    DATA_FILE_PATH,
    REFERENCE_FILE_PATH,
    GRAPH_CONFIG,
    Y_RANGE_MARGIN_FACTOR,
    format,
)


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("複数系列時系列グラフビューア")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.move(SHOW_WINDOW_X, SHOW_WINDOW_Y)

        self.win = pg.GraphicsLayoutWidget()
        self.win.setBackground(BACKGROUND_COLOR)
        self.setCentralWidget(self.win)

        self.plots = []
        self.curves = []

        # ファイル監視用
        self.last_mtime = 0
        self.last_size = 0

        # 中心値の初期値（設定ファイル or 参照ファイル）
        self.y_centers = self._load_or_create_reference()

        self._setup_plots()
        self._start_update_timer()

    def _load_or_create_reference(self) -> list[float]:
        """参照ファイルがあれば読み込み、なければ初期値を使う"""
        if REFERENCE_FILE_PATH.exists():
            try:
                df = pd.read_csv(REFERENCE_FILE_PATH)
                return df.iloc[-1].round(-1).values.tolist()
            except Exception:
                print("参照ファイル読み込み失敗 → 初期値を使用")
        # 初期値（configから）
        return [item["center"] for item in GRAPH_CONFIG]

    def _save_reference(self, df: pd.DataFrame):
        """最新行を丸めて保存（10単位）"""
        try:
            latest = df.tail(1).round(-1)
            latest.to_csv(REFERENCE_FILE_PATH, index=False, encoding="utf-8")
        except Exception as e:
            print("参照値保存エラー:", e)

    def _setup_plots(self):
        """グラフエリアの初期化"""
        font = QFont()
        font.setPixelSize(AXIS_TICK_FONT_SIZE)

        for i, cfg in enumerate(GRAPH_CONFIG):
            row = i // GRID_COLS
            col = i % GRID_COLS

            title = cfg["title"]
            center = self.y_centers[i]

            # print(f"i={i}, center={center}, type={type(center)}")
            half_range = center * Y_RANGE_MARGIN_FACTOR

            p = self.win.addPlot(row=row, col=col, title=title)
            p.setTitle(title, size=GRAPH_TITLE_FONT_SIZE)
            p.setFixedWidth(WINDOW_WIDTH // GRID_COLS - OFFSET_WIDTH)
            p.setFixedHeight(WINDOW_HEIGHT // GRID_ROWS - OFFSET_HEIGHT)

            p.showGrid(x=True, y=True, alpha=0.3)
            p.setXRange(0, MAX_POINTS, padding=0)
            p.setYRange(center - half_range, center + half_range, padding=0)

            # 軸フォント
            p.getAxis("left").setWidth(36)
            p.getAxis("bottom").setTickFont(font)
            p.getAxis("left").setTickFont(font)

            # 曲線
            curve = p.plot(pen=pg.mkPen(color="y", width=1.2))
            self.curves.append(curve)
            self.plots.append(p)

    def _start_update_timer(self):
        """次回、データ更新有無の確認時間設定"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_from_file)
        self.timer.start(200)  # ms

    def update_from_file(self):
        """
        データの更新があればグラフを更新
        読み込むデータファイル(csv)の更新時間とサイズを確認する
        """
        if not DATA_FILE_PATH.exists():
            return

        try:
            mtime = os.path.getmtime(DATA_FILE_PATH)
            size = os.path.getsize(DATA_FILE_PATH)

            if mtime == self.last_mtime and size == self.last_size:
                return

            # df = pd.read_csv(DATA_FILE_PATH)
            df = format(DATA_FILE_PATH)
            if len(df) == 0:
                return

            # 参照値保存（必要なら）
            self._save_reference(df)

            # 最新の中心値でY範囲を更新（必要に応じて）
            self._update_y_ranges_if_needed(df)

            # 転置して各列＝1系列
            data = df.values.T  # shape: (N_GRAPHS, n_rows)

            for i in range(min(N_GRAPHS, data.shape[0])):
                y = data[i][-MAX_POINTS:]
                x = np.arange(len(y))
                self.curves[i].setData(x, y)

            self.last_mtime = mtime
            self.last_size = size

        except Exception as e:
            print("データ更新エラー:", e)

    def _update_y_ranges_if_needed(self, df: pd.DataFrame):
        # 必要に応じて実装（今回は初回のみ中心値固定で省略可）
        pass


if __name__ == "__main__":
    """
    PyQt6を使用した複数リアルタイム表示グラフ

    """
    app = pg.mkQApp("Multi Graph Viewer")
    window = GraphWindow()
    window.show()

    if sys.flags.interactive != 1 or not hasattr(pg.QtCore, "PYQT_VERSION"):
        pg.exec()
