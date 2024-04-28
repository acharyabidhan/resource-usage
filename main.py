import psutil
from tkinter import Tk, BOTH, Label, NW, SW
from tkinter import Canvas
from win32api import GetMonitorInfo, MonitorFromPoint

app = Tk()
app.overrideredirect(True)
app.resizable(0,0)
width = 280
height = 125

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
monitorInfo = GetMonitorInfo(MonitorFromPoint((0,0)))

screenSize = monitorInfo.get("Monitor")
workingArea = monitorInfo.get("Work")

position_top = (screen_height//2) - (height//2)
position_right = (screen_width//2) - (width//2)
app.geometry(f'{width}x{height}+{position_right}+{position_top}')

transparentColor = "pink"
app.config(background=transparentColor)

def round_rectangle(x1, y1, x2, y2, radius, color, **kwargs):
    points = [
        x1+radius, y1,
        x1+radius, y1,
        x2-radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True, fill=color)

canvas = Canvas(app, bg=transparentColor, highlightthickness=0)
canvas.pack(fill=BOTH, expand=1)
round_rectangle(0, 0, width, height, radius=20, color="#000000")

offsetx = 0
offsety = 0

leftLimit = workingArea[0]
topLimit = workingArea[1]
rightLimit = workingArea[2]
bottomLimit = workingArea[3]

def drag(event):
    x = app.winfo_pointerx() - app.offsetx
    y = app.winfo_pointery() - app.offsety
    windowRight = x + width
    windowBottom = y + height
    if x < leftLimit:
        x = leftLimit
    if windowRight > rightLimit:
        x = rightLimit - width
    if y < topLimit:
        y = topLimit
    if windowBottom > bottomLimit:
        y = bottomLimit - height
    app.geometry('+{x}+{y}'.format(x=x,y=y))

def click(event):
    app.offsetx = event.x
    app.offsety = event.y

pin = False

def pinWidget(event):
    global pin
    pin = not pin
    app.attributes('-topmost', pin)

cpu = Label(app, text="CPU", background="#000000", foreground="#FFFFFF", font=("bold"))
cpu.place(relx=0.02, rely=0.09, anchor=NW)

memory = Label(app, text="Memory", background="#000000", foreground="#FFFFFF", font=("bold"))
memory.place(relx=0.02, rely=0.3, anchor=NW)

net = Label(app, text="Net Send/Recv", background="#000000", foreground="#FFFFFF", font=("bold"))
net.place(relx=0.02, rely=0.7, anchor=SW)

disk = Label(app, text="Disk Read/Write", background="#000000", foreground="#FFFFFF", font=("bold"))
disk.place(relx=0.02, rely=0.91, anchor=SW)

cpu_value = Label(app, text="0%", background="#0000FF", foreground="#FFFFFF", font=("Helvetica ", 11, "bold"), width=14, anchor="w")
cpu_value.place(relx=0.5, rely=0.09, anchor=NW)

memory_value = Label(app, text="0%", background="#0000FF", foreground="#FFFFFF", font=("Helvetica ", 11, "bold"), width=14, anchor="w")
memory_value.place(relx=0.5, rely=0.3, anchor=NW)

net_value = Label(app, text="0MB/0MB", background="#0000FF", foreground="#FFFFFF", font=("Helvetica ", 11, "bold"), width=14, anchor="w")
net_value.place(relx=0.5, rely=0.7, anchor=SW)

disk_value = Label(app, text="0MB/0MB", background="#0000FF", foreground="#FFFFFF", font=("Helvetica ", 11, "bold"), width=14, anchor="w")
disk_value.place(relx=0.5, rely=0.91, anchor=SW)

def convert_b2mb(b):
    return round(b / 1024 / 1024, 1)

network_info = psutil.net_io_counters()
initial_bytes_sent = network_info.bytes_sent
initial_bytes_recv = network_info.bytes_recv

disk_info = psutil.disk_io_counters()
initial_read_bytes = disk_info.read_bytes
initial_write_bytes = disk_info.write_bytes

def update_ui():
    global initial_bytes_sent, initial_bytes_recv, initial_read_bytes, initial_write_bytes

    cpu_usage = psutil.cpu_percent()
    cpu_value.config(text = f"{cpu_usage}%", background="#FF0000" if cpu_usage > 50 else "#0000FF")

    memory_usage = psutil.virtual_memory().percent
    memory_value.config(text = f"{memory_usage}%", background="#FF0000" if memory_usage > 75 else "#0000FF")

    network_info = psutil.net_io_counters()
    bytes_sent = convert_b2mb(network_info.bytes_sent - initial_bytes_sent)
    bytes_recv = convert_b2mb(network_info.bytes_recv - initial_bytes_recv)
    net_value.config(text = f"{bytes_sent}MB/{bytes_recv}MB", background="#00FF00" if bytes_sent > 10 or bytes_recv > 10 else "#0000FF")
    initial_bytes_sent = network_info.bytes_sent
    initial_bytes_recv = network_info.bytes_recv

    disk_info = psutil.disk_io_counters()
    read_bytes = disk_info.read_bytes - initial_read_bytes
    write_bytes = disk_info.write_bytes - initial_write_bytes
    bytes_read_write = f"{convert_b2mb(read_bytes)}MB/{convert_b2mb(write_bytes)}MB"
    disk_value.config(text = bytes_read_write)
    initial_read_bytes = disk_info.read_bytes
    initial_write_bytes = disk_info.write_bytes

    app.after(1000, update_ui)

update_ui()

def doNothing():pass
app.wm_attributes("-transparentcolor", "pink")
app.bind("<Button-1>", click)
app.bind("<B1-Motion>", drag)
app.protocol("WM_DELETE_WINDOW", doNothing)
app.bind('<Double-Button-1>', pinWidget)
app.mainloop()