import Tkinter as tk
import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import random
import FaDleDiagLib as dgcmd
import time
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#from scipy import interpolate
import random
from datetime import datetime
import sys
#from Tkinter import filedialog
import os
import math
from datetime import datetime


obj = dgcmd.diagCmdLibClass(1) 

AttrObj = dgcmd.FlashAttributesClass()
AttrObj.BlkType = dgcmd.BlkType.SLC
AttrObj.PlaneType = dgcmd.PlaneType.single
AttrObj.FDReset = 1
AttrObj.FlashReset = 0
AttrObj.Pattern = 0x1122
AttrObj.Payload = "SLCRead_modi.bin" 
AttrObj.isVerbose = 0
AttrObj.isFBC = 0

CustomShifts = dgcmd.CustomShiftClass()

fig, ax = plt.subplots()

BlockType_Flag = 2

AttrObj.isVerbose = 0


vt_Shift = 0.025
Max_Vlt = 6.98

FlashInfoObj = dgcmd.FlashInfoClass()
FlashInfoObj.ce = 0    # keep fixed at 0

######################################################################
#Input Physical Address Here  
######################################################################

FlashInfoObj.fim = 0   
FlashInfoObj.die = 0  #physical die number. Don't give logical die numer
FlashInfoObj.block_no = 0 #meta block_no number
FlashInfoObj.wl = 0
FlashInfoObj.string = 0

for ce in range(2):
    for fim in range(4):
        for die in range(8):
            obj.Manual_POR_FDh(fim, ce, die)



def BombeToolDecode(HBFileInput, SB1FileInput = None, SB2FileInput = None):
    import os
    import os.path
    import time
    
    cwd = os.getcwd()
    os.chdir("C:\\Users\\user\\Downloads\\Latest_BOMBE_Release\\FA_Bombe_2.4.2\\Windows\\")

    ResultOutput = "C:\\CVDDump\Result15"
    HBFile = "\"" + cwd + "\\" + HBFileInput + "\""
    if SB1FileInput == None:
        SB1File = " \"\""
    else:
        SB1File =  "\"" + cwd + "\\" + SB1FileInput + "\""
     
    if SB2FileInput == None:
        SB2File = " \"\""
    else:
        SB2File = "\"" + cwd + "\\" + SB2FileInput + "\""
        
    CmdArgs = ResultOutput + " "  + "CREX " + "X3 " + HBFile + " " + SB1File + SB2File + " 2 " +  " 0 "
    print CmdArgs
    os.system("C:\\Users\\user\\Downloads\\Latest_BOMBE_Release\\FA_Bombe_2.4.2\\Windows\\bombe.bat " + CmdArgs)
    os.chdir(cwd)

    
    file_path = ResultOutput + "\\" + HBFileInput.strip(".bin") + "_Fmu4" +  "\\FA insights.txt" 
    print file_path

    time_to_wait = 5*60
    time_counter = 0
    while not os.path.exists(file_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:break
        
    if os.path.isfile(file_path):
        file1 = open(file_path,"r")
        print("Output of Read file : " + file_path)
        #print(file1.read())
        lines = file1.readlines()
        BERResult = "Fail"
        for row in lines:
            # check if string present on a current line
            word = 'Page BER'
            #print(row.find(word))
            # find() method returns -1 if the value is not found,
            # if found it returns index of the first occurrence of the substring
            if row.find(word) != -1:
                print('string exists in file')
                print('line Number:', lines.index(row))
                li = list(row.split(" "))
                BERResult = li[3] + " Fail"
                #res=[]
                #for i in li:
                #    print (i)
                #    BERRe
                    
        for row in lines:
            # check if string present on a current line
            word = 'Decoded Successfully'
            print(row)
            #print(row.find(word))
            # find() method returns -1 if the value is not found,
            # if found it returns index of the first occurrence of the substring
            if row.find(word) != -1:
                print('string exists in file')
                print('line Number:', lines.index(row))
                BERResult = BERResult.split(" ")[0] + " Pass"
    else:
        raise ValueError("%s isn't a file!" % file_path)
    
    print BERResult
    return BERResult
    
def Vt_Tracking(fadi_file_1,fig):
    
    fig.clear()
    fig, ax = plt.subplots(figsize=(12, 8))
    # fadi_file_1 = "TLC_CVD_EPWR__0_0_400_0_0_"+".csv"
    df = pd.read_csv(fadi_file_1)
    x = df['vlt X-axis']
    #df = df1['data']

    n = 5  # number of points to be checked before and after

    # Find local peaks

    df['min'] = np.nan
    df['max'] = np.nan

    for i in range(n, len(df) - n):
        if all(df['Population Y-Axis'].iloc[i] <= df['Population Y-Axis'].iloc[i - n:i + n + 1]):
            df.at[i, 'min'] = df['Population Y-Axis'].iloc[i]
        elif all(df['Population Y-Axis'].iloc[i] >= df['Population Y-Axis'].iloc[i - n:i + n + 1]):
            df.at[i, 'max'] = df['Population Y-Axis'].iloc[i]

    s = df['min']

    print( df['min'])
    print( df.dropna(subset=['min']) )
    mindf = df.dropna(subset=['min'])
    optinum = mindf['vlt X-axis'].to_numpy()
    print (optinum)

    if plane_no :
        Adef = ADef_P1
        Bdef = BDef_P1
        Cdef = CDef_P1
        Ddef = DDef_P1
        Edef = EDef_P1
        Fdef = FDef_P1
        Gdef = GDef_P1
    else:
        Adef = ADef_P0
        Bdef = BDef_P0
        Cdef = CDef_P0
        Ddef = DDef_P0
        Edef = EDef_P0
        Fdef = FDef_P0
        Gdef = GDef_P0

    Arange = 0.5
    Brange = 1.5
    CRange = 2.2
    DRange = 2.8
    ERange = 3.6
    FRange = 4.5
    GRange = 5.5

    for i in optinum:
        if i < Arange:
            Aoptimal = i
        if i < Brange:
            Boptimal = i
        if i < CRange:
            Coptimal = i
        if i < DRange:
            Doptimal = i
        if i < ERange:
            Eoptimal = i
        if i < FRange:
            Foptimal = i
        if i < GRange:
            Goptimal = i

    ADelta = (np.uint8)(math.ceil((Aoptimal-Adef)/0.0125))
    BDelta = (np.uint8)(math.ceil((Boptimal-Bdef)/0.0125))
    CDelta = (np.uint8)(math.ceil((Coptimal-Cdef)/0.0125))
    DDelta = (np.uint8)(math.ceil((Doptimal-Ddef)/0.0125))
    EDelta = (np.uint8)(math.ceil((Eoptimal-Edef)/0.0125))
    FDelta = (np.uint8)(math.ceil((Foptimal-Fdef)/0.0125))
    GDelta = (np.uint8)(math.ceil((Goptimal-Gdef)/0.0125))   
    print  (hex(ADelta))
    print  (hex(BDelta))
    print  (hex(CDelta))
    print  (hex(DDelta))
    print  (hex(EDelta))
    print  (hex(FDelta))
    print  (hex(GDelta))
    print ("Adef = " + str(Adef) + " Aopti = " + str(Aoptimal) + " Delta = " + str(Aoptimal-Adef) + " DAC = " + str((Aoptimal-Adef)/0.0125) )
    print ("Bdef = " + str(Bdef) + " Bopti = " + str(Boptimal) + " Delta = " + str(Boptimal-Bdef) + " DAC = " + str((Boptimal-Bdef)/0.0125))
    print ("Cdef = " + str(Cdef) + " Copti = " + str(Coptimal) + " Delta = " + str(Coptimal-Cdef) + " DAC = " + str((Coptimal-Cdef)/0.0125))
    print ("Ddef = " + str(Ddef) + " Dopti = " + str(Doptimal) + " Delta = " + str(Doptimal-Ddef) + " DAC = " + str((Doptimal-Ddef)/0.0125))
    print ("Edef = " + str(Edef) + " Eopti = " + str(Eoptimal) + " Delta = " + str(Eoptimal-Edef) + " DAC = " + str((Eoptimal-Edef)/0.0125))
    print ("Fdef = " + str(Fdef) + " Fopti = " + str(Foptimal) + " Delta = " + str(Foptimal-Fdef) + " DAC = " + str((Foptimal-Fdef)/0.0125))
    print ("Gdef = " + str(Gdef) + " Gopti = " + str(Goptimal) + " Delta = " + str(Goptimal-Gdef) + " DAC = " + str((Goptimal-Gdef)/0.0125))
     
    vlinesref = [Adef,Bdef,Cdef,Ddef,Edef,Fdef,Gdef]

    for ref in vlinesref:
        plt.vlines(x = ref , ymin = 0, ymax = 10000 ,colors = 'red')

    ax.scatter(x, df['min'], c='r')
    ax.scatter(x, df['max'], c='g')
    df.to_csv("create3.csv")
    ax.plot(x, df['Population Y-Axis'], label = str(fadi_file_1), lw=1)

    fadi_file_1 = "TLC_CVD_CMDB2_Refs"+".csv" 
    df = pd.read_csv(fadi_file_1)
    x = df['vlt X-axis']
    y1 = df['Population Y-Axis']
    ax.plot(x,y1, color='#9A0EEA',label="Good Drive",lw=0.8)

    #fig = plt.figure()
    #ax = fig.add_subplot(111)

    #for xmaj in ax.xaxis.get_majorticklocs():
      #ax.axvline(x=xmaj, ls='-')
    #for xmin in ax.xaxis.get_minorticklocs():
    #  ax.axvline(x=xmin, ls='--')
      
    # plt.yscale("log")
    # plt.xlim(0,7)
    # plt.ylim(1,10000000)
    # plt.legend(ncol=5,fontsize=5)
    # plt.grid()
    # resolution_value = 1200

    # plt.grid(which = "minor")
    # plt.minorticks_on()

    #plt.grid(True, which='major', color='b', axis = 'y', linestyle='-')
    #plt.grid(True, which='minor', color='r', axis = 'y', linestyle='--')
    #plt.grid(True, which='major', color='b', axis = 'x', linestyle='-')
    #plt.grid(True, which='minor', color='r', axis = 'x', linestyle='--')

    # plt.savefig("CVD_" + str (datetime.now().strftime("%Y_%m_%d_%I_%M_%S_%p")) + ".png", format="png", dpi=resolution_value)
    # plt.show()
    

    # Set labels and title
    ax.set_xlabel('Voltage')
    ax.set_ylabel('No of Cells')
    ax.set_title('CVD Plot')
    ax.set_yscale('log')
    ax.set_xlim(0,7)
    ax.set_ylim(1,10**5)
    ax.legend(ncol=5,fontsize=5)
    plt.grid()
    
    plt.grid(which = "minor")
    plt.minorticks_on()

    # Create a Tkinter canvas for the plot
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()

    # Place the canvas on the left-hand side
    canvas.get_tk_widget().place(relx=0, rely=0, relwidth=0.8, relheight=1)
    
    DeltaOffsets = [ADelta, BDelta, CDelta, DDelta, EDelta, FDelta, GDelta]

    hex_values = [
    hex(ADelta),
    hex(BDelta),
    hex(CDelta),
    hex(DDelta),
    hex(EDelta),
    hex(FDelta),
    hex(GDelta)
    ]

    hex_names = [
    'ADelta',
    'BDelta',
    'CDelta',
    'DDelta',
    'EDelta',
    'FDelta',
    'GDelta'
    ]
	
	
    for i, hex_val in enumerate(hex_values):
        label = tk.Label(window, text= str(hex_names[i]) + ' = ' + str(hex_val) + ', ',  bg="purple", fg="white")
        label.grid(row=0, column=i)

    CustomShifts.AShift = int(ADelta)
    CustomShifts.BShift = int(BDelta)
    CustomShifts.CShift = int(CDelta)
    CustomShifts.DShift = int(DDelta)
    CustomShifts.EShift = int(EDelta)
    CustomShifts.FShift = int(FDelta)
    CustomShifts.GShift = int(GDelta)    
    
    # CustomShifts.AShift = 0x4
    # CustomShifts.BShift = 0xFC
    # CustomShifts.CShift = 0xFA
    # CustomShifts.DShift = 0xFA
    # CustomShifts.EShift = 0xF0
    # CustomShifts.FShift = 0xE7
    # CustomShifts.GShift = 0xD8
    
    print (FlashInfoObj.block_no1)
    FlashInfoObj.PageType = dgcmd.PageType.LP
    readbuf = obj.TLC_Read_Page_CustomShifts(FlashInfoObj, AttrObj, CustomShifts)
    readbuf.WriteToFile("VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_HB.bin", 18336)
    LPHBFile = "VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_HB.bin"
    LPHBFileSts = BombeToolDecode(LPHBFile)
    
    FlashInfoObj.PageType = dgcmd.PageType.LP
    readbuf = obj.TLC_Read_Page_CustomShifts_SB1(FlashInfoObj, AttrObj, CustomShifts)
    readbuf.WriteToFile("VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_SB1.bin", 18336)
    LPSBFile = "VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_SB1.bin"
    LPSBFileSts =  BombeToolDecode(LPHBFile, LPSBFile)
    
    FlashInfoObj.PageType = dgcmd.PageType.MP
    readbuf = obj.TLC_Read_Page_CustomShifts(FlashInfoObj, AttrObj, CustomShifts)
    readbuf.WriteToFile("VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_HB.bin", 18336)
    MPHBFile = "VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_HB.bin"
    MPHBFileSts = BombeToolDecode(MPHBFile)
    
    FlashInfoObj.PageType = dgcmd.PageType.MP
    readbuf = obj.TLC_Read_Page_CustomShifts_SB1(FlashInfoObj, AttrObj, CustomShifts)
    readbuf.WriteToFile("VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_SB1.bin", 18336)
    MPSBFile = "VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_SB1.bin"
    MPSBFileSts = BombeToolDecode(MPHBFile, MPSBFile)
    
    FlashInfoObj.PageType = dgcmd.PageType.UP
    readbuf = obj.TLC_Read_Page_CustomShifts(FlashInfoObj, AttrObj, CustomShifts)
    readbuf.WriteToFile("VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_HB.bin", 18336)
    UPHBFile = "VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_HB.bin"
    UPHBFileSts = BombeToolDecode(UPHBFile)
    
    FlashInfoObj.PageType = dgcmd.PageType.UP
    readbuf = obj.TLC_Read_Page_CustomShifts_SB1(FlashInfoObj, AttrObj, CustomShifts)
    readbuf.WriteToFile("VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_SB1.bin", 18336)
    UPSBFile = "VTTrack_" + str(FlashInfoObj.die) + "-" + str(FlashInfoObj.block_no1) + "-" + FlashInfoObj.PageType.name + "_Cus_SB1.bin"
    UPSBFileSts = BombeToolDecode(UPHBFile, UPSBFile)
    
    res2 = [
    LPHBFileSts,
    LPSBFileSts,
    MPHBFileSts,
    MPSBFileSts,
    UPHBFileSts,
    UPSBFileSts,
    ]

    res1 = [
    LPHBFile,
    LPSBFile,
    MPHBFile,
    MPSBFile,
    UPHBFile,
    UPSBFile,
    ]
    #Label(root, text="Position 1 : x=0, y=0", bg="#FFFF00", fg="white").place(x=5, y=0)
    #Label(root, text="Position 2 : x=50, y=40", bg="#3300CC", fg="white").place(x=50, y=40)
    #Label(root, text="Position 3 : x=75, y=80", bg="#FF0099", fg="white").place(x=75, y=80)

    #for i, res_val in enumerate(res2):
    label = tk.Label(window, text= str(res1[0]) + ' = ' + str(res2[0]) + ', ', bg="red", fg="white").place(x=0, y=25)
    label = tk.Label(window, text= str(res1[1]) + ' = ' + str(res2[1]) + ', ', bg="red", fg="white").place(x=300, y=25)
    label = tk.Label(window, text= str(res1[2]) + ' = ' + str(res2[2]) + ', ', bg="blue", fg="white").place(x=0, y=50)
    label = tk.Label(window, text= str(res1[3]) + ' = ' + str(res2[3]) + ', ', bg="blue", fg="white").place(x=300, y=50)
    label = tk.Label(window, text= str(res1[4]) + ' = ' + str(res2[4]) + ', ', bg="black", fg="white").place(x=0, y=75)
    label = tk.Label(window, text= str(res1[5]) + ' = ' + str(res2[5]) + ', ', bg="black", fg="white").place(x=300, y=75)
    
        #label.grid(row=20, column=i)
        
    return DeltaOffsets

def ReadDecode():
    print "Read Decode"

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



def get_bics_type(*args):
    bics_type = button_bics_type.get()
    selected_bics_type.set(bics_type)
    print("Selected:", bics_type)  # Print the selected option to the command terminal

# Function to handle the block type selection
def get_block_type(*args):
    global BlockType_Flag
    block_type = button_block_type.get()
    if block_type == "SLC":
        flag = 1
    elif block_type == "TLC":
        flag = 2
    elif block_type == "NDWL":
        flag = 3
        # Show the additional information label
        additional_info_label.pack()
    else:
        # Hide the additional information label for other block types
        additional_info_label.pack_forget()
    BlockType_Flag = flag
    print("Block Type", BlockType_Flag)
	
#BlockType_Flag = 2 # SLC =1 , TLC =2, NDWL = 3


				
def Set_Param():
    print("Runing Set Param")
    
    # Retrieve the values from the input fields
    ce_values = parse_range_values(ce_entry.get())
    fim_values = parse_range_values(fim_entry.get())
    die_values = parse_range_values(die_entry.get())
    plane_values = parse_range_values(plane_entry.get())
    

    F_VCG_AV3 = int(F_VCG_AV3_entry.get(), 16)
    F_VCG_BV3 = int(F_VCG_BV3_entry.get(), 16)
    F_VCG_CV3 = int(F_VCG_CV3_entry.get(), 16)
    F_VCG_DV3 = int(F_VCG_DV3_entry.get(), 16)
    F_VCG_EV3 = int(F_VCG_EV3_entry.get(), 16)
    F_VCG_FV3 = int(F_VCG_FV3_entry.get(), 16)
    F_VCG_GV3 = int(F_VCG_GV3_entry.get(), 16)
	
    for ce in ce_values:
		for fim in fim_values:
			for die in die_values:
				for plane in plane_values:
				
					FlashInfoObj.ce = int(ce)
					FlashInfoObj.fim = int(fim)
					FlashInfoObj.die = int(die)
					FlashInfoObj.plane = int(plane)
					
					if FlashInfoObj.plane == 0:
						F_VCG_AV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D, F_VCG_AV3)
						#F_VCG_AV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D)
						F_VCG_AV3_entry.delete(0, tk.END)
						F_VCG_AV3_entry.insert(0, hex(F_VCG_AV3))
                        
						F_VCG_BV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2E, F_VCG_BV3)
						#F_VCG_BV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2E)
						F_VCG_BV3_entry.delete(0, tk.END)
						F_VCG_BV3_entry.insert(0, hex(F_VCG_BV3))
                        
						F_VCG_CV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2F, F_VCG_CV3)
						#F_VCG_CV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2F)
						F_VCG_CV3_entry.delete(0, tk.END)
						F_VCG_CV3_entry.insert(0, hex(F_VCG_CV3))
                        
						F_VCG_DV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x30, F_VCG_DV3)
						#F_VCG_DV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x30)
						F_VCG_DV3_entry.delete(0, tk.END)
						F_VCG_DV3_entry.insert(0, hex(F_VCG_DV3))
                        
						F_VCG_EV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x31, F_VCG_EV3)
						#F_VCG_EV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x31)
						F_VCG_EV3_entry.delete(0, tk.END)
						F_VCG_EV3_entry.insert(0, hex(F_VCG_EV3))
                        
						F_VCG_FV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x32, F_VCG_FV3)
						#F_VCG_FV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x32)
						F_VCG_FV3_entry.delete(0, tk.END)
						F_VCG_FV3_entry.insert(0, hex(F_VCG_FV3))
                        
						F_VCG_GV3 = obj.SetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x33, F_VCG_GV3)
						#F_VCG_GV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x33)
						F_VCG_GV3_entry.delete(0, tk.END)
						F_VCG_GV3_entry.insert(0, hex(F_VCG_GV3))
                        
						VCG_AV3 = F_VCG_AV3
						DVCG_AV3 = F_DVCG_AR3 & 0x3F
						DVCG_AV3_Delta_v = (DVCG_AV3 * 0.0125) + (-0.65)
						ADef_P0 = (VCG_AV3 * 0.0125 ) + DVCG_AV3_Delta_v
                        
						VCG_BV3 = F_VCG_BV3 
						DVCG_BV3 = F_DVCG_BR3 & 0x3F
						DVCG_BV3_Delta_v = (DVCG_BV3 * 0.0125) + (-0.725)
						BDef_P0 = (VCG_BV3 * 0.0125 ) + DVCG_BV3_Delta_v
                                                    
						VCG_CV3 = F_VCG_CV3
						DVCG_CV3 = F_DVCG_CR3 & 0x3F 
						DVCG_CV3_Delta_v = (DVCG_CV3 * 0.0125) + (-0.725)
						CDef_P0 = (0.8 + VCG_CV3 * 0.0125 ) + DVCG_CV3_Delta_v 
                        
						VCG_DV3 = F_VCG_DV3
						DVCG_DV3 = F_DVCG_DR3 & 0x3F
						DVCG_DV3_Delta_v = (DVCG_DV3 * 0.0125) + (-0.725)
						DDef_P0 = (1.6 + VCG_DV3 * 0.0125 ) + DVCG_DV3_Delta_v
                        
						VCG_EV3 = F_VCG_EV3
						DVCG_EV3 = F_DVCG_ER3 & 0x3F
						DVCG_EV3_Delta_v = (DVCG_EV3 * 0.0125) + (-0.725)
						EDef_P0 = (2.4 + VCG_EV3 * 0.0125 ) + DVCG_EV3_Delta_v 
                        
						VCG_FV3 = F_VCG_FV3
						DVCG_FV3 = F_DVCG_FR3 & 0x3F
						DVCG_FV3_Delta_v = (DVCG_FV3 * 0.0125) + (-0.825)
						FDef_P0 = (3.2 + VCG_FV3 * 0.0125 ) + DVCG_FV3_Delta_v 
                        
						VCG_GV3 = F_VCG_GV3
						DVCG_GV3 = F_DVCG_GR3 & 0x3F
						DVCG_GV3_Delta_v = (DVCG_GV3 * 0.0125) + (-0.925)
						GDef_P0 = (4.0 + VCG_GV3 * 0.0125 ) + DVCG_GV3_Delta_v 
                        
						VCG_P0_new.append(ADef_P0)
						VCG_P0_new.append(BDef_P0)
						VCG_P0_new.append(CDef_P0)
						VCG_P0_new.append(DDef_P0)
						VCG_P0_new.append(EDef_P0)
						VCG_P0_new.append(FDef_P0)
						VCG_P0_new.append(GDef_P0)
                        
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
				  
						VCG_AV3_P1 = F_VCG_AV3
						DVCG_AV3 = F_DVCG_AR3 & 0x3F
						DVCG_AV3_Delta_v = (DVCG_AV3 * 0.0125) + (-0.65)
						ADef_P1 = (VCG_AV3_P1 * 0.0125 ) + DVCG_AV3_Delta_v
                        
						VCG_BV3_P1 = F_VCG_BV3 
						DVCG_BV3 = F_DVCG_BR3 & 0x3F
						DVCG_BV3_Delta_v = (DVCG_BV3 * 0.0125) + (-0.725)
						BDef_P1 = (VCG_BV3_P1 * 0.0125 ) + DVCG_BV3_Delta_v
                                                    
						VCG_CV3_P1 = F_VCG_CV3
						DVCG_CV3 = F_DVCG_CR3 & 0x3F 
						DVCG_CV3_Delta_v = (DVCG_CV3 * 0.0125) + (-0.725)
						CDef_P1 = (0.8 + VCG_CV3_P1 * 0.0125 ) + DVCG_CV3_Delta_v 
                        
						VCG_DV3_P1 = F_VCG_DV3
						DVCG_DV3 = F_DVCG_DR3 & 0x3F
						DVCG_DV3_Delta_v = (DVCG_DV3 * 0.0125) + (-0.725)
						DDef_P1 = (1.6 + VCG_DV3_P1 * 0.0125 ) + DVCG_DV3_Delta_v
                        
						VCG_EV3_P1 = F_VCG_EV3
						DVCG_EV3 = F_DVCG_ER3 & 0x3F
						DVCG_EV3_Delta_v = (DVCG_EV3 * 0.0125) + (-0.725)
						EDef_P1 = (2.4 + VCG_EV3_P1 * 0.0125 ) + DVCG_EV3_Delta_v 
                        
						VCG_FV3_P1 = F_VCG_FV3
						DVCG_FV3 = F_DVCG_FR3 & 0x3F
						DVCG_FV3_Delta_v = (DVCG_FV3 * 0.0125) + (-0.825)
						FDef_P1 = (3.2 + VCG_FV3_P1 * 0.0125 ) + DVCG_FV3_Delta_v 
                        
						VCG_GV3_P1 = F_VCG_GV3
						DVCG_GV3 = F_DVCG_GR3 & 0x3F
						DVCG_GV3_Delta_v = (DVCG_GV3 * 0.0125) + (-0.925)
						GDef_P1 = (4.0 + VCG_FV3_P1 * 0.0125 ) + DVCG_GV3_Delta_v 
                        
						VCG_P1_new.append(ADef_P1)
						VCG_P1_new.append(BDef_P1)
						VCG_P1_new.append(CDef_P1)
						VCG_P1_new.append(DDef_P1)
						VCG_P1_new.append(EDef_P1)
						VCG_P1_new.append(FDef_P1)
						VCG_P1_new.append(GDef_P1)
   

F_VCG_AV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D)
#print("\r\nF_VCG_AV3 = \t {}".format(hex(F_VCG_AV3)))

F_VCG_AV3_P1 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x36)
#print("\r\nF_VCG_AV3_P1 = \t {}".format(hex(F_VCG_AV3_P1)))

F_DVCG_AR3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3F)
#print("\r\nF_DVCG_AR3 = \t {}".format(hex(F_DVCG_AR3)))

F_VCG_BV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2E)
#print("\r\nF_VCG_BV3 = \t {}".format(hex(F_VCG_BV3)))

F_VCG_BV3_P1 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x37)
#print("\r\nF_VCG_BV3_P1 = \t {}".format(hex(F_VCG_BV3_P1)))

F_DVCG_BR3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x40)
#print("\r\nF_DVCG_BR3 = \t {}".format(hex(F_DVCG_BR3)))

F_VCG_CV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2F)
#print("\r\nF_VCG_CV3 = \t {}".format(hex(F_VCG_CV3)))

F_VCG_CV3_P1 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x38)
#print("\r\nF_VCG_CV3_P1 = \t {}".format(hex(F_VCG_CV3_P1)))

F_DVCG_CR3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x41)
#print("\r\nF_DVCG_CR3 = \t {}".format(hex(F_DVCG_CR3)))

F_VCG_DV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x30)
#print("\r\nF_VCG_DV3 = \t {}".format(hex(F_VCG_DV3)))

F_VCG_DV3_P1 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x39)
#print("\r\nF_VCG_DV3_P1 = \t {}".format(hex(F_VCG_DV3_P1)))

F_DVCG_DR3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x42)
#print("\r\nF_DVCG_DR3 = \t {}".format(hex(F_DVCG_DR3)))

F_VCG_EV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x31)
#print("F_VCG_EV3 = \t {}".format(hex(F_VCG_EV3)))

F_VCG_EV3_P1 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3A)
#print("F_VCG_EV3_P1 = \t {}".format(hex(F_VCG_EV3_P1)))

F_DVCG_ER3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x43)
#print("F_DVCG_ER3 = \t {}".format(hex(F_DVCG_ER3)))

F_VCG_FV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x32)
#print("F_VCG_FV3 = \t {}".format(hex(F_VCG_FV3)))

F_VCG_FV3_P1 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3B)
#print("F_VCG_FV3_P1 = \t {}".format(hex(F_VCG_FV3_P1)))

F_DVCG_FR3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x44)
#print("F_DVCG_FR3 = \t {}".format(hex(F_DVCG_FR3)))

F_VCG_GV3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x33)
#print("F_VCG_GV3 = \t {}".format(hex(F_VCG_GV3)))

F_VCG_GV3_P1 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3c)
#print("F_VCG_GV3_P1 = \t {}".format(hex(F_VCG_GV3_P1)))

F_DVCG_GR3 = obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x45)
#print("F_DVCG_GR3 = \t {}".format(hex(F_DVCG_GR3))) 



VCG_P0 = []
VCG_P1 = []

VCG_P0_new = []
VCG_P1_new = []


VCG_AV3 = F_VCG_AV3 #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D)
VCG_AV3_P1 = F_VCG_AV3_P1 #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x36)
DVCG_AV3 = F_DVCG_AR3 & 0x3F#obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3F)
DVCG_AV3_start = 0.125
DVCG_AV3_0_Offset = 0x34 #Greater than 0x34 are possitive, lesser than 0x34 are negative
DVCG_AV3_Delta = DVCG_AV3 - DVCG_AV3_0_Offset
DVCG_BV3_Delta_v = (0x20 * 0.0125) + (-0.65)
ADef_P0 = (VCG_AV3 * 0.0125 ) +((DVCG_AV3_Delta * 0.0125)) 
ADef_P1 = (VCG_AV3_P1 * 0.0125) + ((DVCG_AV3_Delta * 0.0125))  
print(ADef_P0) 
print(ADef_P1)

VCG_P0.append(ADef_P0)
VCG_P1.append(ADef_P1)

VCG_BV3 = F_VCG_BV3 #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D)
VCG_BV3_P1 = F_VCG_BV3_P1 #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x36)
DVCG_BV3 = F_DVCG_BR3 & 0x3F #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3F)
DVCG_BV3_start = 0.125
DVCG_BV3_0_Offset = 0x3A #Greater than 0x34 are possitive, lesser than 0x34 are negative
DVCG_BV3_Delta = DVCG_BV3 - DVCG_BV3_0_Offset
DVCG_BV3_Delta_v = (0x2E * 0.0125) + (-0.725)
BDef_P0 = (VCG_BV3 * 0.0125 ) + DVCG_BV3_Delta_v
BDef_P1 = (VCG_BV3_P1 * 0.0125) +  DVCG_BV3_Delta_v
print(BDef_P0)
print(BDef_P1)

VCG_P0.append(BDef_P0)
VCG_P1.append(BDef_P1)

VCG_CV3 = F_VCG_CV3 #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x2D)
VCG_CV3_P1 = F_VCG_CV3_P1 #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x36)
DVCG_CV3 = F_DVCG_CR3 & 0x3F #obj.GetParam(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, 0x3F)
DVCG_CV3_0_Offset = 0x3A #Greater than 0x34 are possitive, lesser than 0x34 are negative
DVCG_CV3_Delta = DVCG_CV3 - DVCG_CV3_0_Offset
DVCG_CV3_Delta_v = (DVCG_CV3 * 0.0125) + (-0.725)
#CDef_P0 = (0.8 + VCG_CV3 * 0.0125 ) +((DVCG_CV3_Delta * 0.0125)) 
#CDef_P1 = (VCG_CV3_P1 * 0.0125) + ((DVCG_CV3_Delta * 0.0125))
CDef_P0 = (0.8 + VCG_CV3 * 0.0125 ) + DVCG_CV3_Delta_v 
CDef_P1 = (0.8 + VCG_CV3_P1 * 0.0125) + DVCG_CV3_Delta_v
print(CDef_P0) 
print(CDef_P1)

VCG_P0.append(CDef_P0)
VCG_P1.append(CDef_P1)

VCG_DV3 = F_VCG_DV3
VCG_DV3_P1 = F_VCG_DV3_P1
DVCG_DV3 = F_DVCG_DR3 & 0x3F
DVCG_DV3_Delta_v = (DVCG_DV3 * 0.0125) + (-0.725)
DDef_P0 = (1.6 + VCG_DV3 * 0.0125 ) + DVCG_DV3_Delta_v
DDef_P1 = (1.6 + VCG_DV3_P1 * 0.0125) + DVCG_DV3_Delta_v
print(DDef_P0) 
print(DDef_P1)

VCG_P0.append(DDef_P0)
VCG_P1.append(DDef_P1)

VCG_EV3 = F_VCG_EV3
VCG_EV3_P1 = F_VCG_EV3_P1
DVCG_EV3 = F_DVCG_ER3 & 0x3F
DVCG_EV3_Delta_v = (DVCG_EV3 * 0.0125) + (-0.725)
EDef_P0 = (2.4 + VCG_EV3 * 0.0125 ) + DVCG_EV3_Delta_v 
EDef_P1 = (2.4 + VCG_EV3_P1 * 0.0125) + DVCG_EV3_Delta_v
print(EDef_P0) 
print(EDef_P1)

VCG_P0.append(EDef_P0)
VCG_P1.append(EDef_P1)

VCG_FV3 = F_VCG_FV3
VCG_FV3_P1 = F_VCG_FV3_P1
DVCG_FV3 = F_DVCG_FR3 & 0x3F
DVCG_FV3_Delta_v = (DVCG_FV3 * 0.0125) + (-0.825)
FDef_P0 = (3.2 + VCG_FV3 * 0.0125 ) + DVCG_FV3_Delta_v 
FDef_P1 = (3.2 + VCG_FV3_P1 * 0.0125) + DVCG_FV3_Delta_v
print(FDef_P0) 
print(FDef_P1)

VCG_P0.append(FDef_P0)
VCG_P1.append(FDef_P1)

VCG_GV3 = F_VCG_GV3
VCG_GV3_P1 = F_VCG_GV3_P1
DVCG_GV3 = F_DVCG_GR3 & 0x3F
DVCG_GV3_Delta_v = (DVCG_GV3 * 0.0125) + (-0.925)
GDef_P0 = (4.0 + VCG_GV3 * 0.0125 ) + DVCG_GV3_Delta_v 
GDef_P1 = (4.0 + VCG_GV3_P1 * 0.0125) + DVCG_GV3_Delta_v
print(GDef_P0)
print(GDef_P1) 

VCG_P0.append(GDef_P0)
VCG_P1.append(GDef_P1)



######################################################################
######################################################################




def get_cvd():
    
    global outFileName
    global plane_no
    vt_Shift = 0.025
    Max_Vlt = 6.98
	
	
    # Retrieve the values from the input fields
    ce_values = parse_range_values(ce_entry.get())
    fim_values = parse_range_values(fim_entry.get())
    die_values = parse_range_values(die_entry.get())
    plane_values = parse_range_values(plane_entry.get())
    block_no_values = parse_range_values(block_no_entry.get())
    wl_values = parse_range_values(wl_entry.get())
    string_values = parse_range_values(string_entry.get())

   
    
    # Create the figure and axes
    global fig, ax
    fig, ax = plt.subplots(figsize=(12, 8))

    # Loop through the values and plot data for each combination
    for ce in ce_values:
		for fim in fim_values:
			for die in die_values:
				for plane in plane_values:
					for block_no in block_no_values:
						for wl in wl_values:
							for string in string_values:
								plane_no = int(plane)
								FlashInfoObj.ce	 = int(ce)
								FlashInfoObj.fim = int(fim)
								FlashInfoObj.die = int(die) #physical die number. Don't give logical die numer
								FlashInfoObj.block_no = int(block_no)*2+plane_no #meta block_no number
								FlashInfoObj.wl = int(wl)
								FlashInfoObj.string = int(string)
								
								#FlashInfoObj.ce = 0 # keep fixed at 0
								
								#outFileName = "TLC_CVD_EPWR_" +"_" + str(FlashInfoObj.fim) + "_" + str(FlashInfoObj.die) + "_" + str(FlashInfoObj.block_no*2+plane) + "_" + str(FlashInfoObj.wl) + "_" + str(FlashInfoObj.string) + "_"+ ".csv"
								outFileName = "TLC_CVD_EPWR_" +"_" + str(FlashInfoObj.ce) + str(FlashInfoObj.fim) + "_" + str(FlashInfoObj.die) + "_" + str(FlashInfoObj.block_no) + "_" + str(FlashInfoObj.wl) + "_" + str(FlashInfoObj.string) + "_"+ ".csv"
								
								ouputcsv = open(outFileName, 'wb')
								csvWriter = csv.writer(ouputcsv, delimiter=',')
								csvWriter.writerow(["user_WL", "fim", "ce", "die", "wl", "string", "count", "block_no", "vlt X-axis","Population Y-Axis"])
								
								print("Getting CVD of - CE: " + str(FlashInfoObj.ce) + " FIM :" + str(FlashInfoObj.fim) + " DIE :" + str(FlashInfoObj.die) + " Plane :" + str(plane_no) + " Blk:" + str(FlashInfoObj.block_no) + " WL :" + str(FlashInfoObj.wl) + " Str :" + str(FlashInfoObj.string))
								
								obj.getCVD(FlashInfoObj.fim, FlashInfoObj.ce, FlashInfoObj.die, FlashInfoObj.block_no, FlashInfoObj.wl, FlashInfoObj.string, BlockType_Flag, vt_Shift, csvWriter, AttrObj.isVerbose)
							
								ouputcsv.close()
								
								outFileName = "TLC_CVD_EPWR_" + "_" + str(FlashInfoObj.ce) + str(FlashInfoObj.fim) + "_" + str(FlashInfoObj.die) + "_" + str(FlashInfoObj.block_no) + "_" + str(FlashInfoObj.wl) + "_" + str(FlashInfoObj.string) + "_"+ ".csv"  
								
								print("Plotting CVD of - CE: " + str(FlashInfoObj.ce) + " FIM :" + str(FlashInfoObj.fim) + " DIE :" + str(FlashInfoObj.die) + " Plane :" + str(plane_no) + " Blk:" + str(FlashInfoObj.block_no) + " WL :" + str(FlashInfoObj.wl) + " Str :" + str(FlashInfoObj.string))
								
								df = pd.read_csv(outFileName)
								
								x = df['vlt X-axis']
								y = df['Population Y-Axis']
								
								ax.plot(x, y, color='#%06X' % random.randint(0, 0xFFFFFF), linestyle = 'solid',label = "CE:"+str(ce)+"FIM:"+str(fim)+" Die:"+str(die)+" Plane:"+str(plane)+" Block:"+str(block_no)+" WL:"+str(wl)+" String:"+str(string),lw=1)
								#ax.plot(x, y, '-r', label=f"FIM:{fim} Die:{die} Plane:{plane} Block:{block_no} WL:{wl} String:{string}",lw = 0.1)
								
								if plane_no == 0:
									for x in VCG_P0:
										ax.axvline(x=x, ymin = 0, ymax = 10**4, color='b', linestyle='-', linewidth=2)
									if VCG_P0_new !=[]:
										for x in VCG_P0_new:
											ax.axvline(x=x, ymin = 0, ymax = 10**4, color='r', linestyle='-', linewidth=2)
                                            
                                            
								if plane_no == 1:
									for x in VCG_P1:
										ax.axvline(x=x, ymin = 0, ymax = 10**4, color='b', linestyle='-', linewidth=2)
									if VCG_P0_new !=[]:
										for x in VCG_P0_new:
											ax.axvline(x=x, ymin = 0, ymax = 10**4, color='r', linestyle='-', linewidth=2)
    # Set labels and title
    ax.set_xlabel('Voltage')
    ax.set_ylabel('No of Cells')
    ax.set_title('CVD Plot')
    ax.set_yscale('log')
    ax.set_xlim(0,Max_Vlt)
    ax.set_ylim(1,10**5)
    ax.legend(ncol=5,fontsize=5)
    ax.grid()
    
    ax.grid(which = "minor")
    ax.minorticks_on()

    # Create a Tkinter canvas for the plot
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()

    # Place the canvas on the left-hand side
    canvas.get_tk_widget().place(relx=0, rely=0, relwidth=0.8, relheight=1)


def save_figure():
    # Create an entry field for the file name
    file_name_label = tk.Label(frame, text='File Name:')
    file_name_label.pack()
    file_name_entry = tk.Entry(frame)
    file_name_entry.pack()

    # Create a button to save the figure
    save_button = tk.Button(frame, text='Save', command=lambda: save_figure_to_file(file_name_entry.get()), font=('Arial', 14), padx=10, pady=10)
    save_button.pack()

def save_figure_to_file(file_name):
    # Check if a file name is provided
    if file_name:
        # Save the figure as a PNG file
        file_path = os.path.join(os.getcwd(), str(file_name)+".png")
        fig.savefig(file_path)
        print("Figure saved as "+str(file_path))
    else:
        print("Please provide a file name.")

def on_closing():
    # Close the command prompt when the GUI is closed
    sys.exit()




# Create the main window
window = tk.Tk()
window.title('CVD Plotter')
window.geometry('1900x950')

# Create a frame for buttons and data entries on the right-hand side
frame = tk.Frame(window)
frame.place(relx=0.8, rely=0, relwidth=0.2, relheight=1)




#----------------------------------------------------------------------------------------------------#
# Create a drop-down button for BiCS Type
label_bics_type = tk.Label(frame, text="BiCS Type")
label_bics_type.pack()
button_bics_type = ttk.Combobox(frame, values=["BiCS5 x3","BiCS8 x3", "BiCS9 x3"], state="readonly")
button_bics_type.pack()
# Set the initial value of the Combobox
initial_bics_type = "BiCS5 x3"
button_bics_type.set(initial_bics_type)
# Create a string variable to store the selected option
selected_bics_type = tk.StringVar()
# Set the initial value of the string variable
selected_bics_type.set(button_bics_type.get())
# Bind the update_variable function to the drop-down selection event
button_bics_type.bind("<<ComboboxSelected>>", get_bics_type)

#--------------------------------------------------BLOCK TYPE-----------------------------------------------------------#
# Create a drop-down button for Block Type
label_block_type = tk.Label(frame, text="Block Type")
label_block_type.pack()
button_block_type = ttk.Combobox(frame, values=["SLC", "TLC", "NDWL"], state="readonly")
button_block_type.pack()
# Set the initial value of the Combobox
initial_block_type = "TLC"
button_block_type.set(initial_block_type)
# Create a string variable to store the selected option
selected_block_type = tk.StringVar()
# Set the initial value of the string variable
selected_block_type.set(button_block_type.get())
# Bind the update_variable function to the drop-down selection event
button_block_type.bind("<<ComboboxSelected>>", get_block_type)


# Create a label for additional information
additional_info_label = tk.Label(frame, text='Note- WL=0: WLDS0, WL=1: WLDS1,' +'\n' + 'WL=2: WLDD0, WL=3: WLDD1,' + '\n' + 'WL=4: SGS, WL=5: SGD,' + '\n' + 'WL=6: WLDL, WL=7: WLDU', fg='red')
additional_info_label.pack(pady=5)
additional_info_label.pack_forget()  # Hide the label initially

# Create input fields for FIM, Die, Plane, Block, WL, and String
ce_label = tk.Label(frame, text='CE:')
ce_label.pack()
ce_entry = tk.Entry(frame)
ce_entry.pack()
ce_entry.insert(0,0)

fim_label = tk.Label(frame, text='FIM:')
fim_label.pack()
fim_entry = tk.Entry(frame)
fim_entry.pack()
fim_entry.insert(0,0)

die_label = tk.Label(frame, text='Die:')
die_label.pack()
die_entry = tk.Entry(frame)
die_entry.pack()
die_entry.insert(0,0)

plane_label = tk.Label(frame, text='Plane:')
plane_label.pack()
plane_entry = tk.Entry(frame)
plane_entry.pack()
plane_entry.insert(0,0)

block_no_label = tk.Label(frame, text='Block:')
block_no_label.pack()
block_no_entry = tk.Entry(frame)
block_no_entry.pack()
block_no_entry.insert(0,200)

wl_label = tk.Label(frame, text='WL:')
wl_label.pack()
wl_entry = tk.Entry(frame)
wl_entry.pack()
wl_entry.insert(0,0)

string_label = tk.Label(frame, text='String:')
string_label.pack()
string_entry = tk.Entry(frame)
string_entry.pack()
string_entry.insert(0,0)


# Create input fields for AVCGRV, BCGRV, CCGRV, DCGRV, ECGRV, FCGRV, and ECGRV
F_VCG_AV3_label = tk.Label(frame, text='F_VCG_AV3:')
F_VCG_AV3_label.pack()
F_VCG_AV3_entry = tk.Entry(frame)
F_VCG_AV3_entry.pack()
F_VCG_AV3_entry.insert(0, hex(F_VCG_AV3))  # Insert a default hexadecimal value, replace with actual value from your list

F_VCG_BV3_label = tk.Label(frame, text='F_VCG_BV3:')
F_VCG_BV3_label.pack()
F_VCG_BV3_entry = tk.Entry(frame)
F_VCG_BV3_entry.pack()
F_VCG_BV3_entry.insert(0, hex(F_VCG_BV3))  # Insert a default hexadecimal value, replace with actual value from your list

F_VCG_CV3_label = tk.Label(frame, text='F_VCG_CV3:')
F_VCG_CV3_label.pack()
F_VCG_CV3_entry = tk.Entry(frame)
F_VCG_CV3_entry.pack()
F_VCG_CV3_entry.insert(0, hex(F_VCG_CV3))  # Insert a default hexadecimal value, replace with actual value from your list

F_VCG_DV3_label = tk.Label(frame, text='F_VCG_DV3:')
F_VCG_DV3_label.pack()
F_VCG_DV3_entry = tk.Entry(frame)
F_VCG_DV3_entry.pack()
F_VCG_DV3_entry.insert(0, hex(F_VCG_DV3))  # Insert a default hexadecimal value, replace with actual value from your list

F_VCG_EV3_label = tk.Label(frame, text='F_VCG_EV3:')
F_VCG_EV3_label.pack()
F_VCG_EV3_entry = tk.Entry(frame)
F_VCG_EV3_entry.pack()
F_VCG_EV3_entry.insert(0, hex(F_VCG_EV3))  # Insert a default hexadecimal value, replace with actual value from your list

F_VCG_FV3_label = tk.Label(frame, text='F_VCG_FV3:')
F_VCG_FV3_label.pack()
F_VCG_FV3_entry = tk.Entry(frame)
F_VCG_FV3_entry.pack()
F_VCG_FV3_entry.insert(0, hex(F_VCG_FV3))  # Insert a default hexadecimal value, replace with actual value from your list

F_VCG_GV3_label = tk.Label(frame, text='F_VCG_GV3:')
F_VCG_GV3_label.pack()
F_VCG_GV3_entry = tk.Entry(frame)
F_VCG_GV3_entry.pack()
F_VCG_GV3_entry.insert(0, hex(F_VCG_GV3))  # Insert a default hexadecimal value, replace with actual value from your list

# Create 'Set Param' button
set_param_button = tk.Button(frame, text='Set Param', command=Set_Param, font=('Arial', 14), padx=10, pady=10)
set_param_button.pack(pady=5)


# Create 'Get CVD' button
get_cvd_button = tk.Button(frame, text='Get CVD', command = get_cvd, font=('Arial', 14), padx=10, pady=10)
get_cvd_button.pack(pady = 5)

# Create 'Save Figure' button
save_figure_button = tk.Button(frame, text='Save Figure', command=save_figure, font=('Arial', 14), padx=10, pady=10)
save_figure_button.pack(pady = 10)

Vt_track_button = tk.Button(frame, text='Vt Tracking', command = lambda: Vt_Tracking(outFileName, fig), font=('Arial', 14), padx=10, pady=10)
Vt_track_button.pack(pady = 15)

# Run the Tkinter event loop
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()

