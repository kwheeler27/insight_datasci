#!flask/bin/python
from app import app
app.run(host='0.0.0.0', port='80')

'''
The script simply imports the app variable from our app package and invokes its run method to start the server

To start the app you just run this script. On OS X, Linux and Cygwin you have to indicate that this is an executable file before you can run it:

chmod a+x run.py
Then the script can simply be executed as follows:

./run.py
'''