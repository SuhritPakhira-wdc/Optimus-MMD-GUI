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
AttrObj.FDReset = 1
AttrObj.FlashReset = 1
AttrObj.Pattern = 0x1122
AttrObj.Payload = None
AttrObj.isVerbose = 1
AttrObj.isFBC = 0

FailBlock = 0x6e
FlashInfoObj = dgcmd.FlashInfoClass()
FlashInfoObj.fim = 0
FlashInfoObj.ce = 1
FlashInfoObj.die = 2
FlashInfoObj.block_no1 = FailBlock * 2
FlashInfoObj.block_no2 = 0
FlashInfoObj.wl = 0
FlashInfoObj.string = 0


root = tk.Tk()
root.title("EPR Operations")
root.geometry('1024x550')

ce_var=tk.StringVar()
fim_var=tk.StringVar()
die_var=tk.StringVar()
block_var=tk.StringVar()
wl_var=tk.StringVar()
string_var=tk.StringVar()
plane_var=tk.StringVar()
#ce_varar=tk.StringVar()

ce_var_hex=tk.StringVar()
fim_var_hex=tk.StringVar()
die_var_hex=tk.StringVar()
block_var_hex=tk.StringVar()
wl_var_hex=tk.StringVar()
string_var_hex=tk.StringVar()
plane_var_hex=tk.StringVar()
#ce_var_hex=tk.string_var()

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

def submit_prog():
 
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
    
    block_type = selected_option_block.get()
            
    plane_type = selected_option_plane.get()
    
    if "TLC" in block_type:
        AttrObj.BlkType = dgcmd.BlkType.TLC
    else:
        AttrObj.BlkType = dgcmd.BlkType.SLC
        
    if "Single" in plane_type:
        AttrObj.PlaneType = dgcmd.PlaneType.single
    else:
        AttrObj.PlaneType = dgcmd.PlaneType.dual
        
        
    #fim_var_g_list=int(fim_var_g_list)
    #die_var_g_list=int(die_var_g_list)    
    #block_var_g_list=int(block_var_g_list)
    #wl_var_g_list=int(wl_var_g_list)
    #string_var_g_list=int(string_var_g_list)
    #plane_var_g_list=int(plane_var_g_list)
    
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

        #print("The FIM is : " , fim_var_g_list)
        #print("The Die is : " , die_var_g_list)
        #print("The Block is : " , block_var_g_list)
        #print("The WL is : " , wl_var_g_list)
        #print("The String is : " , string_var_g_list)
        #print("The Plane is : " , plane_var_g_list)
        
        
        #print(block_type)
        list_of_ce = ce_var_g_list
        list_of_fim = fim_var_g_list           # for range use range function e.g. list_of_fim = range (0,20,5)
        list_of_die = die_var_g_list           #physical die number. Don't give logical die numer
        list_of_blocks = block_var_g_list
        list_of_wl = wl_var_g_list
        list_of_string = string_var_g_list
        list_of_plane = plane_var_g_list
        
        if AttrObj.BlkType == dgcmd.BlkType.TLC:
            if AttrObj.PlaneType == dgcmd.PlaneType.single:

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
					
											AttrObj.Payload =  "All_new.bin"
											obj.TLC_Program_Single_Plane_NonCache(FlashInfoObj, AttrObj)   
				
            elif AttrObj.PlaneType == dgcmd.PlaneType.dual:
			
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
						
												AttrObj.Payload =  "All.bin"
												obj.TLC_Program_Dual_Plane_NonCache(FlashInfoObj, AttrObj)  
												
        if AttrObj.BlkType == dgcmd.BlkType.SLC:
            if AttrObj.PlaneType == dgcmd.PlaneType.single:
						
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
											obj.SLC_Program_Single_Plane_NonCache(FlashInfoObj, AttrObj)
											
            elif AttrObj.PlaneType == dgcmd.PlaneType.dual:
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
								
											#AttrObj.Pattern = 0xAA55
											AttrObj.Payload = "LP.bin"
											obj.SLC_Program_Dual_Plane_NonCache(FlashInfoObj, AttrObj)
											
def submit_erase():
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
        
        block_type = selected_option_block.get()
            
        plane_type = selected_option_plane.get()
        
        if "TLC" in block_type:
            AttrObj.BlkType = dgcmd.BlkType.TLC
        else:
            AttrObj.BlkType = dgcmd.BlkType.SLC
            
        if "Single" in plane_type:
            AttrObj.PlaneType = dgcmd.PlaneType.single
        else:
            AttrObj.PlaneType = dgcmd.PlaneType.dual
            
        #fim_var_g=int(fim_var_g)
        #die_var_g=int(die_var_g)    
        #block_var_g=int(block_var_g)
        #wl_var_g=int(wl_var_g)
        #string_var_g=int(string_var_g)
        #plane_var_g=int(plane_var_g)

        #print("The FIM is : " , fim_var_g_list)
        #print("The Die is : " , die_var_g_list)
        #print("The Block is : " , block_var_g_list)
        #print("The WL is : " , wl_var_g_list)
        #print("The String is : " , string_var_g_list)
        #print("The Plane is : " , plane_var_g_list)
		
        if not ce_var.get():
            msgbox.showerror("Error", "No CE input provided")

        if not fim_var.get():
            msgbox.showerror("Error", "No FIM input provided")

        if not die_var.get():
            msgbox.showerror("Error", "No Die input provided")

        if not block_var.get():
            msgbox.showerror("Error", "No Block input provided")
            
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
			
            for ce in range(len(list_of_ce)):
				FlashInfoObj.ce=int(list_of_ce[ce])

				for fim in range(len(list_of_fim)):
					FlashInfoObj.fim=int(list_of_fim[fim])
			
					for die in range(len(list_of_die)):
						FlashInfoObj.die=int(list_of_die[die])
				
						#for wl in range(len(list_of_wl)):
							#FlashInfoObj.wl = int(list_of_wl[wl])
					
						for plane in range(len(list_of_plane)):
							plane_no = int(list_of_plane[plane])
						
								#for string in range (len(list_of_string)):
									#FlashInfoObj.string = int(list_of_string[string])
							
							for block in range (len(list_of_blocks)):
								FlashInfoObj.block_no1 = int(list_of_blocks[block])*2 + plane_no
								#print("CE = " + str(FlashInfoObj.ce) + ", FIM = " + str(FlashInfoObj.fim) + ", Die = " + str(FlashInfoObj.die) + ", Block = " + str(FlashInfoObj.block_no1))
								
								if AttrObj.PlaneType == dgcmd.PlaneType.single:
									obj.EraseBlock_Single(FlashInfoObj, AttrObj)
								elif AttrObj.PlaneType == dgcmd.PlaneType.dual:
									obj.EraseBlock_Dual(FlashInfoObj, AttrObj)

            
            
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
    
    block_type = selected_option_block.get()
            
    plane_type = selected_option_plane.get()
    
    if "TLC" in block_type:
        AttrObj.BlkType = dgcmd.BlkType.TLC
    else:
        AttrObj.BlkType = dgcmd.BlkType.SLC
        
    if "Single" in plane_type:
        AttrObj.PlaneType = dgcmd.PlaneType.single
    else:
        AttrObj.PlaneType = dgcmd.PlaneType.dual
        
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
        
        AttrObj.isFBC = 1
        AttrObj.FDReset = 1
        
        if AttrObj.BlkType == dgcmd.BlkType.TLC:
            if AttrObj.PlaneType == dgcmd.PlaneType.single:
            
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
											readbuf.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
					
											FlashInfoObj.PageType = dgcmd.PageType.MP
											AttrObj.Payload = "MP_new.bin"
											readbuf = obj.TLC_Read_Page(FlashInfoObj, AttrObj)
											readbuf.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)

											FlashInfoObj.PageType = dgcmd.PageType.UP
											AttrObj.Payload = "UP_new.bin"
											readbuf = obj.TLC_Read_Page(FlashInfoObj, AttrObj)
											readbuf.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
            
            elif AttrObj.PlaneType == dgcmd.PlaneType.dual:
            
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
											AttrObj.Payload = "LP.bin"                    
											[retbuf, retbuf1] = obj.TLC_Read_DualPlane(FlashInfoObj, AttrObj)
											readbuf.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
											readbuf1.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no + 1) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
					
											FlashInfoObj.PageType = dgcmd.PageType.MP
											AttrObj.Payload = "MP.bin"
											[retbuf, retbuf1] = obj.TLC_Read_DualPlane(FlashInfoObj, AttrObj)
											readbuf.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
											readbuf1.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no + 1) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
					
											FlashInfoObj.PageType = dgcmd.PageType.UP
											AttrObj.Payload = "UP.bin"
											[retbuf, retbuf1] = obj.TLC_Read_DualPlane(FlashInfoObj, AttrObj)
											readbuf.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
											readbuf1.WriteToFile("TLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no + 1) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
                
                
        if AttrObj.BlkType == dgcmd.BlkType.SLC:
            if AttrObj.PlaneType == dgcmd.PlaneType.single:
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
											readbuf.WriteToFile("SLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
            
            elif AttrObj.PlaneType == dgcmd.PlaneType.dual:
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
											
											AttrObj.Payload = "LP.bin"
											[retbuf, retbuf1] = obj.SLC_Read_Page(FlashInfoObj, AttrObj)
											readbuf.WriteToFile("SLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
											readbuf1.WriteToFile("SLCRead_Fim" + str(FlashInfoObj.fim) + "-Die"+ str(FlashInfoObj.die) +"-Pl" +str(plane_no + 1) +"-Blk" + str(FlashInfoObj.block_no1)+"-Str" + str(FlashInfoObj.string) + "-Pg" + FlashInfoObj.PageType.name +"-wl"+ str(FlashInfoObj.wl) + "_.bin", 18336)
				

selected_option_block = tk.StringVar(root)
selected_option_block.set("SLC")

option_menu_block = tk.OptionMenu(root, selected_option_block, "SLC", "TLC")
option_menu_block.pack()

option_menu_block.place(x=350, y=400)

selected_option_plane = tk.StringVar(root)
selected_option_plane.set("Single")

option_menu_plane = tk.OptionMenu(root, selected_option_plane, "Single", "Dual")
option_menu_plane.pack()

option_menu_plane.place(x=350, y=450)

#selected_option1 = tk.StringVar(root)
#selected_option1.set("List")

#option_menu1 = tk.OptionMenu(root, selected_option1, "List", "Range")
#option_menu1.pack()

#option_menu1.place(x=350, y=400)

title_label = tk.Label(root, text="Enter Details:")
title_label.pack(padx=0, pady=0)

ce_label = tk.Label(root, text = 'CE(Dec)', font=('calibre',10, 'bold')).place(x=300,y=0)
#fim_label.grid(row=1, column=0)
ce_label1 = tk.Label(root, text = 'CE(HEX)', font=('calibre',10, 'bold')).place(x=650,y=0)


ce_entry=tk.Entry(root,textvariable=ce_var)
ce_entry.place(x=300,y=25)
#fim_entry.grid(row=1, column=1)
ce_entry1=tk.Entry(root,textvariable=ce_var_hex)
ce_entry1.place(x=650,y=25)


fim_label = tk.Label(root, text = 'FIM(Dec)', font=('calibre',10, 'bold')).place(x=300,y=50)
#fim_label.grid(row=1, column=0)
fim_label1 = tk.Label(root, text = 'FIM(HEX)', font=('calibre',10, 'bold')).place(x=650,y=50)


fim_entry=tk.Entry(root,textvariable=fim_var)
fim_entry.place(x=300,y=75)
#fim_entry.grid(row=1, column=1)
fim_entry1=tk.Entry(root,textvariable=fim_var_hex)
fim_entry1.place(x=650,y=75)


die_label = tk.Label(root, text = 'Die(Dec)', font=('calibre',10, 'bold')).place(x=300,y=100)
#die_label.grid(row=2, column=0)
die_label1 = tk.Label(root, text = 'Die(HEX)', font=('calibre',10, 'bold')).place(x=650,y=100)


die_entry=tk.Entry(root,textvariable=die_var)
die_entry.place(x=300,y=125)
#die_entry.grid(row=2, column=1)
die_entry1=tk.Entry(root,textvariable=die_var_hex)
die_entry1.place(x=650,y=125)


block_label = tk.Label(root, text = 'Block(Dec)', font=('calibre',10, 'bold')).place(x=300,y=150)
#block_label.grid(row=3, column=0)
block_label1 = tk.Label(root, text = 'Block(HEX)', font=('calibre',10, 'bold')).place(x=650,y=150)


block_entry=tk.Entry(root,textvariable=block_var)
block_entry.place(x=300,y=175)
#block_entry.grid(row=3, column=1)
block_entry1=tk.Entry(root,textvariable=block_var_hex)
block_entry1.place(x=650,y=175)


Wl_label = tk.Label(root, text = 'WL(Dec)', font=('calibre',10, 'bold')).place(x=300,y=200)
#Wl_label.grid(row=4, column=0)
Wl_label1 = tk.Label(root, text = 'WL(HEX)', font=('calibre',10, 'bold')).place(x=650,y=200)


Wl_entry=tk.Entry(root,textvariable=wl_var)
Wl_entry.place(x=300,y=225)
#Wl_entry.grid(row=4, column=1)
Wl_entry1=tk.Entry(root,textvariable=wl_var_hex)
Wl_entry1.place(x=650,y=225)


String_label = tk.Label(root, text = 'String(Dec)', font=('calibre',10, 'bold')).place(x=300,y=250)
#String_label.grid(row=5, column=0)
String_label1 = tk.Label(root, text = 'String(HEX)', font=('calibre',10, 'bold')).place(x=650,y=250)


String_entry=tk.Entry(root,textvariable=string_var)
String_entry.place(x=300,y=275)
#String_entry.grid(row=5, column=1)
String_entry1=tk.Entry(root,textvariable=string_var_hex)
String_entry1.place(x=650,y=275)


plane_label = tk.Label(root, text = 'Plane(Dec)', font=('calibre',10, 'bold')).place(x=300,y=300)
#plane_label.grid(row=6, column=0)
plane_label1 = tk.Label(root, text = 'Plane(HEX)', font=('calibre',10, 'bold')).place(x=650,y=300)


plane_entry=tk.Entry(root,textvariable=plane_var)
plane_entry.place(x=300,y=325)
#plane_entry.grid(row=6, column=1)
plane_entry1=tk.Entry(root,textvariable=plane_var_hex)
plane_entry1.place(x=650,y=325)

#fim_var_hex.trace('w',hex_to_dec_fim)
#fim_var.trace('w',dec_to_hex_fim)
ce_entry.bind('<KeyRelease>',dec_to_hex_ce)
ce_entry1.bind('<KeyRelease>',hex_to_dec_ce)


fim_entry.bind('<KeyRelease>',dec_to_hex_fim)
fim_entry1.bind('<KeyRelease>',hex_to_dec_fim)

#die_var_hex.trace('w',hex_to_dec_die)
#die_var.trace('w',dec_to_hex_die)
die_entry.bind('<KeyRelease>',dec_to_hex_die)
die_entry1.bind('<KeyRelease>',hex_to_dec_die)

block_entry.bind('<KeyRelease>',dec_to_hex_block)
block_entry1.bind('<KeyRelease>',hex_to_dec_block)
#block_var.trace('w',dec_to_hex_block)
#block_var_hex.trace('w',hex_to_dec_block)

#wl_var_hex.trace('w',hex_to_dec_wl)
#wl_var.trace('w',dec_to_hex_wl)
Wl_entry.bind('<KeyRelease>',dec_to_hex_wl)
Wl_entry1.bind('<KeyRelease>',hex_to_dec_wl)

#string_var_hex.trace('w',hex_to_dec_string)
#string_var.trace('w',dec_to_hex_string)
String_entry.bind('<KeyRelease>',dec_to_hex_string)
String_entry1.bind('<KeyRelease>',hex_to_dec_string)

#plane_var_hex.trace('w',hex_to_dec_plane)
#plane_var.trace('w',dec_to_hex_plane)
plane_entry.bind('<KeyRelease>',dec_to_hex_plane)
plane_entry1.bind('<KeyRelease>',hex_to_dec_plane)



#fim_label.pack()

#fim_label1.pack()

#fim_entry.pack()

#die_label.pack()
#die_entry.pack()

#block_label.pack()
#block_entry.pack()

#Wl_label.pack()
#Wl_entry.pack()

#String_label.pack()
#String_entry.pack()

#plane_label.pack()
#plane_entry.pack()


erase_button = tk.Button(root, text="Erase", font=("Helvetica", 20, "bold"), width=8, height=2, command=submit_erase)
erase_button.pack(side="left", padx=10, pady=10)
erase_button.place(x=100,y=400)


program_button = tk.Button(root, text="Program", font=("Helvetica", 20, "bold"), width=8, height=2, command=submit_prog)
program_button.pack(side="top", padx=10, pady=10)
program_button.place(x=450,y=400)

read_button = tk.Button(root, text="Read", font=("Helvetica", 20, "bold"), width=8, height=2, command=submit_read)
read_button.pack(side="right", padx=10, pady=10)
read_button.place(x=800,y=400)

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(pady=5)
open_button.place(x=700,y=400)


root.mainloop()
