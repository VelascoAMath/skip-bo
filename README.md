# skip-bo
A full stack implementation of the modern-day classic Skip-Bo


In order to run this program, you will need need to terminals to run the front and back ends.
You should have Postgresql, Python, node, and npm already install on your machine.



## Front-end

App.js creates a websocket connection which should handle the back-end connection.
By default, it assumes that the game is being run locally and connects to localhost.
If other users wish to play the game on other devices, the address must be changed to the server's address.

This is an example list of commands that one may run in order to run the program.

``
> cd front-end
> emacs App.js
> npm install
> npm start
``


## Back-end

A postgresql server should be running on the back-end computer.
In order to access the appropriate database, you will have to create a file called database.ini.
A sample has been provided below.
Change the values to your desired database.
A file called create_databases.py will be included in socket/
Run this program once after creating your database.ini file and starting the postgres server.
This program will create the tables needed to play Skip-Bo.
Finally, run Skip_Bo.py to provide the main server.

``
[postgresql]
host=localhost
database=skip_bo
user=example_user
password=mypassword
port=5432
``


This is an example list of commands that one may run in order to run the program.

``
> cd socket
> emacs database.ini
> python Skip_Bo.py
``
