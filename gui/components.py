# Northshore Logistics System - Reusable UI Component Library
import tkinter as tk
from tkinter import messagebox
import sys

class ScrollableFrame(tk.Frame):
    """A high-performance scrollable container with improved macOS scroll support."""
    def __init__(self, parent, bg="white", *args, **kwargs):
        super().__init__(parent, bg=bg, *args, **kwargs)
        
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas, bg=bg)

        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Localize mousewheel support
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        # Platform-agnostic mousewheel binding
        if sys.platform == "darwin":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        try:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
            else:
                delta = event.delta if sys.platform == "darwin" else int(event.delta/120)
                self.canvas.yview_scroll(int(-1 * delta), "units")
        except tk.TclError:
            pass

class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title="System Entry", width=500, height=600):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(bg="#f5f6fa")
        self.transient(parent)
        self.grab_set()
        
        self.content_frame = tk.Frame(self, bg="white", padx=40, pady=40)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.title_lbl = tk.Label(self.content_frame, text=title.upper(), 
                                  font=("Arial", 12, "bold"), bg="white", fg="#2d3436")
        self.title_lbl.pack(anchor="w", pady=(0, 20))

    def create_field(self, parent, label_text, attr_name, is_pwd=False):
        tk.Label(parent, text=label_text, bg="white", fg="#95a5a6", font=("Arial", 8, "bold")).pack(anchor="w")
        
        # Consistent minimalist 1px border and 11pt font
        entry = tk.Entry(parent, bg="white", fg="#2d3436", font=("Arial", 11), 
                         relief="flat", borderwidth=0, 
                         highlightthickness=1, 
                         highlightbackground="black",
                         highlightcolor="#3498db",
                         insertbackground="black") 
        
        entry.pack(fill="x", pady=(5, 12), ipady=1)
        if is_pwd: entry.config(show="*")
        
        setattr(self, attr_name, entry)
        return entry

class ControlButton(tk.Frame):
    def __init__(self, parent, text, command, bg="#0984e3", fg="white", font=("Arial", 10, "bold"), padx=20, pady=10):
        super().__init__(parent, bg=bg)
        self.command = command
        self.bg_color = bg
        self.hover_color = "#0771c1"
        
        self.lbl = tk.Label(self, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady, cursor="hand2")
        self.lbl.pack(fill="both", expand=True)
        
        for w in [self, self.lbl]:
            w.bind("<Button-1>", lambda e: self.command())
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.config(bg=self.hover_color)
        self.lbl.config(bg=self.hover_color)

    def _on_leave(self, event):
        self.config(bg=self.bg_color)
        self.lbl.config(bg=self.bg_color)
