# import tkinter module
from Tkinter import *
import os , shutil
import csv
import tkFileDialog
import diagCmdLib as dgcmd
import CTFServiceWrapper as PyServiceWrap
from datetime import datetime

obj = dgcmd.diagCmdLibClass(1)


# creating main tkinter window/toplevel
root = Tk()
root.title("RSSD - MSFA Tool - FADI Module")
root.geometry('1024x768')
root.iconbitmap("WD.ico")

Label(root,text="  ").grid(row=0,column=0)


cwd=os.getcwd()
newpath = cwd+"\FADI_Dumps"
if not os.path.exists(newpath):
    os.makedirs(newpath)

LabelFrame(root,text="",padx=200, pady=200, height=5,width=1024).grid(row=9,column=0,columnspan=10)
Label(root,text="  ").grid(row=10,column=0)

Reference_Folder = "C:\\CVDDump"
Schema_File = []
BOT_File = []
for files in os.listdir(Reference_Folder):
    if files.endswith(".sdb"):
        Schema_File=files
    if files.endswith(".bot"):
        BOT_File=files    

Label(text="Default Schema File: "+str("   ")+str(Schema_File)).grid(row=11,column=1,sticky="W")
Label(text="Default BOT File: "+str("   ")+str(BOT_File)).grid(row=12,column=1,sticky="W")
Label(root,text="  ").grid(row=13,column=0)
LabelFrame(root,text="",padx=200, pady=200, height=5,width=1024).grid(row=15,column=0,columnspan=10)


Label(root,text="").grid(row=30,column=0,columnspan=10)
Label(root,text="").grid(row=50,column=0)
Label(root,text="").grid(row=61,column=0)
Label(root,text="").grid(row=66,column=0)
Label(root,text="").grid(row=66,column=0)
Label(root,text="").grid(row=75,column=0,columnspan=10)
Label(root,text="").grid(row=82,column=0,columnspan=10)
Label(root,text="").grid(row=90,column=0)
Label(root,text="").grid(row=110,column=0)
Label(root,text="").grid(row=121,column=0)



def Schema_File_Input():
    filename = tkFileDialog.askopenfilename() 
    global Schema_File
    Schema_File = filename
    Label(root, text="Updated Schema File : "+filename).grid(row=40,column=4, columnspan=2, sticky="E")

Button (root, text="Select Updated Schema File ",padx=10,pady=2,width=25,command=Schema_File_Input).grid(row=40, column=1, sticky="W")

def BOT_File_Input():
    filename = tkFileDialog.askopenfilename() 
    global BOT_File
    BOT_File = filename
    Label(root, text="Updated BOT File : "+filename).grid(row=60,column=4, columnspan=2, sticky="E")

Button (root, text="Select Updated BOT File ",padx=10,pady=2,width=25,command=BOT_File_Input).grid(row=60, column=1,columnspan=2, sticky="W")

LabelFrame(root,text="",padx=2, pady=2, height=5,width=1024).grid(row=65,column=0,columnspan=10)


Label(root,text="Enter FADI Name :").grid(row=70,column=1,sticky="W")
FADI_Var = StringVar()
FADI_Entry = Entry(root,textvariable=FADI_Var)
FADI_Entry.grid(row=70,column=1,columnspan=5)

FADI_Name = ""


def FADI_Dump():
    obj.FALogDump()
    global newpath
    global cwd
    global FADI_Name
    shutil.move(str(cwd)+str('\\Yoda_FADump.FAD'), str(newpath)+str('\\Yoda_FADump.FAD'))
    
    global FADI_Name
    global FADI_Entry
    #FADI_Name=FADI_Entry.get()
    FADI_Name = str(FADI_Entry.get()) + str("_")+str (datetime.now().strftime("%Y_%m_%d_%I_%M_%S_%p"))
    print(FADI_Name)
    os.chdir(newpath)
    os.rename("Yoda_FADump.FAD",str(FADI_Name)+str(".fad"))
    os.chdir(cwd)

    Label(root,text="FADI File Dumped to location : "+str(newpath)).grid(row=80, column=4)


Button (root, text="Get Drive FADI ",padx=10,pady=2,width=25,command=FADI_Dump).grid(row=80, column=1,columnspan=2, sticky="W")

LabelFrame(root,text="",padx=2, pady=2, height=5,width=1024).grid(row=85,column=0,columnspan=10)



def FADI_File_Input():
    filename = tkFileDialog.askopenfilename()
    global FADI_File
    FADI_File = filename 
    Label(root, text="Selected FADI File : "+filename).grid(row=100,column=4, columnspan=2, sticky="E")

Button (root, text="Select FADI File ",padx=10,pady=2,width=25,command=FADI_File_Input).grid(row=100, column=1,columnspan=2, sticky="W")



def FADI_Parse():

    global newpath
    global Schema_File
    global FADI_Name
    
    print (r"C:\\Program Files (x86)\\SanDisk\\CVF_2.0_x64\\Python\\FADI_Dumps\\"+str(FADI_Name)+str(".fad"))
    print (r"C:\\CVDDump\\"+Schema_File)
    
    obj.ParseFADLog(r'"C:\\Program Files (x86)\\SanDisk\\CVF_2.0_x64\\Python\\FADI_Dumps\\"'+str(FADI_Name)+str(".fad"), r"C:\\CVDDump\\"+Schema_File)
    Label(root,text="FADI File Parsed & Dumped to location : "+str(newpath)).grid(row=120, column=4)

Button (root, text="Parse FADI ",padx=10,pady=2,width=25,command=FADI_Parse).grid(row=120, column=1, columnspan=2,sticky="W")

LabelFrame(root,text="",padx=2, pady=2, height=5,width=1024).grid(row=125,column=0,columnspan=10)


root.mainloop()