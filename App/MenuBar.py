import tkinter as tk
from tkinter import Menu, StringVar, messagebox, Toplevel
import ttkbootstrap as ttk
import GUI

def Menubar(window):
    """Create and configure the menu bar."""
    menubar = Menu(window)
    window.config(menu=menubar)

    # Create an Account menu
    account_menu = Menu(menubar, tearoff=0)
    account_menu.add_command(label="Account")
    account_menu.add_command(label="Change Password")
    menubar.add_cascade(label="Account", menu=account_menu)

    # Create an Edit menu
    edit_menu = Menu(menubar, tearoff=0)
    edit_menu.add_command(label="test")
    edit_menu.add_command(label="test")
    edit_menu.add_separator()
    edit_menu.add_command(label="test")
    edit_menu.add_command(label="test")
    edit_menu.add_command(label="test")
    menubar.add_cascade(label="Edit", menu=edit_menu)

    # Create a Sys menu
    sys_menu = Menu(menubar, tearoff=0)
    sys_menu.add_command(label='Resolution', command=lambda: ResolutionWindow(window))
    
    # Create a Mode submenu
    mode_menu = Menu(sys_menu, tearoff=0)
    mode_menu.add_command(label='Full Screen', command=lambda: set_fullscreen(window))
    mode_menu.add_command(label='Windowed', command=lambda: set_windowed(window))
    mode_menu.add_command(label='Borderless', command=lambda: set_borderless(window))
    sys_menu.add_cascade(label='Mode', menu=mode_menu)
    
    sys_menu.add_command(label="Forced Exit", command=lambda: exit())
    menubar.add_cascade(label="System", menu=sys_menu)

def ResolutionWindow(parent):
    """Create a window for selecting resolution."""
    resolution_window = Toplevel(parent)
    resolution_window.title("Select Resolution")
    resolution_window.geometry("250x200")
    resolution_window.resizable(False, False)

    # Dropdown menu for resolution selection
    resolutions = ["1920x1080", "1600x900", "1440x900", "1366x768", "1280x720", "1024x768", "800x600", "640x480"]
    selected_resolution = StringVar(value=GUI.DEFAULT_RESOLUTION)
    
    resolution_menu = ttk.Combobox(resolution_window, textvariable=selected_resolution, values=resolutions)
    resolution_menu.grid(row=1, column=1, padx=10, pady=10)
    
    def validate_resolution():
        """Validate and apply the selected resolution."""
        res = selected_resolution.get()
        if 'x' in res:
            width, height = res.split('x')
            if width.isdigit() and height.isdigit():
                GUI.update_resolution(parent, res)
                resolution_window.destroy()
                return
        messagebox.showerror("Invalid Resolution", "The selected resolution is not valid. Please enter a valid resolution (e.g., 1920x1080).")
        selected_resolution.set(GUI.DEFAULT_RESOLUTION)
    
    def on_enter(event):
        validate_resolution()
    
    def close_resolution():
        resolution_window.destroy()
    
    resolution_menu.bind("<Return>", on_enter)
    
    # Add Apply button
    apply_button = ttk.Button(resolution_window, text="Apply", width=6, command=validate_resolution)
    apply_button.grid(row=1, column=5, padx=10, pady=10)

    # Add Close button
    close_button = ttk.Button(resolution_window, text="Exit", width=6, command=close_resolution)
    close_button.grid(row=2, column=5, padx=10, pady=5)

def set_fullscreen(window):
    """Set the window to full screen mode."""
    window.overrideredirect(False)  # Ensure decorations are restored
    window.attributes('-fullscreen', True)

def set_windowed(window):
    """Set the window to windowed mode."""
    window.attributes('-fullscreen', False)
    window.overrideredirect(False)  # Ensure decorations are restored
    current_width = window.winfo_width()
    current_height = window.winfo_height()
    window.geometry(f"{current_width}x{current_height}")

def set_borderless(window):
    """Set the window to borderless mode."""
    window.attributes('-fullscreen', False)
    window.overrideredirect(True)
    current_width = window.winfo_width()
    current_height = window.winfo_height()
    window.geometry(f"{current_width}x{current_height}")
