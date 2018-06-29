# Squad Maker Web App

Implements a Squad Maker web application using the python
[Flask](http://flask.pocoo.org/) framework and [Bootstrap](https://getbootstrap.com/)
library. For a description of the challenge project and its requirements visit this
[link](https://github.com/darryl-mccool/squad-maker).

An instance of this application has been deployed to
[PythonAnywhere](https://www.pythonanywhere.com/) and is
temporarily accessible at <http://rhyanarthur.pythonanywhere.com>

## Assumptions
1. The Players REST API will not require authentication.
2. The application will not be expected to scale to a very large amount of players.
It will be reasonable to display all players and/or squads on the same page without
the need for pagination. This also implies an O(n^2) squad-making algorithm will be
acceptable.
3. The Bootstrap CDN and googleapis.com domain will be accessible from the client
(I didn't download local copies of the hosted resources I'm using).

## Running the App

1. Clone the squad-maker repository <br>
`git clone https://github.com/arthurcode/squad-maker.git`
2. Create a python 3.6 virtualenv <br>
`mkvirtualenv --python=/usr/bin/python3.6 my-virtualenv`
3. Install required python packages in the virtualenv <br>
`pip install -r /path/to/squad-maker/requirements.txt`
4. Set the FLASK_APP and FLASK_ENV environment variables <br>
`export FLASK_APP=squad_maker_app` <br>
`export FLASK_ENV=development`
5. Run the development server (IP address and port will be printed to the screen)<br>
`cd /path/to/squad-maker` <br>
`flask run`

## Configuring the App

To modify the default application settings create a new configuration file .py file
and set the SQUAD_MAKER_SETTINGS environment variable to point at the new file.

`export SQUAD_MAKER_SETTINGS=/path/to/new/config.py`

Then restart the development server.

## Running Tests

1. Make sure the squad-maker directory is on your PYTHONPATH <br>
`export PYTHONPATH=/path/to/squad-maker/`
2. Run the unit tests <br>
`cd /path/to/squad-maker/tests/unit` <br>
`python -m unittest`
3. Run the benchmark.py integration test <br>
`cd /path/to/squad-maker/tests/integration` <br>
`./benchmark.py`


