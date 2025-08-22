# flatbat
Inspired by https://github.com/CODeRUS/harbour-batteryoverlay

A minimalist tkinter-based system monitor that shows CPU, RAM, GPU, battery, and a clock as thin border overlays.

## Install

### From AUR: 
```bash
yay -S flatbat

Flatbat uses a YAML config file located at `~/.config/flatbat/config.yaml`.

general:
  gpu: False
  cpu: True
  mem: True
  batt: True
  clock: False

gpu:
  colour: "#800080"
  thickness: 3
cpu:
  colour: "#FF0000"
  thickness: 3
mem:
  colour: "#0000FF"
  thickness: 3
batt:
  critical_battery_level: 20
  critical_battery_color: "#FF0000"
  plugged: "#00FFF0"
  unplugged: "#00FF00"
  thickness: 3
clock:
  hour: "#00FF00"
  min: "#FFD700"
