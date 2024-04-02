from Tkinter import *
import Tkinter as tk
import tkMessageBox as msgbox
import FaDleDiagLib as dgcmd
import tkFileDialog as fileinput
import binascii
import subprocess



obj = dgcmd.diagCmdLibClass(1) 

AttrObj = dgcmd.FlashAttributesClass()
AttrObj.BlkType = dgcmd.BlkType.SLC
AttrObj.PlaneType = dgcmd.PlaneType.single
AttrObj.FDReset = 0
AttrObj.FlashReset = 1
AttrObj.Pattern = 0x1122
AttrObj.Payload = None
AttrObj.isVerbose = 1
AttrObj.isFBC = 1

FailBlock = 0x6e
FlashInfoObj = dgcmd.FlashInfoClass()
FlashInfoObj.fim = 0
FlashInfoObj.ce = 1
FlashInfoObj.die = 2
FlashInfoObj.block_no1 = FailBlock * 2
FlashInfoObj.block_no2 = 0
FlashInfoObj.wl = 0
FlashInfoObj.string = 0


def Get_Param():
    print("Runing Get Param")
    ce_var_g=ce_var.get()
    ce_var_g_list=ce_var_g.split(",")
    	
    fim_var_g=fim_var.get()
    fim_var_g_list=fim_var_g.split(",")
    
    die_var_g=die_var.get()
    die_var_g_list=die_var_g.split(",")
    
    plane_var_g=plane_var.get()
    plane_var_g_list=plane_var_g.split(",")
            
    
    if not ce_var.get():
        msgbox.showerror("Error", "No CE input provided")

    if not fim_var.get():
        msgbox.showerror("Error", "No FIM input provided")

    if not die_var.get():
        msgbox.showerror("Error", "No Die input provided")

    if not plane_var.get():
        msgbox.showerror("Error", "No Plane input provided")

    else:

        list_of_ce = ce_var_g_list       
        list_of_fim = fim_var_g_list
        list_of_die = die_var_g_list
        list_of_plane = plane_var_g_list
        
		
    for ce in list_of_ce:
		for fim in list_of_fim:
			for die in list_of_die:
				for plane in list_of_plane:
				
					FlashInfoObj.ce = int(ce)
					FlashInfoObj.fim = int(fim)
					FlashInfoObj.die = int(die)
					FlashInfoObj.plane = int(plane)
					
					if FlashInfoObj.plane == 0:
						F_VCG_AV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D)
						F_VCG_AV3_entry.delete(0, tk.END)
						F_VCG_AV3_entry.insert(0, str(F_VCG_AV3))
                        
						F_VCG_BV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2E)
						F_VCG_BV3_entry.delete(0, tk.END)
						F_VCG_BV3_entry.insert(0, str(F_VCG_BV3))
                        
						F_VCG_CV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2F)
						F_VCG_CV3_entry.delete(0, tk.END)
						F_VCG_CV3_entry.insert(0, str(F_VCG_CV3))
                        
						F_VCG_DV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x30)
						F_VCG_DV3_entry.delete(0, tk.END)
						F_VCG_DV3_entry.insert(0, str(F_VCG_DV3))
                        
						F_VCG_EV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x31)
						F_VCG_EV3_entry.delete(0, tk.END)
						F_VCG_EV3_entry.insert(0, str(F_VCG_EV3))
                        
						F_VCG_FV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x32)
						F_VCG_FV3_entry.delete(0, tk.END)
						F_VCG_FV3_entry.insert(0, str(F_VCG_FV3))
                        
						F_VCG_GV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x33)
						F_VCG_GV3_entry.delete(0, tk.END)
						F_VCG_GV3_entry.insert(0, str(F_VCG_GV3))
						
					if FlashInfoObj.plane == 1:
						F_VCG_AV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x36)
						F_VCG_AV3_entry.delete(0, tk.END)
						F_VCG_AV3_entry.insert(0, str(F_VCG_AV3))
                        
						F_VCG_BV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x37)
						F_VCG_BV3_entry.delete(0, tk.END)
						F_VCG_BV3_entry.insert(0, str(F_VCG_BV3))
                        
						F_VCG_CV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x38)
						F_VCG_CV3_entry.delete(0, tk.END)
						F_VCG_CV3_entry.insert(0, str(F_VCG_CV3))
                        
						F_VCG_DV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x39)
						F_VCG_DV3_entry.delete(0, tk.END)
						F_VCG_DV3_entry.insert(0, str(F_VCG_DV3))
                        
						F_VCG_EV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3A)
						F_VCG_EV3_entry.delete(0, tk.END)
						F_VCG_EV3_entry.insert(0, str(F_VCG_EV3))
                        
						F_VCG_FV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3B)
						F_VCG_FV3_entry.delete(0, tk.END)
						F_VCG_FV3_entry.insert(0, str(F_VCG_FV3))
                        
						F_VCG_GV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3c)
						F_VCG_GV3_entry.delete(0, tk.END)
						F_VCG_GV3_entry.insert(0, str(F_VCG_GV3))
						
					
				
def Set_Param():
    print("Runing Set Param")
    ce_var_g=ce_var.get()
    ce_var_g_list=ce_var_g.split(",")
    	
    fim_var_g=fim_var.get()
    fim_var_g_list=fim_var_g.split(",")
    
    die_var_g=die_var.get()
    die_var_g_list=die_var_g.split(",")
    
    plane_var_g=plane_var.get()
    plane_var_g_list=plane_var_g.split(",")
            
    
    if not ce_var.get():
        msgbox.showerror("Error", "No CE input provided")

    if not fim_var.get():
        msgbox.showerror("Error", "No FIM input provided")

    if not die_var.get():
        msgbox.showerror("Error", "No Die input provided")

    if not plane_var.get():
        msgbox.showerror("Error", "No Plane input provided")

    else:

        list_of_ce = ce_var_g_list       
        list_of_fim = fim_var_g_list
        list_of_die = die_var_g_list
        list_of_plane = plane_var_g_list
        
	
    F_VCG_AV3 = int(F_VCG_AV3_entry.get())
    F_VCG_BV3 = int(F_VCG_BV3_entry.get())
    F_VCG_CV3 = int(F_VCG_CV3_entry.get())
    F_VCG_DV3 = int(F_VCG_DV3_entry.get())
    F_VCG_EV3 = int(F_VCG_EV3_entry.get())
    F_VCG_FV3 = int(F_VCG_FV3_entry.get())
    F_VCG_GV3 = int(F_VCG_GV3_entry.get())
	
    for ce in list_of_ce:
		for fim in list_of_fim:
			for die in list_of_die:
				for plane in list_of_plane:
				
					FlashInfoObj.ce = int(ce)
					FlashInfoObj.fim = int(fim)
					FlashInfoObj.die = int(die)
					FlashInfoObj.plane = int(plane)
					
					if FlashInfoObj.plane == 0:
						F_VCG_AV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D, F_VCG_AV3)
						#F_VCG_AV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D)
						F_VCG_AV3_entry.delete(0, tk.END)
						F_VCG_AV3_entry.insert(0, str(F_VCG_AV3))
                        
						F_VCG_BV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2E, F_VCG_BV3)
						#F_VCG_BV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2E)
						F_VCG_BV3_entry.delete(0, tk.END)
						F_VCG_BV3_entry.insert(0, str(F_VCG_BV3))
                        
						F_VCG_CV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2F, F_VCG_CV3)
						#F_VCG_CV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2F)
						F_VCG_CV3_entry.delete(0, tk.END)
						F_VCG_CV3_entry.insert(0, str(F_VCG_CV3))
                        
						F_VCG_DV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x30, F_VCG_DV3)
						#F_VCG_DV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x30)
						F_VCG_DV3_entry.delete(0, tk.END)
						F_VCG_DV3_entry.insert(0, str(F_VCG_DV3))
                        
						F_VCG_EV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x31, F_VCG_EV3)
						#F_VCG_EV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x31)
						F_VCG_EV3_entry.delete(0, tk.END)
						F_VCG_EV3_entry.insert(0, str(F_VCG_EV3))
                        
						F_VCG_FV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x32, F_VCG_FV3)
						#F_VCG_FV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x32)
						F_VCG_FV3_entry.delete(0, tk.END)
						F_VCG_FV3_entry.insert(0, str(F_VCG_FV3))
                        
						F_VCG_GV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x33, F_VCG_GV3)
						#F_VCG_GV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x33)
						F_VCG_GV3_entry.delete(0, tk.END)
						F_VCG_GV3_entry.insert(0, str(F_VCG_GV3))
                        
					if FlashInfoObj.plane == 1:
						F_VCG_AV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x36, F_VCG_AV3)
						#F_VCG_AV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x36)
						F_VCG_AV3_entry.delete(0, tk.END)
						F_VCG_AV3_entry.insert(0, str(F_VCG_AV3))
                        
						F_VCG_BV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x37, F_VCG_BV3)
						#F_VCG_BV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x37)
						F_VCG_BV3_entry.delete(0, tk.END)
						F_VCG_BV3_entry.insert(0, str(F_VCG_BV3))
                        
						F_VCG_CV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x38, F_VCG_CV3)
						#F_VCG_CV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x38)
						F_VCG_CV3_entry.delete(0, tk.END)
						F_VCG_CV3_entry.insert(0, str(F_VCG_CV3))
                        
						F_VCG_DV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x39, F_VCG_DV3)
						#F_VCG_DV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x39)
						F_VCG_DV3_entry.delete(0, tk.END)
						F_VCG_DV3_entry.insert(0, str(F_VCG_DV3))
                        
						F_VCG_EV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3A, F_VCG_EV3)
						#F_VCG_EV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3A)
						F_VCG_EV3_entry.delete(0, tk.END)
						F_VCG_EV3_entry.insert(0, str(F_VCG_EV3))
                        
						F_VCG_FV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3B, F_VCG_FV3)
						#F_VCG_FV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3B)
						F_VCG_FV3_entry.delete(0, tk.END)
						F_VCG_FV3_entry.insert(0, str(F_VCG_FV3))
                        
						F_VCG_GV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3c, F_VCG_GV3)
						#F_VCG_GV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3c)
						F_VCG_GV3_entry.delete(0, tk.END)
						F_VCG_GV3_entry.insert(0, str(F_VCG_GV3))
				  
      

def dec_to_hex_ce(*args):
    decimal_values = ce_var.get().split(",")
    hex_values = []
    for decimal_value in decimal_values:
        decimal_value = decimal_value.strip()
        if decimal_value:
            try:
                decimal_value = int(decimal_value)
                hex_value = hex(decimal_value)[2:].upper()
                hex_values.append(hex_value)
            except ValueError:
                hex_values.append("Invalid Input")
        else:
            hex_values.append("")
    ce_var_hex.set(",".join(hex_values ))


def hex_to_dec_ce(*args): 
    hex_values = ce_var_hex.get().split(",")
    decimal_values = []
    for hex_value in hex_values:
        hex_value = hex_value.strip()
        if hex_value:
            try: 
                decimal_value = int(hex_value, 16)
                decimal_values.append(decimal_value)
            except ValueError:
                decimal_values.append("Invalid Input")
        else:
            decimal_values.append("")
    ce_var.set(",".join(str(value) for value in decimal_values))


def dec_to_hex_fim(*args):
    decimal_values = fim_var.get().split(",")
    hex_values = []
    for decimal_value in decimal_values:
        decimal_value = decimal_value.strip()
        if decimal_value:
            try:
                decimal_value = int(decimal_value)
                hex_value = hex(decimal_value)[2:].upper()
                hex_values.append(hex_value)
            except ValueError:
                hex_values.append("Invalid Input")
        else:
            hex_values.append("")
    fim_var_hex.set(",".join(hex_values ))


def hex_to_dec_fim(*args): 
    hex_values = fim_var_hex.get().split(",")
    decimal_values = []
    for hex_value in hex_values:
        hex_value = hex_value.strip()
        if hex_value:
            try: 
                decimal_value = int(hex_value, 16)
                decimal_values.append(decimal_value)
            except ValueError:
                decimal_values.append("Invalid Input")
        else:
            decimal_values.append("")
    fim_var.set(",".join(str(value) for value in decimal_values))

def dec_to_hex_die(*args):
    decimal_values = die_var.get().split(",")
    hex_values = []
    for decimal_value in decimal_values:
        decimal_value = decimal_value.strip()
        if decimal_value:
            try:
                decimal_value = int(decimal_value)
                hex_value = hex(decimal_value)[2:].upper()
                hex_values.append(hex_value)
            except ValueError:
                hex_values.append("Invalid Input")
        else:
            hex_values.append("")
    die_var_hex.set(",".join(hex_values ))


def hex_to_dec_die(*args): 
    hex_values = die_var_hex.get().split(",")
    decimal_values = []
    for hex_value in hex_values:
        hex_value = hex_value.strip()
        if hex_value:
            try: 
                decimal_value = int(hex_value, 16)
                decimal_values.append(decimal_value)
            except ValueError:
                decimal_values.append("Invalid Input")
        else:
            decimal_values.append("")
    die_var.set(",".join(str(value) for value in decimal_values))

def dec_to_hex_block(*args):
    decimal_values = block_var.get().split(",")
    hex_values = []
    for decimal_value in decimal_values:
        decimal_value = decimal_value.strip()
        if decimal_value:
            try:
                decimal_value = int(decimal_value)
                hex_value = hex(decimal_value)[2:].upper()
                hex_values.append(hex_value)
            except ValueError:
                hex_values.append("Invalid Input")
        else:
            hex_values.append("")
    block_var_hex.set(",".join(hex_values ))


def hex_to_dec_block(*args): 
    hex_values = block_var_hex.get().split(",")
    decimal_values = []
    for hex_value in hex_values:
        hex_value = hex_value.strip()
        if hex_value:
            try: 
                decimal_value = int(hex_value, 16)
                decimal_values.append(decimal_value)
            except ValueError:
                decimal_values.append("Invalid Input")
        else:
            decimal_values.append("")
    block_var.set(",".join(str(value) for value in decimal_values))

def dec_to_hex_wl(*args):
    decimal_values = wl_var.get().split(",")
    hex_values = []
    for decimal_value in decimal_values:
        decimal_value = decimal_value.strip()
        if decimal_value:
            try:
                decimal_value = int(decimal_value)
                hex_value = hex(decimal_value)[2:].upper()
                hex_values.append(hex_value)
            except ValueError:
                hex_values.append("Invalid Input")
        else:
            hex_values.append("")
    wl_var_hex.set(",".join(hex_values ))


def hex_to_dec_wl(*args): 
    hex_values = wl_var_hex.get().split(",")
    decimal_values = []
    for hex_value in hex_values:
        hex_value = hex_value.strip()
        if hex_value:
            try: 
                decimal_value = int(hex_value, 16)
                decimal_values.append(decimal_value)
            except ValueError:
                decimal_values.append("Invalid Input")
        else:
            decimal_values.append("")
    wl_var.set(",".join(str(value) for value in decimal_values))

def dec_to_hex_string(*args):
    decimal_values = string_var.get().split(",")
    hex_values = []
    for decimal_value in decimal_values:
        decimal_value = decimal_value.strip()
        if decimal_value:
            try:
                decimal_value = int(decimal_value)
                hex_value = hex(decimal_value)[2:].upper()
                hex_values.append(hex_value)
            except ValueError:
                hex_values.append("Invalid Input")
        else:
            hex_values.append("")
    string_var_hex.set(",".join(hex_values ))


def hex_to_dec_string(*args): 
    hex_values = string_var_hex.get().split(",")
    decimal_values = []
    for hex_value in hex_values:
        hex_value = hex_value.strip()
        if hex_value:
            try: 
                decimal_value = int(hex_value, 16)
                decimal_values.append(decimal_value)
            except ValueError:
                decimal_values.append("Invalid Input")
        else:
            decimal_values.append("")
    string_var.set(",".join(str(value) for value in decimal_values))

def dec_to_hex_plane(*args):
    decimal_values = plane_var.get().split(",")
    hex_values = []
    for decimal_value in decimal_values:
        decimal_value = decimal_value.strip()
        if decimal_value:
            try:
                decimal_value = int(decimal_value)
                hex_value = hex(decimal_value)[2:].upper()
                hex_values.append(hex_value)
            except ValueError:
                hex_values.append("Invalid Input")
        else:
            hex_values.append("")
    plane_var_hex.set(",".join(hex_values ))


def hex_to_dec_plane(*args): 
    hex_values = plane_var_hex.get().split(",")
    decimal_values = []
    for hex_value in hex_values:
        hex_value = hex_value.strip()
        if hex_value:
            try: 
                decimal_value = int(hex_value, 16)
                decimal_values.append(decimal_value)
            except ValueError:
                decimal_values.append("Invalid Input")
        else:
            decimal_values.append("")
    plane_var.set(",".join(str(value) for value in decimal_values))

def open_file():
    
    file_path = fileinput.askopenfilename(filetypes=[("Binary Files", "*.bin")])
    
    read_window = tk.Toplevel(root)
    read_window.title("Hex Viewer")
    
    # Create a scrollbar
    scrollbar = tk.Scrollbar(read_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

    # Create a text widget
    text = tk.Text(read_window, wrap=tk.NONE, yscrollcommand=scrollbar.set)
    text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

    # Configure the scrollbar
    scrollbar.config(command=text.yview)
    
    
    if file_path:
        with open(file_path, 'rb') as file:
            data = file.read()
            hex_data = binascii.hexlify(data).decode('utf-8')

            formatted_hex = '00000000 '
            
            for i, c in enumerate(hex_data, 1):
                formatted_hex += c
                if i % 2 == 0:
                    formatted_hex += ' '
                if i % 16 == 0:
                    formatted_hex += '\t'
                if i % 64 == 0:
                    j = int(i*0.5)
                    formatted_hex += '\n' + '{:08x} '.format(j)

            text.delete(1.0, tk.END)  # Clear previous contents
            text.insert(tk.END, formatted_hex)
            
def submit_read():
    ce_var_g=ce_var.get()
    ce_var_g_list=ce_var_g.split(",")
    	
    fim_var_g=fim_var.get()
    fim_var_g_list=fim_var_g.split(",")
    
    
    die_var_g=die_var.get()
    die_var_g_list=die_var_g.split(",")
    
    
    block_var_g=block_var.get()
    block_var_g_list=block_var_g.split(",")
    
    
    wl_var_g=wl_var.get()
    wl_var_g_list=wl_var_g.split(",")
    
    
    string_var_g=string_var.get()
    string_var_g_list=string_var_g.split(",")
    
    
    plane_var_g=plane_var.get()
    plane_var_g_list=plane_var_g.split(",")
    
    AttrObj.BlkType = dgcmd.BlkType.TLC
    
        
    
    AttrObj.PlaneType = dgcmd.PlaneType.single
    
        
    #fim_var_g=int(fim_var_g)
    #die_var_g=int(die_var_g)    
    #block_var_g=int(block_var_g)
    #wl_var_g=int(wl_var_g)
    #string_var_g=int(string_var_g)
    #plane_var_g=int(plane_var_g)
	
    if not ce_var.get():
        msgbox.showerror("Error", "No CE input provided")

    if not fim_var.get():
        msgbox.showerror("Error", "No FIM input provided")

    if not die_var.get():
        msgbox.showerror("Error", "No Die input provided")

    if not block_var.get():
        msgbox.showerror("Error", "No Block input provided")
        
    if not wl_var.get():
        msgbox.showerror("Error", "No WL input provided")
        
    if not string_var.get():
        msgbox.showerror("Error", "No String input provided")

    if not plane_var.get():
        msgbox.showerror("Error", "No Plane input provided")

    else:

        list_of_ce = ce_var_g_list       
        list_of_fim = fim_var_g_list           # for range use range function e.g. list_of_fim = range (0,20,5)
        list_of_die = die_var_g_list           #physical die number. Don't give logical die numer
        list_of_blocks = block_var_g_list
        list_of_wl = wl_var_g_list
        list_of_string = string_var_g_list
        list_of_plane = plane_var_g_list
        
        
        if AttrObj.BlkType == dgcmd.BlkType.TLC:
		
			for ce in range(len(list_of_ce)):
				FlashInfoObj.ce=int(list_of_ce[ce])
				
				for fim in range(len(list_of_fim)):
					FlashInfoObj.fim=int(list_of_fim[fim])
					
					for die in range(len(list_of_die)):
						FlashInfoObj.die=int(list_of_die[die])
				
						for wl in range(len(list_of_wl)):
							FlashInfoObj.wl = int(list_of_wl[wl])
					
							for plane in range(len(list_of_plane)):
								plane_no = int(list_of_plane[plane])
						
								for string in range (len(list_of_string)):
									FlashInfoObj.string = int(list_of_string[string])
							
									for block in range (len(list_of_blocks)):
										FlashInfoObj.block_no1 = int(list_of_blocks[block])*2 + int(plane_no)
				
										FlashInfoObj.PageType = dgcmd.PageType.LP
										AttrObj.Payload = "LP_new.bin"                    
										readbuf = obj.TLC_Read_Page(FlashInfoObj, AttrObj)
										readbuf.WriteToFile("TLC_Custom_Read_CE" + str(FlashInfoObj.ce) + "-FIM" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
				
										FlashInfoObj.PageType = dgcmd.PageType.MP
										AttrObj.Payload = "MP_new.bin"
										readbuf = obj.TLC_Read_Page(FlashInfoObj, AttrObj)
										readbuf.WriteToFile("TLC_Custom_Read_CE" + str(FlashInfoObj.ce) + "-FIM" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)

										FlashInfoObj.PageType = dgcmd.PageType.UP
										AttrObj.Payload = "UP_new.bin"
										readbuf = obj.TLC_Read_Page(FlashInfoObj, AttrObj)
										readbuf.WriteToFile("TLC_Custom_Read_CE" + str(FlashInfoObj.ce) + "-FIM" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
            
                
                
        if AttrObj.BlkType == dgcmd.BlkType.SLC:
			for ce in range(len(list_of_ce)):
				FlashInfoObj.ce=int(list_of_ce[ce])
				
				for fim in range(len(list_of_fim)):
					FlashInfoObj.fim=int(list_of_fim[fim])
					
					for die in range(len(list_of_die)):
						FlashInfoObj.die=int(list_of_die[die])
				
						for wl in range(len(list_of_wl)):
							FlashInfoObj.wl = int(list_of_wl[wl])
					
							for plane in range(len(list_of_plane)):
								plane_no = int(list_of_plane[plane])
						
								for string in range (len(list_of_string)):
									FlashInfoObj.string = int(list_of_string[string])
							
									for block in range (len(list_of_blocks)):
										FlashInfoObj.block_no1 = int(list_of_blocks[block])*2 + plane_no
										
										AttrObj.Payload = "LP_new.bin"
										#AttrObj.Pattern = 0xAA55
										readbuf = obj.SLC_Read_Page(FlashInfoObj, AttrObj)
										readbuf.WriteToFile("SLC_Custom_Read_CE" + str(FlashInfoObj.ce) + "-FIM" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)

root = tk.Tk()
root.title("Custom Read Operations")
root.geometry('1100x550')

ce_var=tk.StringVar()
fim_var=tk.StringVar()
die_var=tk.StringVar()
block_var=tk.StringVar()
wl_var=tk.StringVar()
string_var=tk.StringVar()
plane_var=tk.StringVar()

ce_var_hex=tk.StringVar()
fim_var_hex=tk.StringVar()
die_var_hex=tk.StringVar()
block_var_hex=tk.StringVar()
wl_var_hex=tk.StringVar()
string_var_hex=tk.StringVar()
plane_var_hex=tk.StringVar()


global F_VCG_AV3, F_VCG_BV3, F_VCG_CV3, F_VCG_DV3, F_VCG_EV3, F_VCG_FV3, F_VCG_GV3


ce_label = tk.Label(root, text = 'CE(Dec)', font=('calibre',10, 'bold')).place(x=100,y=0)
ce_label1 = tk.Label(root, text = 'CE(HEX)', font=('calibre',10, 'bold')).place(x=500,y=0)


ce_entry=tk.Entry(root,textvariable=ce_var)
ce_entry.place(x=100,y=25)
ce_entry1=tk.Entry(root,textvariable=ce_var_hex)
ce_entry1.place(x=500,y=25)


fim_label = tk.Label(root, text = 'FIM(Dec)', font=('calibre',10, 'bold')).place(x=100,y=50)
fim_label1 = tk.Label(root, text = 'FIM(HEX)', font=('calibre',10, 'bold')).place(x=500,y=50)


fim_entry=tk.Entry(root,textvariable=fim_var)
fim_entry.place(x=100,y=75)
fim_entry1=tk.Entry(root,textvariable=fim_var_hex)
fim_entry1.place(x=500,y=75)


die_label = tk.Label(root, text = 'Die(Dec)', font=('calibre',10, 'bold')).place(x=100,y=100)
die_label1 = tk.Label(root, text = 'Die(HEX)', font=('calibre',10, 'bold')).place(x=500,y=100)


die_entry=tk.Entry(root,textvariable=die_var)
die_entry.place(x=100,y=125)
die_entry1=tk.Entry(root,textvariable=die_var_hex)
die_entry1.place(x=500,y=125)


block_label = tk.Label(root, text = 'Block(Dec)', font=('calibre',10, 'bold')).place(x=100,y=150)
block_label1 = tk.Label(root, text = 'Block(HEX)', font=('calibre',10, 'bold')).place(x=500,y=150)


block_entry=tk.Entry(root,textvariable=block_var)
block_entry.place(x=100,y=175)
block_entry1=tk.Entry(root,textvariable=block_var_hex)
block_entry1.place(x=500,y=175)


Wl_label = tk.Label(root, text = 'WL(Dec)', font=('calibre',10, 'bold')).place(x=100,y=200)
Wl_label1 = tk.Label(root, text = 'WL(HEX)', font=('calibre',10, 'bold')).place(x=500,y=200)


Wl_entry=tk.Entry(root,textvariable=wl_var)
Wl_entry.place(x=100,y=225)
Wl_entry1=tk.Entry(root,textvariable=wl_var_hex)
Wl_entry1.place(x=500,y=225)


String_label = tk.Label(root, text = 'String(Dec)', font=('calibre',10, 'bold')).place(x=100,y=250)
String_label1 = tk.Label(root, text = 'String(HEX)', font=('calibre',10, 'bold')).place(x=500,y=250)


String_entry=tk.Entry(root,textvariable=string_var)
String_entry.place(x=100,y=275)
String_entry1=tk.Entry(root,textvariable=string_var_hex)
String_entry1.place(x=500,y=275)


plane_label = tk.Label(root, text = 'Plane(Dec)', font=('calibre',10, 'bold')).place(x=100,y=300)
plane_label1 = tk.Label(root, text = 'Plane(HEX)', font=('calibre',10, 'bold')).place(x=500,y=300)


plane_entry=tk.Entry(root,textvariable=plane_var)
plane_entry.place(x=100,y=325)
plane_entry1=tk.Entry(root,textvariable=plane_var_hex)
plane_entry1.place(x=500,y=325)

ce_entry.bind('<KeyRelease>',dec_to_hex_ce)
ce_entry1.bind('<KeyRelease>',hex_to_dec_ce)


fim_entry.bind('<KeyRelease>',dec_to_hex_fim)
fim_entry1.bind('<KeyRelease>',hex_to_dec_fim)

die_entry.bind('<KeyRelease>',dec_to_hex_die)
die_entry1.bind('<KeyRelease>',hex_to_dec_die)

block_entry.bind('<KeyRelease>',dec_to_hex_block)
block_entry1.bind('<KeyRelease>',hex_to_dec_block)

Wl_entry.bind('<KeyRelease>',dec_to_hex_wl)
Wl_entry1.bind('<KeyRelease>',hex_to_dec_wl)

String_entry.bind('<KeyRelease>',dec_to_hex_string)
String_entry1.bind('<KeyRelease>',hex_to_dec_string)

plane_entry.bind('<KeyRelease>',dec_to_hex_plane)
plane_entry1.bind('<KeyRelease>',hex_to_dec_plane)

F_VCG_AV3_label = tk.Label(root, text='F_VCG_AV3(Dec)', font=('calibre', 10, 'bold'))
F_VCG_AV3_label.place(x=900, y=0)
F_VCG_AV3_entry = tk.Entry(root)
F_VCG_AV3_entry.place(x=900, y=25)

F_VCG_BV3_label = tk.Label(root, text='F_VCG_BV3(Dec)', font=('calibre', 10, 'bold'))
F_VCG_BV3_label.place(x=900, y=50)
F_VCG_BV3_entry = tk.Entry(root)
F_VCG_BV3_entry.place(x=900, y=75)

F_VCG_CV3_label = tk.Label(root, text='F_VCG_CV3(Dec)', font=('calibre', 10, 'bold'))
F_VCG_CV3_label.place(x=900, y=100)
F_VCG_CV3_entry = tk.Entry(root)
F_VCG_CV3_entry.place(x=900, y=125)

F_VCG_DV3_label = tk.Label(root, text='F_VCG_DV3(Dec)', font=('calibre', 10, 'bold'))
F_VCG_DV3_label.place(x=900, y=150)
F_VCG_DV3_entry = tk.Entry(root)
F_VCG_DV3_entry.place(x=900, y=175)

F_VCG_EV3_label = tk.Label(root, text='F_VCG_EV3(Dec)', font=('calibre', 10, 'bold'))
F_VCG_EV3_label.place(x=900, y=200)
F_VCG_EV3_entry = tk.Entry(root)
F_VCG_EV3_entry.place(x=900, y=225)

F_VCG_FV3_label = tk.Label(root, text='F_VCG_FV3(Dec)', font=('calibre', 10, 'bold'))
F_VCG_FV3_label.place(x=900, y=250)
F_VCG_FV3_entry = tk.Entry(root)
F_VCG_FV3_entry.place(x=900, y=275)

F_VCG_GV3_label = tk.Label(root, text='F_VCG_GV3(Dec)', font=('calibre', 10, 'bold'))
F_VCG_GV3_label.place(x=900, y=300)
F_VCG_GV3_entry = tk.Entry(root)
F_VCG_GV3_entry.place(x=900, y=325)

get_param_button = tk.Button(root, text="Get Param", font=("Helvetica", 20, "bold"), width=8, height=2, command=Get_Param)
get_param_button.pack(side="left", padx=10, pady=10)
get_param_button.place(x=100,y=400)


set_param_button = tk.Button(root, text="Set Param", font=("Helvetica", 20, "bold"), width=8, height=2, command=Set_Param)
set_param_button.pack(side="top", padx=10, pady=10)
set_param_button.place(x=500,y=400)

read_button = tk.Button(root, text="Read", font=("Helvetica", 20, "bold"), width=8, height=2, command=submit_read)
read_button.pack(side="right", padx=10, pady=10)
read_button.place(x=900,y=400)

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(pady=5)
open_button.place(x=700,y=400)


root.mainloop()