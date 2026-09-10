# BGIQ
Battlegrounds tool

hearthstone-bg-solver

'''
├── desktop_overlay.py  # Run this to boot up the desktop game overlay
├── solver.py           # The mathematical LP calculation script 
├── requirements.txt    # Lists Python packages to install
└── README.md           # Instructions on how to use the Sheet vs the Overlay
'''

🔧 How to Enable Hearthstone's Live Log Output (log.config)Every user running your desktop overlay app needs to create a tiny configuration file in their local Hearthstone AppData directory.1. Navigate to the Hidden Settings FolderPress the Windows Key + R on your keyboard to open the Windows "Run" prompt box.Paste this exact directory path inside it and hit Enter:text%localappdata%\Blizzard\Hearthstone
Use code with caution.This opens a folder containing your system settings files (like options.txt).2. Create the Configuration FileRight-click an empty space inside that folder, select New, and click Text Document.Name the file exactly:textlog.config
Use code with caution.(Make sure to erase the .txt extension at the very end so it saves purely as a .config extension file type!)3. Paste the Logging Rule BlocksDouble-click your brand-new log.config file to open it in Notepad.Copy and paste these exact instruction blocks inside it, then Save and close the file:ini[Power]
LogLevel=1
ConsolePrinting=True
ScreenPrinting=False

[Zone]
LogLevel=1
ConsolePrinting=True
ScreenPrinting=False
