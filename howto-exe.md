# Converting to an executable for Unix systems

``
source env/bin/activate
sudo pyinstaller --onefile cf.py
...
...
cd dist
sudo mv cf /usr/local/bin/cf
``
  
Navigate to your contest problems folder and run cf <COMMAND> <ARGUMENTS>