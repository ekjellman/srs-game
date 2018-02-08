# srs-game

An RPG you play with only the arrow keys! :arrow_backward: :arrow_up_small: :arrow_down_small: :arrow_forward:

## Quick Start

### Set up Conda environment

#### Python 2
```
conda create -n tmab python=2.7 anaconda mock wxpython
source activate tmab
```

#### Python 3
```
conda create -n tmab python=3.6 anaconda mock
source activate tmab
conda install -c newville wxpython-phoenix
```

### Run tests
```
bin/unit-tests
```

### Play the game
```
bin/play-game
```
