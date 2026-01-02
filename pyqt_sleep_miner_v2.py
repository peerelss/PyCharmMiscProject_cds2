import sys
import datetime
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QDateTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils.get_hour_power_price import get_ercot_hb_west_prices
from utils.utils_k import date_to_string, date_to_string_tomorrow
# 导入 Matplotlib
import matplotlib as mpl

# =======================================================
# --- 字体配置（针对 Windows 11） ---
# =======================================================
CHINESE_FONT = "Microsoft YaHei"
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = [CHINESE_FONT, 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False
# =======================================================

# 默认阈值
THRESHOLD_1 = 70
THRESHOLD_2 = 70

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


# -------------------------------------------------------
# --- 1. 模拟数据获取函数 ---
# -------------------------------------------------------
def fetch_simulated_price_data(is_today_empty=False):
    """
    模拟从外部 API 获取数据。
    每次调用会为“今天”的数据生成一组新的、随机波动的价格。
    """
    # 昨天的数据 (保持稳定)

    data_string  = date_to_string ()
    price_data_1 = get_higher_70_power_price(data_string)
    # 今天的数据 (模拟实时更新和波动)
    if is_today_empty:
        price_data_2 = {}
    else:
        data_string_tomorrow = date_to_string_tomorrow()
        price_data_2 = get_higher_70_power_price(data_string_tomorrow)

    return price_data_1, price_data_2


# -------------------------------------------------------
# --- 2. 图表绘制组件 ---
# -------------------------------------------------------
class PriceBarChart(QWidget):
    # 构造函数保持不变，仅用于绘制单个图表
    def __init__(self, data, date_str="", threshold=70):
        super().__init__()
        self.data = data
        self.date_str = date_str
        self.threshold = threshold
        self.layout = QVBoxLayout(self)
        self.canvas = None
        self.draw_chart()

    def draw_chart(self):
        # 清除旧图表
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

        if not self.data:
            return

        fig = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        hours = list(self.data.keys())
        prices = list(self.data.values())

        colors = ["red" if p >= self.threshold else "green" for p in prices]
        ax.bar(hours, prices, color=colors, width=1.0)

        ax.axhline(self.threshold, color="gray", linestyle="--", linewidth=1, label=f"阈值 = {self.threshold}")

        hour_ticks = range(1, 25)
        ax.set_xticks(hour_ticks)
        ax.set_xlim(0.5, 24.5)

        time_labels = [f"{h:02d}:00-{((h + 1) % 24):02d}:00" if h != 23 else "23:00-00:00" for h in range(24)]
        ax.set_xticklabels(time_labels, rotation=45, ha="right", fontsize=9)

        title_text = f"DAM 市场 {self.date_str} 电价 (阈值: ${self.threshold})"

        ax.set_xlabel("时段 (Hour Ending)")
        ax.set_ylabel("价格 ($/MWh)")
        ax.set_title(title_text, fontsize=12)

        ax.grid(axis="y")
        ax.legend(fontsize=9, loc='upper right')

        fig.tight_layout(pad=0.5)

        self.layout.addWidget(self.canvas)
        self.setMinimumWidth(800)
        self.setMinimumHeight(450)

    def update_data(self, new_data):
        """外部调用此方法更新数据并重绘图表"""
        self.data = new_data
        self.draw_chart()


# -------------------------------------------------------
# --- 3. 主窗口与定时器逻辑 ---
# -------------------------------------------------------
class DualChartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("电价数据实时对比与定时刷新")
        self.resize(850, 950)

        self.init_ui()
        self.init_charts()

        # 初始加载数据 (确保第一次显示时有数据)
        self.update_data_and_ui()

        # 设置定时器：每 30 分钟 (30 * 60 * 1000 毫秒) 触发一次
        REFRESH_INTERVAL_MS = 3 * 60 * 1000  # 30分钟
        # REFESH_INTERVAL_MS = 5 * 1000 # 快速测试：5秒钟

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data_and_ui)
        self.timer.start(REFRESH_INTERVAL_MS)

        print(f"定时刷新已启动，间隔 {REFRESH_INTERVAL_MS // 1000} 秒。")

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)

        # 1. 顶部总标题
        total_title = QLabel("DAM 市场电价垂直对比分析")
        total_title.setAlignment(Qt.AlignCenter)
        total_title.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 10px;")
        self.main_layout.addWidget(total_title)

        # 2. 刷新时间标签 (新的组件)
        self.time_label = QLabel("上次刷新时间: 首次加载")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 10pt; color: #3498db; padding-bottom: 5px;")
        self.main_layout.addWidget(self.time_label)

        # 3. 图表容器布局
        self.chart_container_layout = QVBoxLayout()
        self.main_layout.addLayout(self.chart_container_layout)

    def init_charts(self):
        """初始化图表组件，但不填充数据 (数据在 update_data_and_ui 中填充)"""

        # 清除旧的图表/标签
        while self.chart_container_layout.count():
            item = self.chart_container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        date_1 = date_to_string()  # 今天
        date_2 = date_to_string_tomorrow()  # 明天

        # 实例化 chart_1 (昨天数据)
        self.chart_1 = PriceBarChart({}, date_str=date_1, threshold=THRESHOLD_1)
        self.chart_container_layout.addWidget(self.chart_1)

        # 实例化 chart_2 (今天数据) 或 info_label
        self.chart_2_container = QWidget()  # 使用一个容器来放置 chart_2 或 info_label
        self.chart_container_layout.addWidget(self.chart_2_container)

    def update_data_and_ui(self):
        """定时器触发时调用的方法：获取数据、更新图表和时间标签"""
        print("--- 正在更新数据和 UI... ---")

        # 1. 获取新数据
        # 第一次获取数据时，假设 price_data_2 可能是空 (随机性演示)
        is_empty_on_first_run = (random.random() < 0.2 and self.chart_1.data == {})

        data1, data2 = fetch_simulated_price_data(is_today_empty=is_empty_on_first_run)
        date_2 = date_to_string_tomorrow()

        # 2. 更新图表 1 (昨天的数据)
        self.chart_1.update_data(data1)

        # 3. 更新图表 2 (今天的数据) 或显示提示
        self.update_chart_2(data2, date_2)

        # 4. 更新刷新时间标签
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.time_label.setText(f"上次刷新时间: {current_time}")

        print("--- 更新完成。 ---")

    def update_chart_2(self, data2, date_str):
        """根据数据是否存在，更新 chart_2_container 的内容"""

        # 清除 chart_2_container 中的所有现有组件
        container_layout = self.chart_2_container.layout()
        if container_layout is None:
            container_layout = QVBoxLayout(self.chart_2_container)
            container_layout.setContentsMargins(0, 0, 0, 0)

        # 删除所有子组件
        while container_layout.count():
            item = container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if data2:
            # 数据存在：创建并显示图表
            chart_2 = PriceBarChart(data2, date_str=date_str, threshold=THRESHOLD_2)
            container_layout.addWidget(chart_2)
        else:
            # 数据为空：创建并显示提示标签
            info_label = QLabel(f"--- {date_str} 的电价数据尚未获取或数据为空 ---")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-size: 14pt; color: #e74c3c; border: 2px dashed #e74c3c; padding: 50px;")
            container_layout.addWidget(info_label)

        # 强制刷新布局
        self.chart_2_container.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DualChartWindow()
    window.show()
    sys.exit(app.exec_())