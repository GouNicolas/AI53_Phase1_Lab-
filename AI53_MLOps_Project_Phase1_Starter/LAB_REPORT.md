

## Q0 starter audit

| file or setting | problem and fix/check |
|---|---|
| `src/reproducibility.py` | The generator was called like a function. Worker seeds ignored PyTorch's seed. Return the generator and use `torch.initial_seed()`. |
| `src/validate_data.py` | The checks and report were incomplete. Check the data and write a stable report. |
| `dvc.yaml` | The prepare command was wrong. The train and evaluate stages were empty. Add all four stages and check them with `dvc dag`. |
| `src/provenance.py` | `build_run_manifest()` was not implemented. Record the code, data and environment. |
| `src/train.py` | MLflow logging was incomplete. Log the settings, metrics, files and model. |
| `params.yaml` (`selection.run_id`) | The run id is empty. Select a run before evaluation. |

## Q1
A model.pt is simply an history of the model weights, but the run is still stochastic itself thus it does not guarantee reproducibility.

## Q2
pyproject.toml is a config file used to say which versions can run the project. 

uv.lock is there to select which versions are used to run the code (versions in the ranges given in the toml)

.venv/ is the python virtual environment used for storing the dependencies locally.

## Q3
random_state = 42 is a way to set the seed, but different computers will have slightly different results due to different hardware and software.

## Q4
git remote stores code, dvc the model weights and the raw images are not transferred with git push, but with dvc push.

## Q5
the model file does not show which code, data or settings produced it. the run manifest records them. the provenance test checks the data identity and settings.

## Q6

| tool | what it records |
|---|---|
| git | code and commits |
| dvc | data and pipeline outputs |
| mlflow | run settings, data, metrics, files and model |

## Q7

i use validation macro-f1 because it treats each class equally. if runs tie, i choose the one with lower validation loss. i expect a lower learning rate to train more slowly.

| change | validate | prepare | train | evaluate |
|---|---|---|---|---|
| `train.learning_rate` | reused | reused | rerun | reused |
| `data.image_size` | reused | rerun | rerun | needs update |
| edit `src/validate_data.py`; report is unchanged | rerun | reused | reused | reused |
| edit `README.md` only | reused | reused | reused | reused |

the learning rate only affects train. image size affects prepared images and later results. a validator edit reruns validate, but an unchanged report lets later stages reuse outputs. the readme is not a stage input.

these are dvc predictions. i checked the graph with `dvc dag`. i could not run `dvc repro` because uv was unavailable, so i ran the modules with the project python.

## Q8

for run c, i changed dropout from 0.30 to 0.50. i expected it might improve macro-f1.

| run | change | validation accuracy | validation macro-f1 | training time (s) | run id |
|---|---|---:|---:|---:|---|
| a | baseline | 0.6391 | 0.6254 | 15.88 | `fbaecc6cfab1445ebac044c8e48f88f6` |
| b | learning rate 0.0003 | 0.6165 | 0.6091 | 16.00 | `3ac7aeb8915947ad92c6ffc57b4cfad7` |
| c | dropout 0.50 | 0.6165 | 0.6068 | 15.63 | `975eece697714e50ada15041b0411865` |

run b scored lower than run a. this fits the slower learning rate. run c did not improve the score. one seed and a small validation set are not enough to prove a setting is better.

macro-f1 is my main metric because it treats each class equally. i used the test set after choosing the model.

## Q9

i chose run a because it had the highest validation macro-f1. its accuracy was 0.6391 and its loss was 0.8327. this comparison used one seed.

the final test used run a (`fbaecc6cfab1445ebac044c8e48f88f6`). accuracy was 0.6484 and macro-f1 was 0.6445. i did not use test results to choose the run.
