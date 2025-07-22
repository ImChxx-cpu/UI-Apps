from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from customtkinter import CTkFrame, CTkLabel


class NeumorphButton(CTkFrame):
    """Simple neumorphic button using a canvas for shadows."""

    def __init__(
        self,
        master: tk.Misc | None = None,
        *,
        text: str = "",
        command: Optional[Callable[[], None]] = None,
        width: int = 140,
        height: int = 40,
        corner_radius: int = 15,
        fg_color: str = "#e0e5ec",
        light_color: str = "#ffffff",
        dark_color: str = "#a3b1c6",
        text_color: str = "#555555",
    ) -> None:
        super().__init__(master, width=width, height=height, corner_radius=corner_radius)
        self.configure(fg_color=fg_color)
        self._command = command
        self._light = light_color
        self._dark = dark_color
        self._radius = corner_radius
        self._canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0, bg=fg_color)
        self._canvas.pack(fill="both", expand=True)
        self._label = CTkLabel(self, text=text, text_color=text_color, fg_color="transparent")
        self._label.place(relx=0.5, rely=0.5, anchor="center")
        self._canvas.bind("<Button-1>", self._on_click)
        self._label.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", lambda e: self._draw())
        self._pressed = False

    def _draw(self) -> None:
        self._canvas.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self._radius
        # Outer rounded rectangle
        self._canvas.create_rectangle(0, 0, w, h, outline="", fill=self._canvas["bg"])
        # Light shadow top-left
        self._canvas.create_line(r, 2, w - r, 2, fill=self._light)
        self._canvas.create_line(2, r, 2, h - r, fill=self._light)
        # Dark shadow bottom-right
        self._canvas.create_line(r, h - 2, w - r, h - 2, fill=self._dark)
        self._canvas.create_line(w - 2, r, w - 2, h - r, fill=self._dark)

    def _on_click(self, event: tk.Event) -> None:
        if self._command:
            self._command()


def apply_neumorph_style(widget: tk.Widget, *, fg_color: str = "#e0e5ec") -> None:
    """Configure basic neumorph background and rounded corners if supported."""
    if isinstance(widget, CTkFrame):
        widget.configure(fg_color=fg_color, corner_radius=15)
    elif hasattr(widget, "configure"):
        try:
            widget.configure(fg_color=fg_color)
        except Exception:
            try:
                widget.configure(background=fg_color)
            except Exception:
                pass

