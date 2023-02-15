# Agent based social model (julia) coupled with System Dynamics ecological model (Python)


This repository was created to test the possibility to [bidirectionally] couple an ABM built witn [Agents.jl](https://juliadynamics.github.io/Agents.jl/stable/) and an SD model built with [PySD](https://pysd.readthedocs.io/en/master/).

The models are inspired by [Martin and Schlüter (2015)](https://www.frontiersin.org/articles/10.3389/fenvs.2015.00066/full). For practical reasons, the SD model was overly simplified, while the ABM is more similar to the original, but could not be fully reproduced based on the article and the supplementary materials.

The ABM simulates how social pressure and Municipality enforcement motivate households to upgrade their wastewater treatment system, to reduce pollution of a downstream lake.

The SD model simulates how lake pollution affects the population of a fish species.

When the fish population declines below a certain threshold, the Municipality informs polluting households about the need to upgrade their treatmen systems. Moreover, households that have already upgraded their systems, encourage their (close) neighbours to do the same. If after 3 years of breaching the threshold, households have not yet upgraded, the Municipality encourages them to do so (enforcement). When households upgrade the treatment system, they stop polluting the lake.

Both the SD and the ABM exchange information every year, but the SD model time step is 0.25 years.

The workflow is the following:
1. ABM estimates anual pollution, which becomes an input to the SD model
2. Based on the input pollution, the SD model updates the lake pollution and the fish population.
3. The fish population is used as input to the ABM

# Requirements
The ABM model is written in julia, while the SD model is written in Python. A julia script is used to couple the two models, using PyCall to run the SD model.

Users should have [Julia](https://julialang.org/) installed, and a Python conda environment with [PySD](https://pypi.org/project/pysd/) installed on it.

A `config.toml` file needs to be created inside the project, whith the following contents:

```bash
python_path = "path_to_the_python_executable_in_your_conda_environment"
```

# Running the models

From a terminal, load the julia REPL with the required dependencies:

```bash
julia --project
```

## Running the ABM alone and plotting results
```julia
include("social_model_plots.jl")
```

This will create an `mp4` video, representing the Municipality (red dot) and the households. Blue means that households are polluting, orange means that they already upgraded their systems.

## Running the SD model alone

```julia
include("sd_model.jl")

sd_model.run()
```

This should return a DataFrame with the simulation results.


## Running the coupled model

```julia
include("coupling.jl")
```

# Limitations
The dynamics simulated with the current versions of the models are not realistic.

For now only the variables from the ABM model are stored in a DataFrame.






