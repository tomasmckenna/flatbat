#!/usr/bin/env python3
import tkinter as tk
import datetime
import math

def run_clock():
    root = tk.Tk()
    root.withdraw()  # Hide the root window completely
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Bar width for all edges
    bar_width = 4  
    # Length and width of hand indicators
    hand_length = 44
    hand_width = 4 

    # Create windows for each edge
    top_window = tk.Toplevel(root)
    top_window.overrideredirect(True)
    top_window.geometry(f"{screen_width}x{bar_width}+0+0")
    top_window.attributes("-topmost", True)
    top_canvas = tk.Canvas(top_window, width=screen_width, height=bar_width, bg="black", highlightthickness=0)
    top_canvas.pack()

    bottom_window = tk.Toplevel(root)
    bottom_window.overrideredirect(True)
    bottom_window.geometry(f"{screen_width}x{bar_width}+0+{screen_height - bar_width}")
    bottom_window.attributes("-topmost", True)
    bottom_canvas = tk.Canvas(bottom_window, width=screen_width, height=bar_width, bg="black", highlightthickness=0)
    bottom_canvas.pack()

    left_window = tk.Toplevel(root)
    left_window.overrideredirect(True)
    left_window.geometry(f"{bar_width}x{screen_height}+0+0")
    left_window.attributes("-topmost", True)
    left_canvas = tk.Canvas(left_window, width=bar_width, height=screen_height, bg="black", highlightthickness=0)
    left_canvas.pack()

    right_window = tk.Toplevel(root)
    right_window.overrideredirect(True)
    right_window.geometry(f"{bar_width}x{screen_height}+{screen_width - bar_width}+0")
    right_window.attributes("-topmost", True)
    right_canvas = tk.Canvas(right_window, width=bar_width, height=screen_height, bg="black", highlightthickness=0)
    right_canvas.pack()

    def draw_clock():
        # Clear all canvases
        top_canvas.delete("all")
        bottom_canvas.delete("all")
        left_canvas.delete("all")
        right_canvas.delete("all")

        now = datetime.datetime.now()
        hour = now.hour % 12
        minute = now.minute

        hour_angle = (hour + minute / 60) * 30
        minute_angle = minute * 6

        # Draw hour markers (12, 3, 6, 9)
        draw_hour_marker(0, "gray")    # 12 o'clock
        draw_hour_marker(30, "gray")   # 3 o'clock
        draw_hour_marker(60, "gray")  # 9 o'clock  
        draw_hour_marker(90, "gray")  # 6 o'clock
        draw_hour_marker(120, "gray")    # 12 o'clock
        draw_hour_marker(150, "gray")  # 6 o'clock
        draw_hour_marker(180, "gray")   # 3 o'clock
        draw_hour_marker(210, "gray")   # 3 o'clock
        draw_hour_marker(240, "gray")  # 9 o'clock  
        draw_hour_marker(270, "gray")  # 6 o'clock
        draw_hour_marker(300, "gray")    # 12 o'clock
        draw_hour_marker(330, "gray")    # 12 o'clock

        # Draw hour hand
        draw_hand(hour_angle, "#ff2266", hand_length, hand_width)

        # Draw minute hand
        draw_hand(minute_angle, "#5577ff", hand_length, hand_width)

        # Schedule next update
        root.after(60000, draw_clock)

    def draw_hour_marker(angle, color):
        # Draw a small marker at the specific hour positions
        x, y, edge = calculate_position(angle, screen_width, screen_height)
        if edge == "top":
            top_canvas.create_rectangle(x, 0, x + bar_width, bar_width, fill=color, outline='')
        elif edge == "bottom":
            bottom_canvas.create_rectangle(x, 0, x + bar_width, bar_width, fill=color, outline='')
        elif edge == "left":
            left_canvas.create_rectangle(0, y, bar_width, y + bar_width, fill=color, outline='')
        elif edge == "right":
            right_canvas.create_rectangle(0, y, bar_width, y + bar_width, fill=color, outline='')

    def draw_hand(angle, color, length, width):
        x, y, edge = calculate_position(angle, screen_width, screen_height)
        
        if edge == "top":
            # Draw horizontally on top edge with specified width
            half_length = length // 2
            start_x = max(0, x - half_length)
            end_x = min(screen_width, x + half_length)
            top_canvas.create_rectangle(start_x, 0, end_x, width, fill=color, outline='')
        elif edge == "bottom":
            # Draw horizontally on bottom edge with specified width
            half_length = length // 2
            start_x = max(0, x - half_length)
            end_x = min(screen_width, x + half_length)
            bottom_canvas.create_rectangle(start_x, 0, end_x, width, fill=color, outline='')
        elif edge == "left":
            # Draw vertically on left edge with specified width
            half_length = length // 2
            start_y = max(0, y - half_length)
            end_y = min(screen_height, y + half_length)
            left_canvas.create_rectangle(0, start_y, width, end_y, fill=color, outline='')
        elif edge == "right":
            # Draw vertically on right edge with specified width
            half_length = length // 2
            start_y = max(0, y - half_length)
            end_y = min(screen_height, y + half_length)
            right_canvas.create_rectangle(0, start_y, width, end_y, fill=color, outline='')

    def calculate_position(angle, width, height):
        # Normalize angle to 0-360
        angle = angle % 360
        
        # Determine which edge the position is on
        if 45 <= angle < 135:
            # Right edge
            proportion = (angle - 45) / 90
            y = int(proportion * height)
            return width - bar_width, y, "right"
        elif 135 <= angle < 225:
            # Bottom edge
            proportion = (angle - 135) / 90
            x = int((1 - proportion) * width)
            return x, height - bar_width, "bottom"
        elif 225 <= angle < 315:
            # Left edge
            proportion = (angle - 225) / 90
            y = int((1 - proportion) * height)
            return 0, y, "left"
        else:
            # Top edge (315-360 and 0-45)
            if angle >= 315:
                proportion = (angle - 315) / 90
            else:
                proportion = (angle + 45) / 90
            x = int(proportion * width)
            return x, 0, "top"

    # Start the clock
    draw_clock()
    root.mainloop()

if __name__ == "__main__":
    run_clock()