# flatbat
Inspired by https://github.com/CODeRUS/harbour-batteryoverlay

A minimalist tkinter-based system monitor that shows CPU, RAM, GPU, battery, and a clock as thin border overlays.

## Install

### From AUR: 
```bash
yay -S flatbat

Flatbat uses a YAML config file located at `~/.config/flatbat/config.yaml`.

general:
  gpu: true
  cpu: true
  mem: true
  batt: true
  clock: true

gpu:
  colour: "#800080"

cpu:
  colour: "#FF0000"

mem:
  colour: "#0000FF"

batt:
  plugged: "#00FF00"
  unplugged: "#009944"

clock:
  hour: "#00FF00"
  min: "#FFD700"

