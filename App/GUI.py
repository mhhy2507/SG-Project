import ttkbootstrap as ttk

DEFAULT_RESOLUTION = "1280x720"

def update_resolution(window, resolution):
    window.geometry(resolution)

def create_window():
    window = ttk.Window(themename='cosmo')
    window.title("Viettrix Camera App")
    
    # Set default resolution
    window.geometry(DEFAULT_RESOLUTION)
    window.resizable(True, True)
    
    # Maximize window by default
    window.state('zoomed')
    
    style()

    return window

def style():
    # White Background for Buttons
    style = ttk.Style()
    style.configure('White.TButton', background='white', foreground='black', bordercolor='white', relief='flat')
    style.map('White.TButton', background=[('active', 'white')])
