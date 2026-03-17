# Flatbat

*A minimalist, border-based system monitor for Linux*

Flatbat Screenshot  
*(Example: CPU, RAM, GPU, battery, and clock overlays in action)*

---

## **Inspiration**

Flatbat is inspired by [harbour-batteryoverlay](https://github.com/CODeRUS/harbour-batteryoverlay), but designed for desktop Linux users who want a clean, unobtrusive way to monitor system stats as thin border overlays.

---

## **Features**

- **Real-time monitoring**: CPU, RAM, GPU, battery, and clock.
- **Customizable**: Adjust colors, thickness, refresh rates, and visibility for each module.
- **Presets**: Quickly switch between color themes (`solarized`, `highcontrast`, `rembrandt`, `bauhaus`, `cyberpunk`).
- **Lightweight**: Built with `tkinter` and `GtkLayerShell` for minimal resource usage.
- **Configurable**: YAML-based config file for easy tweaking.

---

## **Installation**

### **From AUR (Arch Linux)**

```bash
yay -S flatbat
```

### **Manual Installation**

1. Clone the repo:
  ```bash
   git clone https://github.com/yourusername/flatbat.git
   cd flatbat
  ```
2. Install dependencies:
  ```bash
   pip install -r requirements.txt
  ```
3. Run:
  ```bash
   python flatbat.py
  ```

---

## **Configuration**

Flatbat uses a YAML config file at `~/.config/flatbat/config.yaml`. Here’s the default structure with all new options:

```yaml
# ── flatbat config ────────────────────────────────────────────────────────────
#
# Presets (override colours only, leave your other settings intact):
#   flatbat -solarized
#   flatbat -highcontrast
#   flatbat -rembrandt
#   flatbat -bauhaus
#   flatbat -cyberpunk
#   flatbat --preset cyberpunk
#
# All colours accept #RRGGBB, #RRGGBBAA, or "transparent"
# ─────────────────────────────────────────────────────────────────────────────

general:
  overlay: true       # true = OVERLAY layer (above everything), false = TOP
  gaps: 5             # px gap between bars
  batt: true
  clock: true
  cpu: true
  mem: true
  gpu: false

# ── Battery ───────────────────────────────────────────────────────────────────
batt:
  thickness: 3
  refresh: 10                       # seconds between updates
  plugged: "#00FFF0"                # colour when charging
  unplugged: "#00FF00"              # colour when on battery
  empty: "transparent"              # colour of the unfilled section
  critical_battery_level: 20        # % at which critical colour kicks in
  critical_battery_color: "#FF0000"
  fuse: true                        # glowing tip showing power draw rate
  fuse_max_watts: 20                # watts = full fuse size + high colour
  fuse_min_px: 5                   # fuse size at lowest draw
  fuse_max_px: 60                   # fuse size at highest draw
  fuse_steps: 7                     # gradient steps between low and high colour
  fuse_color_low: "#00FF00"         # colour at low power draw
  fuse_color_high: "#FF0000"        # colour at high power draw

# ── Clock ─────────────────────────────────────────────────────────────────────
clock:
  thickness: 5
  refresh: 10
  24h: false                        # true = 24 segments full width, no minutes bar
                                    # false = left half hours / right half minutes
  hour: "#228844"                   # filled hour segments
  min: "#994A99"                    # filled minute segments (12h mode only)
  current: "#00F0F0"                # active subdivision tip colour
  segments: "#0000FF"               # minor gap colour between segments
  marker: "#000000"                 # major division gap fill (every 3h / 6h)
  marker_highlight: "#FFFFFF"       # 1px edge highlight either side of major gap

# ── CPU ───────────────────────────────────────────────────────────────────────
cpu:
  thickness: 3
  refresh: 2
  colour: "#FF0000"

# ── Memory ────────────────────────────────────────────────────────────────────
mem:
  thickness: 6
  refresh: 5
  colour: "#3333FF"

# ── GPU ───────────────────────────────────────────────────────────────────────
gpu:
  thickness: 5
  refresh: 2
  colour: "#800080"
```

### **Presets**

Flatbat includes several built-in color presets for quick theming:

- **Solarized**: Subtle, terminal-friendly colors.
- **High Contrast**: Bold, accessible colors.
- **Rembrandt**: Warm, painterly palette.
- **Bauhaus**: Primary colors, modernist style.
- **Cyberpunk**: Neon, futuristic vibe.

Use them with:

```bash
flatbat --preset solarized
```

### **Customization Tips**

- **Colors**: Use hex codes (e.g., `#FF0000` for red) or `transparent`.
- **Thickness**: Adjust the border thickness (e.g., `3` for a 3px border).
- **Refresh Rate**: Set how often each module updates (in seconds).
- **Fuse**: Visualize power draw with a glowing tip (battery only).

---

## **Interface Overview**

Flatbat renders system stats as thin, colored borders around your screen:


| Module      | Color (Default)    | Description                                                               |
| ----------- | ------------------ | ------------------------------------------------------------------------- |
| **CPU**     | Red (`#FF0000`)    | Shows CPU usage as a border.                                              |
| **RAM**     | Blue (`#3333FF`)   | Displays memory usage.                                                    |
| **GPU**     | Purple (`#800080`) | GPU usage (if enabled).                                                   |
| **Battery** | Green/Red          | Battery level; turns red when critical. The "fuse" visualizes power draw. |
| **Clock**   | Green/Gold         | Hour and minute markers, with 12h or 24h modes.                           |


---

## **Screenshots**


1. **Battery with Fuse**

<img width="1920" height="1080" alt="high_fuse" src="https://github.com/user-attachments/assets/02ccfc37-05ca-4c27-b2e8-236e8f6eb50f" />


2. **24h Clock Mode**

<img width="1920" height="1075" alt="24 hour clock" src="https://github.com/user-attachments/assets/505dae5c-00c6-4511-800e-0f7c3ea447ce" />


3. **Battery, 12 hour clock, CPU and RAM Overlay**

<img width="1920" height="1080" alt="Battery 12hour clock RAM and CPU" src="https://github.com/user-attachments/assets/bb888c07-b649-411f-a36b-2186a780a15f" />

---

## **Usage**

1. Launch Flatbat:
  ```bash
   flatbat
  ```
2. Edit `config.yaml` to customize.
3. Restart Flatbat to apply changes.

---

## **Contributing**

Pull requests and issues are welcome! For major changes, open an issue first.

---

## **License**

[MIT](LICENSE)
