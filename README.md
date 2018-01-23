# srs-game

## Install and run with Conda

```
conda create -n python2 python=2.7 anaconda
source ~/anaconda3/bin/activate python2
conda install wxpython
pythonw game_app.py
```

## Run tests

```
python -m unittest discover tests "test*.py" -v
```
