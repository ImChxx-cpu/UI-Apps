import tkinter as tk
from PIL import Image, ImageFilter, ImageDraw, ImageTk


NEUMORPH_BG = "#e0e5ec"  # base background color


def create_neumorph_image(size, *, radius=20, color=NEUMORPH_BG,
                          offset=8, blur=12,
                          light="#ffffff", dark="#a3b1c6"):
    """Return a PIL.Image with neumorphic style."""
    width, height = size
    base = Image.new("RGBA", (width, height), color)

    # Light shadow towards top-left
    img_light = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_l = ImageDraw.Draw(img_light)
    draw_l.rounded_rectangle(
        [ -offset, -offset, width, height],
        radius, fill=light
    )
    img_light = img_light.filter(ImageFilter.GaussianBlur(blur))

    # Dark shadow towards bottom-right
    img_dark = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_d = ImageDraw.Draw(img_dark)
    draw_d.rounded_rectangle(
        [ offset, offset, width + offset, height + offset],
        radius, fill=dark
    )
    img_dark = img_dark.filter(ImageFilter.GaussianBlur(blur))

    # Paste shadows and main rectangle
    base.paste(img_light, mask=img_light)
    base.paste(img_dark, mask=img_dark)
    draw_base = ImageDraw.Draw(base)
    draw_base.rounded_rectangle(
        [0, 0, width, height], radius, fill=color
    )
    return base


class NeumorphButton(tk.Canvas):
    """Simple neumorphic button implemented with Canvas."""

    def __init__(self, master=None, text="", command=None, width=150, height=50,
                 radius=20, color=NEUMORPH_BG, **kwargs):
        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=color, **kwargs)
        self._command = command
        self._size = (width, height)
        self._radius = radius
        self._color = color
        self._offset = 6
        self._blur = 8
        # Create normal and pressed images
        normal_img = create_neumorph_image(self._size, radius=radius,
                                           color=color, offset=self._offset,
                                           blur=self._blur)
        pressed_img = create_neumorph_image(self._size, radius=radius,
                                            color=color, offset=-self._offset,
                                            blur=self._blur)
        self._photo_normal = ImageTk.PhotoImage(normal_img)
        self._photo_pressed = ImageTk.PhotoImage(pressed_img)
        self._img_id = self.create_image(0, 0, image=self._photo_normal, anchor="nw")
        self._text_id = self.create_text(width // 2, height // 2,
                                         text=text, font=("Helvetica", 12),
                                         fill="#333333")
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", lambda e: self.configure(cursor="hand2"))

    def _on_press(self, event):
        self.itemconfigure(self._img_id, image=self._photo_pressed)

    def _on_release(self, event):
        self.itemconfigure(self._img_id, image=self._photo_normal)
        if self._command:
            self._command()


def apply_neumorph_style(widget, *, radius=20, color=NEUMORPH_BG):
    """Apply base colors and rounding to customtkinter widgets."""
    try:
        widget.configure(fg_color=color, bg_color=color,
                         corner_radius=radius, border_width=0)
    except tk.TclError:
        pass
    return widget


"""Example usage:

from customtkinter import CTk

root = CTk()
apply_neumorph_style(root)
btn = NeumorphButton(root, text="Click me")
btn.pack(padx=20, pady=20)

root.mainloop()
"""
