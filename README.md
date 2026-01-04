# AutoReg - InnoWing Booking Bot

AutoReg is an automated booking tool designed for the Inno Wing Machine room booking system. It streamlines the process of reserving equipment like the **ProtoMAX abrasive waterjet** and **CNC milling machine** by automating the form-filling and slot-selection process.

> **Note**: The UI mode is currently in beta. Data retrieval may take some time, and minor bugs may occur.

## Prerequisites

Before running the bot, ensure you have the following installed:

*   **Python 3.10+**
*   **Google Chrome** (Latest version recommended)
*   **Git**

## Installation

1.  **Clone the repository**:
    ```bash
    git clone -b ui https://github.com/RyanPangSY/00_autoReg.git
    cd 00_autoReg
    ```

2.  **Install dependencies**:
    This project requires `selenium`.
    ```bash
    pip install selenium
    ```
## Features

*   **Automated Booking**: Automatically navigates the booking site, selects dates/times, and fills user details.
*   **Graphical User Interface (GUI)**: Easy-to-use calendar interface for selecting booking dates.
*   **Multi-Machine Support**: Supports both Waterjet and CNC Milling machines.
*   **Human-like Interaction**: Simulates human mouse movements and clicks to avoid bot detection.
*   **Headless Mode**: Can run in the background without opening a visible browser window (default). **(Currently Disabled: The bot forces a visible window for stability)**

## Configuration

Create or edit the `userInfo.txt` file in the root directory. This file must contain your booking details in the following format:

```text
Last Name: Doe
First Name: John
Phone Number: 12345678
Email: john.doe@example.com
Content: Project Description
```

## Usage

To start the application with the GUI:

```bash
python main.py
```

> **Note**: Headless mode is currently disabled to ensure better compatibility with the booking site's anti-bot measures. The browser window will always open.

### Command Line Arguments

You can customize the execution using the following flags:

*   **`-n` or `--non_headless`**: Run the browser in non-headless mode (visible window). **(Currently enforced by default)**
    ```bash
    python main.py -n
    ```
*   **`-d` or `--debug`**: Disable debug mode (default is enabled).
    ```bash
    python main.py -d
    ```

## How to Use the GUI

1.  Run the script. A calendar window will appear.
2.  **Select Equipment**: Check the box for the machine you want to book (Waterjet or CNC).
3.  **Select Dates**: Click on the dates you wish to book in the calendar.
4.  **Start Booking**: Click the "Start" button (or equivalent) to begin the automation process.
5.  **Monitor**: The bot will launch Chrome (if `-n` is used) and perform the booking. Check the terminal for logs and status updates.

## Troubleshooting

*   **Captcha/Bot Detection**: The bot includes "human-like" mouse movements to mitigate this. If you see a "Something went wrong" popup, the bot is designed to try refreshing the page. ***The problem cannot be solved, try enter the non_headless `-n` mode.***

## Disclaimer

This tool is for educational and personal productivity purposes. Please use it responsibly and adhere to the booking policies of the facility.
