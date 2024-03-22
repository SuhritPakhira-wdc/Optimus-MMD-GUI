import Tkinter as tk
import subprocess
import os
import time
# Function to run CVDdump.bat file
def run_cvd_dump():
    # Add your command for DLE here
    print("Running DLE command")
    #subprocess.call(["DLE.bat"], shell=True)

# Function to run FW.py file
def run_firmware():
    # Add your command for Firmware here
    print("Running Power Cycle command")
    #subprocess.call(["PowerCycle.bat"], shell=True)
    
# Function to handle the execute button click event
def execute():
    if dle_check_var.get() == 1:
        run_cvd_dump()
        show_dle_buttons()
    if firmware_check_var.get() == 1:
        run_firmware()
        show_fw_buttons()

# Function to show the buttons
def show_dle_buttons():
    execute_button.pack_forget()
    button_commands = [
        run_address_converter,
        run_get_cvd,
        run_bombe_tool,
        run_ber_check,
        run_epr_operation,
        run_regfuse_dump,
        run_bes_ber,
        run_wafer_lot,
        run_parameter_edit,
        run_fadi_parse
    ]
    button_labels = [
        "Address converter",
        "Get CVD",
        "Bombe Tool",
        "BER Check",
        "EPR Operation",
        "Regfuse Dump",
        "BES BER",
        "Wafer Lot",
        "Parameter Edit",
        "FADI Parsing"
    ]
    # Create frames for each row
    button_frames = []
    for i in range(0, len(button_labels), 3):
        frame = tk.Frame(button_frame)
        frame.pack()
        button_frames.append(frame)

    # Create buttons and pack them in the respective frames
    for i in range(len(button_labels)):
        frame_index = i // 3
        frame = button_frames[frame_index]
        button = tk.Button(frame, text=button_labels[i], command=button_commands[i], font=('Arial', 14))
        button.pack(side=tk.LEFT, padx=10, pady=10)

def show_fw_buttons():
    execute_button.pack_forget()
    button_commands = [
        run_SCSI_read_write,
        run_bombe_tool,
        run_parameter_edit
    ]
    button_labels = [
        "SCSI Read Write",
        "Bombe Tool",
        "Parameter Edit",
    ]
    # Create frames for each row
    button_frames = []
    for i in range(0, len(button_labels), 3):
        frame = tk.Frame(button_frame)
        frame.pack()
        button_frames.append(frame)

    # Create buttons and pack them in the respective frames
    for i in range(len(button_labels)):
        frame_index = i // 3
        frame = button_frames[frame_index]
        button = tk.Button(frame, text=button_labels[i], command=button_commands[i], font=('Arial', 14))
        button.pack(side=tk.LEFT, padx=10, pady=10)


def run_SCSI_read_write():
	# Add your command for Address converter here
    print("Running SCSI Read Write command")
    subprocess.Popen(["python", "SCSI_Read_Write_GUI.py"], shell=True)

# Function to execute the command for Address converter button
def run_address_converter():
    # Add your command for Address converter here
    print("Running Address converter command")
    #subprocess.Popen(["python", "All_Integrated_Optimus_B51TB_SLC_TLC.py"], shell=True)

# Function to execute the command for Get CVD button
def run_get_cvd():
    # Add your command for Get CVD here
    print("Running Get CVD command")
    subprocess.Popen(["python", "CVD_GUI_with_Vt_Tracking.py"], shell=True)


# Function to execute the command for Bombe Tool button
def run_bombe_tool():
    # Add your command for Bombe Tool here)
    status.set("Bombe tool launching, wait!")
    time.sleep(1)
    subprocess.Popen(['C:\Users\user\Desktop\FA_Bombe.exe'])
    status.set("Bombe tool launched")
   


# Function to execute the command for BER Check button
def run_ber_check():
    # Add your command for BER Check here
    print("Running BER Check command")
    subprocess.Popen(["python", "BER_Check_GUI.py"], shell=True)
    

# Function to execute the command for EPR Operation button
def run_epr_operation():
    # Add your command for EPR Operation here
    print("Running EPR Operation command")
    subprocess.Popen(["python", "EPR_GUI.py"], shell=True)


# Function to execute the command for Regfuse Dump button
def run_regfuse_dump():
    # Add your command for Regfuse Dump here
    print("Running Regfuse Dump command")
    subprocess.Popen(["python", "GUI_Regfuse.py"], shell=True)

# Function to execute the command for BES BER button
def run_bes_ber():
    # Add your command for BES BER here
    print("Running BES BER command")

# Function to execute the command for Wafer Lot button
def run_wafer_lot():
    # Add your command for Wafer Lot here
    print("Running Wafer Lot command")
    subprocess.Popen(["python", "Wafer_Lot_ID_Module.py"], shell=True)
    

# Function to execute the command for Parameter Edit button
def run_parameter_edit():
    # Add your command for Parameter Edit here
    print("Running Parameter Edit command")
    subprocess.Popen(["python", "Param_Module_Updated.py"], shell=True)


# Function to execute the command for Parameter Edit button
def run_fadi_parse():
    # Add your command for Parameter Edit here
    print("Running FADI Parse command")
    subprocess.Popen(["python", "FADI_Module.py"], shell=True)


class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self)
        self.label.pack(side=tk.LEFT)
        self.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set(self, newText):
        self.label.config(text=newText)
    
    def clear(self):
        self.label.config(text="")
   
    
# Create the main window
window = tk.Tk()
window.title('Optimus GUI')
window.geometry("800x600")

# Add a Logo Icon on the top
logo_image = tk.PhotoImage(file="WD.gif").subsample(6, 6)
logo_label = tk.Label(window, image=logo_image)
logo_label.pack(side="top", anchor="n", padx=10, pady=10, fill="x")

# Create a frame to contain the checkboxes
checkbox_frame = tk.Frame(window)
checkbox_frame.pack(pady=100)

# Create the DLE checkbox
dle_check_var = tk.IntVar()
dle_check = tk.Checkbutton(checkbox_frame, text="DLE", variable=dle_check_var)
dle_check.pack(side=tk.LEFT, padx=10)

# Create the Firmware checkbox
firmware_check_var = tk.IntVar()
firmware_check = tk.Checkbutton(checkbox_frame, text="Power Cycle", variable=firmware_check_var)
firmware_check.pack(side=tk.LEFT, padx=10)

# Create a frame to contain the button
button_frame = tk.Frame(window)
button_frame.pack()


global status 
status = StatusBar(button_frame)
button_frame.pack(expand=True, fill=tk.BOTH)
status.set("Tool Launched")


# Create the Execute button
execute_button = tk.Button(button_frame, text="Execute", command=execute, font=('Arial', 14))
execute_button.pack(pady=20)

# Start the main event loop
window.mainloop()
