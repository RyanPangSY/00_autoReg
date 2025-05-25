import tkinter as tk
from tkinter import ttk
from calendar import monthrange, month_name
from datetime import datetime
import yaml
import os
import time
import datetime
from threading import Thread
from autoReg import AutoRegistor
from dataExtract import DataExtractor # Ensure this is the correct import path for your data extraction function
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CalendarApp:
    def __init__(self, root, year=2025):
        self.root = root
        self.year = year
        self.months = []  # List of month names from date.yaml
        self.month_index = 0  # Current month index
        self.month = 1  # Numerical month (updated in load_availability_data)
        self.selected_dates = []  # List to store selected dates
        self.buttons = {}  # Dictionary to store date buttons/labels
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, pady=5)  # Reduced pady
        self.refreshing_data = False
        self.last_refreshed_time = str(datetime.datetime.now()).split(".")[0]
        self.monthDict = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }
        self.inv_monthDict = {self.monthDict[k]: k for k in self.monthDict.keys()}
        # Equipment dictionary
        self.equipment_dict = {
            0: ["ProtoMAX abrasive waterjet cutting machine", "https://innowingwaterjet.ycb.me"],
            1: ["CNC milling machine", "https://innowingcncmilling.ycb.me"]
        }
        self.cnc_var = tk.IntVar(value=0)
        # Load availability data from DataExtractor
        self.extractor = DataExtractor()
        self.date_multiple_data = self.extractor.extractMultipleData()  # Call the data extraction function
        self.availability_data = self.load_availability_data()
        # Initialize AutoRegistor
        self.registor = AutoRegistor()
        # Set up window and styles
        self.root.title(f"Calendar - {self.monthDict[self.months[self.month_index]]} {self.year}")
        self.root.geometry("450x450")
        self.root.resizable(False, False)  # Fix window size
        # Create styles for rounded square buttons and labels
        style = ttk.Style()
        style.configure("Rounded.TButton",
                        borderwidth=2,
                        relief="flat",
                        background="#90EE90",  # Green for available
                        padding=6,
                        font=("Arial", 10))
        style.configure("Bold.TButton",
                        borderwidth=2,
                        relief="flat",
                        background="#90EE90",  # Green for available
                        padding=6,
                        font=("Arial", 10, 'bold'))
        style.configure("Selected.TButton",
                        borderwidth=2,
                        relief="sunken",
                        background="#A9A9A9",  # Dull grayish-blue for selected
                        padding=6,
                        font=("Arial", 10))
        style.map("Rounded.TButton",
                  background=[("active", "#87CEEB")])  # Blue for hover
        style.map("Bold.TButton",
                  background=[("active", "#87CEEB")])  # Blue for hover
        style.map("Selected.TButton",
                  background=[("active", "#87CEEB")])  # Blue for hover
        # Style for unavailable dates (labels)
        self.unavailable_style = {
            "background": "#D3D3D3",  # Gray for unavailable
            "font": ("Arial", 10),
            "width": 5,
            "borderwidth": 2,
            "relief": "flat"
        }
        # Checkbox variables
        self.waterjet_var = tk.IntVar(value=1)
        # Initial calendar setup
        self.update_calendar()

    def extract_data(self):
        self.date_data = self.extractor.extractMultipleData()  # Call the data extraction function

    def load_availability_data(self):
        # Check equipment selection
        try:
            if self.waterjet_var.get():
                equipment = 0  # ProtoMAX Waterjet
            elif self.cnc_var.get():
                equipment = 1  # CNC Milling
            else:
                logging.warning("Please select an equipment (ProtoMAX Waterjet or CNC Milling).")
                return
        except AttributeError as e:
            logging.error(f"Error in equipment selection: {e}")
            logging.info("Defaulting to ProtoMAX Waterjet.")
            equipment = 0  # Default to ProtoMAX Waterjet if selection fails

        if not self.date_multiple_data[equipment]:
            logging.warning("data cannot be obtained, using empty availability data.")
            return {}
        # Get list of months
        self.months = list(self.date_multiple_data[equipment].keys())
        if not self.months:
            logging.warning("No months found in the data obtained, using empty availability data.")
            return {}
        # Set initial month
        self.month_index = 0
        self.month = self.months[0]
        return self.date_multiple_data[equipment]

    def update_calendar(self):
        # Clear existing widgets in main_frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Update window title
        current_month_name = self.monthDict[self.months[self.month_index]]
        self.root.title(f"Auto Booking - {current_month_name} {self.year}")

        # Header: Month and Year
        header = tk.Label(self.main_frame, text=f"{current_month_name} {self.year}", font=("Arial", 14, "bold"))
        header.grid(row=0, column=0, columnspan=7, pady=3)  # Reduced pady

        # Days of the week, starting with Sunday
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            tk.Label(self.main_frame, text=day, font=("Arial", 10)).grid(row=1, column=i, padx=5)

        # Get first day of the month and number of days
        first_day, num_days = monthrange(self.year, self.month)
        # Adjust first_day for Sunday start (calendar.monthrange: 0=Monday, 6=Sunday)
        first_day = (first_day + 1) % 7  # Shift so 0=Sunday, 1=Monday, ..., 6=Saturday
        row = 2
        col = first_day

        # Clear previous buttons
        self.buttons.clear()

        # Get availability for current month
        availability = self.availability_data.get(self.inv_monthDict[current_month_name], [False])

        # Create date buttons or labels
        for day in range(1, num_days + 1):
            # Determine if date is available
            is_available = availability[day] if day < len(availability) else False
            if is_available:
                # Available dates: Use ttk.Button with hover and click
                style_name = "Selected.TButton" if day in self.selected_dates else "Rounded.TButton"
                btn = ttk.Button(
                    self.main_frame,
                    text=str(day),
                    width=4,
                    style=style_name,
                    command=lambda d=day: self.toggle_date(d)
                )
                # Bind hover events
                btn.bind("<Enter>", lambda event, d=day: self.on_enter(d))
                btn.bind("<Leave>", lambda event, d=day: self.on_leave(d))
                btn.grid(row=row, column=col, padx=2, pady=2)
                self.buttons[day] = btn
            else:
                # Unavailable dates: Use tk.Label, no hover or click
                lbl = tk.Label(
                    self.main_frame,
                    text=str(day),
                    **self.unavailable_style
                )
                lbl.grid(row=row, column=col, padx=2, pady=2)
                self.buttons[day] = lbl
            col += 1
            if col > 6:  # New row after Saturday
                col = 0
                row += 1

        # Month navigation button
        button_text = "Next Month" if self.month_index < len(self.months) - 1 else "Previous Month"
        button_command = self.next_month if self.month_index < len(self.months) - 1 else self.previous_month
        month_button = ttk.Button(
            self.main_frame,
            text=button_text,
            style="Rounded.TButton",
            command=button_command
        )
        month_button.grid(row=row + 1, column=5, columnspan=2, pady=(2,10))  # Reduced pady

        # Note about availability, centered with smaller font
        note_label = tk.Label(self.main_frame, text="Green: Available, Gray: Unavailable", font=("Arial", 8))
        note_label.grid(row=row + 1, column=0, columnspan=3, pady=(2,10))  # Reduced pady

        # Label to display selected dates
        selected_text = f"Selected Dates: {', '.join(str(day) for day in sorted(self.selected_dates))}" if self.selected_dates else "Selected Dates: None"
        selected_label = tk.Label(self.main_frame, text=selected_text, wraplength=350, font=("Arial", 10))
        selected_label.grid(row=row + 2, column=0, columnspan=7, pady=(0,2))  # Reduced pady

        # Equipment selection checkboxes
        checkbox_frame = tk.Frame(self.main_frame)
        checkbox_frame.grid(row=row + 3, column=0, columnspan=7, pady=(0,2))  # Reduced pady
        tk.Checkbutton(
            checkbox_frame,
            text="ProtoMAX Waterjet",
            variable=self.waterjet_var,
            command=self.select_waterjet,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(
            checkbox_frame,
            text="CNC Milling",
            variable=self.cnc_var,
            command=self.select_cnc,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=10)

        # Register button
        register_button = ttk.Button(
            self.main_frame,
            text="Register",
            style="Bold.TButton",
            command=self.register
        )
        register_button.grid(row=row + 4, column=0, columnspan=7, pady=(0,10))  # Reduced pady

        refresh_button = ttk.Button(
            self.main_frame,
            text="Refresh",
            style="Rounded.TButton",
            command=self.refresh_data
        )
        refresh_button.grid(row=row + 5, column=0, columnspan=7, pady=0)  # Reduced pady
        refreshing_label = tk.Label(self.main_frame, fg="green", text="Refreshing data" if self.refreshing_data else f"Last refreshed at: {self.last_refreshed_time}", font=("Arial", 8))
        refreshing_label.grid(row=row + 6, column=0, columnspan=7, pady=0)  # Reduced pady

    def select_waterjet(self):
        # Ensure only one checkbox is selected
        if self.waterjet_var.get():
            self.cnc_var.set(0)
            self.selected_dates.clear()
        else:
            self.waterjet_var.set(1)  # Re-select if deselected, to maintain state
            return # Do nothing if waterjet is deselected
        self.availability_data = self.load_availability_data()
        self.update_calendar()


    def select_cnc(self):
        # Ensure only one checkbox is selected
        if self.cnc_var.get():
            self.waterjet_var.set(0)
            self.selected_dates.clear()
        else:
            self.cnc_var.set(1)
            return # Do nothing if CNC is deselected
        self.availability_data = self.load_availability_data()
        self.update_calendar()

    def on_enter(self, day):
        # Change to blue on hover (only for buttons)
        if isinstance(self.buttons[day], ttk.Button):
            self.buttons[day].state(['active'])

    def on_leave(self, day):
        # Revert to original style (only for buttons)
        if isinstance(self.buttons[day], ttk.Button):
            self.buttons[day].state(['!active'])

    def toggle_date(self, day):
        # Toggle selection for available dates only
        if day in self.selected_dates:
            self.selected_dates.remove(day)
            self.buttons[day].config(style="Rounded.TButton")
        else:
            self.selected_dates.append(day)
            self.buttons[day].config(style="Selected.TButton")
        # Sort dates for consistent display
        self.selected_dates.sort()
        # Update selected dates label
        self.update_selected_label()

    def update_selected_label(self):
        selected_text = f"Selected Dates: {', '.join(str(day) for day in sorted(self.selected_dates))}" if self.selected_dates else "Selected Dates: None"
        for widget in self.main_frame.grid_slaves(row=self.main_frame.grid_size()[1] - 5, column=0):
            widget.config(text=selected_text)

    def next_month(self):
        if self.month_index < len(self.months) - 1:
            self.month_index += 1
            self.month = self.months[self.month_index]
            self.selected_dates.clear()
            self.update_calendar()

    def previous_month(self):
        if self.month_index > 0:
            self.month_index -= 1
            self.month = self.months[self.month_index]
            self.selected_dates.clear()
            self.update_calendar()

    def refresh_data(self):
        if self.refreshing_data:
            logging.info("Data is already being refreshed.")
            return
        self.refreshing_data = True
        logging.info("refreshing_data: %s", self.refreshing_data)
        self.update_calendar()
        time.sleep(1)  # Optional delay to show refreshing state
        # Call extractData to refresh availability data (for multiple months)
        self.date_multiple_data = self.extractor.extractMultipleData()  # Call the data extraction function
        self.availability_data = self.load_availability_data()
        self.refreshing_data = False
        # Update last refreshed time
        self.last_refreshed_time = str(datetime.datetime.now()).split(".")[0]
        self.update_calendar()

    def register(self):
        if not self.selected_dates:
            logging.warning("No dates selected for registration.")
            return

        # Check equipment selection
        if self.waterjet_var.get():
            equipment = 0  # ProtoMAX Waterjet
        elif self.cnc_var.get():
            equipment = 1  # CNC Milling
        else:
            logging.warning("Please select an equipment (ProtoMAX Waterjet or CNC Milling).")
            return

        # Load user info from userInfo.txt
        file_path = os.path.join(os.path.dirname(__file__), 'userInfo.txt')
        user_info = {}
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    info_type, data = map(str.strip, line.split(": ", 1))
                    user_info[info_type] = data
        except FileNotFoundError:
            logging.error("userInfo.txt not found.")
            return

        # Convert selected dates to YYMMDD format
        dates = []
        for day in self.selected_dates:
            date_str = f"25{self.month:02d}{day:02d}"  # e.g., 250501 for May 1, 2025
            dates.append(date_str)

        # Use AutoRegistor object to register
        logging.info(f"Starting registration for {self.equipment_dict[equipment][0]}...")
        self.registor.register_multiple_dates(
            lastName=user_info.get("Last Name", ""),
            firstName=user_info.get("First Name", ""),
            phoneNum=user_info.get("Phone Number", ""),
            email=user_info.get("Email", ""),
            content=user_info.get("Content", ""),
            url=self.equipment_dict[equipment][1],
            dates=dates,
            month=self.month
        )

def main():
    root = tk.Tk()
    app = CalendarApp(root)
    root.iconbitmap("autoReg_icon.ico")
    root.mainloop()

if __name__ == "__main__":
    main()