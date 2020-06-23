import numpy as np

class Person:

    def __init__(self, pos_x, pos_y, initial_state="S"):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.state = initial_state
        self.infected_period = np.random.binomial(20,0.5) if initial_state == "I" else None
        self.infected_time = 0 if initial_state == "I" else None
        self.associated_cell = None
        self.associated_text_cell = None

    def __repr__(self):
        return self.state

    # returns whether the person can be infected
    def infect(self):
        if self.state == "R":
            return False
        else:
            self.state = "I"
            self.infected_period = np.random.binomial(20,0.5)
            self.infected_time = 0
            return True

    def associate_cell(self, cell):
        self.associated_cell = cell

    def associate_text_cell(self, t_cell):
        self.associated_text_cell = t_cell

    def reset(self):
        self.state = "S"
        self.associated_cell.config(bg = 'green')
        self.associated_text_cell.set("S")

    def remove(self):
        self.state = "R"
        self.associated_cell.config(bg = 'black')
        self.associated_text_cell.set("R")
