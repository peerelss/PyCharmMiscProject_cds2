import sys
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils.get_hour_power_price import get_ercot_hb_west_prices
from utils.utils_k import date_to_string, date_to_string_tomorrow
# 导入 Matplotlib
import matplotlib as mpl

# =======================================================
# --- 针对 Windows 11 的字体配置 ---
# 确保中文正常显示
# =======================================================
CHINESE_FONT = "Microsoft YaHei"
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = [CHINESE_FONT, 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False
# =======================================================

# 示例电价数据 1: 原始数据

THRESHOLD_1 = 70  # 图表 1 阈值较低

# 示例电价数据 2: 模拟高价数据 (用于对比)

THRESHOLD_2 = 70  # 图表 2 阈值较高


def get_higher_70_power_price(date_string_tomorrow):
    print(date_string_tomorrow)
    url = "https://www.ercot.com/content/cdr/html/DATE_STRING_dam_spp.html".replace("DATE_STRING", date_string_tomorrow)
    date_price_d = get_ercot_hb_west_prices(url)
    high_price_messages = []
    print(date_price_d)
    if date_price_d:
        print(f"--- ERCOT HB_WEST 20251205 每小时电价 ---")
        for hour, price in date_price_d.items():
            if price > 70:
                print(f"小时 {hour:02d}: ${price:.2f}")
                message = f"小时 {hour:02d}: ${price:.2f}"
                high_price_messages.append(message)

    else:
        print("未能成功获取电价数据。")
    return date_price_d


class PriceBarChart(QWidget):
    def __init__(self, data, date_str="", threshold=70):
        super().__init__()

        # 确保 Matplotlib 图表添加到 QWidget 中
        layout = QVBoxLayout(self)

        fig = Figure(figsize=(5, 4))  # 调整 figsize 以适应布局
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        hours = list(data.keys())
        prices = list(data.values())

        # --- 根据阈值设置颜色 ---
        colors = ["red" if p >= threshold else "green" for p in prices]

        # --- 画连续柱状图 ---
        ax.bar(hours, prices, color=colors, width=1.0)

        # --- 基准线 ---
        ax.axhline(
            threshold,
            color="gray",
            linestyle="--",
            linewidth=1,
            label=f"阈值 = {threshold}"
        )

        # --- X 轴设置 ---
        hour_ticks = range(1, 25)
        ax.set_xticks(hour_ticks)
        ax.set_xlim(0.5, 24.5)

        # 定义时段标签 (HE 1 -> 00:00-01:00)
        time_labels = []
        for h in range(24):
            start_time = f"{h:02d}:00"
            end_time = f"{(h + 1) % 24:02d}:00"
            if h == 23:
                end_time = "00:00"
            time_labels.append(f"{start_time}-{end_time}")

        ax.set_xticklabels(time_labels, rotation=45, ha="right", fontsize=8)

        # --- 标题设置 ---
        if date_str:
            title_text = f"DAM 市场 {date_str} (阈值: ${threshold})"
        else:
            title_text = f"每小时 DAM 电价 (阈值: ${threshold})"

        ax.set_xlabel("时段 (Hour Ending)")
        ax.set_ylabel("价格 ($/MWh)")
        ax.set_title(title_text, fontsize=10)  # 减小标题字体，适应并排显示

        ax.grid(axis="y")
        ax.legend(fontsize=8, loc='upper right')

        fig.tight_layout(pad=0.5)  # 调整布局，增加紧凑度

        layout.addWidget(canvas)
        # 设置 QWidget 的最小大小，防止图表被压缩
        self.setMinimumWidth(480)
        self.setMinimumHeight(450)


class DualChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("电价数据实时对比与定时刷新")
        self.setWindowTitle("双图表对比界面 - DAM 市场电价")
        self.resize(1200, 600)  # 增加窗口宽度以容纳两个图表

        # 使用主垂直布局 (QVBoxLayout) 包含所有内容
        main_layout = QVBoxLayout(self)

        # 1. 顶部总标题 (可选)
        total_title = QLabel("DAM 市场电价对比分析")
        total_title.setAlignment(Qt.AlignCenter)
        total_title.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 10px;")
        main_layout.addWidget(total_title)

        # 2. 创建水平布局 (QHBoxLayout) 来放置两个图表
        chart_container_layout = QVBoxLayout()
        # / 今天价格
        # --- 图表 1 实例 ---
        data_string = date_to_string()
        price_data_1 = get_higher_70_power_price(data_string)
        chart_1 = PriceBarChart(
            price_data_1,
            date_str=data_string,
            threshold=THRESHOLD_1
        )
        chart_container_layout.addWidget(chart_1)

        # --- 图表 2 实例 ---
        data_string_tomorrow = date_to_string_tomorrow()
        price_data_tomorrow = get_higher_70_power_price(data_string_tomorrow)
        if len(price_data_tomorrow) > 2:

            chart_2 = PriceBarChart(
                price_data_tomorrow,
                date_str=data_string_tomorrow,
                threshold=THRESHOLD_2
            )
            chart_container_layout.addWidget(chart_2)
        else:
            info_label = QLabel(f"--- {data_string_tomorrow} 的电价数据尚未获取或数据为空 ---")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-size: 14pt; color: #e74c3c; border: 2px dashed #e74c3c; padding: 50px;")

            # 为了让 QLabel 占据和图表差不多的空间，设置其布局策略
            info_label.setSizePolicy(
                info_label.sizePolicy().horizontalPolicy(),
                info_label.sizePolicy().verticalPolicy()
            )
            chart_container_layout.addWidget(info_label)
        # 3. 将图表容器添加到主布局
        main_layout.addLayout(chart_container_layout)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DualChartWindow()
    window.show()
    sys.exit(app.exec_())
