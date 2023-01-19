# How to start

Make sure you have installed Python 3.x.

To use this project, you need to following the steps below:

### Install the dependencies

Create a evnironment with Python 3.x and venv:

```
python3 -m venv env
```

### Active the environment:

```
source env/bin/activate
```

### Install the dependencies:

```
pip install -r requirements.txt
```

### Run the project

```
uvicorn main:app --reload --port 5000
```

Now you can access the project at [http://localhost:5000](http://localhost:5000) and see your API documentation at [http://localhost:5000/docs](http://localhost:5000/docs).

Enjoy!
