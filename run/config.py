from dataclasses import dataclass
from pathlib import Path

# * Directory path  -> ใช้ตำแหน่งไฟล์นี้เป็นฐาน
BASE_DIR = Path(__file__).resolve().parent  # * = .../Project.Omic-UV/run
ICON_DIR = BASE_DIR / "icon"
SAVE_BASE = BASE_DIR / "saved"

@dataclass(frozen=True)
class Paths:
    base: Path = BASE_DIR
    icons: Path = ICON_DIR
    bg_image: Path = ICON_DIR / "background_2.png"
    icon_ready: Path = ICON_DIR / "ready.png"
    icon_ok: Path = ICON_DIR / "OK.png"
    icon_not: Path = ICON_DIR / "NOT.png"
    icon_durian: Path = ICON_DIR / "durian.png"
    icon_by2: Path = ICON_DIR / "BY2.png"
    icon_nstda: Path = ICON_DIR / "NSTDA.png"
    icon_biotec: Path = ICON_DIR / "biotec.png"
    icon_noc: Path = ICON_DIR / "NOC.png"
    icon_nfed: Path = ICON_DIR / "nfed.png"
    save_base: Path = SAVE_BASE
    save_images: Path = SAVE_BASE / "images"
    save_logs: Path = SAVE_BASE / "logs"

@dataclass(frozen=True)
class Meta:
    version_text: str = "git 1.0"   # * <-- Version software

@dataclass(frozen=True)
class UI:
    window_title: str = "OMIC UV Light measurement"
    window_w: int = 1600
    window_h: int = 900
    image_label_geom: tuple[int, int, int, int] = (120, 140, 640, 480)
    bg_box_geom: tuple[int, int, int, int] = (100, 120, 1040, 510)

@dataclass(frozen=True)
class Camera:
    # * ขนาดพรีวิวจาก Picamera2
    preview_size: tuple[int, int] = (640, 480)
    # * คอนโทรลกล้องเริ่มต้น
    controls: dict = None

    def __init__(self):
        object.__setattr__(self, "controls", {
            "AfMode": 0,                # * fixed focus
            "LensPosition": 10,         # * ปรับตามชุดเลนส์/ความห่าง
            "AwbEnable": False
        })

@dataclass(frozen=True)
class Processing:
    roi_window_size: int = 5            # *   กรอบเฉลี่ยจุดกลาง 5x5
    ema_alpha: float = 0.2              # *   smoothing factor
    gb_fail_threshold: float = 0.45
    gb_pass_min: float = 0.2            # *   >0.2 และ <= fail_threshold = PASS
    history_len: int = 10
    timer_ms: int = 30                  # *   frame update interval

@dataclass(frozen=True)
class Hardware:
    led_pin: int = 23                   # *   gpiozero LED pin

@dataclass(frozen=True)
class Flags:
    hide_debug_labels: bool = True      # *     ซ่อน R,G,B,G/B บนจอ
    verbose_console: bool = True        # *     print ค่าบางส่วนใน terminal

@dataclass(frozen=True)
class Config:
    paths: Paths = Paths()
    ui: UI = UI()
    camera: Camera = Camera()
    processing: Processing = Processing()
    hardware: Hardware = Hardware()
    flags: Flags = Flags()
    meta: Meta = Meta() 

# * instance พร้อมใช้
cfg = Config()