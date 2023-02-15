using InteractiveDynamics
using CairoMakie

include("social_model.jl")

social_model = initialize_model()

groupcolor(a::Household) = a.pollutes ? :blue : :orange
groupcolor(::Municipality) = :red
groupmarker(::Household) = :rect
groupmarker(::Municipality) = :circle
markersize(::Municipality) = 30
markersize(::Household) = 10

abmvideo(
    "polluters.mp4", social_model, agent_step!;
    ac = groupcolor, am = groupmarker, as = markersize,
    framerate = 4, frames = 30,
    title = "Polluters are blue"
)
