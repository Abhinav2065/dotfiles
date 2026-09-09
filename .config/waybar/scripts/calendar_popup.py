#!/usr/bin/env python3
import sys
import os
import signal
import datetime
import calendar
import nepali_datetime
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell

PID_FILE = "/tmp/waybar_calendar.pid"

# Check toggle: if already running, kill the old process and exit
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
def to_devanagari(n):
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
DAYS_NP = ["आइ", "सोम", "मङ्ग", "बुध", "बिही", "शुक्र", "शनि"]

CSS_DATA = """
window {
    background-color: transparent;
}

.calendar-card {
    background-color: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    padding: 18px;
    min-width: 320px;
}

.time-label {
    font-size: 26px;
    font-weight: 900;
    color: #000000;
    font-family: "JetBrainsMono Nerd Font Propo", "JetBrainsMono NFP", monospace;
}

.date-label {
    font-size: 12px;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.55);
}

.toggle-container {
    background-color: #f0f0f0;
    border-radius: 8px;
    padding: 2px;
}

.lang-btn {
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
    color: rgba(0, 0, 0, 0.6);
    background-color: transparent;
    border: none;
    transition: all 0.15s ease;
}

.lang-btn:hover {
    color: #000000;
}

.lang-btn.active {
    background-color: #000000;
    color: #ffffff;
}

.nav-bar {
    margin-top: 14px;
    margin-bottom: 8px;
}

.nav-title {
    font-size: 14px;
    font-weight: 800;
    color: #000000;
}

.nav-arrow {
    background-color: #f5f5f5;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 6px;
    color: #000000;
    font-size: 15px;
    font-weight: 700;
    min-width: 28px;
    min-height: 28px;
    padding: 2px 8px;
}

.nav-arrow:hover {
    background-color: #000000;
    color: #ffffff;
}

.today-btn {
    background-color: #f5f5f5;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 6px;
    color: #000000;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 8px;
}

.today-btn:hover {
    background-color: #000000;
    color: #ffffff;
}

.weekday-header {
    font-size: 11px;
    font-weight: 700;
    color: rgba(0, 0, 0, 0.45);
    padding: 6px 0;
    min-width: 38px;
}

.weekday-header.sat {
    color: #d20f39;
}

.day-cell {
    min-width: 38px;
    min-height: 34px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: #000000;
}

.day-cell:hover {
    background-color: #f2f2f2;
}

.day-cell.other-month {
    color: rgba(0, 0, 0, 0.22);
}

.day-cell.saturday {
    color: #c02040;
}

.day-cell.other-month.saturday {
    color: rgba(192, 32, 64, 0.25);
}

.day-cell.today {
    background-color: #000000;
    color: #ffffff;
    font-weight: 900;
    border-radius: 8px;
}

.day-cell.today:hover {
    background-color: #262626;
}

.footer-box {
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.footer-text {
    font-size: 11px;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.55);
}
"""

class CalendarApp(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.mode = "EN"  # "EN" or "NP"
        self.today_greg = datetime.date.today()
        self.today_nep = nepali_datetime.date.today()

        self.cur_greg_year = self.today_greg.year
        self.cur_greg_month = self.today_greg.month

        self.cur_nep_year = self.today_nep.year
        self.cur_nep_month = self.today_nep.month

        self.setup_window()
        self.setup_css()
        self.build_ui()
        self.update_calendar()

        GLib.timeout_add_seconds(1, self.update_clock)

    def setup_window(self):
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        # Fullscreen click catcher
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
                     GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self, edge, True)

        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        # Transparent window background
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.connect("destroy", cleanup)
        self.connect("key-press-event", self.on_key_press)

    def setup_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS_DATA.encode())
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            cleanup()
            return True
        return False

    def build_ui(self):
        # Click outside dismisser
        outer_event = Gtk.EventBox()
        outer_event.connect("button-press-event", lambda *_: cleanup())

        # Container positioning card at top-right
        align_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        align_box.set_halign(Gtk.Align.END)
        align_box.set_valign(Gtk.Align.START)
        align_box.set_margin_top(10)
        align_box.set_margin_end(48)  # 40px Waybar width + 8px gap

        # Prevent clicks inside card from closing
        card_event = Gtk.EventBox()
        card_event.connect("button-press-event", lambda w, e: True)

        self.card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.card.get_style_context().add_class("calendar-card")

        # Top Header (Time + Date + Lang Switcher)
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.time_label = Gtk.Label()
        self.time_label.set_xalign(0)
        self.time_label.get_style_context().add_class("time-label")

        self.date_label = Gtk.Label()
        self.date_label.set_xalign(0)
        self.date_label.get_style_context().add_class("date-label")

        title_box.pack_start(self.time_label, False, False, 0)
        title_box.pack_start(self.date_label, False, False, 0)
        header_box.pack_start(title_box, True, True, 0)

        # Language Toggle Switcher (EN / NP)
        toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        toggle_box.get_style_context().add_class("toggle-container")
        toggle_box.set_valign(Gtk.Align.CENTER)

        self.btn_en = Gtk.Button(label="EN")
        self.btn_en.get_style_context().add_class("lang-btn")
        self.btn_en.get_style_context().add_class("active")
        self.btn_en.connect("clicked", lambda *_: self.switch_mode("EN"))

        self.btn_np = Gtk.Button(label="NP")
        self.btn_np.get_style_context().add_class("lang-btn")
        self.btn_np.connect("clicked", lambda *_: self.switch_mode("NP"))

        toggle_box.pack_start(self.btn_en, False, False, 0)
        toggle_box.pack_start(self.btn_np, False, False, 0)
        header_box.pack_start(toggle_box, False, False, 0)

        self.card.pack_start(header_box, False, False, 0)

        # Navigation Bar (< Month Year Today >)
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        nav_box.get_style_context().add_class("nav-bar")

        btn_prev = Gtk.Button(label="‹")
        btn_prev.get_style_context().add_class("nav-arrow")
        btn_prev.connect("clicked", lambda *_: self.navigate_month(-1))

        self.nav_title = Gtk.Label()
        self.nav_title.get_style_context().add_class("nav-title")
        self.nav_title.set_xalign(0.5)

        btn_today = Gtk.Button(label="Today")
        btn_today.get_style_context().add_class("today-btn")
        btn_today.connect("clicked", lambda *_: self.jump_today())

        btn_next = Gtk.Button(label="›")
        btn_next.get_style_context().add_class("nav-arrow")
        btn_next.connect("clicked", lambda *_: self.navigate_month(1))

        nav_box.pack_start(btn_prev, False, False, 0)
        nav_box.pack_start(self.nav_title, True, True, 0)
        nav_box.pack_start(btn_today, False, False, 0)
        nav_box.pack_start(btn_next, False, False, 0)

        self.card.pack_start(nav_box, False, False, 0)

        # Days of Week Header
        self.weekdays_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.weekday_labels = []
        for i in range(7):
            lbl = Gtk.Label()
            lbl.get_style_context().add_class("weekday-header")
            lbl.set_xalign(0.5)
            if i == 6:  # Saturday
                lbl.get_style_context().add_class("sat")
            self.weekdays_box.pack_start(lbl, True, True, 0)
            self.weekday_labels.append(lbl)

        self.card.pack_start(self.weekdays_box, False, False, 0)

        # Calendar Grid
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(2)
        self.grid.set_column_spacing(2)
        self.card.pack_start(self.grid, False, False, 4)

        # Footer info (Dual Conversion)
        footer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        footer_box.get_style_context().add_class("footer-box")

        self.footer_label = Gtk.Label()
        self.footer_label.set_xalign(0)
        self.footer_label.set_use_markup(True)
        self.footer_label.get_style_context().add_class("footer-text")
        footer_box.pack_start(self.footer_label, False, False, 0)

        self.card.pack_start(footer_box, False, False, 0)

        card_event.add(self.card)
        align_box.pack_start(card_event, False, False, 0)
        outer_event.add(align_box)
        self.add(outer_event)

        self.update_clock()

    def update_clock(self):
        now = datetime.datetime.now()
        self.time_label.set_text(now.strftime("%H:%M:%S"))

        if self.mode == "EN":
            self.date_label.set_text(self.today_greg.strftime("%A, %d %B %Y"))
        else:
            np_today_str = self.today_nep.strftime("%K %N %D, %G")
            self.date_label.set_text(np_today_str)
        return True

    def switch_mode(self, mode):
        if self.mode == mode:
            return
        self.mode = mode
        if mode == "EN":
            self.btn_en.get_style_context().add_class("active")
            self.btn_np.get_style_context().remove_class("active")
        else:
            self.btn_np.get_style_context().add_class("active")
            self.btn_en.get_style_context().remove_class("active")
        self.update_clock()
        self.update_calendar()

    def jump_today(self):
        if self.mode == "EN":
            self.cur_greg_year = self.today_greg.year
            self.cur_greg_month = self.today_greg.month
        else:
            self.cur_nep_year = self.today_nep.year
            self.cur_nep_month = self.today_nep.month
        self.update_calendar()

    def navigate_month(self, step):
        if self.mode == "EN":
            m = self.cur_greg_month + step
            y = self.cur_greg_year
            if m < 1:
                m = 12
                y -= 1
            elif m > 12:
                m = 1
                y += 1
            self.cur_greg_month = m
            self.cur_greg_year = y
        else:
            m = self.cur_nep_month + step
            y = self.cur_nep_year
            if m < 1:
                m = 12
                y -= 1
            elif m > 12:
                m = 1
                y += 1
            self.cur_nep_month = m
            self.cur_nep_year = y
        self.update_calendar()

    def update_calendar(self):
        # Clear grid
        for child in self.grid.get_children():
            self.grid.remove(child)

        if self.mode == "EN":
            self.render_english_calendar()
        else:
            self.render_nepali_calendar()

        self.show_all()

    def render_english_calendar(self):
        # Update weekday headers
        for i, name in enumerate(DAYS_EN):
            self.weekday_labels[i].set_text(name)

        # Title
        month_name = calendar.month_name[self.cur_greg_month]
        self.nav_title.set_text(f"{month_name} {self.cur_greg_year}")

        cal = calendar.Calendar(firstweekday=6) # Sunday = 6
        weeks = cal.monthdayscalendar(self.cur_greg_year, self.cur_greg_month)

        prev_y = self.cur_greg_year if self.cur_greg_month > 1 else self.cur_greg_year - 1
        prev_m = self.cur_greg_month - 1 if self.cur_greg_month > 1 else 12
        _, prev_days_in_m = calendar.monthrange(prev_y, prev_m)

        grid_matrix = []
        for w_idx, week in enumerate(weeks):
            row = []
            for d_idx, day in enumerate(week):
                if day != 0:
                    row.append({'day': day, 'current': True})
                else:
                    if w_idx == 0:
                        count_zeros = week.count(0)
                        val = prev_days_in_m - count_zeros + d_idx + 1
                        row.append({'day': val, 'current': False})
                    else:
                        row.append({'day': 0, 'current': False})
            grid_matrix.append(row)

        next_val = 1
        for row in grid_matrix:
            for item in row:
                if item['day'] == 0:
                    item['day'] = next_val
                    next_val += 1

        for r_idx, row in enumerate(grid_matrix):
            for c_idx, item in enumerate(row):
                lbl = Gtk.Label(label=str(item['day']))
                lbl.set_xalign(0.5)
                lbl.get_style_context().add_class("day-cell")
                if not item['current']:
                    lbl.get_style_context().add_class("other-month")
                if c_idx == 6:
                    lbl.get_style_context().add_class("saturday")
                if (item['current'] and
                    item['day'] == self.today_greg.day and
                    self.cur_greg_month == self.today_greg.month and
                    self.cur_greg_year == self.today_greg.year):
                    lbl.get_style_context().add_class("today")
                self.grid.attach(lbl, c_idx, r_idx, 1, 1)

        # Footer: Equivalent Nepali date
        np_date = self.today_nep.strftime("%K %N %D, %G")
        self.footer_label.set_markup(f"Nepali Date: <span foreground='#000000'><b>{np_date}</b></span>")

    def render_nepali_calendar(self):
        # Update weekday headers
        for i, name in enumerate(DAYS_NP):
            self.weekday_labels[i].set_text(name)

        # Title
        m_np = NEPALI_MONTHS_NP[self.cur_nep_month]
        m_en = NEPALI_MONTHS_EN[self.cur_nep_month]
        y_dev = to_devanagari(self.cur_nep_year)
        self.nav_title.set_text(f"{m_np} {y_dev} ({m_en})")

        total_days = nepali_datetime._days_in_month(self.cur_nep_year, self.cur_nep_month)
        first_day = nepali_datetime.date(self.cur_nep_year, self.cur_nep_month, 1)
        start_col = first_day.weekday() # 0=Sun, ..., 6=Sat

        prev_y = self.cur_nep_year if self.cur_nep_month > 1 else self.cur_nep_year - 1
        prev_m = self.cur_nep_month - 1 if self.cur_nep_month > 1 else 12
        prev_total = nepali_datetime._days_in_month(prev_y, prev_m)

        grid_matrix = []
        week = []
        # Leading padding
        for i in range(start_col):
            week.append({'day': prev_total - start_col + 1 + i, 'current': False})

        for d in range(1, total_days + 1):
            week.append({'day': d, 'current': True})
            if len(week) == 7:
                grid_matrix.append(week)
                week = []

        if week:
            next_d = 1
            while len(week) < 7:
                week.append({'day': next_d, 'current': False})
                next_d += 1
            grid_matrix.append(week)

        for r_idx, row in enumerate(grid_matrix):
            for c_idx, item in enumerate(row):
                day_num = item['day']
                day_str = to_devanagari(day_num)
                lbl = Gtk.Label(label=day_str)
                lbl.set_xalign(0.5)
                lbl.get_style_context().add_class("day-cell")
                if not item['current']:
                    lbl.get_style_context().add_class("other-month")
                if c_idx == 6:
                    lbl.get_style_context().add_class("saturday")
                if (item['current'] and
                    day_num == self.today_nep.day and
                    self.cur_nep_month == self.today_nep.month and
                    self.cur_nep_year == self.today_nep.year):
                    lbl.get_style_context().add_class("today")
                self.grid.attach(lbl, c_idx, r_idx, 1, 1)

        # Footer: Equivalent English date
        en_date = self.today_greg.strftime("%A, %d %B %Y")
        self.footer_label.set_markup(f"English Date: <span foreground='#000000'><b>{en_date}</b></span>")

def main():
    app = CalendarApp()
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
