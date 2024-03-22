import Tkinter as tk
import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import pandas as pd
import sys
import numpy as np
import FaDleDiagLib as dgcmd
import CTFServiceWrapper as PyServiceWrap

obj = dgcmd.diagCmdLibClass(1)


ber_data = {}  # Dictionary to store BER values for each block
# Create the figure object
fig, ax = plt.subplots()

# Function to handle the block type selection

def get_page_type(*args):
    global selected_options
    global PageType_Flag
    
    page_type = button_page_type.get()
    selected_options = []
    if page_type == "LP":
        selected_options = ['LP']
    elif page_type == "MP":
        selected_options = ['MP']
    elif page_type == "UP":
        selected_options = ['UP']
    elif page_type == "LP + MP":
        selected_options = ['LP', 'MP']
    elif page_type == "LP + UP":
        selected_options = ['LP', 'UP']
    elif page_type == "MP + UP":
        selected_options = ['MP', 'UP']
    elif page_type == "All Page":
        selected_options = ['LP', 'MP', 'UP']
		
		
def parse_range_values(input_str):
    # Check if the input string contains a range value
    if '-' in input_str:
        start, end = input_str.split('-')
        start = int(start.strip())
        end = int(end.strip())
        
        # Create a range of values from start to end
        values = list(range(start, end + 1))
    else:
        # If no range value, split the input string by comma and convert to integers
        values = [int(x.strip()) for x in input_str.split(',') if x.strip()]
    
    return values


def Get_BER():
    
    # Retrieve the values from the input fields
    ce_values = parse_range_values(ce_entry.get())
    fim_values = parse_range_values(fim_entry.get())
    die_values = parse_range_values(die_entry.get())
    plane_values = parse_range_values(plane_entry.get())
    block_numbers = parse_range_values(block_entry.get())
    
    display_text.delete('1.0', tk.END)  # Clear the display area
    # print(block_numbers)
	
    global ber_data
    for ce in ce_values:
		for fim in fim_values:
			for die in die_values:
				for plane in plane_values:
					for block in block_numbers:
						fmu_data = {}  # Dictionary to store BER values for each FMU
						# display_text.insert(tk.END, f"Block No: {block}\n")
					 
						outFileName = "BER_data_CE" + str(ce) + "_FIM" + str(fim) + "_Die" + str(die) + "_Plane" + str(plane) + "_Block" + str(block) + ".csv"
						
						with open(outFileName, 'wb') as outputFile:
							csvWriter = csv.writer(outputFile)
							
							csvWriter.writerow(["CE", "Fim", "Die", "Plane", "Block", "fmu", "Page type", "BER"])
						
							fmu_data = {}  # Dictionary to store BER values for each FMU
							
							for fmu in range(0, 112*4*4*3): # WL*String*FMU*Page
								
								logical_die = ce * 32 + die * 4 + fim
								
								print("Getting BER for " + str(hex(logical_die)) + " Block " + str(hex(block)) + " FMU " + str(hex(fmu)))
								
								BER = obj.GetBER(logical_die, plane, block, fmu , 1) # 8 is fmu
								
								fmum = fmu % 12
								
								if fmum == 0:
									page = "LP"
									#BER = np.random.randint(30, 50)
								elif fmum == 4:
									page = "MP"
									#BER = np.random.randint(180, 200)
								elif fmum == 8:
									page = "UP"
									#BER = np.random.randint(100, 120)
								
								fmu_data[fmu] = (page, BER)
								
								csvWriter.writerow([ce, fim, die, plane, block, fmu, page, BER])
		
							ber_data[block] = fmu_data

    # Print BER data on the display area
    for ce in ce_values:	
		for fim in fim_values:
			for die in die_values:
				for plane in plane_values:
					for block, fmu_data in ber_data.items():
						
						outFileName = "BER_data_CE" + str(ce) + "_FIM" + str(fim) + "_Die" + str(die) + "_Plane" + str(plane) + "_Block" + str(block) + ".csv"
						
						df = pd.read_csv(outFileName)
						fmu = df['fmu']
						page = df["Page type"]
						ber_value = df['BER']
						display_text.insert(tk.END, "CE " + str(ce) + " FIM " + str(fim) + " Die " + str(die) + " Plane " + str(plane) + " Block " + str(block) + "\n")
						
						for i in range(len(fmu)):
							display_text.insert(tk.END, "FMU " + str(fmu[i]) + "(" + str(page[i]) + ") - BER = " + str(ber_value[i]) + "\n")

						display_text.insert(tk.END, "\n")


def plot_ber(fig):
    # print(1)
    # Retrieve the values from the input fields
    ce_value = ce_no.get()
    ces = ce_value.split(',')
    fim_value = fim_no.get()
    fims = fim_value.split(',')
    die_value = die_no.get()
    dies = die_value.split(',')
    
    plane_value = plane_no.get()
    planes = plane_value.split(',')
    
    block_value = block_no.get()
    blocks = block_value.split(',')
    
    
    fig.clear()
    num_plots = len(selected_options)
    
    axes = fig.subplots(num_plots, 1, sharex=True)
    
    colors = {'LP': 'blue', 'MP': 'red', 'UP': 'green'}  # Mapping of FMU types to colors
    
    if num_plots == 1:
        axes = [axes]  # Convert single subplot to a list for iteration
    
    for ax, option in zip(axes, selected_options):
        selected_fmus = []
        selected_bers = []
		
        for ce in ces:
			for fim in fims:
				for die in dies:
					for plane in planes:
						for block in blocks:
							outFileName = "BER_data_CE" + str(ce) + "_FIM" + str(fim) + "_Die" + str(die) + "_Plane" + str(plane) + "_Block" + str(block) + ".csv"
							df = pd.read_csv(outFileName)
							fmu = df['fmu']
							page = df["Page type"]
							ber_value = df['BER']
							for i in range(len(fmu)):
								if page[i] == option:
									selected_fmus.append(fmu[i])
									selected_bers.append(ber_value[i])
			
        # To do bar plot                        
        # ax.bar(selected_fmus, selected_bers, color=colors[option])
        
        
        ax.plot(selected_fmus, selected_bers, '.-', color = colors[option])
        ax.set_ylabel("BER Values")
        ax.set_title(str(option) + " - Block " + str(block) + " BER Plot")
    
    if num_plots > 1:
        axes[-1].set_xlabel("FMU")
    else:
        axes[0].set_xlabel("FMU")
    
    fig.tight_layout()
    canvas.draw()

def on_closing():
    # Close the command prompt when the GUI is closed
    sys.exit()


# Create the main window
window = tk.Tk()
window.title("BER Profile")
window.geometry("1500x768")

# Create a grid layout for the main window
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=3)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=3)

# Create part 1 frame (Blocks data entry, Get BER button, and scrollbar)
part1_frame = tk.Frame(window)
part1_frame.grid(row=0, column=0, sticky="nsew")

# Create labels and entry fields for CE, FIM and Die in the 1st row of Part1 frame
ce_label = tk.Label(part1_frame, text='CE:')
ce_label.grid(row=0, column=0, padx=5, pady=10)
ce_entry = tk.Entry(part1_frame)
ce_entry.grid(row=0, column=1, padx=5, pady=10)

fim_label = tk.Label(part1_frame, text='FIM:')
fim_label.grid(row=0, column=2, padx=5, pady=10)
fim_entry = tk.Entry(part1_frame)
fim_entry.grid(row=0, column=3, padx=5, pady=10)

die_label = tk.Label(part1_frame, text='Die:')
die_label.grid(row=1, column=0, padx=5, pady=10)
die_entry = tk.Entry(part1_frame)
die_entry.grid(row=1, column=1, padx=5, pady=10)

# Create labels and entry fields for Plane and Block in the 2nd row of Part1 frame
plane_label = tk.Label(part1_frame, text='Plane:')
plane_label.grid(row=1, column=2, padx=5, pady=10)
plane_entry = tk.Entry(part1_frame)
plane_entry.grid(row=1, column=3, padx=5, pady=10)

block_label = tk.Label(part1_frame, text='Block:')
block_label.grid(row=2, column=0, padx=5, pady=10)
block_entry = tk.Entry(part1_frame)
block_entry.grid(row=2, column=1, padx=5, pady=10)

# Create a button for Get BER on the 3rd row of Part1 frame
get_ber_button = tk.Button(part1_frame, text="Get BER", command=Get_BER)
get_ber_button.grid(row=2, column=2, columnspan=4, padx=5, pady=10)

# Create a display area for showing the block and BER data on the 4th row of Part1 frame
display_text = tk.Text(part1_frame, width=50, height=35)
display_text.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

# Create a scrollbar for the display area
scrollbar = tk.Scrollbar(part1_frame)
scrollbar.grid(row=3, column=4, sticky=tk.N + tk.S)
display_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=display_text.yview)

# Create part 2 frame (FMU check buttons, Get BER Plot button, and Plot image)
part2_frame = tk.Frame(window)
part2_frame.grid(row=0, column=1, sticky="nsew")

# Adding CE, FIM, Die, Plane, and Block entry fields to Part2 frame
ce_no_label = tk.Label(part2_frame, text='CE:')
ce_no_label.grid(row=0, column=0, sticky="e")
ce_no = tk.Entry(part2_frame)
ce_no.grid(row=0, column=1, sticky="w")

fim_no_label = tk.Label(part2_frame, text='FIM:')
fim_no_label.grid(row=0, column=2, sticky="e")
fim_no = tk.Entry(part2_frame)
fim_no.grid(row=0, column=3, sticky="w")

die_no_label = tk.Label(part2_frame, text='Die:')
die_no_label.grid(row=1, column=0, sticky="e")
die_no = tk.Entry(part2_frame)
die_no.grid(row=1, column=1, sticky="w")

plane_no_label = tk.Label(part2_frame, text='Plane:')
plane_no_label.grid(row=1, column=2, sticky="e")
plane_no = tk.Entry(part2_frame)
plane_no.grid(row=1, column=3, sticky="w")

block_no_label = tk.Label(part2_frame, text='Block:')
block_no_label.grid(row=2, column=0, sticky="e")
block_no = tk.Entry(part2_frame)
block_no.grid(row=2, column=1, sticky="w")


# --------------------------------------------------PAGE TYPE-----------------------------------------------------------#
# Create a drop-down button for Block Type
label_page_type = tk.Label(part2_frame, text="Page Type")
label_page_type.grid(row=2, column=2, sticky="nsew")
button_page_type = ttk.Combobox(part2_frame, values=["LP", "MP", "UP", "LP + MP", "LP + UP", "MP + UP", "All Page"], state="readonly")
button_page_type.grid(row=2, column=3, sticky="nsew")
# Set the initial value of the Combobox
initial_page_type = "LP"
button_page_type.set(initial_page_type)
# Create a string variable to store the selected option
selected_page_type = tk.StringVar()
# Set the initial value of the string variable
selected_page_type.set(button_page_type.get())
# Bind the update_variable function to the drop-down selection event
button_page_type.bind("<<ComboboxSelected>>", get_page_type)


# Create a button for Get BER Plot
get_ber_plot_button = tk.Button(part2_frame, text="Get BER Plot", command=lambda: plot_ber(fig))
get_ber_plot_button.grid(row=3, column=2, sticky="nsew")

# Create a frame to hold the canvas and toolbar
canvas_frame = tk.Frame(part2_frame)
canvas_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")

# Create a canvas to display the plot image
fig = Figure(figsize=(8, 6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

# Start the main event loop
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()