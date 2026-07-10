# time_total_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import os
import sys
import sv_ttk


APP_FILENAME = "time_total_gui"
SAVE_CSV = "time_totals.csv"

def parse_line(s):
    s = s.strip()
    if not s:
        return None
    # accept "mm.ss" or "mm:ss" or "mm"
    if '.' in s:
        parts = s.split('.', 1)
    elif ':' in s:
        parts = s.split(':', 1)
    else:
        # plain minutes
        try:
            m = int(s)
            return m * 60
        except ValueError:
            raise ValueError(f"Can't parse '{s}'")
    # now parts[0]=minutes, parts[1]=seconds
    try:
        m = int(parts[0])
        sec_str = parts[1]
        # allow seconds like "3" meaning 3 seconds, or "03", or "30"
        ssec = int(sec_str)
    except ValueError:
        raise ValueError(f"Can't parse '{s}'")
    # normalize if seconds >=60
    extra_m, ssec = divmod(ssec, 60)
    m += extra_m
    return m * 60 + ssec

def compute_total_seconds(lines):
    total = 0
    parsed = []
    for i, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            secs = parse_line(line)
            if secs is None:
                continue
            parsed.append((line, secs))
            total += secs
        except Exception as e:
            raise ValueError(f"Line {i}: {e}")
    return total, parsed

def secs_to_hms(secs):
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    return h, m, s

def on_calculate():
    text = txt_input.get("1.0", tk.END)
    lines = text.splitlines()
    try:
        total_seconds, parsed = compute_total_seconds(lines)
    except ValueError as e:
        messagebox.showerror("Parse error", str(e))
        return
    h, m, s = secs_to_hms(total_seconds)
    total_minutes = total_seconds / 60.0
    total_hours = total_seconds / 3600.0
    result_str = f"Total: {h}h {m}m {s}s  —  {total_minutes:.3f} minutes  —  {total_hours:.3f} hours"
    lbl_result.config(text=result_str)

    # Save to CSV
    save_path = os.path.join(os.path.dirname(__file__), SAVE_CSV)
    header_needed = not os.path.exists(save_path)
    now = datetime.now().isoformat(sep=' ', timespec='seconds')
    raw_input = "\\n".join([ln for ln in lines if ln.strip() != ""])
    try:
        with open(save_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if header_needed:
                writer.writerow(["timestamp", "raw_input", "total_seconds", "total_minutes", "total_hh_mm_ss", "total_hours_decimal"])
            hhmmss = f"{h:02d}:{m:02d}:{s:02d}"
            writer.writerow([now, raw_input, total_seconds, f"{total_minutes:.3f}", hhmmss, f"{total_hours:.6f}"])
    except Exception as e:
        messagebox.showwarning("Save failed", f"Could not save results to CSV:\n{e}")

def on_clear():
    txt_input.delete("1.0", tk.END)
    lbl_result.config(text="")

def on_open_example():
    example = "\n".join(["8", "11.27", "19", "8.14", "5.19"])
    txt_input.delete("1.0", tk.END)
    txt_input.insert("1.0", example)

def on_save_as():
    # allow user to save current CSV copy somewhere
    save_path = os.path.join(os.path.dirname(__file__), SAVE_CSV)
    if not os.path.exists(save_path):
        messagebox.showinfo("No file", "No saved CSV found yet. Calculate once to create it.")
        return
    dest = filedialog.asksaveasfilename(title="Save CSV as", defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if dest:
        try:
            with open(save_path, 'rb') as src, open(dest, 'wb') as dst:
                dst.write(src.read())
            messagebox.showinfo("Saved", f"Saved copy to:\n{dest}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Time Totaler")
root.geometry("700x500")

# Modern Sun Valley theme (EXE-safe)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

theme_path = os.path.join(base_path, "sv.tcl")

try:
    root.tk.call("source", theme_path)
    sv_ttk.set_theme("light")   # or "dark"
except Exception as e:
    print("Theme load failed:", e)
    ttk.Style().theme_use("clam")

# Track always-on-top state
always_on_top = tk.BooleanVar(value=False)

def toggle_on_top():
    root.attributes('-topmost', always_on_top.get())

# Menu bar
menubar = tk.Menu(root)

settings_menu = tk.Menu(menubar, tearoff=0)
settings_menu.add_checkbutton(
    label="Always on Top",
    variable=always_on_top,
    command=toggle_on_top
)

menubar.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menubar)


frm = ttk.Frame(root, padding=12)
frm.pack(fill=tk.BOTH, expand=True)

lbl = ttk.Label(frm, text="Paste times (format: minutes.seconds e.g. 11.27). One per line:")
lbl.pack(anchor=tk.W)

txt_input = tk.Text(frm, height=18, wrap=tk.NONE)
txt_input.pack(fill=tk.BOTH, expand=True, pady=6)

btn_frame = ttk.Frame(frm)
btn_frame.pack(fill=tk.X, pady=6)
btn_calc = ttk.Button(btn_frame, text="Calculate & Save", command=on_calculate)
btn_calc.pack(side=tk.LEFT, padx=4)
btn_clear = ttk.Button(btn_frame, text="Clear", command=on_clear)
btn_clear.pack(side=tk.LEFT, padx=4)
btn_example = ttk.Button(btn_frame, text="Load Example", command=on_open_example)
btn_example.pack(side=tk.LEFT, padx=4)
btn_saveas = ttk.Button(btn_frame, text="Save CSV As...", command=on_save_as)
btn_saveas.pack(side=tk.LEFT, padx=4)

lbl_result = ttk.Label(frm, text="", font=("Segoe UI", 11))
lbl_result.pack(anchor=tk.W, pady=6)

note = ttk.Label(frm, text="Saved CSV (append): " + SAVE_CSV)
note.pack(anchor=tk.W)

root.mainloop()
