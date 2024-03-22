# import tkinter module
from Tkinter import *
import os , shutil
import csv
import tkFileDialog
import FaDleDiagLib as dgcmd
from datetime import datetime

obj = dgcmd.diagCmdLibClass(1)


# creating main tkinter window/toplevel
root = Tk()
root.title("RSSD - MSFA Tool - Parameter Module")
root.geometry('1280x720')
root.iconbitmap("WD.ico")

Label(root,text="  ").grid(row=0,column=0)



cwd=os.getcwd()
newpath = cwd+"\Parameter_Dumps"
if not os.path.exists(newpath):
    os.makedirs(newpath)

Top_Frame = LabelFrame(root,text="Get Parameter Section",padx=200, pady=200, height=20,width=1280).grid(row=1,column=0,columnspan=10)

Label(root,text="").grid(row=2,column=0)
Label(root,text="").grid(row=3,column=0)

Label(root,text="CE").grid(row=3,column=1,sticky="W")
Label(root,text="FIM").grid(row=3,column=2,sticky="W")
Label(root,text="DIE").grid(row=3,column=3,sticky="W")
Label(root,text="PARAM ADDRESS (int) ").grid(row=3,column=4,sticky="W")


# 1st Row
Label(root,text="").grid(row=4,column=0)

CE_1 = StringVar()
CE_11= Entry(root,textvariable=CE_1,width=10)
CE_11.grid(row=4,column=1,sticky="W")

FIM_1 = StringVar()
FIM_11= Entry(root,textvariable=FIM_1,width=10)
FIM_11.grid(row=4,column=2,sticky="W")

DIE_1 = StringVar()
DIE_11= Entry(root,textvariable=DIE_1,width=10)
DIE_11.grid(row=4,column=3,sticky="W")

ADDR_1 = StringVar()
ADDR_11= Entry(root,textvariable=ADDR_1,width=10)
ADDR_11.grid(row=4,column=4,sticky="W")


def Get_Param_1():
    
    FIM = FIM_11.get()
    CE = CE_11.get()
    DIE = DIE_11.get()
    ADDR = ADDR_11.get()
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="PARAM VALUE : " +str(hex(Value))).grid(row=4,column=6, sticky="W")
    #Label(root, text="   ").grid(row=2,column=12, columnspan=2, sticky="W")


Button(root, text="Get Value ",padx=10,pady=2,width=10,command=Get_Param_1).grid(row=4, column=5, sticky="W")


# 2nd Row
Label(root,text="").grid(row=5,column=0)
Label(root,text="").grid(row=6,column=0)

CE_2 = StringVar()
CE_21= Entry(root,textvariable=CE_2,width=10)
CE_21.grid(row=6,column=1,sticky="W")

FIM_2 = StringVar()
FIM_21= Entry(root,textvariable=FIM_2,width=10)
FIM_21.grid(row=6,column=2,sticky="W")

DIE_2 = StringVar()
DIE_21= Entry(root,textvariable=DIE_2,width=10)
DIE_21.grid(row=6,column=3,sticky="W")

ADDR_2 = StringVar()
ADDR_21= Entry(root,textvariable=ADDR_2,width=10)
ADDR_21.grid(row=6,column=4,sticky="W")


def Get_Param_2():
    FIM = FIM_21.get()
    CE = CE_21.get()
    DIE = DIE_21.get()
    ADDR = ADDR_21.get()
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="PARAM VALUE : " +str(hex(Value))).grid(row=6,column=6, sticky="W")
    #Label(root, text="   ").grid(row=4,column=12, columnspan=2, sticky="W")


Button(root, text="Get Value ",padx=10,pady=2,width=10,command=Get_Param_2).grid(row=6, column=5, sticky="W")

# 3rd Row
Label(root,text="").grid(row=7,column=0)
Label(root,text="").grid(row=8,column=0)

CE_3 = StringVar()
CE_31= Entry(root,textvariable=CE_3,width=10)
CE_31.grid(row=8,column=1,sticky="W")

FIM_3 = StringVar()
FIM_31= Entry(root,textvariable=FIM_3,width=10)
FIM_31.grid(row=8,column=2,sticky="W")

DIE_3 = StringVar()
DIE_31= Entry(root,textvariable=DIE_3,width=10)
DIE_31.grid(row=8,column=3,sticky="W")

ADDR_3 = StringVar()
ADDR_31= Entry(root,textvariable=ADDR_3,width=10)
ADDR_31.grid(row=8,column=4,sticky="W")


def Get_Param_3():
    
    FIM = FIM_31.get()
    CE = CE_31.get()
    DIE = DIE_31.get()
    ADDR = ADDR_31.get()
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="PARAM VALUE : " +str(hex(Value))).grid(row=8,column=6, sticky="W")
    #Label(root, text="   ").grid(row=6,column=12, columnspan=2, sticky="W")


Button(root, text="Get Value ",padx=10,pady=2,width=10,command=Get_Param_3).grid(row=8, column=5, sticky="W")

# 4th  Row
Label(root,text="").grid(row=9,column=0)
Label(root,text="").grid(row=10,column=0)

CE_4 = StringVar()
CE_41= Entry(root,textvariable=CE_4,width=10)
CE_41.grid(row=10,column=1,sticky="W")

FIM_4 = StringVar()
FIM_41= Entry(root,textvariable=FIM_4,width=10)
FIM_41.grid(row=10,column=2,sticky="W")

DIE_4 = StringVar()
DIE_41= Entry(root,textvariable=DIE_4,width=10)
DIE_41.grid(row=10,column=3,sticky="W")

ADDR_4 = StringVar()
ADDR_41= Entry(root,textvariable=ADDR_4,width=10)
ADDR_41.grid(row=10,column=4,sticky="W")


def Get_Param_4():
    
    FIM = FIM_41.get()
    CE = CE_41.get()
    DIE = DIE_41.get()
    ADDR = ADDR_41.get()
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="PARAM VALUE : " +str(hex(Value))).grid(row=10,column=6, sticky="W")
    #Label(root, text="   ").grid(row=8,column=12, columnspan=2, sticky="W")


Button(root, text="Get Value ",padx=10,pady=2,width=10,command=Get_Param_4).grid(row=10, column=5, sticky="W")

# 5th Row
Label(root,text="").grid(row=11,column=0)
Label(root,text="").grid(row=12,column=0)

CE_5 = StringVar()
CE_51= Entry(root,textvariable=CE_5,width=10)
CE_51.grid(row=12,column=1,sticky="W")

FIM_5 = StringVar()
FIM_51= Entry(root,textvariable=FIM_5,width=10)
FIM_51.grid(row=12,column=2,sticky="W")

DIE_5 = StringVar()
DIE_51= Entry(root,textvariable=DIE_5,width=10)
DIE_51.grid(row=12,column=3,sticky="W")

ADDR_5 = StringVar()
ADDR_51= Entry(root,textvariable=ADDR_5,width=10)
ADDR_51.grid(row=12,column=4,sticky="W")


def Get_Param_5():
    
    FIM = FIM_51.get()
    CE = CE_51.get()
    DIE = DIE_51.get()
    ADDR = ADDR_51.get()
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="PARAM VALUE : " +str(hex(Value))).grid(row=12,column=6, sticky="W")
    #Label(root, text="  ").grid(row=10,column=10, columnspan=2, sticky="W")


Button(root, text="Get Value ",padx=10,pady=2,width=10,command=Get_Param_5).grid(row=12, column=5, sticky="W")

Label(root,text="").grid(row=13,column=0)

Bottom_Frame = LabelFrame(root,text="Set Parameter Section",padx=200, pady=200, height=20,width=1280).grid(row=14,column=0,columnspan=10)

Label(root,text="").grid(row=15,column=0)
Label(root,text="").grid(row=16,column=0)

Label(root,text="CE").grid(row=16,column=1,sticky="W")
Label(root,text="FIM").grid(row=16,column=2,sticky="W")
Label(root,text="DIE").grid(row=16,column=3,sticky="W")
Label(root,text="PARAM ADDRESS (int)").grid(row=16,column=4,sticky="W")
Label(root,text="PARAM VALUE (int)").grid(row=16,column=5,sticky="W")

# 1st Row
Label(root,text="").grid(row=17,column=0)

CE_13 = StringVar()
CE_113= Entry(root,textvariable=CE_13,width=10)
CE_113.grid(row=17,column=1,sticky="W")

FIM_13 = StringVar()
FIM_113= Entry(root,textvariable=FIM_13,width=10)
FIM_113.grid(row=17,column=2,sticky="W")

DIE_13 = StringVar()
DIE_113= Entry(root,textvariable=DIE_13,width=10)
DIE_113.grid(row=17,column=3,sticky="W")

ADDR_13 = StringVar()
ADDR_113= Entry(root,textvariable=ADDR_13,width=10)
ADDR_113.grid(row=17,column=4,sticky="W")

VALUE_13 = StringVar()
VALUE_113= Entry(root,textvariable=VALUE_13,width=10)
VALUE_113.grid(row=17,column=5,sticky="W")

def Set_Param_1():
    
    FIM = FIM_113.get()
    CE = CE_113.get()
    DIE = DIE_113.get()
    ADDR = ADDR_113.get()
    VAL = VALUE_113.get()
    obj.SetParam(int(FIM),int(CE),int(DIE),int(ADDR),int(VAL))
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="SET TO : " +str(hex(Value))).grid(row=17,column=7, sticky="W")
    #Label(root, text="   ").grid(row=21,column=11, columnspan=2, sticky="W")


Button(root, text="Set Value ",padx=10,pady=2,width=10,command=Set_Param_1).grid(row=17, column=6,sticky="W")

# 2nd Row
Label(root,text="").grid(row=18,column=0)
Label(root,text="").grid(row=19,column=0)

CE_23 = StringVar()
CE_213= Entry(root,textvariable=CE_23,width=10)
CE_213.grid(row=19,column=1,sticky="W")

FIM_23 = StringVar()
FIM_213= Entry(root,textvariable=FIM_23,width=10)
FIM_213.grid(row=19,column=2,sticky="W")

DIE_23 = StringVar()
DIE_213= Entry(root,textvariable=DIE_23,width=10)
DIE_213.grid(row=19,column=3,sticky="W")

ADDR_23 = StringVar()
ADDR_213= Entry(root,textvariable=ADDR_23,width=10)
ADDR_213.grid(row=19,column=4,sticky="W")

VALUE_23 = StringVar()
VALUE_213= Entry(root,textvariable=VALUE_23,width=10)
VALUE_213.grid(row=19,column=5,sticky="W")


def Set_Param_2():
    FIM = FIM_213.get()
    CE = CE_213.get()
    DIE = DIE_213.get()
    ADDR = ADDR_213.get()
    VAL = VALUE_213.get()
    obj.SetParam(int(FIM),int(CE),int(DIE),int(ADDR),int(VAL))
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="SET TO : " +str(hex(Value))).grid(row=19,column=7, sticky="W")
    #Label(root, text="   ").grid(row=24,column=11, columnspan=2, sticky="W")


Button(root, text="Set Value ",padx=10,pady=2,width=10,command=Set_Param_2).grid(row=19, column=6, sticky="W")

# 3rd Row 
Label(root,text="").grid(row=20,column=0)
Label(root,text="").grid(row=21,column=0)

CE_33 = StringVar()
CE_313= Entry(root,textvariable=CE_33,width=10)
CE_313.grid(row=21,column=1,sticky="W")

FIM_33 = StringVar()
FIM_313= Entry(root,textvariable=FIM_33,width=10)
FIM_313.grid(row=21,column=2,sticky="W")

DIE_33 = StringVar()
DIE_313= Entry(root,textvariable=DIE_33,width=10)
DIE_313.grid(row=21,column=3,sticky="W")

ADDR_33 = StringVar()
ADDR_313= Entry(root,textvariable=ADDR_33,width=10)
ADDR_313.grid(row=21,column=4,sticky="W")

VALUE_33 = StringVar()
VALUE_313= Entry(root,textvariable=VALUE_33,width=10)
VALUE_313.grid(row=21,column=5,sticky="W")



def Set_Param_3():
    
    FIM = FIM_313.get()
    CE = CE_313.get()
    DIE = DIE_313.get()
    ADDR = ADDR_313.get()
    VAL = VALUE_313.get()
    obj.SetParam(int(FIM),int(CE),int(DIE),int(ADDR),int(VAL))
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="SET TO : " +str(hex(Value))).grid(row=21,column=7, sticky="W")
    #Label(root, text="   ").grid(row=26,column=11, columnspan=2, sticky="W")



Button(root, text="Set Value ",padx=10,pady=2,width=10,command=Set_Param_3).grid(row=21, column=6, sticky="W")

# 4th Row 
Label(root,text="").grid(row=22,column=0)
Label(root,text="").grid(row=23,column=0)

CE_43 = StringVar()
CE_413= Entry(root,textvariable=CE_43,width=10)
CE_413.grid(row=23,column=1,sticky="W")

FIM_43 = StringVar()
FIM_413= Entry(root,textvariable=FIM_43,width=10)
FIM_413.grid(row=23,column=2,sticky="W")

DIE_43 = StringVar()
DIE_413= Entry(root,textvariable=DIE_43,width=10)
DIE_413.grid(row=23,column=3,sticky="W")

ADDR_43 = StringVar()
ADDR_413= Entry(root,textvariable=ADDR_43,width=10)
ADDR_413.grid(row=23,column=4,sticky="W")

VALUE_43 = StringVar()
VALUE_413= Entry(root,textvariable=VALUE_43,width=10)
VALUE_413.grid(row=23,column=5,sticky="W")


def Set_Param_4():
    
    FIM = FIM_413.get()
    CE = CE_413.get()
    DIE = DIE_413.get()
    ADDR = ADDR_413.get()
    VAL = VALUE_413.get()
    obj.SetParam(int(FIM),int(CE),int(DIE),int(ADDR),int(VAL))
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="SET TO : " +str(hex(Value))).grid(row=23,column=7, sticky="W")
    #Label(root, text="   ").grid(row=28,column=11, columnspan=2, sticky="W")


Button(root, text="Set Value ",padx=10,pady=2,width=10,command=Set_Param_4).grid(row=23, column=6, sticky="W")

# 5th Row
Label(root,text="").grid(row=24,column=0)
Label(root,text="").grid(row=25,column=0)

CE_53 = StringVar()
CE_513= Entry(root,textvariable=CE_53,width=10)
CE_513.grid(row=25,column=1,sticky="W")

FIM_53 = StringVar()
FIM_513= Entry(root,textvariable=FIM_53,width=10)
FIM_513.grid(row=25,column=2,sticky="W")

DIE_53 = StringVar()
DIE_513= Entry(root,textvariable=DIE_53,width=10)
DIE_513.grid(row=25,column=3,sticky="W")

ADDR_53 = StringVar()
ADDR_513= Entry(root,textvariable=ADDR_53,width=10)
ADDR_513.grid(row=25,column=4,sticky="W")

VALUE_53 = StringVar()
VALUE_513= Entry(root,textvariable=VALUE_53,width=10)
VALUE_513.grid(row=25,column=5,sticky="W")



def Set_Param_5():
    
    FIM = FIM_513.get()
    CE = CE_513.get()
    DIE = DIE_513.get()
    ADDR = ADDR_513.get()
    VAL = VALUE_513.get()
    obj.SetParam(int(FIM),int(CE),int(DIE),int(ADDR),int(VAL))
    Value = obj.GetParam(int(FIM),int(CE),int(DIE),int(ADDR))
    Label(root, text="SET TO : " +str(hex(Value))).grid(row=25,column=7, sticky="W")
    #Label(root, text="   ").grid(row=30,column=12, columnspan=2, sticky="W")


Button(root, text="Set Value ",padx=10,pady=2,width=10,command=Set_Param_5).grid(row=25, column=6, sticky="W")

root.mainloop()