using Agents
using Random

@agent Household GridAgent{2} begin
    pollutes::Bool
    willingness_to_upgrade::Float64
end

mutable struct Municipality <: AbstractAgent
    id::Int
    pos::NTuple{2, Int}
    has_legislated::Bool
end

function initialize_model(;
                          num_households = 100,
                          neighbour_distance = 2,
                          griddims = (20, 20),
                          pike_threshold = 400,
                          initial_pike_abundance = 390.,
                          household_pollution = 30,
                          social_influence = 1.2,
                          enforcement_influence = 1.4,
                          seed = 1234)

    properties = Dict(
        :neighbour_distance => neighbour_distance,
        :pike_abundance => initial_pike_abundance,
        :total_pollution => 0,
        :household_pollution => household_pollution,
        :pike_threshold => pike_threshold,
        :years_after_threshold_breach => 0,
        :social_influence => social_influence,
        :enforcement_influence => enforcement_influence)

    space = GridSpaceSingle(griddims, periodic = false)

    rng = Random.MersenneTwister(seed)

    agents_types = Union{Household, Municipality}

    model = ABM(agents_types, space;
                properties = properties,
                rng = rng,
                scheduler = Schedulers.ByType(false, true, agents_types))

    for n in 1:num_households
        household = Household(n, (1,1), true, rand())
        add_agent_single!(household, model)
    end

    municipality = Municipality(num_households + 1, (1,1), false)
    add_agent_single!(municipality, model)

    return model
end

function pollute!(model::ABM, amount)
    model.total_pollution += amount
end

function upgrade_oss!(house::Household)
    house.pollutes = false
end


function update_willingness!(agent::Household, value = 1.5)
    new_willingness = agent.willingness_to_upgrade * value
    agent.willingness_to_upgrade = new_willingness >= 1 ? 1 : new_willingness
end

function inform_neighbours(agent::Household, model)
    all_neighbours = nearby_agents(agent, model, model.neighbour_distance)
    polluting_neighbours = filter(x -> isa(x, Household) && x.pollutes, collect(all_neighbours))

    if !isempty(polluting_neighbours)
        #neighbour = rand(polluting_neighbours)
        for neighbour in polluting_neighbours
            update_willingness!(neighbour, model.social_influence)
        end
    end
end

function inform_neighbours(::Municipality, model)
    """municipality informs, but only those with an already high willingnes to
    upgrade will actually upgrade their systems"""
    num_households = nagents(model) - 1
    # inform all agents but Municipality
    for id in shuffle(1:num_households)
        neighbour = model[id]
        if neighbour.pollutes && neighbour.willingness_to_upgrade >= 0.90
            neighbour.willingness_to_upgrade = 1
        end
    end
end

"""inform all neighbours randomly"""
function enforce(::Municipality, model)
    """they foresee sanctions, so households increase their willingness to
    upgrade"""
    num_households = nagents(model) - 1
    # inform all agents but Municipality
    for id in shuffle(1:num_households)
        household = model[id]
        if household.pollutes
            update_willingness!(household, model.social_influence)
        end
    end
end


function agent_step!(agent::Household, model::ABM)
    if agent.pollutes
        pollute!(model, model.household_pollution)

        if agent.willingness_to_upgrade == 1
            upgrade_oss!(agent)
            # social engacement scenario
            inform_neighbours(agent, model)
        end
    end
end


function agent_step!(municipality::Municipality, model::ABM)
    if model.pike_abundance <= model.pike_threshold
        if model.years_after_threshold_breach == 0 && !municipality.has_legislated
            println("Municipality starts legislation process")
            model.years_after_threshold_breach += 1
            municipality.has_legislated = true
        end
    end

    if model.years_after_threshold_breach == 1
        inform_neighbours(municipality, model)
        model.years_after_threshold_breach += 1
        println("Municipality informs neighbors")
    elseif model.years_after_threshold_breach == 2
        model.years_after_threshold_breach += 1
        println("Municipality still legislating")
    else # after 3 years legislating, the municipality punishes
        enforce(municipality, model)
        println("Municipality enforces")
    end
end

function model_step!(model::ABM)
    model.total_pollution = 0
end
