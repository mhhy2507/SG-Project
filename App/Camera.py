import cv2
import GUI
import Viettrix
import tkinter as tk
import ttkbootstrap as ttk

from tkinter import *
from pyfirmata2 import Arduino, util
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import messagebox, filedialog

# Defining CreateWidgets() function to create necessary tkinter widgets
def createwidgets(window):
    # Creating object of class VideoCapture with webcam index
    window.cap = cv2.VideoCapture(0)
    
    if not window.cap.isOpened():
        print("Error: Could not open video device")
        return

    # Configure the grid to expand
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_columnconfigure(3, weight=1)
    window.grid_columnconfigure(4, weight=1)
    window.grid_columnconfigure(5, weight=1)
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(1, weight=1)
    window.grid_rowconfigure(2, weight=1)
    window.grid_rowconfigure(3, weight=1)
    window.grid_rowconfigure(4, weight=1)
    window.grid_rowconfigure(5, weight=1)
    window.grid_rowconfigure(6, weight=1)

    # Label Field
    window.feedlabel = ttk.Label(master=window, text="WEBCAM FEED", font=('Comic Sans MS', 20))
    window.feedlabel.grid(row=1, column=1, padx=10, pady=10, columnspan=2, sticky="nsew")
    
    window.previewlabel = ttk.Label(master=window, text="IMAGE PREVIEW", font=('Comic Sans MS', 20))
    window.previewlabel.grid(row=1, column=4, padx=10, pady=10, columnspan=2, sticky="nsew")

    window.cameraLabel = ttk.Label(master=window, borderwidth=3, relief="groove")
    window.cameraLabel.grid(row=2, column=1, padx=10, pady=10, columnspan=2, sticky="nsew")

    window.imageLabel = ttk.Label(master=window, borderwidth=3, relief="groove")
    window.imageLabel.grid(row=2, column=4, padx=10, pady=10, columnspan=2, sticky="nsew")

    # Input Field
    window.input_frame = ttk.Frame(master=window)
    window.input_frame.grid(row=3, column=5, padx=10, pady=10, sticky="nsew")

    window.openImageButton = ttk.Button(master=window.input_frame, width=10, text="BROWSE", command=lambda: imageBrowse(window))
    window.openImageButton.grid(row=3, column=5, padx=10, pady=10, sticky="nsew")

    # Create arrow buttons
    back_button = ttk.Button(window, text="Back", command=lambda: BackToHome(window))
    back_button.grid(row=0, column=0, padx=20, pady=5, sticky="nsew")

    window.UpButton = Button(window, width=10, text="UP", command=led_on)
    window.UpButton.grid(row=5, column=6, padx=10, pady=10, sticky="nsew")

    window.DownButton = Button(window, width=10, text="DOWN", command=led_off)
    window.DownButton.grid(row=6, column=6, padx=10, pady=10, sticky="nsew")

    window.LeftButton = Button(window, width=10, text="LEFT", command=led_on)
    window.LeftButton.grid(row=6, column=5, padx=10, pady=10, sticky="nsew")

    window.RightButton = Button(window, width=10, text="RIGHT", command=led_off)
    window.RightButton.grid(row=6, column=7, padx=10, pady=10, sticky="nsew")

    window.captureBTN = Button(window, text="CAPTURE", command=lambda: Capture(window), font='Calibri', width=20)
    window.captureBTN.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")

    window.CAMBTN = Button(window, text="STOP CAMERA", command=lambda: StopCAM(window), font=('Comic Sans MS', 15), width=13)
    window.CAMBTN.grid(row=4, column=2, sticky="nsew")

    # Initialize the image attribute
    window.imgtk = None

    # Calling ShowFeed() function
    ShowFeed(window)



# Defining ShowFeed() function to display webcam feed in the cameraLabel;
def ShowFeed(window):
    # Capturing frame by frame
    ret, frame = window.cap.read()

    if ret:
        # Flipping the frame vertically
        frame = cv2.flip(frame, 1)

        # Displaying date and time on the feed
        cv2.putText(frame, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255))

        # Changing the frame color from BGR to RGB
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        # Creating an image memory from the above frame exporting array interface
        videoImg = Image.fromarray(cv2image)

        # Creating object of PhotoImage() class to display the frame
        window.imgtk = ImageTk.PhotoImage(image=videoImg)

        # Configuring the label to display the frame
        window.cameraLabel.configure(image=window.imgtk)

        # Calling the function after 10 milliseconds
        window.cameraLabel.after(10, lambda: ShowFeed(window))

    else:
        # Configuring the label to display the frame
        window.cameraLabel.configure(image='')


def destBrowse():
    global destPath
    destDirectory = filedialog.askdirectory(initialdir="YOUR DIRECTORY PATH")
    destPath.set(destDirectory)

def imageBrowse(window):
    global imagePath
    openDirectory = filedialog.askopenfilename(initialdir="YOUR DIRECTORY PATH")
    imagePath.set(openDirectory)

    imageView = Image.open(openDirectory)
    imageResize = imageView.resize((640, 480), Image.ANTIALIAS)
    imageDisplay = ImageTk.PhotoImage(imageResize)

    window.imageLabel.config(image=imageDisplay)
    window.imageLabel.photo = imageDisplay

def Capture(window):
    image_name = datetime.now().strftime('%d-%m-%Y %H-%M-%S')

    if destPath.get() != '':
        image_path = destPath.get()
    else:
        messagebox.showerror("ERROR", "NO DIRECTORY SELECTED TO STORE IMAGE!!")
        return

    imgName = image_path + '/' + image_name + ".jpg"
    ret, frame = window.cap.read()

    cv2.putText(frame, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (430, 460), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255))
    success = cv2.imwrite(imgName, frame)

    saved_image = Image.open(imgName)
    saved_image = ImageTk.PhotoImage(saved_image)

    window.imageLabel.config(image=saved_image)
    window.imageLabel.photo = saved_image

    if success:
        messagebox.showinfo("SUCCESS", "IMAGE CAPTURED AND SAVED IN " + imgName)

led_pin = None

def led_on():
    global led_pin
    try:
        if not led_pin:
            board = Arduino('COM3')
            led_pin = board.get_pin('d:13:o')
        led_pin.write(1)
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to Arduino: {str(e)}")

def led_off():
    global led_pin
    try:
        if not led_pin:
            board = Arduino('COM3')
            led_pin = board.get_pin('d:13:o')
        led_pin.write(0)
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to Arduino: {str(e)}")

def StopCAM(window):
    window.cap.release()
    window.CAMBTN.config(text="START CAMERA", command=lambda: StartCAM(window))
    window.cameraLabel.config(text="OFF CAM", font=('Comic Sans MS', 70))

def StartCAM(window):
    window.cap = cv2.VideoCapture(0)
    window.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    window.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    window.CAMBTN.config(text="STOP CAMERA", command=lambda: StopCAM(window))
    window.cameraLabel.config(text="")
    ShowFeed(window)

def clear_window(window):
    """Clear all widgets from the window."""
    for widget in window.winfo_children():
        widget.destroy()

def BackToHome(window):
    clear_window(window)
    window.cap.release()
    Viettrix.HomeWidget(window)

if __name__ == "__main__":
    window = GUI.create_window()
    createwidgets(window)
    window.mainloop()
