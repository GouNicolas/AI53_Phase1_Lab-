

## Q1
A model.pt is simply an history of the model weights, but the run is still stochastic itself thus it does not guarantee reproducibility.

## Q2
pyproject.toml is a config file used to say which versions can run the project. 

uv.lock is there to select which versions are used to run the code (versions in the ranges given in the toml)

.venv/ is the python virtual environment used for storing the dependencies locally.

## Q3