# Discord-overlay

A Discord PyQT6 app that provide a discord overlay over the windows.

![alt text](/docs/main_frame.png?raw=true  "Window frame visible - default")
![alt text](/docs/main_frame_hidden.png?raw=true  "Window frame hidden - full imersive")

# Usage
## Install and Run
- Start discord
- Download a [release](https://github.com/bashtian-fr/discord-overlay-v2/releases/) according to your system or build it.
- Run the downloaded release. Warning: Windows may see the application as threat. Click 'More info' then 'Run anyway'.
- Discord will ask you to authorize ![Streamkit](https://discord.com/streamkit) to access your discord messages and channels. ![Streamkit](https://discord.com/streamkit) is the official discord app to manage apis/rpc.
- Start the overlay, the frame will be visible, you can hide it using the icon: ![alt text](/docs/toggle_button.png?raw=true  "Hide button")
- You can also toggle the frame using the systray menu:
![alt text](/docs/systray_menu.png?raw=true  "System tray icon and menu")
- You can resize the frame with the bottom corner button.
- Drag the window using the title bar.

## Settings
The setting window can be opened by right clicking on the systemtray icon
There few settings:
- Show only Speakers: will hide all people and only show the person that speak.
- Speaker border color: the color of the border of the avatar when someone speak.
- User nickname fontSize: the size of the text of the nicknames.
- User nickanme color: the color of the text of the nicknames.
- User avatar size: the size of the avatars.

# build
## Windows

1. install python and git:
- https://www.python.org/downloads/
- https://git-scm.com/downloads

2. create a virtualenv
`python3 -m venv .pyvenv3`

3. Source the venv
- windows:
`.pyvenv\Scripts\Activate`

4. clone the sources
`git clone https://github.com/bashtian-fr/discord-overlay-v2.git`

5. install the build deps
`pip install ".[tests]"`

6. Build an executable
`pip install pyinstaller`
`pyinstaller --icon src/discord_overlay/static/images/icon.ico -n discord-overlay --onefile --windowed src/discord_overlay/scripts/__init__.py --add-data "src/discord_overlay/static/;discord_overlay/static/"`

The executable will be create in dist/ folder

## Linux/Macos

In progress
