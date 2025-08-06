import sys # for system path handling
import os # for file path handling
import tkinter as tk
from tkinter import filedialog, Label, Button, Canvas # for GUI components
from PIL import Image, ImageTk # for image processing
import cv2 # for image processing
from ultralytics import YOLO
import threading # for running live detection in a separate thread
from tkinter import messagebox # for popup messages
# import darkdetect
from tkinter import ttk
# from playsound import playsound
import pygame # for playing sound (used instead of playsound as it allows for better control)

cap = None # this will be used for storing the camera access
live_running = False # this for storing information about live detection
record_buffer_seconds = 5 # default buffer time for recording
recording = False # this will be used to check if recording is in progress
recording_writer = None # this will be used to write the video frames to a file
recording_start_time = None # this will be used to store the start time of recording
recording_frames = []
selected_fps = 25 # setting default fps to 25 for live detection
alarm_enabled = True  # by default the alarm is enabled
camera_source = "Webcam"  # default value
ip_camera_url = ""        # optionally pre-fill or leave empty


# dark_mode = False
# theme_preference = "System"  # "Light", "Dark", or "System" the default
# is_dark_mode = darkdetect.isDark()  # Initial theme flag

# function to read the model to avoid errors in .exe files later
# we can use the normal way of reading model like model(yolo) but when we run the code
# as a stand alone we get error of no model found so this is the 
# best way to integrate model within the gui
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# loading model via function
model_path = resource_path("best4.pt")
model = YOLO(model_path)

# Tooltip class for hovering mouse for info and help button

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.label = None
        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide_tip)

    def schedule(self, event=None):
        self.widget.after_idle(self.show_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.attributes("-topmost", True)

        self.label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Helvetica", 10, "normal"),
            wraplength=250,
            padx=6,
            pady=3
        )
        self.label.pack(ipadx=1)

        tw.update_idletasks()

        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        width = tw.winfo_width()
        height = tw.winfo_height()

        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10

        tw.geometry(f"+{x}+{y}")
        tw.update_idletasks()  # Force redraw (macOS needs this)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# GUI setup
root = tk.Tk() # creating the UI window

icon_image = tk.PhotoImage(file="logo.png") # loading the icon image
root.iconphoto(True, icon_image) # setting the icon of the app

# funtion to dynamically resize the background image when the window is resized
def resize_background(event):
    global bg_image, resized_bg, bg_label
    new_width = event.width
    new_height = event.height
    resized_bg = image.resize((new_width, new_height), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_bg)
    bg_label.config(image=bg_image)

    
# Load background image (match window size or resize as needed)
image = Image.open("BG.png")  # loading image
# bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
bg_image = ImageTk.PhotoImage(image)




# # Create label and place it
# bg_label = tk.Label(root, image=bg_photo)
# bg_label.image = bg_photo  # keep reference
# bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # full window

bg_label = tk.Label(root, image=bg_image)
bg_label.image = bg_image  # keep reference
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_label.bind("<Configure>", resize_background)


root.title("Smart Behavior and Weapon Detection") # title displaying on top of the window
root.geometry("1200x850") # size of the application window
root.attributes('-fullscreen', True)
# def get_system_theme():
    # return "Dark" if darkdetect.isDark() else "Light"

# defining a function to change settings like fps, recording time etc..
def open_settings():
    global selected_fps # accessing global variable

    settings_window = tk.Toplevel(root) # creating the settings window
    settings_window.title("Settings") # title on top of the window
    settings_window.geometry("300x300") # size of the settings window

    ttk.Label(settings_window, text="Settings Panel", font=("Arial", 14)).pack(pady=10) # label inside the settings window itself

    # FPS option
    fps_frame = ttk.Frame(settings_window)
    fps_frame.pack(pady=10)

    ttk.Label(fps_frame, text="Live Detection FPS: ").pack(side=tk.LEFT)

    fps_spinbox = ttk.Spinbox(fps_frame, from_=10, to=90, width=5)
    fps_spinbox.pack(side=tk.LEFT)
    fps_spinbox.delete(0, "end")
    fps_spinbox.insert(0, selected_fps)

    # buffer time option
    buffer_frame = ttk.Frame(settings_window)
    buffer_frame.pack(pady=10)

    ttk.Label(buffer_frame, text="Record Seconds (Pre & Post): ").pack(side=tk.LEFT)

    buffer_spinbox = ttk.Spinbox(buffer_frame, from_=1, to=60, width=5)
    buffer_spinbox.pack(side=tk.LEFT)
    buffer_spinbox.delete(0, "end")
    buffer_spinbox.insert(0, record_buffer_seconds)

    # check box to toggle alarm on or off
    alarm_var = tk.BooleanVar()
    alarm_var.set(alarm_enabled)
    
    alarm_check = ttk.Checkbutton(
        settings_window,
        text="Enable Alarm Sound",
        variable=alarm_var
    )
    alarm_check.pack(pady=10)

    # # Create a custom style
    # style = ttk.Style()
    # style.theme_use('clam')
    
    # # Customize the TMenubutton part of OptionMenu
    # style.configure('Custom.TMenubutton',
    #                 foreground='blue',  # text color
    #                 background='gray',  # background of button
    #                 font=('Arial', 12))

    
    # selecting camera source option
    camera_frame = tk.Frame(settings_window)
    camera_frame.pack(pady=10)
    
    tk.Label(camera_frame, text="Camera Source:").pack(side=tk.LEFT)
    
    camera_var = tk.StringVar(value=camera_source)
    camera_menu = ttk.OptionMenu(camera_frame, camera_var, camera_var.get(), "Webcam", "IP Camera")
    # camera_menu.configure(style='Custom.TMenubutton')
    camera_menu.pack(side=tk.LEFT)
    
    # IP camera URL input (shown only if "IP Camera" is selected)
    ip_url_var = tk.StringVar(value=ip_camera_url)
    ip_url_frame = ttk.Frame(settings_window)
    ip_url_entry = ttk.Entry(ip_url_frame, textvariable=ip_url_var, width=25)

    def toggle_ip_url_field(*args):
        if camera_var.get() == "IP Camera":
            ip_url_frame.pack(pady=5)
            ttk.Label(ip_url_frame, text="IP Camera URL:").pack(side=tk.LEFT)
            ip_url_entry.pack(side=tk.LEFT)
        else:
            ip_url_frame.pack_forget()
    
    camera_var.trace_add("write", toggle_ip_url_field)
    toggle_ip_url_field()  # call initially to hide/show



    def save_settings():
        global selected_fps, record_buffer_seconds, alarm_enabled, camera_source, ip_camera_url
        try:
            selected_fps = int(fps_spinbox.get()) # saving the fps set by user
            record_buffer_seconds = int(buffer_spinbox.get()) # saving the recoring seconds set by user
            alarm_enabled = alarm_var.get() # saving alarm preference
            camera_source = camera_var.get()
            ip_camera_url = ip_url_var.get()
            messagebox.showinfo("Settings Saved", f"FPS: {selected_fps}\nBuffer: {record_buffer_seconds}s\nAlarm: {'On' if alarm_enabled else 'Off'}")
            settings_window.destroy()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid FPS/Buffer value.")

    bf = ttk.Frame(settings_window)
    bf.pack(pady=10)
    tk.Button(bf, text="Save", command=save_settings).pack(side="left", padx=5)
    tk.Button(bf, text="Close", command=settings_window.destroy).pack(side="left", padx=5)



# main title displaying inside the application
# Label(root, text="Smart Behavior and Weapon Detection System", font=("Arial", 16)).pack(pady=10)

# creating a function to browse in the computer to select the file to perform detection upon (file selection)
def select_file():
    # only the file types specified are allowed
    file_path = filedialog.askopenfilename(filetypes=[('Images', '*.jpg *.png *.jpeg'), ('Videos', '*.mp4 *.avi *.mkv')])
    if file_path: # if file path is valid
        file_label.config(text=f"Selected: {file_path}") # just above the picture it displays path of the file selected or shows no file selected
        process_file(file_path) # calling the process file function on the selected picture to perform detection 


# function to start live deteciton
def start_live_detection():
    global cap, live_running # declaring variables as global variables
    cap = cv2.VideoCapture(0) # this opens the default camera
    if not cap.isOpened(): # if there is an error opening the default camera
        # result_label.config(text="Camera not accessible") # a label below the picture will say the text specified
        return
    live_running = True # set live running to true while live detection is on
    threading.Thread(target=show_live_frame, daemon=True).start() # running the live detection on a seperate thread of cpu for better performance 
    file_label.config(text="Doing Live Detection") # display the text specified above the picture

# function to stop detection
def stop_live_detection():
    global cap, live_running, recording, recording_writer, recording_frames # accessing global variables
    live_running = False # setting live running to false because now we are stopping live detection
    if cap: # checking if there is something in th ecap variable
        cap.release() # releasing all frames
    canvas.delete("all") # clearing the canvas (the gray frame in the UI)
    # result_label.config(text="Live detection stopped.") # text at the bottom of the application
    file_label.config(text="Live Detection Stopped") # reset the file label if previously any file was selected

    # if recording is in progress, save it now
    if recording and recording_writer:
        for f in recording_frames:
            recording_writer.write(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
        recording_writer.release()
        print("Recording saved on stop.")
    recording = False # setting the recording variable back to false
    recording_writer = None
    recording_frames = []

prev_time = None
# display frames of camera and run model upon also save 5 seconds pre and post weapon detection
from datetime import datetime


def show_live_frame():
    global cap, live_running, selected_fps, record_buffer_seconds

    from collections import deque
    import time
    import imageio
    import threading
    # from playsound import playsound

    pygame.mixer.init()  # initialize pygame mixer

    fps = selected_fps
    buffer_seconds = record_buffer_seconds

    frame_buffer = deque(maxlen=int(buffer_seconds * fps))  # circular buffer to store previous frames
    video_frames = []  # frames to save for recording
    recording = False
    recording_end_time = 0
    last_alert_time = -float("inf")

    if not os.path.exists("recordings"):
        os.makedirs("recordings")

    print("Live detection started.")

    prev_time = time.time()

    # Create a persistent canvas image object once
    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    canvas_center_x = canvas_width // 2
    canvas_center_y = canvas_height // 2
    dummy_img = ImageTk.PhotoImage(Image.new("RGB", (400, 400)))
    canvas.image_item_id = canvas.create_image(canvas_center_x, canvas_center_y, anchor=tk.CENTER, image=dummy_img)

    # Determine camera source
    if camera_source == "Webcam":
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(ip_camera_url)

    if not cap.isOpened():
        print("[ERROR] Unable to open video stream")
        return

    while cap and live_running:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        elapsed_time = current_time - prev_time
        if elapsed_time < 1.0 / fps:
            time.sleep(1.0 / fps - elapsed_time)
        prev_time = current_time

        results = model(frame)
        result = results[0]  # single-frame detection result

        Gun = False
        weapon_keywords = ("revolver", 'pistol') # keywords which will trigger the alarm and save recording
        allowed_classes = ['Pistol', 'Revolver', 'Assault Rifle'] # which will draw the bounding box

        # Check if any detection boxes exist
        if result.boxes is not None and len(result.boxes) > 0:
            # Loop through detections
            for box in result.boxes:
                label = model.names[int(box.cls[0])].lower()

                # Check for weapon keywords
                if any(keyword in label for keyword in weapon_keywords):
                    Gun = True

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert to RGB for tkinter

        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]

                if box.conf[0] > 0.70 and class_name in allowed_classes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = f"{class_name} {box.conf[0]:.2f}"
                    cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame_rgb, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        frame_buffer.append(frame_rgb.copy())  # store latest frame in buffer

        if Gun:
            # here 5 second means alarm will sound after 5 seconds of previous alarm
            if alarm_enabled and time.time() - last_alert_time > 5:
                def play_alert():
                    try:
                        pygame.mixer.music.load("siren alert.mp3")
                        pygame.mixer.music.play()
                    except Exception as e:
                        print("[ERROR] Playing sound:", e)

                threading.Thread(target=play_alert, daemon=True).start()
                last_alert_time = time.time()

            if not recording:
                recording = True
                recording_end_time = time.time() + 5  # record next 5 seconds
                video_frames = list(frame_buffer)  # include previous frames
            else:
                recording_end_time = time.time() + 5  # extend recording window

        if recording:
            video_frames.append(frame_rgb.copy())

            if time.time() > recording_end_time:
                recording = False
                timestamp = int(time.time())
                out_path = os.path.join("recordings", f"detection_{timestamp}.mp4")

                try:
                    imageio.mimsave(out_path, video_frames, fps=int(fps))  # save video
                    print(f"[SAVED] Recording saved: {out_path}")
                except Exception as e:
                    print("[ERROR] Failed to save recording:", e)

                pygame.mixer.music.stop()  # stop the siren after recording ends
                video_frames = []

        cv2.putText(frame_rgb, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)  # timestamp

        fps_text = f"FPS: {fps:.2f}"
        text_size, _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_x = frame_rgb.shape[1] - text_size[0] - 10
        cv2.putText(frame_rgb, fps_text, (text_x, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)  # show fps

        # img = Image.fromarray(frame_rgb)

        # Dynamically get current canvas size
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        img = Image.fromarray(frame_rgb)
        # Resize to fill the entire canvas (may stretch image slightly)
        img_resized = img.resize((canvas_width, canvas_height), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img_resized)

        # img = img.resize((current_width, current_height), Image.LANCZOS)
        # imgtk = ImageTk.PhotoImage(img)

        canvas.imgtk = imgtk  # keep a reference so image is not garbage collected
        canvas.itemconfig(canvas.image_item_id, image=imgtk)

        canvas.coords(canvas.image_item_id, canvas.winfo_width() // 2, canvas.winfo_height() // 2)

        root.update_idletasks()  # update UI
        root.update()


# frame to group buttons to the left side
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, anchor="n", padx=10, pady=50)

# button to select an image or a video from the computer
select_btn_img = tk.PhotoImage(file="new buttons/Select.png")
select_button = tk.Button(left_frame, image=select_btn_img, borderwidth=0, highlightthickness=0, command=select_file)
select_button.image = select_btn_img
select_button.pack(pady=5)

# Button(left_frame, text="Select Image/Video", command=select_file).pack(pady=5) 

# button to start live detection, calls the start_live_detection function when pressed
start_btn_img = tk.PhotoImage(file="new buttons/start.png")
start_button = tk.Button(left_frame, image=start_btn_img, borderwidth=0, highlightthickness=0, command=start_live_detection)
start_button.image = start_btn_img
start_button.pack(pady=5)

# Button(left_frame, text="Start Live Detection", command=start_live_detection).pack(pady=5)


# button to stop live detection, calls the stop_live_detection function when pressed
stop_btn_img = tk.PhotoImage(file="new buttons/stop.png")
stop_button = tk.Button(left_frame, image=stop_btn_img, borderwidth=0, highlightthickness=0, command=stop_live_detection)
stop_button.image = stop_btn_img
stop_button.pack(pady=5)

# Button(left_frame, text="Stop Live Detection", command=stop_live_detection).pack(pady=5)
normal_mode_buttons = []
essential_buttons = []

stop_sound_btn_img = tk.PhotoImage(file="new buttons/Soundoff.png")
stop_sound_button = tk.Button(root, image=stop_sound_btn_img, borderwidth=0, highlightthickness=0, command=lambda: pygame.mixer.music.stop())
stop_sound_button.image = stop_sound_btn_img
stop_sound_button.place(relx=1.0, rely=0.5, anchor="e")
# essential_buttons.append(stop_sound_button)

# stop_sound = tk.Button(root, text="Stop Sound", command=lambda: pygame.mixer.music.stop())
# stop_sound.pack(side=tk.RIGHT, anchor="e", padx=1, pady=5)

root.bind("<m>", lambda event: pygame.mixer.music.stop())


# function that will clear the ui, like images that are stuck in the canvas or the file labels
def clear_canvas():
    canvas.delete("all") # command that deletes everything on the canvas
    canvas.image = None # setting image back to none
    file_label.config(text="No file selected") # resetting the file label on top of the canvas
    # result_label.config(text="") # label below the image


# Button(root, text="Clear Screen", command=clear_canvas).pack(pady=5) 


# Button(root, text="Exit", command=root.destroy).pack(pady=5)

# path or name of the file selected by the user shown above the canvas image,
# if none is selected it displays text specified
file_label = Label(root, text="No file selected", fg="red")
file_label.place(relx=0.55,y=240, anchor='n')

is_canvas_fullscreen = False

# Update layout
root.update_idletasks()

# Canvas size and position
canvas_width = 750
canvas_height = 550
canvas_x = (root.winfo_width() - canvas_width) // 2
canvas_y = file_label.winfo_y() + file_label.winfo_height() + 10  # 10px gap

# Create canvas and place it at the bottom center
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="gray")
# canvas.place(relx=0.5, y=1, anchor="s")
canvas.place(
    relx=0.55,
    rely=0.6,
    anchor="center",
    width=canvas_width,
    height=canvas_height
)

root.update_idletasks()
original_canvas_geometry = {
    "width": canvas.winfo_width(),
    "height": canvas.winfo_height()
}

# Function to center image on canvas
def center_canvas_image(event=None):
    if hasattr(canvas, "image_item_id"):
        canvas.coords(
            canvas.image_item_id,
            canvas.winfo_width() // 2,
            canvas.winfo_height() // 2
        )

canvas.bind("<Configure>", center_canvas_image)

exit_fs_img = tk.PhotoImage(file="new buttons/ExitFS.png")

# to turn canvas into fullscreen mode
def toggle_canvas_fullscreen():
    global is_canvas_fullscreen

    is_canvas_fullscreen = not is_canvas_fullscreen

    if is_canvas_fullscreen:
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        lower_right_frame.place_forget()
        lower_right_frame.pack_forget()
        # show only essential buttons
        for btn in normal_mode_buttons:
            btn.pack_forget()
        for btn in essential_buttons:
            btn.pack(pady=5)
        stop_sound_button.pack_forget()
        stop_sound_button.grid_forget()
        stop_sound_button.place(relx=1.0, rely=0.5, anchor="e")
        stop_sound_button.lift()
        fullscreen_button.config(image=exit_fs_img)  # change image to exit fullscreen image
    else:
        canvas.place_forget()
        canvas.place(
            relx=0.55,
            rely=0.6,
            anchor="center",
            width=original_canvas_geometry["width"],
            height=original_canvas_geometry["height"]
        )
        fullscreen_button.config(image=fs_btn_img)  # original image
        for btn in essential_buttons + normal_mode_buttons:
            btn.pack(pady=5)
        lower_right_frame.place(relx=1.0, rely=0.9, anchor="se")
        stop_sound_button.place(relx=1.0, rely=0.5, anchor="e")
    root.update_idletasks()



# frame to group buttons to the upper right side
upper_right_frame = tk.Frame(root)
upper_right_frame.place(relx=1.0, rely=0.05, anchor="ne")

# exit button to exit the application
exit_btn_img = tk.PhotoImage(file="new buttons/cancel.png")
exit_button = tk.Button(upper_right_frame, image=exit_btn_img, borderwidth=0, highlightthickness=0, command=root.destroy)
exit_button.image = exit_btn_img
exit_button.pack(pady=5)
essential_buttons.append(exit_button)

# button to turn canvas into full screen mode
fs_btn_img = tk.PhotoImage(file="new buttons/FS.png")
fullscreen_button = tk.Button(upper_right_frame, image=fs_btn_img, borderwidth=0, highlightthickness=0, command=toggle_canvas_fullscreen)
fullscreen_button.image = fs_btn_img
fullscreen_button.pack(pady=5)
essential_buttons.append(fullscreen_button)

# fullscreen_button = tk.Button(root, text="Enable Full Screen", command=toggle_canvas_fullscreen)
# fullscreen_button.place(relx=0.99, rely=0.99, anchor="se")

# the clear canvas button, calls the clear_canvas function
clear_btn_img = tk.PhotoImage(file="new buttons/CLS.png")
clear_button = tk.Button(upper_right_frame, image=clear_btn_img, borderwidth=0, highlightthickness=0, command=clear_canvas)
clear_button.image = clear_btn_img
clear_button.pack(pady=5)
normal_mode_buttons.append(clear_button)

# frame to group buttons to the upper right side
lower_right_frame = tk.Frame(root)
lower_right_frame.place(relx=1.0, rely=0.9, anchor="se")

settings_btn_img = tk.PhotoImage(file="new buttons/settings.png")
settings_button = tk.Button(lower_right_frame, image=settings_btn_img, borderwidth=0, highlightthickness=0, command=open_settings)
settings_button.image = settings_btn_img
settings_button.pack(pady=5)
normal_mode_buttons.append(settings_button)

info_btn_img = tk.PhotoImage(file="new buttons/info.png")
info_button = tk.Button(lower_right_frame, image=info_btn_img, borderwidth=0, highlightthickness=0)
info_button.image = info_btn_img
info_button.pack(pady=5)
normal_mode_buttons.append(info_button)

help_btn_img = tk.PhotoImage(file="new buttons/help.png")
help_button = tk.Button(lower_right_frame, image=help_btn_img, borderwidth=0, highlightthickness=0)
help_button.image = help_btn_img
help_button.pack(pady=5)
normal_mode_buttons.append(help_button)



if info_button.winfo_exists():
    ToolTip(info_button, """The Smart Weapon Detection System automatically /n 
                    detects weapons and keeps you safe by sending an /n
                    alarm as soon as a weapon is detected""")

if help_button.winfo_exists():
    ToolTip(help_button, """For any kind of help or instruction please/n 
                    e-mail us at smartdetection@help.com""")


# binding escape key to exit fullscreen when entered with ctrl f or cmnd f
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

def on_f_key(event=None):
    toggle_canvas_fullscreen()
    root.attributes('-fullscreen', True)
    
# binding f key to enter or exit full canvas mode
root.bind("<f>", on_f_key)

def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))
    
import platform
# platform-specific fullscreen toggle
if platform.system() == "Darwin":  # macOS
    root.bind("<Command-f>", toggle_fullscreen)
else:  # Windows or Linux
    root.bind("<Control-f>", toggle_fullscreen)

# result_label = Label(root, text="", fg="green")
# result_label.pack()

# Image/Video Detection Handler
def process_file(file_path):
    # display and open image preview
    if file_path.lower().endswith(('jpg', 'jpeg', 'png')):
        img = Image.open(file_path) # opening image using PILLOW
        img.thumbnail((400, 400)) # resizing image
        imgtk = ImageTk.PhotoImage(img) # Keeps the image saved so garbage collection dont remove it
        canvas.imgtk = imgtk  # store as an attribute of canvas to persist

        # center the image on canvas
        canvas.update()  # make sure canvas has correct width/height
        cx = canvas.winfo_width() // 2
        cy = canvas.winfo_height() // 2
        canvas.create_image(cx, cy, anchor=tk.CENTER, image=canvas.imgtk) # display image on canvas

        # run the model and get results
        results = model(file_path, save=True, project="detections", name="results", exist_ok=True)
        boxes = results[0].boxes
        num_detections = len(boxes)
        
        # draw boxes on image
        frame = cv2.imread(file_path)
        for box in boxes:
            if box.conf >= 0.5:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = f"{model.names[int(box.cls[0])]} {box.conf[0]:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # convert to RGB and display in canvas
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((400, 400))
        imgtk = ImageTk.PhotoImage(img)

        # center the detection image on canvas
        cx = canvas.winfo_width() // 2
        cy = canvas.winfo_height() // 2
        canvas.create_image(cx, cy, anchor=tk.CENTER, image=imgtk)
        canvas.image = imgtk # Keeps the image saved so garbage collection dont remove it
        
        # update label at the bottom of the application
        # result_label.config(text="Detection Complete! Check 'detections/' folder.")
        
        # result_label.config(text="Detection Complete! Check 'detections/' folder.") # message at the bottom of screen
        # this command refreshes the ui before moving to the next code, before doing this the result
        # of the detection was not updating until i clicked ok
        root.update_idletasks()
        # popup message
        messagebox.showinfo("Detection Complete",
                            f"Weapons Detected: {num_detections}\n"
                            f"Results saved in: detections/results/")
    
    elif file_path.lower().endswith(('mp4', 'avi', 'mkv', 'gif')):
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            # result_label.config(text="Failed to open video.")
            return
    
        import datetime
        import imageio.v2 as imageio  # safer import
        video_frames = []
        total_detections = 0
    
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or fps > 240:
            fps = 20
    
        while True:
            ret, frame = cap.read()
            if not ret:
                break
    
            results = model(frame)[0]
    
            for box in results.boxes:
                if box.conf >= 0.5:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = f"{model.names[int(box.cls[0])]} {box.conf[0]:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    total_detections += 1
    
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_frames.append(frame_rgb)
    
        cap.release()
    
        os.makedirs("detections", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join("detections", f"video_result_{timestamp}.mp4")
    
        try:
            imageio.mimsave(out_path, video_frames, fps=int(fps))
            # result_label.config(text=f"Video Detection Complete! Saved to {out_path}")
            messagebox.showinfo("Detection Complete",
                                f"Weapons Detected: {total_detections}\n"
                                f"Results saved in: {out_path}")
        except Exception as e:
            # result_label.config(text="Failed to save video.")
            messagebox.showerror("Save Error", f"Could not save video.\nError: {e}")


# Start GUI loop
root.mainloop()