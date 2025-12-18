import sys
import subprocess
import platform
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QGridLayout, QFrame
)
from PyQt5.QtMultimedia import QSoundEffect
from datetime import datetime

from ob_monitor import get_active_miner_and_hashrate


# ---------------- Ping 工作线程 ----------------
class PingWorker(QThread):
    result = pyqtSignal(bool)

    def __init__(self, ip):
        super().__init__()
        self.ip = ip

    def run(self):
        fail_count = 0
        system = platform.system()

        for _ in range(10):
            if system == "Windows":
                cmd = ["ping", "-n", "1", "-w", "1000", self.ip]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", self.ip]

            r = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if r.returncode != 0:
                fail_count += 1

        # ≥3 次失败判定离线
        self.result.emit(fail_count < 3)


# ---------------- 主界面 ----------------
class MonitorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.ip = "100.88.16.1"  # 示例 IP
        self.init_ui()
        self.init_sound()
        self.init_timer()

    def init_ui(self):
        self.setWindowTitle("矿机监控系统")
        self.setFixedSize(520, 300)

        layout = QGridLayout()
        layout.setSpacing(15)

        # 标题
        title = QLabel("矿机状态监控")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold;")
        layout.addWidget(title, 0, 0, 1, 2)

        # 数据展示
        self.ip_label = QLabel(f"IP：{self.ip}")
        self.miner_count_label = QLabel("矿机在线数：0")
        self.hashrate_label = QLabel("算力：0 TH/s")

        for lbl in (self.ip_label, self.miner_count_label, self.hashrate_label):
            lbl.setStyleSheet("font-size:16px;")

        layout.addWidget(self.ip_label, 1, 0)
        layout.addWidget(self.miner_count_label, 2, 0)
        layout.addWidget(self.hashrate_label, 3, 0)

        # 状态栏
        self.ip_status = self.make_status("未知")
        self.miner_status = self.make_status("未知")
        self.hashrate_status = self.make_status("未知")

        layout.addWidget(self.ip_status, 1, 1)
        layout.addWidget(self.miner_status, 2, 1)
        layout.addWidget(self.hashrate_status, 3, 1)

        # 按钮
        self.start_btn = QPushButton("开始监控")
        self.start_btn.clicked.connect(self.start_monitor)
        self.start_btn.setFixedHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size:16px;
                background:#2d89ef;
                color:white;
                border-radius:6px;
            }
            QPushButton:hover { background:#1e5fa8; }
        """)
        layout.addWidget(self.start_btn, 4, 0, 1, 2)
        self.update_time_label = QLabel("最后更新时间：--")
        self.update_time_label.setAlignment(Qt.AlignCenter)
        self.update_time_label.setStyleSheet("""
            QLabel {
                color:#aaa;
                font-size:12px;
            }
        """)
        layout.addWidget(self.update_time_label, 5, 0, 1, 2)
        self.setLayout(layout)

    def make_status(self, text):
        frame = QFrame()
        frame.setFixedHeight(32)
        frame.setStyleSheet("""
            QFrame {
                border-radius:8px;
                background:#555;
            }
        """)

        layout = QGridLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color:white;
                font-weight:bold;
                font-size:14px;
            }
        """)

        layout.addWidget(label)
        frame.label = label  # 关键：保存引用，方便后续改字

        return frame

    def set_status(self, frame, text, ok=True):
        color = "#2ecc71" if ok else "#e74c3c"
        frame.setStyleSheet(f"""
            QFrame {{
                border-radius:6px;
                background:{color};
                color:white;
                font-weight:bold;
            }}
        """)
        frame.label.setText(text)

    def init_sound(self):
        self.alarm = QSoundEffect()
        self.alarm.setSource(QUrl.fromLocalFile("alarm.wav"))
        self.alarm.setLoopCount(QSoundEffect.Infinite)
        self.alarm.setVolume(0.8)

    def init_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_ip)

    def start_monitor(self):
        self.start_btn.setEnabled(False)
        self.check_ip()
        self.timer.start(5 * 60 * 1000)  # 5 分钟

    def check_ip(self):
        self.worker = PingWorker(self.ip)
        self.worker.result.connect(self.on_ping_result)
        self.worker.start()

    def on_ping_result(self, online):
        self.update_time()  # 👈 更新时间
        if online:
            self.set_status(self.ip_status, "在线", True)
            self.alarm.stop()
        else:
            self.set_status(self.ip_status, "离线", False)
            if not self.alarm.isPlaying():
                self.alarm.play()

    def update_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_time_label.setText(f"最后更新时间：{now}")
        ac, ah = get_active_miner_and_hashrate()
        self.miner_count_label.setText(f"矿机在线数：{ac}")
        self.hashrate_label.setText(f"算力：{ah} TH/s")


# ---------------- 入口 ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = MonitorUI()
    ui.show()
    sys.exit(app.exec_())
