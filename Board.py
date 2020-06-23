import numpy as np
from Person import Person

class Board:

    def __init__(self, n, m, patient_zero=None,p_transmission=1,transition_time=0,sdf=0.65):
        self.transition_time = transition_time
        self.n = n
        self.m = m
        self.p_transmission = p_transmission
        self.board = np.empty([n,m], dtype=object)
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                self.board[row][col] = Person(row,col)
        if patient_zero is None:
            pz_x = np.random.randint(n)
            pz_y = np.random.randint(m)
            self.board[pz_x][pz_y].infect()
            self.infected = [self.board[pz_x][pz_y]]
        else:
            self.board[patient_zero[0]][patient_zero[1]].infect()
            self.infected = [self.board[patient_zero[0]][patient_zero[1]]]
        self.social_distancing_factor = sdf
        self.removed = []
        self.button = None
        self.patient_zero = patient_zero
        self.SIR_data = {"S": [self.frac_susceptible], "I": [self.frac_infected], "R": [self.frac_removed]}
        self.fig = None

    @property
    def num_infected(self):
        return len(self.infected)

    @property
    def frac_infected(self):
        return len(self.infected) / (self.n * self.m)

    @property
    def frac_removed(self):
        return len(self.removed) / (self.n * self.m)

    @property
    def frac_susceptible(self):
        return 1 - (self.frac_removed + self.frac_infected)

    def print_board(self):
        print()
        for row in self.board:
            for col in row:
                print("|", end = "")
                print(col, end = "")
            print("|")
        print()

    def add_button(self,button):
        self.button = button

    def reset(self):
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                self.board[row][col].reset()
        if self.patient_zero is None:
            pz_x = np.random.randint(self.n)
            pz_y = np.random.randint(self.m)
            self.board[pz_x][pz_y].infect()
            self.board[pz_x][pz_y].associated_cell.config(bg = 'red')
            self.board[pz_x][pz_y].associated_text_cell.set("I")
            self.infected = [self.board[pz_x][pz_y]]
        else:
            self.board[self.patient_zero[0]][self.patient_zero[1]].infect()
            self.board[self.patient_zero[0]][self.patient_zero[1]].associated_cell.config(bg = 'red')
            self.board[self.patient_zero[0]][self.patient_zero[1]].associated_text_cell.set("I")
            self.infected = [self.board[self.patient_zero[0]][self.patient_zero[1]]]
        self.removed = []
        self.SIR_data = {"S": [self.frac_susceptible], "I": [self.frac_infected], "R": [self.frac_removed]}

    def add_infected(self,person):
        assert person.state == "I"
        self.infected.append(person)

    def add_removed(self,person):
        assert person.state == "R"
        self.removed.append(person)

    def update_SIR_data(self):
        self.SIR_data['S'].append(self.frac_susceptible)
        self.SIR_data['I'].append(self.frac_infected)
        self.SIR_data['R'].append(self.frac_removed)

    def add_fig(self,fig):
        self.fig = fig
