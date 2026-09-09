#!/usr/bin/env python3
import sys
import os
import signal
import datetime
import calendar as py_calendar
import nepali_datetime
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

PID_FILE = "/tmp/waybar_calendar.pid"

# Toggle: if already open, close it
if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE, "r") as f:
            old_pid = int(f.read().strip())
        if old_pid != os.getpid():
            os.kill(old_pid, signal.SIGTERM)
            os.remove(PID_FILE)
            sys.exit(0)
    except (ProcessLookupError, ValueError):
        pass
    except Exception:
        pass

with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

def cleanup(*_):
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception:
        pass
    Gtk.main_quit()

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

DEV_NUMS = str.maketrans("0123456789", "०१२३४५६७८९")
def to_dev(n):
    return str(n).translate(DEV_NUMS)

NEPALI_MONTHS_EN = [
    "", "Baisakh", "Jestha", "Asar", "Shrawan", "Bhadra",
    "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"
]
NEPALI_MONTHS_NP = [
    "", "वैशाख", "जेठ", "असार", "साउन", "भदौ",
    "असोज", "कार्तिक", "मंसिर", "पुस", "माघ", "फागुन", "चैत"
]

DAYS_EN = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
DAYS_NP = ["आइ", "सो", "मङ्", "बुध", "बिहि", "शुक्र", "शनि"]

MINIMAL_CSS = """
* {
    font-family: "JetBrainsMono Nerd Font Propo", "JetBrainsMono NFP", "DejaVu Sans Mono", monospace;
    font-size: 12px;
}

window {
    background-color: transparent;
}

.calendar-box {
    background-color: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 0px;
    padding: 12px 14px;
    color: #000000;
}

.title-text {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #000000;
}

.sub-title {
    font-size: 10px;
    color: rgba(0, 0, 0, 0.45);
    margin-top: 1px;
    margin-bottom: 8px;
}

.mode-btn {
    border: 1px solid transparent;
    border-radius: 0px;
    background: transparent;
    padding: 1px 5px;
    font-size: 10px;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.4);
}

.mode-btn:hover {
    color: #000000;
}

.mode-btn.active {
    color: #000000;
    font-weight: 800;
    border-bottom: 2px solid #000000;
}

.mode-sep {
    color: rgba(0, 0, 0, 0.2);
    font-size: 10px;
    padding: 0 2px;
}

.nav-btn {
    border: none;
    border-radius: 0px;
    background: transparent;
    color: rgba(0, 0, 0, 0.5);
    font-size: 12px;
    font-weight: 700;
    padding: 0 4px;
    min-width: 16px;
    min-height: 16px;
}

.nav-btn:hover {
    color: #000000;
    background-color: rgba(0, 0, 0, 0.05);
}

.header-cell {
    font-size: 10px;
    font-weight: 700;
    color: rgba(0, 0, 0, 0.35);
    padding: 4px 0;
    min-width: 28px;
}

.day-cell {
    font-size: 11px;
    font-weight: 500;
    color: #000000;
    min-width: 28px;
    min-height: 24px;
    border-radius: 0px;
    padding: 2px 0;
}

.day-cell:hover {
    background-color: rgba(0, 0, 0, 0.06);
}

.day-cell.dim {
    color: rgba(0, 0, 0, 0.18);
}

.day-cell.today {
    background-color: #000000;
    color: #ffffff;
    font-weight: 800;
}

.day-cell.today:hover {
    background-color: #222222;
}

.divider {
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    margin: 6px 0;
}
"""

class MinimalCalendar(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.mode = "EN"
        self.today_en = datetime.date.today()
        self.today_np = nepali_datetime.date.today()

        self.view_en_y = self.today_en.year
        self.view_en_m = self.today_en.month

        self.view_np_y = self.today_np.year
        self.view_np_m = self.today_np.month

        self.setup_window()
        self.setup_css()
        self.build_ui()
        self.render()

    def setup_window(self):
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
                     GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self, edge, True)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.connect("destroy", cleanup)
        self.connect("key-press-event", self.on_key_press)

    def setup_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(MINIMAL_CSS.encode())
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_key_press(self, widget, event):
        if event.keyval in (Gdk.KEY_Escape, Gdk.KEY_q):
            cleanup()
            return True
        elif event.keyval == Gdk.KEY_Left:
            self.nav(-1)
            return True
        elif event.keyval == Gdk.KEY_Right:
            self.nav(1)
            return True
        elif event.keyval in (Gdk.KEY_t, Gdk.KEY_T):
            self.jump_today()
            return True
        return False

    def build_ui(self):
        # Fullscreen click-catcher to dismiss
        backdrop = Gtk.EventBox()
        backdrop.connect("button-press-event", lambda *_: cleanup())

        # Alignment container: top right beside waybar
        align = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        align.set_halign(Gtk.Align.END)
        align.set_valign(Gtk.Align.START)
        align.set_margin_top(8)
        align.set_margin_end(44)

        # Content card
        card_event = Gtk.EventBox()
        card_event.connect("button-press-event", lambda w, e: True)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.get_style_context().add_class("calendar-box")

        # Row 1: Nav + Title + EN/NP Toggle
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        btn_prev = Gtk.Button(label="<")
        btn_prev.get_style_context().add_class("nav-btn")
        btn_prev.connect("clicked", lambda *_: self.nav(-1))

        self.title_lbl = Gtk.Label()
        self.title_lbl.get_style_context().add_class("title-text")
        self.title_lbl.set_xalign(0)

        btn_next = Gtk.Button(label=">")
        btn_next.get_style_context().add_class("nav-btn")
        btn_next.connect("clicked", lambda *_: self.nav(1))

        top_row.pack_start(btn_prev, False, False, 0)
        top_row.pack_start(self.title_lbl, False, False, 2)
        top_row.pack_start(btn_next, False, False, 0)

        # Mode switch (EN | NP)
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mode_box.set_halign(Gtk.Align.END)

        self.btn_en = Gtk.Button(label="EN")
        self.btn_en.get_style_context().add_class("mode-btn")
        self.btn_en.get_style_context().add_class("active")
        self.btn_en.connect("clicked", lambda *_: self.set_mode("EN"))

        sep = Gtk.Label(label="/")
        sep.get_style_context().add_class("mode-sep")

        self.btn_np = Gtk.Button(label="NP")
        self.btn_np.get_style_context().add_class("mode-btn")
        self.btn_np.connect("clicked", lambda *_: self.set_mode("NP"))

        mode_box.pack_start(self.btn_en, False, False, 0)
        mode_box.pack_start(sep, False, False, 0)
        mode_box.pack_start(self.btn_np, False, False, 0)

        top_row.pack_end(mode_box, False, False, 0)
        self.box.pack_start(top_row, False, False, 0)

        # Subtitle: Dual calendar info
        self.sub_lbl = Gtk.Label()
        self.sub_lbl.get_style_context().add_class("sub-title")
        self.sub_lbl.set_xalign(0)
        self.box.pack_start(self.sub_lbl, False, False, 0)

        # Weekdays header
        self.header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.header_lbls = []
        for _ in range(7):
            l = Gtk.Label()
            l.get_style_context().add_class("header-cell")
            l.set_xalign(0.5)
            self.header_row.pack_start(l, True, True, 0)
            self.header_lbls.append(l)
        self.box.pack_start(self.header_row, False, False, 0)

        # Days Grid
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(2)
        self.grid.set_column_spacing(2)
        self.box.pack_start(self.grid, False, False, 0)

        card_event.add(self.box)
        align.pack_start(card_event, False, False, 0)
        backdrop.add(align)
        self.add(backdrop)

    def set_mode(self, m):
        if self.mode == m:
            return
        self.mode = m
        if m == "EN":
            self.btn_en.get_style_context().add_class("active")
            self.btn_np.get_style_context().remove_class("active")
        else:
            self.btn_np.get_style_context().add_class("active")
            self.btn_en.get_style_context().remove_class("active")
        self.render()

    def jump_today(self):
        if self.mode == "EN":
            self.view_en_y = self.today_en.year
            self.view_en_m = self.today_en.month
        else:
            self.view_np_y = self.today_np.year
            self.view_np_m = self.today_np.month
        self.render()

    def nav(self, step):
        if self.mode == "EN":
            m = self.view_en_m + step
            y = self.view_en_y
            if m < 1:
                m = 12
                y -= 1
            elif m > 12:
                m = 1
                y += 1
            self.view_en_m = m
            self.view_en_y = y
        else:
            m = self.view_np_m + step
            y = self.view_np_y
            if m < 1:
                m = 12
                y -= 1
            elif m > 12:
                m = 1
                y += 1
            self.view_np_m = m
            self.view_np_y = y
        self.render()

    def render(self):
        for ch in self.grid.get_children():
            self.grid.remove(ch)

        if self.mode == "EN":
            self.render_en()
        else:
            self.render_np()
        self.show_all()

    def render_en(self):
        # Headers
        for i, d in enumerate(DAYS_EN):
            self.header_lbls[i].set_text(d)

        # Title
        m_name = py_calendar.month_name[self.view_en_m]
        self.title_lbl.set_text(f"{m_name.upper()} {self.view_en_y}")

        # Subtitle
        np_str = self.today_np.strftime("%K %N %D, %G")
        self.sub_lbl.set_text(f"BS: {np_str}")

        cal = py_calendar.Calendar(firstweekday=6)  # Sun = 6
        weeks = cal.monthdayscalendar(self.view_en_y, self.view_en_m)

        prev_y = self.view_en_y if self.view_en_m > 1 else self.view_en_y - 1
        prev_m = self.view_en_m - 1 if self.view_en_m > 1 else 12
        _, prev_days_count = py_calendar.monthrange(prev_y, prev_m)

        matrix = []
        for w_idx, week in enumerate(weeks):
            row = []
            for d_idx, day in enumerate(week):
                if day != 0:
                    row.append({'val': day, 'curr': True})
                else:
                    if w_idx == 0:
                        zeros = week.count(0)
                        v = prev_days_count - zeros + d_idx + 1
                        row.append({'val': v, 'curr': False})
                    else:
                        row.append({'val': 0, 'curr': False})
            matrix.append(row)

        next_d = 1
        for row in matrix:
            for item in row:
                if item['val'] == 0:
                    item['val'] = next_d
                    next_d += 1

        for r_idx, row in enumerate(matrix):
            for c_idx, item in enumerate(row):
                day_val = item['val']
                lbl = Gtk.Label(label=f"{day_val:2d}")
                lbl.get_style_context().add_class("day-cell")
                lbl.set_xalign(0.5)
                if not item['curr']:
                    lbl.get_style_context().add_class("dim")
                if (item['curr'] and
                    day_val == self.today_en.day and
                    self.view_en_m == self.today_en.month and
                    self.view_en_y == self.today_en.year):
                    lbl.get_style_context().add_class("today")
                self.grid.attach(lbl, c_idx, r_idx, 1, 1)

    def render_np(self):
        # Headers
        for i, d in enumerate(DAYS_NP):
            self.header_lbls[i].set_text(d)

        # Title
        m_np = NEPALI_MONTHS_NP[self.view_np_m]
        m_en = NEPALI_MONTHS_EN[self.view_np_m]
        y_dev = to_dev(self.view_np_y)
        self.title_lbl.set_text(f"{m_np} {y_dev} ({m_en})")

        # Subtitle
        en_str = self.today_en.strftime("%a, %d %b %Y")
        self.sub_lbl.set_text(f"AD: {en_str}")

        total_days = nepali_datetime._days_in_month(self.view_np_y, self.view_np_m)
        first_day = nepali_datetime.date(self.view_np_y, self.view_np_m, 1)
        start_col = first_day.weekday()  # 0=Sun ... 6=Sat

        prev_y = self.view_np_y if self.view_np_m > 1 else self.view_np_y - 1
        prev_m = self.view_np_m - 1 if self.view_np_m > 1 else 12
        prev_total = nepali_datetime._days_in_month(prev_y, prev_m)

        matrix = []
        week = []
        for i in range(start_col):
            week.append({'val': prev_total - start_col + 1 + i, 'curr': False})

        for d in range(1, total_days + 1):
            week.append({'val': d, 'curr': True})
            if len(week) == 7:
                matrix.append(week)
                week = []

        if week:
            next_d = 1
            while len(week) < 7:
                week.append({'val': next_d, 'curr': False})
                next_d += 1
            matrix.append(week)

        for r_idx, row in enumerate(matrix):
            for c_idx, item in enumerate(row):
                day_val = item['val']
                lbl = Gtk.Label(label=to_dev(day_val))
                lbl.get_style_context().add_class("day-cell")
                lbl.set_xalign(0.5)
                if not item['curr']:
                    lbl.get_style_context().add_class("dim")
                if (item['curr'] and
                    day_val == self.today_np.day and
                    self.view_np_m == self.today_np.month and
                    self.view_np_y == self.today_np.year):
                    lbl.get_style_context().add_class("today")
                self.grid.attach(lbl, c_idx, r_idx, 1, 1)

def main():
    app = MinimalCalendar()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
