include("social_model.jl")
include("sd_model.jl")


sd_model.initialize()
social_model = initialize_model(neighbour_distance = 2,
                                pike_threshold = 90,
                                household_pollution = 10,
                                social_influence = 1.2,
                                enforcement_influence =1.5)

# the SD has a default time-step of 0.25 (4 steps every ABM step)
final_time = 40

initial_lake_pollution = 200
pike_death_rate = 0.08
self_purification = 500


# updating constants in the SD model
sd_model.components.initial_pollution = py"set_constant"(initial_lake_pollution)
sd_model.components.death_rate = py"set_constant"(pike_death_rate)
sd_model.components.self_purification = py"set_constant"(self_purification)

# Initialize data collection DataFrame for the social model
mdata=[:total_pollution, :pike_abundance]
df_social_model = init_model_dataframe(social_model, mdata)

for time in 1:final_time

    # get pike abundance from SD model and update it in the social model
    social_model.pike_abundance = sd_model.components.pike_population()

    # store results from the social model in a julia DataFrame
    collect_model_data!(df_social_model, social_model, mdata, time-1)

    # step the social model. the last bool corresponds to agents_first.
    step!(social_model, agent_step!, model_step!, 1, false)

    # get the pollution sent to the lake at this step
    total_pollution = df_social_model[time, :total_pollution]

    # update the input_pollution with the output of the ABM
    sd_model.components.input_pollution = py"set_constant"(total_pollution)

    # run the SD model
    sd_model.run(initial_condition="c", final_time = time)


end

return df_social_model

