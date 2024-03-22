
import Tkinter as tk
import FaDleDiagLib_Regfuse
#from .FaDleDiagLib_Regfuse import RegFuseRead
import os
import sys
import tkMessageBox 


cwd = os.getcwd()
window = tk.Tk()
window.minsize(400,400)
window.title("GUI- Regfuse and Bad Block")
obj = FaDleDiagLib_Regfuse.diagCmdLibClass(1) 
logo_image = tk.PhotoImage(file="WD.gif").subsample(6,6)
logo_label = tk.Label(window, image = logo_image)
logo_label.pack(side="top", anchor="nw", padx=10, pady=10)


def Regfuse():   

    smallwindow = tk.Toplevel(window)
    smallwindow.geometry("800x600")
    smallwindow.title("GUI- Regfuse and Bad Block")
    
    #nand generation 
    NAND_Gen_Variable = tk.StringVar(smallwindow)
    Die = tk.StringVar(smallwindow)
    checkbox_var = tk.StringVar(smallwindow)
    fim_l = 0;
    die_l = 0;
    check_l = "false";
    
    def dumpRegfuse(fticked,fim_var,die_var): 
        gen_var = NAND_Gen_Variable.get()
        if fticked == "true":
            obj.Manual_POR_FDh(fim_var, 0, die_var)
            obj.RegFuseRead(fim_var,die_var,3) #fim,die,Avpgm
            print("check ticked")
            print("Fim & Gen", fim_var,gen_var,die_var)
        else:
            print("check UNticked")
            print("Fim & Gen", fim_var,gen_var,die_var)
            obj.RegFuseRead(fim_var,die_var,3) #fim,die,Avpgm
        #print("Fim & Gen", fim_var,gen_var,die_var)

    NAND_Gen_Option = tk.OptionMenu(smallwindow, NAND_Gen_Variable,
                           "BICS5", "BICS6",
                           "BICS8")
    
    #No. of fim entry box
    label = tk.Label(smallwindow, text = "Fim Number {0,4} :")
    label.pack(side = "left" )
    fim = tk.Entry(smallwindow)
    fim.pack(side = "left")
    
    #Die Number code
    die_label = tk.Label(smallwindow, text = "Die Number {0,4} :")
    die_label.pack(side = "left" )
    die = tk.Entry(smallwindow)
    die.pack(side = "left")
    
    
    checkbox = tk.Checkbutton(smallwindow,
                           text='<checkbox label>',                           
                           variable=checkbox_var,
                           onvalue='<value_when_checked>',
                           offvalue='<value_when_unchecked>')
    checkbox.pack(side = "left")
    try:
        fim_l = int(fim.get())
        die_l = int(die.get())
        check_l = checkbox_var.get()
    except Exception as e:
        print("Error: {0}".format(e))
        
    try:
        if not fim.get():
            raise ValueError("fim is empty")
        print("fim value is {0}".format(entry_var.get()))
    except Exception as e:
        print("Error: {0}".format(e))    
 
    try:
        if not die.get():
            raise ValueError("die is empty")
        print("die value is {0}".format(entry_var.get()))
    except Exception as e:
        print("Error: {0}".format(e))  


    button = tk.Button(smallwindow, text="Dump Regfuse",command=lambda: dumpRegfuse(check_l,fim_l,die_l))
    button.pack(side = "left")
        
def BadBlock():
    tkMessageBox.showinfo( "Bad Block", "Data")
    exit()
    

#print("Current working directory:", cwd) 
Regfuse_Button = tk.Button(window, text ="Regfuse", command = Regfuse)
BB_Button = tk.Button(window, text ="Bad Block", command = BadBlock)

# Create a drop-down menu to select the device type

Regfuse_Button.pack(side = "right",padx=200, pady=10)
BB_Button.pack(side ="left",padx=200, pady=10)
# Code to add widgets will go here...
window.mainloop()