import numpy as np
import tkinter as tk
import time
from Logger import logger
from Board import Board
import sys
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

_color_map = {
    "S" : "green",
    "I" : "red",
    "R": "black"
}

def interactions(board):
    # total number of people = m x n = k
    # let each person be represented by a node
    # (0,0) ... (0,m)
    # ...
    # (n,0) ... (n,m)
    # Each node is linked to every other node and the probability of their interaction
    # is a function of their distance
    # an example of the function would be 1 - (normalized Manhattan distance)
    start = time.time()
    m = board.m
    k = board.n * m
    '''
    for i in range(k):
        for j in range(i+1,k):
            pairs.append((i,j))
            exp_dist.append(np.exp(-0.1-(10*((j // m) - (i // m) + abs((j % m)-(i % m))))))
    '''
    pairs = [(i,j) for i in range(k) for j in range(i+1,k)]
    exp_dist = np.exp(-0.01-np.array([(1/board.social_distancing_factor)*((x[1] // m) - (x[0] // m) + abs((x[1] % m)-(x[0] % m))) for x in pairs]))
    # normalise but have min as 0 instead of 1
    max_d = max(exp_dist)
    diff = max_d * np.exp(-0.01)
    exp_dist = np.array(exp_dist)
    pairs = np.array(pairs)

    interacting_pairs = pairs[np.random.uniform(0.0,1.0,size=len(exp_dist)) < ((exp_dist * np.exp(-0.1)) / (max_d))]
    elapsed = time.time() - start
    log.info("Time to calculate interactions: " + str(elapsed))
    return interacting_pairs

def reset(board,fig):
    board.reset()
    # reset graph
    fig.clear()
    x = range(1,1+len(board.SIR_data['S']))
    y = [board.SIR_data['I'],board.SIR_data['S'],board.SIR_data['R']]
    plt.stackplot(x,y, labels = ['I','S','R'], colors = ['tab:red', 'tab:green', 'black'])

def save_cfg(cfg_win,board,p_t,sdf):
    cfg_win.destroy()
    log.info("Setting transmission probability to " + str(p_t.get()))
    board.p_transmission = p_t.get()
    log.info("Setting social distancing factor to " + str(sdf.get()))
    board.social_distancing_factor = sdf.get()

def launch_config(window,board):
    config_window = tk.Toplevel(window)
    config_window.title("Configuration")
    transmission_prob_slider = tk.Scale(master=config_window, from_=0, to=1, digits=3,
                                        orient=tk.HORIZONTAL, resolution = 0.01, sliderlength=20, length = 200,
                                        label = "Transmission Probability")
    transmission_prob_slider.set(board.p_transmission)
    transmission_prob_slider.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
    setp_t = tk.DoubleVar(value = board.p_transmission)
    transmission_prob_freetxt = tk.Entry(master=config_window, width = 20, textvariable=setp_t)
    transmission_prob_freetxt.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    def pt_set_slider(discard):
        transmission_prob_slider.set(setp_t.get())

    transmission_prob_freetxt.bind("<Return>", pt_set_slider)

    def pt_get_value_from_slider(discard):
        setp_t.set(transmission_prob_slider.get())

    transmission_prob_slider.bind("<Leave>", pt_get_value_from_slider)

    sdf_slider = tk.Scale(master=config_window, from_=0, to=1, digits=3,
                                        orient=tk.HORIZONTAL, resolution = 0.01, sliderlength=20, length = 200,
                                        label = "Social Distancing Factor")
    sdf_slider.set(board.social_distancing_factor)
    sdf_slider.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
    set_sdf = tk.DoubleVar(value = board.social_distancing_factor)
    sdf_freetxt = tk.Entry(master=config_window, width = 20, textvariable=set_sdf)
    sdf_freetxt.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

    def sdf_set_slider(discard):
        sdf_slider.set(set_sdf.get())

    sdf_freetxt.bind("<Return>", sdf_set_slider)

    def sdf_get_value_from_slider(discard):
        set_sdf.set(sdf_slider.get())

    sdf_slider.bind("<Leave>", sdf_get_value_from_slider)

    save_cfg_btn = tk.Button(config_window, text="Save and Close", font = (None, 10),
                             command = lambda: save_cfg(config_window,board,setp_t,set_sdf))
    save_cfg_btn.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

def initialise_window(board):
    window = tk.Tk()
    log.info("Initialising GUI")

    window.title("MATH-4076 Project")

    cells = tk.Frame(window, relief = tk.RAISED, bd = 2)

    for i in range(len(board.board)):
        cells.columnconfigure(i, weight=1, minsize=5)
        cells.rowconfigure(i, weight=1, minsize=5)
        for j in range(len(board.board[i])):
            frame = tk.Frame(
                master = cells,
                relief = tk.RAISED,
                borderwidth = 1
            )
            frame.grid(row = i, column = j+1)
            text_display = tk.StringVar()

            label = tk.Label(master = frame, textvariable = text_display,
                             width = 3, font = (None, 8), fg = 'white',
                             bg = _color_map[board.board[i][j].state]
                             )
            text_display.set(board.board[i][j].state)
            board.board[i][j].associate_cell(label)
            board.board[i][j].associate_text_cell(text_display)
            label.pack()

    fig = plt.figure(1)
    plt.ion()
    x = range(1,1+len(board.SIR_data['S']))
    y = [board.SIR_data['I'],board.SIR_data['S'],board.SIR_data['R']]
    plt.stackplot(x,y, labels = ['I','S','R'], colors = ['tab:red', 'tab:green', 'black'])
    board.add_fig(fig)

    canvas = FigureCanvasTkAgg(fig, master = window)
    plot_widget = canvas.get_tk_widget()

    plot_widget.grid(row = 0, column = 2)

    buttons = tk.Frame(master = window, relief=tk.RAISED, bd=2)
    btn_run = tk.Button(buttons, text="Run", font = (None, 10), command = lambda: run_sim(board,False))
    btn_run.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    board.add_button(btn_run)

    btn_reset = tk.Button(buttons, text="Reset", font = (None, 10), command = lambda: reset(board,fig))
    btn_reset.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    btn_step = tk.Button(buttons, text="Step", font = (None, 10), command = lambda: run_sim(board,True))
    btn_step.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

    btn_cfg = tk.Button(buttons, text="Config", font = (None, 10), command = lambda: launch_config(window,board))
    btn_cfg.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

    def exit_program():
        window.quit()

    btn_exit = tk.Button(buttons, text="Exit", font = (None, 10), command = exit_program)
    btn_exit.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

    buttons.grid(row=0, column=0, sticky="ns")
    cells.grid(row = 0, column = 1)

    window.mainloop()

def update_graph(board):
    x = range(1,1+len(board.SIR_data['S']))
    y = [board.SIR_data['I'],board.SIR_data['S'],board.SIR_data['R']]
    plt.stackplot(x,y, labels = ['I','S','R'], colors = ['tab:red', 'tab:green', 'black'])
    board.fig.canvas.draw()

def run_sim(board,step):
    # interactions
    m = board.m
    p_transmission = board.p_transmission
    time_per_iteration = board.transition_time
    start = time.time()
    # everyone infected has a chance of recovering/being removed
    removed = []
    initial_infected = board.num_infected
    log.info("Number of infected: " + str(initial_infected))
    log.info("SIR Stats: {Susceptible: " + str(board.frac_susceptible) +
             ", Infected: " + str(board.frac_infected) +
             ", Removed: " + str(board.frac_removed) + "}")
    for infected in board.infected:
        # binomial distribution E[X] = 5, after 10, it's guaranteed
        if infected.infected_time == infected.infected_period:
            infected.remove()
            removed.append(infected)
        else:
            infected.infected_time += 1
    log.info("Number removed today: " + str(len(removed)))
    for r in removed:
        board.infected.remove(r)
        board.add_removed(r)
    interaction = interactions(board)
    for interact in interaction:
        i = interact[0]
        i_person = board.board[i // m][i % m]
        j = interact[1]
        j_person = board.board[j // m][j % m]
        # one infected and one susceptible
        if i_person.state == "I" and j_person.state != "I":
            if np.random.uniform() < p_transmission:
                if j_person.infect():
                # update cell
                    j_person.associated_cell.config(bg = 'red')
                    j_person.associated_text_cell.set("I")
                    board.add_infected(j_person)
        # vice versa
        if j_person.state == "I" and i_person.state != "I":
            if np.random.uniform() < p_transmission:
                if i_person.infect():
                # update cell
                    i_person.associated_cell.config(bg = 'red')
                    i_person.associated_text_cell.set("I")
                    board.add_infected(i_person)
    daily_infected = board.num_infected - initial_infected
    log.info("Daily Change in Infection: " + str(daily_infected))
    log.info("Estimated R0: " + str(10 * board.p_transmission * len(interaction)/(board.n*m)))
    board.update_SIR_data()
    update_graph(board)
    elapsed_time = time.time()
    diff = start - elapsed_time
    if diff < time_per_iteration:
        timer = time_per_iteration - diff
    else:
        timer = 0

    if not step:
        if board.num_infected < (board.m * board.n) and board.num_infected > 0:
            # call itself again if not over
            board.button.after(int(1000*timer),lambda: run_sim(board, False))
        else:
            log.info("Final SIR Stats: {Susceptible: " + str(board.frac_susceptible) +
                     ", Infected: " + str(board.frac_infected) +
                     ", Removed: " + str(board.frac_removed) + "}")

def main():
    #initial = (3,3)
    initial = None
    # initial probability of transmission
    p_transmission = 0.15
    np.random.seed(1)

    global log
    log = logger()

    # create board
    board = Board(25,25,initial,p_transmission,0)

    initialise_window(board)

if __name__ == '__main__':
    main()
