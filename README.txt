Create a virtualenv and activate it:

python3 -m venv venv
. venv/bin/activate

Or on Windows cmd:
py -3 -m venv venv
venv\Scripts\activate.bat


Install Flaskr:

pip install -e .

Or if you are using the master branch, install Flask from source before installing Flaskr:

pip install -e ../..
pip install -e .


*******

How to Run:

export FLASK_APP=flaskr
export FLASK_ENV=development
flask run

Or on Windows cmd:

set FLASK_APP=flaskr
set FLASK_ENV=development
flask run

Open http://127.0.0.1:5000 in a browser.

How to Test:

pip install '.[test]'
pytest

Run with coverage report:

coverage run -m pytest
coverage report
coverage html  # open htmlcov/index.html in a browser