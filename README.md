To run the game from github:
1) Set up a github codespaces
2) In the codespaces terminal, run ./start-gui.sh and wait for the script to finish
3) In the Ports tab, make port 6080's visibility public
4) In a new terminal (don't stop the first one), run export DISPLAY=:1
5) Run python3 main.py

You will find you game at port 6080 in the Ports tab

If you get the "No module named 'pygame'" error, run pip install pygame or pip install pygame-ce, then run python3 main.py again