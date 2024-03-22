# import tkinter module
from Tkinter import *
import os , shutil
import csv
import FaDleDiagLib as dgcmd
from datetime import datetime
#from tkinter.ttk import *

obj = dgcmd.diagCmdLibClass(1)


# creating main tkinter window/toplevel
root = Tk()
root.title("RSSD - MSFA Tool - Wafer Lot Module")
root.geometry('1024x768')
#root.iconbitmap("WD.ico")
# Load the logo image file
#logo_image = PhotoImage(file="WD.gif").subsample(10,10)
#logo_label = Label(root, image=logo_image)
#logo_label.grid(row = 0,column = 0)

#Define Variables

Value_Input = IntVar ()
List_Input = IntVar ()
Range_Input = IntVar ()

CE_No = StringVar()
FIM_No = StringVar()
DIE_No = StringVar()

CE_Start_No = StringVar()
CE_End_No = StringVar()
FIM_Start_No = StringVar()
FIM_End_No = StringVar()
DIE_Start_No = StringVar()
DIE_End_No = StringVar()

CE_List = StringVar()
FIM_List = StringVar()
DIE_List = StringVar()

fim_list_final = []
die_list_final = []

# Create the Entries Fields
CE_No_Label = Label(root, text = "Enter CE Number :")
FIM_No_Label = Label(root, text = "Enter FIM Number :")
DIE_No_Label = Label(root, text = "Enter DIE Number :")

CE_No_Entry = Entry(root, textvariable=CE_No, state="disabled")
FIM_No_Entry = Entry(root, textvariable=FIM_No, state="disabled")
DIE_No_Entry = Entry(root, textvariable=DIE_No, state="disabled") 

CE_No_Label.grid(row = 8, column = 0, sticky = W, pady = 2)
FIM_No_Label.grid(row = 10, column = 0, sticky = W, pady = 2)
DIE_No_Label.grid(row = 12, column = 0, sticky = W, pady = 2)
     
CE_No_Entry.grid(row = 8, column = 1, columnspan=2,sticky = W, pady = 2)
FIM_No_Entry.grid(row = 10, column = 1, columnspan=2,sticky = W, pady = 2)
DIE_No_Entry.grid(row = 12, column = 1, columnspan=2,sticky = W, pady = 2)


CE_No_Start_Label = Label(root, text = "Enter Starting CE Number :")
CE_No_End_Label = Label(root, text = "Enter Ending CE Number :")

FIM_No_Start_Label = Label(root, text = "Enter Starting FIM Number :")
FIM_No_End_Label = Label(root, text = "Enter Ending FIM Number :")

DIE_No_Start_Label = Label(root, text = "Enter Starting DIE Number :")
DIE_No_End_Label = Label(root, text = "Enter Ending DIE Number :")

Start_CE_No_Entry = Entry(root, textvariable=CE_Start_No, state="disabled")
End_CE_No_Entry = Entry(root, textvariable=CE_End_No, state="disabled")

Start_FIM_No_Entry = Entry(root, textvariable=FIM_Start_No, state="disabled")
End_FIM_No_Entry = Entry(root, textvariable=FIM_End_No, state="disabled")

Start_DIE_No_Entry = Entry(root, textvariable=DIE_Start_No, state="disabled")
End_DIE_No_Entry = Entry(root, textvariable=DIE_End_No, state="disabled") 

CE_No_Start_Label.grid(row = 14, column = 0, sticky = W, pady = 2)
CE_No_End_Label.grid(row = 16, column = 0,  sticky = W, pady = 2)
FIM_No_Start_Label.grid(row = 18, column = 0, sticky = W, pady = 2)
FIM_No_End_Label.grid(row = 20, column = 0,  sticky = W, pady = 2)
DIE_No_Start_Label.grid(row = 22, column = 0,  sticky = W, pady = 2)
DIE_No_End_Label.grid(row = 24, column = 0,  sticky = W, pady = 2)

Start_CE_No_Entry.grid(row = 14, column = 1, columnspan=2,sticky = W, pady = 2)
End_CE_No_Entry.grid(row = 16, column = 1, columnspan=2,sticky = W, pady = 2)
Start_FIM_No_Entry.grid(row = 18, column = 1, columnspan=2,sticky = W, pady = 2)
End_FIM_No_Entry.grid(row = 20, column = 1, columnspan=2,sticky = W, pady = 2)
Start_DIE_No_Entry.grid(row = 22, column = 1, columnspan=2,sticky = W,pady = 2)
End_DIE_No_Entry.grid(row=24,column = 1, columnspan=2,sticky = W,pady = 2)


CE_List_No_Label = Label(root, text = "Enter List of CE Number :")
FIM_List_No_Label = Label(root, text = "Enter List of FIM Number :")
DIE_List_No_Label = Label(root, text = "Enter List of DIE Number :")

CE_List_No_Entry = Entry(root, textvariable=CE_List, state="disabled")
FIM_List_No_Entry = Entry(root, textvariable=FIM_List, state="disabled")
DIE_List_No_Entry = Entry(root, textvariable=DIE_List, state="disabled") 

CE_List_No_Label.grid(row = 26, column = 0, sticky = W, pady = 2)
FIM_List_No_Label.grid(row = 28, column = 0, sticky = W, pady = 2)
DIE_List_No_Label.grid(row = 30, column = 0, sticky = W, pady = 2)
     
CE_List_No_Entry.grid(row = 26, column = 1, columnspan=2,sticky = W, pady = 2)
FIM_List_No_Entry.grid(row = 28, column = 1, columnspan=2,sticky = W, pady = 2)
DIE_List_No_Entry.grid(row = 30, column = 1, columnspan=2,sticky = W,pady = 2)


output1=Label(root,text="")
output1.grid(row=45,column=1,columnspan=2)
output2=Label(root,text="")
output2.grid(row=47,column=1,columnspan=2)
output3=Label(root,text="")
output3.grid(row=51,column=1,columnspan=2)



def get_wafer_lot():

    cwd=os.getcwd()
    newpath = cwd+"\WaferInfoLatest"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    else:
        shutil.rmtree(newpath)
        os.makedirs(newpath)


    global ce_list_final, fim_list_final, die_list_final

    for ce in ce_list_final:
        for fim in fim_list_final:
            for die in die_list_final:
                print("Wafer Info of - CE " + str(ce) + " FIM " + str(fim) + " DIE " + str(die))
                Waferinformation = obj.WaferInfo(int(ce),int(fim),int(die))

    top = Toplevel()
    top.title("RSSD - MSFA Tool - Wafer Lot Module")
    top.geometry('1024x768')
    #top.iconbitmap("WD.ico")
    col_names = ("CE", "FIM", "DIE", "Lot Number", "Wafer ID", "X coordinate", "Y coordinate","Sorted Date","Sorted Time ","Parameter Version","DS Version")
    for i, col_name in enumerate(col_names, start=0):
        Label(top, text=col_name).grid(row=5, column=i, padx=10)

    data=[]

    for file in os.listdir(newpath):
        full_path = os.path.join(newpath, file)		
        #print(file)
        with open(full_path, "rb") as passfile:
            reader = csv.reader(passfile)
            data.append(list(reader)[1]) 

    

    for i, row in enumerate(data, start=0):
        for col in range(0, 10):
            Label(top, text=row[col]).grid(row=6+i, column=col)

def Update_Entry_Type():
    
    Value_Sel= Value_Input.get()
    List_Sel = List_Input.get()
    Range_Sel= Range_Input.get()


    if Value_Sel ==1 and List_Sel==0 and Range_Sel==0: 
        CE_No_Entry.config(state='normal')
        FIM_No_Entry.config(state='normal')
        DIE_No_Entry.config(state='normal')
            
    else:
        CE_No_Entry.config(state='disabled')
        CE_No.set("")
        FIM_No_Entry.config(state='disabled')
        FIM_No.set("")
        DIE_No_Entry.config(state='disabled')
        DIE_No.set("")
        output1.config(text="")
        output2.config(text="")
        output3.config(text="")

    if Value_Sel ==0 and List_Sel==0 and Range_Sel==1: 
        Start_CE_No_Entry.config(state='normal')
        End_CE_No_Entry.config(state='normal')
        Start_FIM_No_Entry.config(state='normal')
        End_FIM_No_Entry.config(state='normal')
        Start_DIE_No_Entry.config(state='normal')
        End_DIE_No_Entry.config(state='normal')
    else:
        Start_CE_No_Entry.config(state='disabled')
        End_CE_No_Entry.config(state='disabled')
        Start_FIM_No_Entry.config(state='disabled')
        End_FIM_No_Entry.config(state='disabled')
        Start_DIE_No_Entry.config(state='disabled')
        End_DIE_No_Entry.config(state='disabled')
        CE_Start_No.set("")
        CE_End_No.set("")
        FIM_Start_No.set("")
        FIM_End_No.set("")
        DIE_Start_No.set("")
        DIE_End_No.set("")
        output1.config(text="")
        output2.config(text="")
        output3.config(text="")

    if Value_Sel ==0 and List_Sel==1 and Range_Sel==0: 
        CE_List_No_Entry.config(state='normal')
        FIM_List_No_Entry.config(state='normal')
        DIE_List_No_Entry.config(state='normal')
    else:
        CE_List_No_Entry.config(state='disabled')
        FIM_List_No_Entry.config(state='disabled')
        DIE_List_No_Entry.config(state='disabled')
        CE_List.set("")
        FIM_List.set("")
        DIE_List.set("")
        output1.config(text="")
        output2.config(text="") 
        output3.config(text="") 
    
        
def Update_FIM_DIE():

    Value_Sel= Value_Input.get()
    List_Sel = List_Input.get()
    Range_Sel= Range_Input.get()
	
    global ce_list_final, fim_list_final,die_list_final
	
    if Value_Sel ==1 and List_Sel==0 and Range_Sel==0: 
        
        ce = CE_No_Entry.get()
        fim = FIM_No_Entry.get()
        die = DIE_No_Entry.get()
        #global fim_list_final,die_list_final
        ce_list_final = []
        fim_list_final = []
        die_list_final = []
        ce_list_final.append(fim)
        fim_list_final.append(fim)
        die_list_final.append(die)
        output1.config(text="Entered CE : "+str(ce))
        output2.config(text="Entered FIM : "+str(fim))
        output3.config(text="Entered DIE : "+ str(die))
        
   
    
    if Value_Sel ==0 and List_Sel==0 and Range_Sel==1: 
        
        ce_start = Start_CE_No_Entry.get()
        ce_end = End_CE_No_Entry.get()
        fim_start = Start_FIM_No_Entry.get()
        fim_end = End_FIM_No_Entry.get()
        die_start = Start_DIE_No_Entry.get()
        die_end= End_DIE_No_Entry.get()
        #global fim_list_final,die_list_final
        ce_list_final = range(int(ce_start),int(ce_end)+1)
        fim_list_final = range(int(fim_start),int(fim_end)+1)
        die_list_final = range(int(die_start),int(die_end)+1)
        output1.config(text="Entered CE range : "+str(ce_start)+" to "+str(ce_end))
        output2.config(text="Entered FIM range : "+str(fim_start)+" to "+str(fim_end))
        output3.config(text="Entered DIE range : "+str(die_start)+" to "+str(die_end))
        #for fim in fim_list_final:
            #for die in die_list_final:
               #print (fim,die)
        
    
    if Value_Sel ==0 and List_Sel==1 and Range_Sel==0: 

        #global fim_list_final,die_list_final
        ce_list_final = str(CE_List_No_Entry.get()).split(",")
        fim_list_final = str(FIM_List_No_Entry.get()).split(",")
        die_list_final = str(DIE_List_No_Entry.get()).split(",")
    
        output1.config(text="Entered CE list : "+str(ce_list_final))
        output2.config(text="Entered FIM list : "+str(fim_list_final))
        output3.config(text="Entered DIE list : "+str(die_list_final))
        #for fim in fim_list_final:
            #for die in die_list_final:
               #print (fim,die)
        


        
Label(root, text = "Select Entry Type :").grid(row=7,column=0, sticky=W)        


Checkbutton(root, text="Value", variable=Value_Input, onvalue = 1, offvalue = 0,command=Update_Entry_Type).grid(row=7,column = 1, sticky=W)
Checkbutton(root, text="Range", variable=Range_Input, onvalue = 1, offvalue = 0,command=Update_Entry_Type).grid(row=7,column = 2, sticky=W)
Checkbutton(root, text="List", variable=List_Input, onvalue = 1, offvalue = 0,command=Update_Entry_Type).grid(row=7, column = 3,sticky=W)

submit_button = Button(root,text="Submit",padx=10,pady=3,command=Update_FIM_DIE).grid(row=40,column=1,columnspan=2,padx=5,pady=2,sticky="W")

fetch_button = Button(root,text="Fetch Wafer Lot Data",padx=10,pady=3,command=get_wafer_lot).grid(row=40,column=3,columnspan=2,padx=5,pady=2,sticky="W")








mainloop()