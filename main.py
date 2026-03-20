import customtkinter as ctk

from controllers.controller import Controller
from database.schema import initialize_database
from views.view import View


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    initialize_database()
    controller = Controller()
    app = View(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
