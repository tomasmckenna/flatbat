#!/usr/bin/env python3
import os
os.environ["GDK_BACKEND"] = "wayland"

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell
import psutil
import yaml
import datetime
import argparse
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".config" / "flatbat" / "config.yaml"

DEFAULTS = {
    "general": {
        "gpu": False, "cpu": False, "mem": False, "batt": True, "clock": True,
        "overlay": True, "gaps": 5,
    },
    "gpu":  {"colour": "#800080", "thickness": 5, "refresh": 2},
    "cpu":  {"colour": "#FF0000", "thickness": 3, "refresh": 2},
    "mem":  {"colour": "#3333FF", "thickness": 6, "refresh": 5},
    "batt": {
        "critical_battery_level": 20,
        "critical_battery_color": "#FF0000",
        "plugged":   "#00FFF0",
        "unplugged": "#00FF00",
        "empty":     "transparent",
        "thickness": 2,
        "refresh":   10,
        "fuse":           True,
        "fuse_max_watts": 20,
        "fuse_min_px":    4,
        "fuse_max_px":    60,
        "fuse_steps":     7,
        "fuse_color_low":  "#00FF00",
        "fuse_color_high": "#FF0000",
    },
    "clock": {
        "24h":              True,
        "hour":             "#228844",
        "min":              "#994A99",
        "segments":         "#0000FF",
        "current":          "#00F0F0",
        "marker":           "#000000",  # major division fill colour
        "marker_highlight": "#FFFFFF",  # 1px highlight either side of major division
        "thickness": 4,
        "refresh":   10,
    },
}

# ── Presets ───────────────────────────────────────────────────────────────────

PRESETS = {
    "solarized": {
        "cpu":   {"colour": "#dc322f"},
        "mem":   {"colour": "#268bd2"},
        "batt":  {"plugged": "#2aa198", "unplugged": "#859900", "empty": "transparent",
                  "critical_battery_color": "#cb4b16",
                  "fuse_color_low": "#859900", "fuse_color_high": "#dc322f"},
        "clock": {"hour": "#b58900", "min": "#6c71c4", "segments": "#073642",
                  "current": "#2aa198", "marker": "#002b36", "marker_highlight": "#839496"},
    },
    "highcontrast": {
        "cpu":   {"colour": "#FFFFFF"},
        "mem":   {"colour": "#FFFF00"},
        "batt":  {"plugged": "#00FFFF", "unplugged": "#00FF00", "empty": "transparent",
                  "critical_battery_color": "#FF0000",
                  "fuse_color_low": "#00FF00", "fuse_color_high": "#FF0000"},
        "clock": {"hour": "#FFFFFF", "min": "#FFFF00", "segments": "#444444",
                  "current": "#00FFFF", "marker": "#000000", "marker_highlight": "#FFFFFF"},
    },
    "rembrandt": {
        "cpu":   {"colour": "#C17D3C"},
        "mem":   {"colour": "#7A5C3A"},
        "batt":  {"plugged": "#D4A85A", "unplugged": "#A0784A", "empty": "transparent",
                  "critical_battery_color": "#8B1A1A",
                  "fuse_color_low": "#D4A85A", "fuse_color_high": "#8B1A1A"},
        "clock": {"hour": "#C17D3C", "min": "#8B6347", "segments": "#3B2A1A",
                  "current": "#F5D08A", "marker": "#1A0F00", "marker_highlight": "#C17D3C"},
    },
    "bauhaus": {
        "cpu":   {"colour": "#FF0000"},
        "mem":   {"colour": "#0000FF"},
        "batt":  {"plugged": "#FFFF00", "unplugged": "#FF0000", "empty": "transparent",
                  "critical_battery_color": "#FF0000",
                  "fuse_color_low": "#FFFF00", "fuse_color_high": "#FF0000"},
        "clock": {"hour": "#FF0000", "min": "#0000FF", "segments": "#222222",
                  "current": "#FFFF00", "marker": "#000000", "marker_highlight": "#FFFFFF"},
    },
    "cyberpunk": {
        "cpu":   {"colour": "#FF00FF"},
        "mem":   {"colour": "#00FFFF"},
        "batt":  {"plugged": "#00FFFF", "unplugged": "#FF00FF", "empty": "transparent",
                  "critical_battery_color": "#FF0040",
                  "fuse_color_low": "#00FF80", "fuse_color_high": "#FF0040"},
        "clock": {"hour": "#FF00FF", "min": "#00FFFF", "segments": "#1A001A",
                  "current": "#00FF80", "marker": "#0D000D", "marker_highlight": "#FF00FF"},
    },
}

def load_config(preset=None):
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULTS, f, default_flow_style=False)
        user = {}
    else:
        with open(CONFIG_PATH) as f:
            user = yaml.safe_load(f) or {}

    # start from defaults
    cfg = {}
    for key, val in DEFAULTS.items():
        if isinstance(val, dict):
            cfg[key] = {**val, **(user.get(key) or {})}
        else:
            cfg[key] = user.get(key, val)

    # apply preset on top (overrides user config colours)
    if preset and preset in PRESETS:
        for key, overrides in PRESETS[preset].items():
            if key in cfg:
                cfg[key] = {**cfg[key], **overrides}

    return cfg


# ── Helpers ───────────────────────────────────────────────────────────────────

def hex_to_rgba(h):
    if not h or str(h).lower() in ("transparent", "none"):
        return (0.0, 0.0, 0.0, 0.0)
    h = str(h).lstrip("#")
    if len(h) == 8:
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4, 6))
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    return (r, g, b, 1.0)

def lerp_color(a, b, t):
    return tuple(a[i] + t * (b[i] - a[i]) for i in range(4))

def fuse_color(t, low_rgba, high_rgba, steps):
    t = max(0.0, min(1.0, t))
    bucket = round(t * (steps - 1)) / (steps - 1) if steps > 1 else t
    return lerp_color(low_rgba, high_rgba, bucket)

def set_color(cr, rgba):
    cr.set_source_rgba(*rgba)

def draw_fill_bar(cr, width, height, fill_frac, fill_rgba, empty_rgba):
    filled = int(width * max(0.0, min(1.0, fill_frac)))
    set_color(cr, fill_rgba)
    cr.rectangle(0, 0, filled, height)
    cr.fill()
    set_color(cr, empty_rgba)
    cr.rectangle(filled, 0, width - filled, height)
    cr.fill()

def read_power_now():
    for path in Path("/sys/class/power_supply").glob("*/power_now"):
        try:
            return int(path.read_text()) / 1_000_000
        except Exception:
            pass
    for bat in Path("/sys/class/power_supply").glob("BAT*"):
        try:
            i = int((bat / "current_now").read_text())
            v = int((bat / "voltage_now").read_text())
            return (i * v) / 1_000_000_000_000
        except Exception:
            pass
    return 0.0

# ── State ─────────────────────────────────────────────────────────────────────

state = {}

def refresh_state(cfg):
    g = cfg["general"]

    if g.get("cpu"):
        state["cpu"] = psutil.cpu_percent(interval=None) / 100.0

    if g.get("mem"):
        state["mem"] = psutil.virtual_memory().percent / 100.0

    if g.get("batt"):
        bat = psutil.sensors_battery()
        if bat:
            state["batt_pct"]     = bat.percent / 100.0
            state["batt_plugged"] = bat.power_plugged
        else:
            state["batt_pct"]     = 1.0
            state["batt_plugged"] = True
        state["batt_power_w"] = read_power_now()

    if g.get("clock"):
        now = datetime.datetime.now()
        state["hour_frac"] = now.hour / 23.0
        state["min_frac"]  = now.minute / 59.0

# ── Draw ──────────────────────────────────────────────────────────────────────

def draw_clock_12h(cr, cfg, y, width, thickness):
    """Original 12h mode: left half = hours, right half = minutes."""
    c         = cfg["clock"]
    hour_col  = hex_to_rgba(c["hour"])
    min_col   = hex_to_rgba(c["min"])
    seg_col   = hex_to_rgba(c.get("segments", "#444444"))
    cur_col   = hex_to_rgba(c.get("current",  "#00F0F0"))
    empty_col = (0.1, 0.1, 0.1, 1.0)
    gap       = 1
    big_gap   = 7

    now         = datetime.datetime.now()
    cur_hour    = now.hour % 12
    cur_min_seg = now.minute // 5
    half        = width // 2

    def draw_subdivided(cx, cy, sw, th, filled_subs):
        sub_w = sw / 5
        for s in range(5):
            sx  = int(cx + s * sub_w)
            snx = int(cx + (s + 1) * sub_w)
            set_color(cr, cur_col if s < filled_subs else empty_col)
            cr.rectangle(sx, cy, snx - sx, th)
            cr.fill()

    # hour segments (left half, 12 segs)
    hour_subs   = now.minute // 12
    total_gap_h = 3 * big_gap + 8 * gap
    seg_w_h     = (half - total_gap_h) / 12
    x = 0.0
    for i in range(12):
        sw = max(1, int(seg_w_h))
        if i < cur_hour:
            set_color(cr, hour_col)
            cr.rectangle(int(x), y, sw, thickness)
            cr.fill()
        elif i == cur_hour:
            draw_subdivided(int(x), y, sw, thickness, hour_subs)
        else:
            set_color(cr, empty_col)
            cr.rectangle(int(x), y, sw, thickness)
            cr.fill()
        x += seg_w_h
        if i < 11:
            marker = (i + 1) in (3, 6, 9)
            gw = big_gap if marker else gap
            set_color(cr, (0, 0, 0, 1) if marker else seg_col)
            cr.rectangle(int(x), y, gw, thickness)
            cr.fill()
            x += gw

    # minute segments (right half, 12 segs of 5 min)
    min_subs    = now.minute % 5
    total_gap_m = 3 * big_gap + 8 * gap
    seg_w_m     = (half - total_gap_m) / 12
    x = float(half)
    for i in range(12):
        sw = max(1, int(seg_w_m))
        if i < cur_min_seg:
            set_color(cr, min_col)
            cr.rectangle(int(x), y, sw, thickness)
            cr.fill()
        elif i == cur_min_seg:
            draw_subdivided(int(x), y, sw, thickness, min_subs)
        else:
            set_color(cr, empty_col)
            cr.rectangle(int(x), y, sw, thickness)
            cr.fill()
        x += seg_w_m
        if i < 11:
            marker = (i + 1) in (3, 6, 9)
            gw = big_gap if marker else gap
            set_color(cr, (0, 0, 0, 1) if marker else seg_col)
            cr.rectangle(int(x), y, gw, thickness)
            cr.fill()
            x += gw


def draw_clock_24h(cr, cfg, y, width, thickness):
    """
    24h mode: 24 segments across full width.
    Past hours lit in hour_col. Current hour subdivided into 12 sub-segments,
    each representing 5 minutes, filled with cur_col.
    """
    c            = cfg["clock"]
    hour_col     = hex_to_rgba(c["hour"])
    seg_col      = hex_to_rgba(c.get("segments",         "#0000FF"))
    cur_col      = hex_to_rgba(c.get("current",          "#00F0F0"))
    marker_col   = hex_to_rgba(c.get("marker",           "#000000"))
    highlight_col= hex_to_rgba(c.get("marker_highlight", "#FFFFFF"))
    empty_col    = (0.1, 0.1, 0.1, 1.0)
    gap          = 1
    # big_gap = 1px highlight + 5px marker + 1px highlight = 7px total
    big_gap      = 7

    now         = datetime.datetime.now()
    cur_hour    = now.hour
    cur_min_seg = now.minute // 5  # 0-11

    # total gaps: 3 big (7px) + 20 small (1px)
    total_gaps = 3 * big_gap + 20 * gap
    seg_w      = (width - total_gaps) / 24

    def draw_subdivided_24(cx, sw, th, filled_subs):
        """
        12 sub-segments (5 min each).
        Filled: gradient from hour_col → cur_col. Unfilled: empty_col.
        """
        sub_w = sw / 12
        for s in range(12):
            sx  = int(cx + s * sub_w)
            snx = int(cx + (s + 1) * sub_w)
            if s < filled_subs:
                t   = s / max(filled_subs - 1, 1)
                col = lerp_color(hour_col, cur_col, t)
            else:
                col = empty_col
            set_color(cr, col)
            cr.rectangle(sx, y, snx - sx, th)
            cr.fill()

    def draw_gap(x, marker):
        """Draw a gap. Markers get white(1px) + black(5px) + white(1px)."""
        if marker:
            set_color(cr, highlight_col)
            cr.rectangle(int(x), y, 1, thickness)
            cr.fill()
            set_color(cr, marker_col)
            cr.rectangle(int(x) + 1, y, big_gap - 2, thickness)
            cr.fill()
            set_color(cr, highlight_col)
            cr.rectangle(int(x) + big_gap - 1, y, 1, thickness)
            cr.fill()
        else:
            set_color(cr, seg_col)
            cr.rectangle(int(x), y, gap, thickness)
            cr.fill()

    x = 0.0
    for i in range(24):
        sw = max(1, int(seg_w))
        if i < cur_hour:
            set_color(cr, hour_col)
            cr.rectangle(int(x), y, sw, thickness)
            cr.fill()
        elif i == cur_hour:
            draw_subdivided_24(int(x), sw, thickness, cur_min_seg)
        else:
            set_color(cr, empty_col)
            cr.rectangle(int(x), y, sw, thickness)
            cr.fill()
        x += seg_w
        if i < 23:
            marker = (i + 1) in (6, 12, 18)
            draw_gap(x, marker)
            x += big_gap if marker else gap


def make_draw_cb(cfg, bars, gaps):
    def on_draw(widget, cr):
        cr.set_operator(1)  # CAIRO_OPERATOR_SOURCE
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(2)  # CAIRO_OPERATOR_OVER

        width = widget.get_allocated_width()
        y = 0

        for idx, (name, thickness) in enumerate(bars):

            if name == "cpu":
                c = cfg["cpu"]
                cr.save(); cr.translate(0, y)
                draw_fill_bar(cr, width, thickness,
                              state.get("cpu", 0),
                              hex_to_rgba(c["colour"]),
                              (0.1, 0.1, 0.1, 1.0))
                cr.restore()

            elif name == "mem":
                c = cfg["mem"]
                cr.save(); cr.translate(0, y)
                draw_fill_bar(cr, width, thickness,
                              state.get("mem", 0),
                              hex_to_rgba(c["colour"]),
                              (0.1, 0.1, 0.1, 1.0))
                cr.restore()

            elif name == "batt":
                c          = cfg["batt"]
                pct        = state.get("batt_pct", 1.0)
                empty_rgba = hex_to_rgba(c.get("empty", "transparent"))
                plugged    = state.get("batt_plugged", True)

                if plugged:
                    fill_rgba = hex_to_rgba(c["plugged"])
                elif pct <= c["critical_battery_level"] / 100.0:
                    fill_rgba = hex_to_rgba(c["critical_battery_color"])
                else:
                    fill_rgba = hex_to_rgba(c["unplugged"])

                filled_px = int(width * max(0.0, min(1.0, pct)))
                cr.save(); cr.translate(0, y)

                if c.get("fuse", True) and not plugged and filled_px > 0:
                    watts     = state.get("batt_power_w", 0.0)
                    max_w     = float(c.get("fuse_max_watts", 20))
                    min_px    = int(c.get("fuse_min_px", 10))
                    max_px    = int(c.get("fuse_max_px", 60))
                    steps     = max(2, int(c.get("fuse_steps", 7)))
                    low_rgba  = hex_to_rgba(c.get("fuse_color_low",  "#00FF00"))
                    high_rgba = hex_to_rgba(c.get("fuse_color_high", "#FF0000"))
                    t         = min(watts / max_w, 1.0) if max_w > 0 else 0.0
                    fuse_px   = min(int(min_px + t * (max_px - min_px)), filled_px)
                    f_rgba    = fuse_color(t, low_rgba, high_rgba, steps)

                    set_color(cr, empty_rgba)
                    cr.rectangle(filled_px, 0, width - filled_px, thickness)
                    cr.fill()
                    set_color(cr, fill_rgba)
                    cr.rectangle(0, 0, filled_px - fuse_px, thickness)
                    cr.fill()
                    set_color(cr, f_rgba)
                    cr.rectangle(filled_px - fuse_px, 0, fuse_px, thickness)
                    cr.fill()
                else:
                    draw_fill_bar(cr, width, thickness, pct, fill_rgba, empty_rgba)

                cr.restore()

            elif name == "clock":
                if cfg["clock"].get("24h", False):
                    draw_clock_24h(cr, cfg, y, width, thickness)
                else:
                    draw_clock_12h(cr, cfg, y, width, thickness)

            y += thickness
            if idx < len(bars) - 1 and gaps > 0:
                cr.set_source_rgba(0, 0, 0, 0)
                cr.rectangle(0, y, width, gaps)
                cr.fill()
                y += gaps

    return on_draw

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="flatbat system overlay")
    parser.add_argument(
        "-p", "--preset",
        choices=list(PRESETS.keys()),
        metavar="PRESET",
        help=f"colour preset: {', '.join(PRESETS.keys())}",
    )
    for name in PRESETS:
        parser.add_argument(f"-{name}", action="store_true", default=False)
    args = parser.parse_args()

    preset = args.preset
    if not preset:
        for name in PRESETS:
            if getattr(args, name, False):
                preset = name
                break

    cfg  = load_config(preset=preset)
    g    = cfg["general"]
    gaps = int(g.get("gaps", 0))

    ORDER = ["batt", "clock", "mem", "cpu"]
    bars  = [(n, cfg[n]["thickness"]) for n in ORDER if g.get(n)]

    if not bars:
        print("No bars enabled in config — nothing to show.")
        return

    total_height = sum(t for _, t in bars) + gaps * (len(bars) - 1)
    refresh_state(cfg)

    window = Gtk.Window()

    screen = window.get_screen()
    visual = screen.get_rgba_visual()
    if visual:
        window.set_visual(visual)
    window.set_app_paintable(True)

    GtkLayerShell.init_for_window(window)
    layer = GtkLayerShell.Layer.OVERLAY if g.get("overlay", True) else GtkLayerShell.Layer.TOP
    GtkLayerShell.set_layer(window, layer)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.TOP,    True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.LEFT,   True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.RIGHT,  True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.BOTTOM, False)
    GtkLayerShell.set_exclusive_zone(window, total_height)
    window.set_decorated(False)

    geom = Gdk.Geometry()
    geom.min_width  = 1
    geom.max_width  = 100000
    geom.min_height = total_height
    geom.max_height = total_height
    window.set_geometry_hints(None, geom,
        Gdk.WindowHints.MIN_SIZE | Gdk.WindowHints.MAX_SIZE)

    canvas = Gtk.DrawingArea()
    canvas.set_size_request(1, total_height)
    canvas.connect("draw", make_draw_cb(cfg, bars, gaps))
    window.add(canvas)
    window.show_all()

    def make_updater():
        def update(_):
            refresh_state(cfg)
            canvas.queue_draw()
            return True
        return update

    seen_rates = set()
    for name, _ in bars:
        rate = int(cfg[name].get("refresh", 2))
        if rate not in seen_rates:
            seen_rates.add(rate)
            GLib.timeout_add_seconds(rate, make_updater(), None)

    refresh_state(cfg)
    canvas.queue_draw()

    window.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()