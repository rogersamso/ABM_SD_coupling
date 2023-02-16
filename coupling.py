import pysd
import mesa

from social_model import SocialModel

sd_model = pysd.load("sd_model.py")
sd_model.initialize()

social_model = SocialModel(neighbour_distance = 2,
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
sd_model.components.initial_pollution = lambda: initial_lake_pollution
sd_model.components.death_rate = lambda: pike_death_rate
sd_model.components.self_purification = lambda: self_purification


for time in range(1,final_time):

    # get pike abundance from SD model and update it in the social model
    social_model.pike_abundance = sd_model.components.pike_population()

    # step the social model. the last bool corresponds to agents_first.
    social_model.step()

    # TODO collect the total pollution from the social model
    total_pollution = social_model.dc.model_reporters["pollution"](social_model)

    # update the input_pollution with the output of the ABM
    sd_model.components.input_pollution = lambda: total_pollution

    # run the SD model
    sd_model.run(initial_condition="c", final_time = time)


# collecting final results
model_df = social_model.dc.get_model_vars_dataframe()
print(model_df)

