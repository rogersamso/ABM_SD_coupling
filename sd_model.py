"""
Python model 'sd_model.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import if_then_else
from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.9.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 30,
    "time_step": lambda: 0.25,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL_TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL_TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME_STEP",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(name="death_rate", comp_type="Constant", comp_subtype="Normal")
def death_rate():
    return 0.08


@component.add(
    name="deaths",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"death_rate": 1, "pike_population": 1},
)
def deaths():
    return death_rate() * pike_population()


@component.add(name="growth_toxicity", comp_type="Constant", comp_subtype="Normal")
def growth_toxicity():
    return 1500


@component.add(name="initial_pollution", comp_type="Constant", comp_subtype="Normal")
def initial_pollution():
    return 200


@component.add(
    name="reproduction_rate",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "max_growth": 1,
        "pike_population": 1,
        "growth_toxicity": 2,
        "lake_concentration": 1,
    },
)
def reproduction_rate():
    return (
        max_growth()
        * pike_population()
        * growth_toxicity()
        / (growth_toxicity() + lake_concentration())
    )


@component.add(
    name="Lake_concentration",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_lake_concentration": 1},
    other_deps={
        "_integ_lake_concentration": {
            "initial": {"initial_pollution": 1},
            "step": {"input_pollution": 1, "output_pollution": 1},
        }
    },
)
def lake_concentration():
    return _integ_lake_concentration()


_integ_lake_concentration = Integ(
    lambda: input_pollution() - output_pollution(),
    lambda: initial_pollution(),
    "_integ_lake_concentration",
)


@component.add(name="max_growth", comp_type="Constant", comp_subtype="Normal")
def max_growth():
    return 0.1


@component.add(
    name="output_pollution",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"lake_concentration": 2, "self_purification": 2},
)
def output_pollution():
    return if_then_else(
        lake_concentration() >= self_purification(),
        lambda: self_purification(),
        lambda: lake_concentration(),
    )


@component.add(name="self_purification", comp_type="Constant", comp_subtype="Normal")
def self_purification():
    return 80


@component.add(name="input_pollution", comp_type="Constant", comp_subtype="Normal")
def input_pollution():
    return 100


@component.add(
    name="Pike_population",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_pike_population": 1},
    other_deps={
        "_integ_pike_population": {
            "initial": {},
            "step": {"reproduction_rate": 1, "deaths": 1},
        }
    },
)
def pike_population():
    return _integ_pike_population()


_integ_pike_population = Integ(
    lambda: reproduction_rate() - deaths(), lambda: 100, "_integ_pike_population"
)
