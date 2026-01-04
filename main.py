import argparse
from calendarApp import CalendarApp

def main(args):
    # Force non_headless mode (disable headless)
    args.non_headless = True
    CalendarApp(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Booking Calendar Application")
    parser.add_argument('-d', '--debug', action='store_true', help='Run the application in debug mode')
    parser.add_argument( '-n', '--non_headless', action='store_true', help='Run the application in headless mode')

    main(parser.parse_args())