#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtCore import QCoreApplication, QSize, Qt, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QColor, QPainterPath
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QAbstractButton, QMessageBox, QGraphicsDropShadowEffect)
from datetime import datetime
import cv2, os, csv

from gpiozero import LED
from picamera2 import Picamera2

from config import cfg 

# todo: ------------------------------< Utilities >------------------------------
def safe_pixmap(path_str: str) -> QPixmap:
    pm = QPixmap(path_str)
    if pm.isNull():
        pm = QPixmap(1, 1)
        pm.fill(Qt.GlobalColor.transparent)
        if cfg.flags.verbose_console:
            print(f"[warn] Cannot load pixmap: {path_str}")
    return pm


# todo: ------------------------------< component : toggle LED switch  >------------------------------
class ToggleSwitch(QAbstractButton):
    stateChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(50, 28)
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#4cd964") if self.isChecked() else QColor("#ccc"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect(), 14, 14)
        handle_rect = QRect(2, 2, 24, 24) if not self.isChecked() else QRect(24, 2, 24, 24)
        p.setBrush(QColor("white"))
        p.drawEllipse(handle_rect)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.stateChanged.emit(Qt.CheckState.Checked if self.isChecked() else Qt.CheckState.Unchecked)
        self.update()


# *** : ////////////////////////////////////// < MAIN WINDOW  > ////////////////////////////////////// ***
class MainWindow(QWidget):

    # * ////////////////////////////////////// < Initialize >
    def __init__(self):
        super().__init__()

        self.setWindowTitle(cfg.ui.window_title)
        self.setFixedSize(QSize(cfg.ui.window_w, cfg.ui.window_h))

        header_font = QFont("Prompt", 20, QFont.Weight.Bold)
        label_font1  = QFont("Prompt", 18)
        label_font2  = QFont("Prompt", 14)

        # * --------------------------------------------------< Header logo >
        lb = QLabel(self)
        lb.setGeometry(450, 20, 400, 80)
        lb.setPixmap(safe_pixmap(str(cfg.paths.icon_by2)).scaled(
            lb.width(), lb.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

        # * --------------------------------------------------< Camera preview area >
        x,y,w,h = cfg.ui.image_label_geom
        self.image_label = QLabel(self)
        self.image_label.setGeometry(x,y,w,h)
        self.image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px solid #aaa;
            border-radius: 12px;
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(4)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.image_label.setGraphicsEffect(shadow)

        # * --------------------------------------------------< Other logo >
        self.durian_label = QLabel(self)
        self.durian_label.setGeometry(350, 20, 80, 80)
        self.durian_label.setPixmap(safe_pixmap(str(cfg.paths.icon_durian)).scaled(
            80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        self.durian_label.setStyleSheet("background-color: transparent;")

        self.nstda_label = QLabel(self)
        self.nstda_label.setGeometry(30, 600, 150, 150)
        self.nstda_label.setPixmap(safe_pixmap(str(cfg.paths.icon_nstda)).scaled(
            150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        self.nstda_label.setStyleSheet("background-color: transparent;")

        self.biotec_label = QLabel(self)
        self.biotec_label.setGeometry(200, 590, 170, 170)
        self.biotec_label.setPixmap(safe_pixmap(str(cfg.paths.icon_biotec)).scaled(
            170, 170, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        self.biotec_label.setStyleSheet("background-color: transparent;")

        self.noc_label = QLabel(self)
        self.noc_label.setGeometry(400, 650, 50, 50)
        self.noc_label.setPixmap(safe_pixmap(str(cfg.paths.icon_noc)).scaled(
            50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        self.noc_label.setStyleSheet("background-color: transparent;")

        self.nfed_label = QLabel(self)
        self.nfed_label.setGeometry(480, 610, 150, 150)
        self.nfed_label.setPixmap(safe_pixmap(str(cfg.paths.icon_nfed)).scaled(
            150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        self.nfed_label.setStyleSheet("background-color: transparent;")


        # * --------------------------------------------------< Main Background box I >
        bx,by,bw,bh = cfg.ui.bg_box_geom
        self.bg_box = QLabel(self); self.bg_box.setGeometry(bx,by,bw,bh)
        self.bg_box.setStyleSheet("""
            background-color: rgb(255, 250, 200);
            border: 1px solid #555;
            border-radius: 16px;
        """)
        self.bg_box.lower()

        # * --------------------------------------------------< G/B Parameter (default: hide) >
        self.x_value_label = QLabel("G/B = N/A", self)
        self.x_value_label.setFont(QFont("Prompt", 12))
        self.x_value_label.move(870, 330)
        self.x_value_label.resize(400, 30)

        # * --------------------------------------------------< G/B Parameter (default: hide) >
        self.result_icon = QLabel(self)
        self.result_icon.setGeometry(700, -25, 500, 500)
        self.result_icon.setStyleSheet("background-color: transparent;")
        self.ready_icon_path = str(cfg.paths.icon_ready)
        self.reset_icon_timer = QTimer(self)
        self.reset_icon_timer.setSingleShot(True)
        self.reset_icon_timer.timeout.connect(self.reset_ready_icon)

        self.result_icon.setPixmap(safe_pixmap(self.ready_icon_path).scaled(
            self.result_icon.width(), self.result_icon.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))

        # * --------------------------------------------------< G/B Parameter (default: hide) >
        self.rgb_value_label = QLabel("R=0 G=0 B=0", self)
        self.rgb_value_label.setFont(QFont("Prompt", 12))
        self.rgb_value_label.move(870, 270)
        self.rgb_value_label.resize(400, 30)

        self.gb_avg_label = QLabel("G/B Avg(10): N/A", self)
        self.gb_avg_label.setFont(QFont("Prompt", 12))
        self.gb_avg_label.move(870, 300)
        self.gb_avg_label.resize(400, 30)

        # * ==================================================< toggle LED switch >
        # * ----------------------------------< "ปิด / เปิด" >
        on_off_label = QLabel("ปิด / เปิด", self)
        on_off_label.setFont(label_font2)
        on_off_label.move(825, 350)

        # * ----------------------------------< Position --> component : toggle LED switch >
        self.led_switch = ToggleSwitch(self)
        self.led_switch.move(835, 380)
        self.led_switch.stateChanged.connect(self.toggle_led)

        # * ----------------------------------< "แสงไฟส่องสว่าง" >
        led_label = QLabel("แสงไฟส่องสว่าง", self)
        led_label.setFont(label_font1)
        led_label.move(900, 375)

        # * --------------------------------------------------< "ปุ่ม Analyze" >
        self.btn = QPushButton("วิเคราะห์ผล", self)
        self.btn.setGeometry(790, 470, 320, 110)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 35px;
                font-weight: bold;
                font-family: Prompt;
            }
        """)
        self.btn.clicked.connect(self.analyze_capture)

        # * --------------------------------------------------< "Exit button" >
        self.exit_btn = QPushButton("X", self)
        self.exit_btn.setGeometry(5, 5, 40, 40)
        self.exit_btn.setStyleSheet("background-color: #dc3545; color: white; font-size: 20px; font-weight: bold; border-radius: 5px;")
        self.exit_btn.clicked.connect(self.exit_app)

        # * --------------------------------------------------< กล้อง > 
        self.picam2 = Picamera2()
        video_config = self.picam2.create_preview_configuration(main={"size": cfg.camera.preview_size})
        self.picam2.configure(video_config)
        self.picam2.start()
        self.picam2.set_controls(cfg.camera.controls)

        # * --------------------------------------------------< EMA smoothing > 
        self.ema_r = 0.0; self.ema_g = 0.0; self.ema_b = 0.0
        self.alpha  = cfg.processing.ema_alpha

        # * --------------------------------------------------< G/B history > 
        self.gb_ratio_list: list[float] = []
        self.rgb_history: list[tuple[int,int,int,float]] = []
        self.avg_ratio: float | None = None

        # * --------------------------------------------------< Timer >
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(cfg.processing.timer_ms)

        # * --------------------------------------------------< LED >
        self.led = LED(cfg.hardware.led_pin)

        # * --------------------------------------------------< ปิด debug labels ตาม flagz >
        if cfg.flags.hide_debug_labels:
            self.rgb_value_label.hide()
            self.gb_avg_label.hide()
            self.x_value_label.hide()

    # * ////////////////////////////////////// < Additional function for main window >
    def paintEvent(self, event):
        painter = QPainter(self)
        bg_pm = safe_pixmap(str(cfg.paths.bg_image))
        scaled = bg_pm.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        painter.drawPixmap(self.rect(), scaled)

    def toggle_led(self, state):
        if self.led_switch.isChecked():
            self.led.on()
        else:
            self.led.off()


    # * ////////////////////////////////////// < Update Frame & Process from Camera >
    def update_frame(self):
        frame = self.picam2.capture_array()
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

        # * --------------------------------------------------< calculating >
        h, w, _ = rgb_frame.shape
        cy, cx = h // 2, w // 2

        win = cfg.processing.roi_window_size
        half = win // 2
        crop = rgb_frame[cy-half:cy+half+1, cx-half:cx+half+1, :]

        mean_rgb = crop.mean(axis=(0, 1))
        r_avg, g_avg, b_avg = map(int, mean_rgb)

        self.ema_r = self.alpha * r_avg + (1 - self.alpha) * self.ema_r
        self.ema_g = self.alpha * g_avg + (1 - self.alpha) * self.ema_g
        self.ema_b = self.alpha * b_avg + (1 - self.alpha) * self.ema_b

        ratio = round(self.ema_g / self.ema_b, 3) if self.ema_b != 0 else 0.0

        self.gb_ratio_list.append(ratio)
        self.rgb_history.append((int(self.ema_r), int(self.ema_g), int(self.ema_b), ratio))

        if len(self.gb_ratio_list) > cfg.processing.history_len:
            self.gb_ratio_list.pop(0)
            self.rgb_history.pop(0)

        if len(self.gb_ratio_list) == cfg.processing.history_len:
            self.avg_ratio = round(sum(self.gb_ratio_list) / len(self.gb_ratio_list), 3)
            self.gb_avg_label.setText(f"G/B Avg({cfg.processing.history_len}): {self.avg_ratio}")
            if cfg.flags.verbose_console:
                print(f"G/B list: {self.gb_ratio_list} -> avg: {self.avg_ratio}")
            self.x_value_label.setText(f"G/B = {self.avg_ratio}")
        else:
            self.avg_ratio = None
            self.gb_avg_label.setText(f"G/B Avg({cfg.processing.history_len}): N/A")
            self.x_value_label.setText("G/B = N/A")

        # * --------------------------------------------------< crosshair position for measuring color RGB >
        cv2.circle(rgb_frame, (cx, cy), 10, (255, 255, 255), 2)

        # * --------------------------------------------------< แสดงภาพ >
        bytes_per_line = 3 * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pm = QPixmap.fromImage(qimg).scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        rounded = QPixmap(pm.size()); rounded.fill(Qt.GlobalColor.transparent)
        p = QPainter(rounded); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(0, 0, pm.width(), pm.height(), 16, 16)
        p.setClipPath(path); p.drawPixmap(0, 0, pm); p.end()
        self.image_label.setPixmap(rounded)

        self.rgb_value_label.setText(f"R = {int(self.ema_r)} G = {int(self.ema_g)} B = {int(self.ema_b)}")


        # * --------------------------------------------------< Result: โชว์ภาพ Icon ตามCondition >
        if self.avg_ratio is None:
            icon_path = str(cfg.paths.icon_ready)
        else:
            if self.avg_ratio > cfg.processing.gb_fail_threshold:
                icon_path = str(cfg.paths.icon_not)
            elif self.avg_ratio > cfg.processing.gb_pass_min:
                icon_path = str(cfg.paths.icon_ok)
            else:
                icon_path = str(cfg.paths.icon_ready)

        self.result_icon.setPixmap(safe_pixmap(icon_path).scaled(
            self.result_icon.width(), self.result_icon.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))


    # * ////////////////////////////////////// < Analyze & Capture >
    def analyze_capture(self):

        # * --------------------------------------------------< ชื่อไฟล์: {YYYY.MM.DD}_{HH.MM.SS} >
        base_stamp = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        final_name = base_stamp

        # * --------------------------------------------------< เตรียมโฟลเดอร์ >
        try:
            cfg.paths.save_images.mkdir(parents=True, exist_ok=True)
            cfg.paths.save_logs.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[mkdir failed] {e}")

        # * --------------------------------------------------< ป้องกันชื่อซ้ำ >
        img_path = cfg.paths.save_images / f"{final_name}.png"
        csv_path = cfg.paths.save_logs / f"{final_name}.csv"
        idx = 1
        while img_path.exists() or csv_path.exists():
            final_name = f"{base_stamp}_{idx:02d}"
            img_path = cfg.paths.save_images / f"{final_name}.png"
            csv_path = cfg.paths.save_logs / f"{final_name}.csv"
            idx += 1

        # * --------------------------------------------------< Save PNG >
        try:
            pixmap = self.grab()
            pixmap.save(str(img_path))
        except Exception as e:
            print(f"[Save PNG Error] {e}")

        # * --------------------------------------------------< Save CSV >
        try:
            with open(csv_path, mode='w', newline='') as f:
                w = csv.writer(f)
                w.writerow(["Timestamp", final_name])
                w.writerow([])
                w.writerow(["Index", "R", "G", "B", "G/B"])
                for i, (r, g, b, gb) in enumerate(self.rgb_history, start=1):
                    w.writerow([i, r, g, b, gb])

                if self.gb_ratio_list:
                    avg_ratio_csv = round(sum(self.gb_ratio_list) / len(self.gb_ratio_list), 3)
                else:
                    avg_ratio_csv = "N/A"
                w.writerow([])
                w.writerow([f"Average G/B (last up to {cfg.processing.history_len})", avg_ratio_csv])
        except Exception as e:
            print(f"[Save CSV Failed] {e}")

        # * --------------------------------------------------< Show Pop-up >
        msg = QMessageBox(self)
        msg.setWindowTitle("Capture Saved")

        msg.setText(f"""
        <p align='center' style="font-family:Prompt; font-size:20px;">  
        บันทึกไฟล์เรียบร้อย<br>
        ภาพ: {img_path.name}<br>
        log: {csv_path.name}
        </p>
        """)

        msg.setStyleSheet("""
            QPushButton {
                font-family: Prompt;
                font-size: 25px;
                padding: 10px 12px;
            }
        """)

        msg.exec()

        # * --------------------------------------------------< Time interval >
        self.reset_icon_timer.start(10_000)


    # * --------------------------------------------------< for G/B icon reset >
    def reset_ready_icon(self):
        self.result_icon.setPixmap(safe_pixmap(self.ready_icon_path).scaled(
            self.result_icon.width(), self.result_icon.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))

    def closeEvent(self, event):
        try:
            self.timer.stop()
            self.picam2.stop()
        except Exception as e:
            print(f"[closeEvent warn] {e}")
        event.accept()

    def exit_app(self):
        self.close()

# ---------- App bootstrap ----------
app = QCoreApplication.instance()
if app is None:
    app = QApplication([])

window = MainWindow()
window.showFullScreen()
app.exec()