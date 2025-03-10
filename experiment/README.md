# Experimental Code

## How to Install Experimental Conda Environment

First, install Mambaforge, which is a faster version of Conda. You can download and install it from the [Mambaforge GitHub page](https://github.com/conda-forge/miniforge#mambaforge).

Once Mambaforge is installed, navigate to the `prob_risk_noise/experiment` folder and run the following command in your terminal:

```sh
mamba env create -f environment.yml # Ensure you are in `prob_risk_noise/experiment`
```

This will create a new conda environment named `prob_risk_noise_experiment` with all the dependencies specified in the `environment.yml` file.

### Activate the Environment

To activate the newly created environment, use the following command:

```sh
mamba activate prob_risk_noise_experiment
```

## Running the Experiment

Once the environment is activated, you can run the experiment using the `task.py` script. For example, to run a session with subject 1, session 1, run 1, and the default response bar type (`natural`), use:

```sh
python task.py 1 1 1 --slider_type natural
```

### Command-line Arguments

```sh
usage: task.py [-h] [--settings SETTINGS] [--calibrate_eyetracker] [--slider_type {natural,log,two-stage}] subject session run

positional arguments:
  subject               Subject number
  session               Session number
  run                   Run number

optional arguments:
  -h, --help            Show this help message and exit
  --settings SETTINGS   Specify a settings label (default: "default")
  --calibrate_eyetracker Enable eye tracker calibration before the task
  --slider_type {natural,log,two-stage} Specify response bar type (default: "natural")
```

### Example Runs

1. Run the task with a **logarithmic response slider**:

   ```sh
   python task.py 2 1 3 --slider_type log
   ```

2. Run the task **with eye tracker calibration**:

   ```sh
   python task.py 3 2 2 --calibrate_eyetracker
   ```

3. Run the task **using custom settings from **``:

   ```sh
   python task.py 4 1 1 --settings custom
   ```

## Configuring the Experiment

You can define different settings for different experimental environments (e.g., home, 7T scanner, testing room) by setting up `.yml` files in the `settings/` directory. To use a specific configuration, add `--settings <setting_name_without_.yml>` when running `task.py`.

## Dependencies

This experiment is based on the [exptools2](https://github.com/Gilles86/exptools2) package developed by Lukas Snoek, Gilles de Hollander, Tomas Knapen, and others in Amsterdam. See their [examples](https://github.com/Gilles86/exptools2/tree/master/demos) for insights into `Trial`, `Session`, and `Stimulus` objects.

Exptools2, in turn, is built upon [PsychoPy](https://www.psychopy.org/index.html).