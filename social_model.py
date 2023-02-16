from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector


class Municipality(Agent):
    def __init__(self, unique_id, has_legislated, model):
        super().__init__(unique_id, model)
        self.has_legislated = has_legislated

    def step(self):

        if self.model.pike_abundance <= self.model.pike_threshold:
            if self.model.years_after_threshold_breach == 0 and not self.has_legislated:
                print("start legislation process")
                self.model.years_after_threshold_breach += 1
                self.has_legislated = True

        if self.model.years_after_threshold_breach == 1:
            self.inform_neighbors()
            print("Municipality informs neighbors")
            self.model.years_after_threshold_breach += 1
        elif self.model.years_after_threshold_breach == 2:
            self.model.years_after_threshold_breach += 1
            print("Municipality still legislating")

        else: # after 3 years legislating, the municipality punishes
            self.enforce()
            print("Municipality enforces")

    def all_households(self):
        """TODO this does not need to be a function"""
        return filter(lambda x: not isinstance(x, Municipality),
                                self.model.schedule.agent_buffer(shuffled=True)
                                )

    def inform_neighbors(self):
        for agent in self.all_households():
            if agent.pollutes and agent.willingness_to_upgrade >= 0.90:
                agent.willingness_to_upgrade = 1

    def enforce(self):
        for agent in self.all_households():
            if agent.pollutes:
                new_willingness = agent.willingness_to_upgrade * self.model.enforcement_influence
                if new_willingness < 1:
                    agent.willingness_to_upgrade = new_willingness
                else:
                    agent.willingness_to_upgrade = 1

class Household(Agent):
    def __init__(self, unique_id, pollutes, willingness, model):
        super().__init__(unique_id, model)
        self.pollutes = pollutes
        self.willingness_to_upgrade = willingness

    def step(self):
        # the random scheduler makes this randomized
        if self.pollutes:
            self.pollute()

            if self.willingness_to_upgrade == 1:
                self.upgrade_oss()
                self.inform_neighbors()


    def inform_neighbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos,
                                                  moore=True,
                                                  include_center=False,
                                                  radius=self.model.neighbour_distance)
        household_neighbors = filter(
            lambda x: not isinstance(x, Municipality), neighbors)

        for agent in household_neighbors:
            if agent.pollutes:
                new_willingness = agent.willingness_to_upgrade * self.model.social_influence
                if new_willingness < 1:
                    agent.willingness_to_upgrade = new_willingness
                else:
                    agent.willingness_to_upgrade = 1

    def pollute(self):
        self.model.total_pollution += self.model.household_pollution

    def upgrade_oss(self):
        self.pollutes = False


class SocialModel(Model):
    def __init__(self,
                 n_agents=100,
                 x_grid=20,
                 y_grid=20,
                 neighbour_distance = 2,
                 pike_threshold = 400,
                 initial_pike_abundance = 390.,
                 household_pollution = 30,
                 social_influence = 1.2,
                 enforcement_influence = 1.4):
        super().__init__()
        self.schedule = RandomActivation(self)
        # if torus=True, top and bottom borders (and left-righ) are connected
        self.grid = SingleGrid(x_grid, y_grid, torus=False)
        self.neighbour_distance = neighbour_distance
        self.pike_threshold = pike_threshold
        self.pike_abundance = initial_pike_abundance
        self.household_pollution = household_pollution
        self.social_influence = social_influence
        self.enforcement_influence = enforcement_influence
        self.total_pollution = 100
        self.years_after_threshold_breach = 0

        # data collection
        self.dc = DataCollector(
            model_reporters={"pollution": lambda m: m.total_pollution,
                             "pike_abundance": lambda m: m.pike_abundance})

        for i in range(n_agents):
            a = Household(i, True, self.random.random(), self)
            self.schedule.add(a)
            self.grid.position_agent(a)

        m = Municipality(n_agents + 1, False, self)
        self.schedule.add(m)
        self.grid.position_agent(m)

    def step(self):
        self.total_pollution = 0
        self.schedule.step()
        self.dc.collect(self)



model = SocialModel()
for i in range(50):
    model.step()

model_df = model.dc.get_model_vars_dataframe()

print(model_df)