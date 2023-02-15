
using PyCall
using Pkg
using TOML

config = TOML.parsefile("config.toml")
ENV["PYTHON"] = config["python_path"]
Pkg.build("PyCall")

pysd = pyimport("pysd")

py"""
def set_constant(x):
    return lambda: x
"""

# translate
#sd_model = pysd.read_vensim("sd_model.mdl")

# load the model
sd_model = pysd.load("sd_model.py")

