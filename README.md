# Wandering (Still in the works)

This contains the files needed to run the PC App and the Wear App

Installation Process of the PC Version:
- Install python 3.7 or higher
- Enter the following in the command line
  - py -m pip install kivy
  - py -m pip install --upgrade pip wheel setuptools
  - py -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew 
  - py -m pip install kivy.deps.gstreamer 
  - py -m pip install kivy.deps.angle 
  - py -m pip install –-upgrade kivy
  - py -m pip install Flask
  - py -m pip install flask
  - py -m pip install xlsxwriter
  
 Running the PC Version: 
  - py wanderPC.py
  
  
  
  Installation of the Wear App:
  - Enter the files into Android Studio
  - Use Wear Configurations
  - Generate a signed apk: Android studios -> Build -> Generate signed apk -> Create new key -> Choose a path for the signature  -> Fill in the required info -> Click finish -> rename apk into wandervXX.apk with XX being version number
  - Connect the watch to the laptop or PC using the usb cable -> Open terminal -> Go to the directory with the apk -> adb install wandervXX.apk
  
 Running the Wear Versio:
  - Click on MyApplication in the Wear and turn of bluetooth
