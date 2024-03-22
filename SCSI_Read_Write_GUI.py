import CTFServiceWrapper as PyServiceWrap
import os, sys
import time
import os
import ScsiCmdWrapper as scsiWrap
import GenericLib as generic
import Tkinter as tk


raw_input("Start ATB/go-logic and press Enter continue")
print "Call Write method"

def execute_command():

    lba_value = int(lba_entry.get(), 16)
    max_lba_value = int(max_lba_entry.get(), 16)
    trLen = 0
    
	
    if slc_var.get() == 1 and write_var.get() == 1:
        trLen = 80
        output1.config(text="Doing SCSI SLC Write")
        output1.config(text="LBA =0x{:X}\n".format(lba_value) + "\nMax LBA = 0x{:X}\n".format(max_lba_value) + "\ntrLen = " + str(trLen))
        
        obj = generic.GenericLib()
        obj.Session_Init()
        obj.WriteLbaExt(lba_value, trLen, max_lba_value)
        
        output3.config(text="Done SCSI SLC Writes")
		
    elif slc_var.get() == 1 and read_var.get() == 1:
        trLen = 80
        output1.config(text="Doing SCSI SLC Reads")
        output1.config(text="LBA =0x{:X}\n".format(lba_value) + "\nMax LBA = 0x{:X}\n".format(max_lba_value) + "\ntrLen = " + str(trLen))
        
        obj = generic.GenericLib()
        obj.Session_Init()		
        obj.ReadLbaExt(lba_value, trLen, max_lba_value)
        
        output3.config(text="Done SCSI SLC Reads")
		
    elif tlc_var.get() == 1 and write_var.get() == 1:
        trLen = 240
        output1.config(text="Doing SCSI TLC Writes\nDisabled Burst Mode")
        output1.config(text="LBA =0x{:X}\n".format(lba_value) + "\nMax LBA = 0x{:X}\n".format(max_lba_value) + "\ntrLen = " + str(trLen))
		
        obj = generic.GenericLib()
        obj.Session_Init()
        obj.DisableBurstMode(trLen,1)
        obj.WriteLbaExt(lba_value, trLen, max_lba_value)
		
        output3.config(text="Done SCSI TLC Writes")
		
    elif tlc_var.get() == 1 and read_var.get() == 1:
        trLen = 240
        output1.config(text="Doing SCSI TLC Reads")
        output1.config(text="LBA =0x{:X}\n".format(lba_value) + "\nMax LBA = 0x{:X}\n".format(max_lba_value) + "\ntrLen = " + str(trLen))

        obj = generic.GenericLib()
        obj.Session_Init()		
        obj.ReadLbaExt(lba_value, trLen, max_lba_value)
        
        output3.config(text="Done SCSI TLC Reads")

def update_decimal_from_hex(event=None):
    try:
        lba_decimal_value = int(lba_hex_entry.get(), 16)
        lba_entry.delete(0, tk.END)
        lba_entry.insert(0, str(lba_decimal_value))
    except ValueError:
        pass

    try:
        max_lba_decimal_value = int(max_lba_hex_entry.get(), 16)
        max_lba_entry.delete(0, tk.END)
        max_lba_entry.insert(0, str(max_lba_decimal_value))
    except ValueError:
        pass

def update_hex_from_decimal(event=None):
    try:
        lba_hex_value = hex(int(lba_entry.get()))
        lba_hex_entry.delete(0, tk.END)
        lba_hex_entry.insert(0, str(lba_hex_value))
    except ValueError:
        pass

    try:
        max_lba_hex_value = hex(int(max_lba_entry.get()))
        max_lba_hex_entry.delete(0, tk.END)
        max_lba_hex_entry.insert(0, str(max_lba_hex_value))
    except ValueError:
        pass
		
# GUI setup
root = tk.Tk()
root.title("SCSI Read Write")

# Set the size of the GUI
root.geometry("800x400") # Width x Hieght

# Labels
tk.Label(root,text="").grid(row=0,column=0)
tk.Label(root, text="LBA (Decimal)").grid(row=0, column=1, sticky='e')
tk.Label(root, text="LBA (Hexadecimal)").grid(row=0, column=3, sticky='e')
tk.Label(root,text="").grid(row=1,column=0)
tk.Label(root, text="Max LBA (Decimal)").grid(row=1, column=1, sticky='e')
tk.Label(root, text="Max LBA (Hexadecimal)").grid(row=1, column=3, sticky='e')

# Entries (Decimal)
lba_entry = tk.Entry(root)
lba_entry.grid(row=0, column=2, sticky='w')
max_lba_entry = tk.Entry(root)
max_lba_entry.grid(row=1, column=2, sticky='w')

# Entries (Hexadecimal)
lba_hex_entry = tk.Entry(root)
lba_hex_entry.grid(row=0, column=4, sticky='w')
max_lba_hex_entry = tk.Entry(root)
max_lba_hex_entry.grid(row=1, column=4, sticky='w')

# Checkboxes
tk.Label(root,text="").grid(row=0,column=5)
slc_var = tk.IntVar()
slc_checkbox = tk.Checkbutton(root, text="SLC", variable=slc_var)
slc_checkbox.grid(row=0, column=6, sticky='w')
tk.Label(root,text="").grid(row=1,column=5)
tlc_var = tk.IntVar()
tlc_checkbox = tk.Checkbutton(root, text="TLC", variable=tlc_var)
tlc_checkbox.grid(row=1, column=6, sticky='w')

tk.Label(root,text="").grid(row=0,column=7)
write_var = tk.IntVar()
write_checkbox = tk.Checkbutton(root, text="Write", variable=write_var)
write_checkbox.grid(row=0, column=8, sticky='w')
tk.Label(root,text="").grid(row=1,column=7)
read_var = tk.IntVar()
read_checkbox = tk.Checkbutton(root, text="Read", variable=read_var)
read_checkbox.grid(row=1, column=8, sticky='w')

# Button
tk.Label(root,text="").grid(row=2,column=0)
execute_button = tk.Button(root, text="Execute Command", command=execute_command)
execute_button.grid(row=3, columnspan=4, pady=10)

tk.Label(root,text="").grid(row=4,column=0)

output1=tk.Label(root,text="")
tk.Label(root,text="").grid(row=4,column=0)
output1.grid(row=4,column=1,columnspan=2)

output2=tk.Label(root,text="")
tk.Label(root,text="").grid(row=5,column=0)
output2.grid(row=5,column=1,columnspan=2)

output3=tk.Label(root,text="")
tk.Label(root,text="").grid(row=6,column=0)
output3.grid(row=6,column=1,columnspan=2)


# Bind entry events
lba_hex_entry.bind('<KeyRelease>', update_decimal_from_hex)
max_lba_hex_entry.bind('<KeyRelease>', update_decimal_from_hex)
lba_entry.bind('<KeyRelease>', update_hex_from_decimal)
max_lba_entry.bind('<KeyRelease>', update_hex_from_decimal)


root.mainloop()



