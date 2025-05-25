# autoReg
The auto-clicker for Inno-wing Machine room booking system.
UI mode is in beta version (data retrieval process may take more time, bugs could appear)

## Initializing
The project requires `selenium` module
```
pip install selenium
pip show selenium
```
Git clone the UI branch
```
git clone -b ui https://github.com/RyanPangSY/00_autoReg.git
```

## Execution
1. Edit the `userInfo.txt` and fill in your information. The information will be used as the info fill in the registration form.
2. Run `python main.py` and a terminal window pops up.
3. Choose the machine that you wish to book and enter the date (in the format of *YYMMDD*).
4. Let the code cook.
