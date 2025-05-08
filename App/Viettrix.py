import tkinter as tk
import ttkbootstrap as ttk
import GUI, Camera
from MenuBar import Menubar
from PIL import Image, ImageTk

def HomeWidget(window):
    """Add content to the home widget."""
    # Load the shutdown icon image
    shutdown_image = Image.open("icon/shutdown.png")
    shutdown_image = shutdown_image.resize((30, 30), Image.Resampling.LANCZOS)  # Resize the image if needed
    shutdown_icon = ImageTk.PhotoImage(shutdown_image)

    # Configure the grid columns
    window.grid_columnconfigure(0, weight=0)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)

    # Create the shutdown button with the custom style
    shutdown_button = ttk.Button(window, image=shutdown_icon, command=shutdown, style='White.TButton')
    shutdown_button.image = shutdown_icon  # Keep a reference to avoid garbage collection
    shutdown_button.grid(row=0, column=2, padx=20, pady=5, sticky='e') 

    # Create the camera button
    camera = ttk.Button(window, text="Camera", command=lambda: OpenCamera(window))
    camera.grid(row=0, column=0, padx=20, pady=5)

def shutdown():
    """Handle the shutdown action."""
    app_window.destroy()

def clear_window(window):
    """Clear all widgets from the window."""
    for widget in window.winfo_children():
        widget.destroy()

def OpenCamera(window):
    clear_window(window)
    Camera.createwidgets(window)

# Example usage
if __name__ == "__main__":
    app_window = GUI.create_window()  # Use the window created in GUI.py
    Menubar(app_window)
    HomeWidget(app_window)
    app_window.mainloop()
