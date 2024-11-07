# Experimental code

## How to install experimental conda environment
First, you need to install Mambaforge, which is a faster version of Conda. You can download and install it from the [Mambaforge GitHub page](https://github.com/conda-forge/miniforge#mambaforge).

Once Mambaforge is installed, you can create the experimental environment using the provided `environment.yml` file. Run the following command in your terminal:

```sh
mamba env create -f environment.yml
```

This will create a new conda environment with all the dependencies specified in the `environment.yml` file.

### Activate environment

To activate the newly created environment, use the following command:

```sh
mamba activate prob_risk_noise_experiment
```

## Running the experiments

Once the environment is activated, you can run the experiments using the provided scripts. For example, to run the main experiment script, use:

```sh
python main.py 1 1 1 narrow # (Subject 1, session 1, run 1, narrow range condition)
```

More info about the main.py-script can be found by running 
```sh
python main.py --help

usage: main.py [-h] [--settings SETTINGS] [--n_runs N_RUNS] [--no_examples] [--no_feedback] subject session start_run {narrow,wide}

positional arguments:
  subject              Subject nr
  session              Session
  start_run            Run
  {narrow,wide}        Range (either narrow or wide)

optional arguments:
  -h, --help           show this help message and exit
  --settings SETTINGS  Settings label
  --n_runs N_RUNS      n_runs_to_run
  --no_examples        Do not run examples block
  --no_feedback        Do not run feedback block
```

## Configuring 
You can set up different settings for different experimental environments (e.g., home, 7T scanner, testing room...)
by setting up .yml-files in (`settings`)[settings]

You can then use a specific setting by including `--settings <setting_name_without_.yml>` after the `main.py`-command.


## Dependencies 

Note that this experiment is based on the (exptools2)[https://github.com/Gilles86/exptools2] package developed by Lukas Snoek, Gilles de Hollander, Tomas Knapen and other in Amsterdam.
See also their (examples)[https://github.com/Gilles86/exptools2/tree/master/demos] for some intuition about `Trial`, `Session` and `Stimulus`-objects.

Exptools2, in turn, is built upon (psychopy)[https://www.psychopy.org/index.html].
