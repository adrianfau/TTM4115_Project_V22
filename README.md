### TTM4115_Project_V22 | Multiplayer Hole In The Wall Game
Two player Hole-In-The-Wall game to enable accidental conversation across remote workplaces.

##Setup
Ensure camera is accessible in system settings.
#Windows
''pip install -r requirements.txt''
''pipwin install pyaudio''

#Mac / Linux
sudo apt install -y portaudio19-dev
sudo apt install -y pyaudio
pip install -r requirements.txt

To run:

''cd /where/you/installed/ttm4115_project_v22''
''jupyter notebook stm.ipynb''

Everything related to the control of the game is run as a graphical interface within the .ipynb file.
The webcam window with the main game is shown in a separate gui window, which the user might have to manually tab into depending on system settings.
Press Invite on client 1 and Accept on client 2 to establish a connection and start the game.
Ensure both clients are running the code before sending an invite, elsewise the invite will simply timeout.

