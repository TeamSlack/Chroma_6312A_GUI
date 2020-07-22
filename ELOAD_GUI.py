import pyvisa, os, time
from ELOAD_command import *
import threading
import tkinter as tk
from tkinter import Button
from tkinter import Entry
from tkinter import Label
from tkinter import LabelFrame
from tkinter import Scale
from tkinter import IntVar, StringVar, DoubleVar
from tkinter import Radiobutton
from tkinter import ttk
from tkinter import Scale
from tkinter import messagebox
from tkinter import PhotoImage

#define control
ONstate = 'normal'
OFFstate = 'disabled'
static_geometry = "550x370"
dynamic_geometry = "1150x370"
L1defaultstring = "Current L1 (A):"
L2defaultstring = "Current L2 (A):"
L1CVstring = "Voltage L1 (V)"
L2CVstring = "Voltage L2 (V)"
startupVal = 0.0
CCDrise_default = "Rise (mA/us)"
CCDfall_default = "Fall (mA/us)"
CCDrise_H = "Rise (A/us)"
CCDfall_H = "Fall (A/us)"
dynConfigImg = "dynamic.gif"

def check_current():
    global levelup

    L1curr = L1SetVal.get()
    L2curr = L2SetVal.get()
    levelup = False #if remain in CCL
    
    if L1curr > 6 or L2curr > 6:
        checkCurr = messagebox.askyesno("Warning!", "Current is > CCL limit, change to CCH?")
        if checkCurr == True:
            levelup = True #to check if change to CCH instead
        else:
            levelup = False
            if L1curr >= 6:
                L1curr = 6.0000
                L1SetVal.set(6.0000)
            if L2curr >= 6:
                L2curr = 6.0000
                L2SetVal.set(6.0000)
            
    return [L1curr,L2curr]

def check_voltage():
    
    L1Volt = L1SetVal.get()
    L2Volt = L2SetVal.get()
    
    if L1Volt > 80 or L2Volt > 80:
        messagebox.showwarning("Warning!", "Voltage is > ELOAD limit, limiting to max value")
        if L1Volt > 80:
            L1Volt = 80.0000
            L1SetVal.set(80.0000)
        if L2Volt > 80:
            L2Volt = 80.0000
            L2SetVal.set(80.0000)
            
    return [L1Volt,L2Volt]

def check_dynamic_config():
    global levelup
    
    T1 = TL1.get()
    T2 = TL2.get()
    Rise = slewRise.get()
    Fall = slewFall.get()
    
    if T1 <= 0 or T2 <= 0:
        messagebox.showwarning("Warning!", "T1 or T2 value is < lower limit, will set to min value")
        if T1 <= 0:
            T1 = 0.025
            TL1.set(0.025)
        if T2 <= 0:
            T2 = 0.025
            TL2.set(0.025)
    
    if Rise <= 0 or Fall <= 0:
        messagebox.showwarning("Warning!", "Rise or Fall value is < lower limit, will set to min value")
        if Rise <= 0:
            if levelup == True:
                Rise = 0.01
                slewRise.set(0.01)
            else:
                Rise = 1
                slewRise.set(1)
        if Fall <= 0:
            if levelup == True:
                Fall = 0.01
                slewFall.set(0.01)
            else:
                Fall = 1
                slewFall.set(1)
    
    return [T1,T2,Rise,Fall]

def load_Ports():
    sel_Port["values"] = Chroma_6312A.get_port_list()
    
def open_Conn():
    if sel_Port.current() is not -1:
        try:
            port_name = sel_Port.get()
            #INFO: USB = ASRLxx where xx is port number
            Chroma_6312A.connect(port_name)
            connVal.set("Connected")
            stat_etry.config(background='green',foreground='white')
            disConn_but.config(state=ONstate)
            chnl_One.config(state=ONstate)
            chnl_Two.config(state=ONstate)
            chnl_Three.config(state=ONstate)
            chnl_Four.config(state=ONstate)
            CCS_but.config(state=ONstate,relief='sunken')
            CCD_but.config(state=ONstate)
            output_but.config(state=ONstate)
            CCSstate.set("CCSL") #default app state is constant current - low
            CV_but.config(state=ONstate)
            CR_but.config(state=ONstate)
            ELOADmodeVal.set(1)
            L1Set_etry.config(state=ONstate)
            L2Set_etry.config(state=ONstate)
            L1Time_etry.config(state=OFFstate)
            L2Time_etry.config(state=OFFstate)
            L1slew_etry.config(state=OFFstate)
            L2slew_etry.config(state=OFFstate)
            L1configlbl.set(L1defaultstring)
            L2configlbl.set(L2defaultstring)
            L1Eloadlbl.set(L1defaultstring)
            L2Eloadlbl.set(L2defaultstring)
            CCDriselbl.set(CCDrise_default)
            CCDfalllbl.set(CCDfall_default)
            L1SetVal.set(startupVal)
            L2SetVal.set(startupVal)
            actL1Val.set(startupVal)
            actL2Val.set(startupVal)
            TL1.set(startupVal)
            TL2.set(startupVal)
            slewRise.set(startupVal)
            slewFall.set(startupVal)
            actT1Val.set(str(startupVal))
            actT2Val.set(startupVal)
            actRiseVal.set(startupVal)
            actFallVal.set(startupVal)
            
        
        except pyvisa.errors.VisaIOError:
            connVal.set("ELOAD not found")
            stat_etry.config(background='red',foreground='white')
    else:
        messagebox.showerror("Error", "Select a port first")
        
def dis_Conn():

    loadStat = loadValStr.get()
    if loadStat == 'LOAD ON':
        messagebox.showwarning("Warning","Turn OFF load first")
    else:
        Chroma_6312A.disconnect()
        connVal.set("Not Connected")
        CCSstate.set("CCS")
        stat_etry.config(background='yellow',foreground='black')
        output_but.config(background='red',foreground='white')
        #keep all buttons disabled while not connected to avoid app erros
        disConn_but.config(state=OFFstate)
        chnl_One.config(state=OFFstate)
        chnl_Two.config(state=OFFstate)
        chnl_Three.config(state=OFFstate)
        chnl_Four.config(state=OFFstate)
        output_but.config(state=OFFstate)
        L1Set_etry.config(state=OFFstate)
        L2Set_etry.config(state=OFFstate)
        L1Time_etry.config(state=OFFstate)
        L2Time_etry.config(state=OFFstate)
        L1slew_etry.config(state=OFFstate)
        L2slew_etry.config(state=OFFstate)
        CCDriselbl.set(CCDrise_default)
        CCDfalllbl.set(CCDfall_default)
        CCS_but.config(state=OFFstate,relief='raised')
        CCD_but.config(state=OFFstate,relief='raised')
        CV_but.config(state=OFFstate,relief='raised')
        CR_but.config(state=OFFstate,relief='raised')
        App.geometry(static_geometry)

def modeSet(): #WIP
    global ticks
    if modeVal.get() == 1:
        ticks = threading.Timer(1,tick_func)
        ticks.start()
        #print("tick timer started") #debug use
    
def chnlSel():
    Chroma_6312A.set_channel("CHAN " + str(chnlVal.get()))

def Eload_Mode(x):
    
    if loadValStr.get() == "LOAD ON":
        Chroma_6312A.load_state('OFF')
        loadValStr.set("LOAD OFF")
        output_but.config(background='red',foreground='white')
        
    if x == 1:
        ELOADmodeVal.set(1)
        CCS_but['relief']='sunken'
        CCD_but['relief']='raised'
        CCDstate.set("CCD")
        CV_but['relief']='raised'
        L1Time_etry.config(state=OFFstate)
        L2Time_etry.config(state=OFFstate)
        L1slew_etry.config(state=OFFstate)
        L2slew_etry.config(state=OFFstate)
        CCDriselbl.set(CCDrise_default)
        CCDfalllbl.set(CCDfall_default)
        L1configlbl.set(L1defaultstring)
        L2configlbl.set(L2defaultstring)
        L1Eloadlbl.set(L1defaultstring)
        L2Eloadlbl.set(L2defaultstring)
        App.geometry(static_geometry)
    elif x == 2:
        ELOADmodeVal.set(2)
        CCS_but['relief']='raised'
        CCD_but['relief']='sunken'
        CV_but['relief']='raised'
        CCSstate.set("CCS")
        CCDstate.set("CCDL")
        L1Time_etry.config(state=ONstate)
        L2Time_etry.config(state=ONstate)
        L1slew_etry.config(state=ONstate)
        L2slew_etry.config(state=ONstate)
        L1configlbl.set(L1defaultstring)
        L2configlbl.set(L2defaultstring)
        L1Eloadlbl.set(L1defaultstring)
        L2Eloadlbl.set(L2defaultstring)       
        App.geometry(dynamic_geometry)
    elif x == 3: #WIP
        ELOADmodeVal.set(3)
        CCS_but['relief']='raised'
        CCD_but['relief']='raised'
        CV_but['relief']='sunken'
        L1configlbl.set(L1CVstring)
        L2configlbl.set(L1CVstring)
        L1Eloadlbl.set(L1CVstring)
        L2Eloadlbl.set(L1CVstring)   
        App.geometry(static_geometry)
    elif x == 4: #WIP
        ELOADmodeVal.set(4)
        #set_eload_mode = "CR"
#         CCS_but['relief']='raised'
#         CCD_but['relief']='raised'
#         CV_but['relief']='sunken'
        App.geometry(static_geometry)
        
    #Chroma_6312A.set_load_mode(x)

    
def start_load():
    global ticks
    global levelup
    
    load_state = loadVal.get()
    ELOADmode = ELOADmodeVal.get()
    
    if load_state == 0:
        if ELOADmode == 1:
            L1Val,L2Val = check_current()
            if levelup == True:
                CCSstate.set("CCSH")
                Chroma_6312A.set_load_mode('CCL',levelup)
            else:
                CCSstate.set("CCSL")
                Chroma_6312A.set_load_mode('CCL',levelup)
        elif ELOADmode == 2:
            L1Val,L2Val = check_current()
            T1,T2,Rise,Fall = check_dynamic_config()
            if levelup == True:
                CCDriselbl.set(CCDrise_H)
                CCDfalllbl.set(CCDfall_H)
                CCDstate.set("CCDH")
                check_next = messagebox.askyesno("Warning!", "CCDH is set, reset T1, T2, RISE & FALL?")
                if check_next == True:
                    return None
                else:
                    Chroma_6312A.set_load_mode('CCDL',levelup)
                
            else:
                CCDriselbl.set(CCDrise_default)
                CCDfalllbl.set(CCDfall_default)
                CCDstate.set("CCDL")
                Chroma_6312A.set_load_mode('CCDL',levelup)
                
            Chroma_6312A.dynamic_config('write',T1,T2,Rise,Fall)
            actT1, actT2, actRise, actFall = Chroma_6312A.dynamic_config('read')
            
            actT1 = str(float(actT1)*1000) + "ms"
            actT2 = str(float(actT2)*1000) + "ms"
            if levelup == True:
                actRise = str(actRise) + "A/us"
                actFal = str(actFall) + "A/us"
            else:
                actRise = str(float(actRise)*1000) + "mA/us"
                actFall = str(float(actFall)*1000) + "mA/us"
        
            actT1Val.set(actT1)
            actT2Val.set(actT2)
            actRiseVal.set(actRise)
            actFallVal.set(actFall)
            
        elif ELOADmode == 3:
            L1Val,L2Val = check_voltage()

        loadVal.set(1)
        loadValStr.set("LOAD ON")
        output_but.config(background='green',foreground='white')
        
        time.sleep(0.5) #short delay for stability
        
        Chroma_6312A.config_output('write', L1Val, L2Val)
        actL1val,actL2val = Chroma_6312A.config_output('read')
        actL1Val.set(actL1val)
        actL2Val.set(actL2val)
        Chroma_6312A.load_state('ON')
        modeSet()
    else:
        loadVal.set(0)
        loadValStr.set("LOAD OFF")
        ticks.cancel()
        output_but.config(background='red',foreground='white')
        Chroma_6312A.load_state("OFF")

#INFO: read ELOAD measured value every 1 second & update on app
def tick_func():
    global ticks
    
    ELOADcurrVal,ELOADvoltVal = Chroma_6312A.read_load(4)

    if len(ELOADcurrVal) < 6:
        ELOADcurrVal = ELOADcurrVal.ljust(6,'0')
    if len(ELOADvoltVal) < 6:
        ELOADvoltVal = ELOADvoltVal.ljust(6,'0')

    currVal.set(ELOADcurrVal[:6])
    voltVal.set(ELOADvoltVal[:6])
    
    ticks.cancel()
    #print(ELOADcurrVal, ELOADvoltVal) #debug use
    modeSet() 
        
def on_closing():
    loadStat = loadValStr.get()
    if loadStat == 'LOAD ON':
        messagebox.showwarning("Warning","Turn OFF load first")
    else:
        try:
            ticks.cancel()
            Chroma_6312A.disconnect()
            App.destroy()
        except:
            App.destroy()
    
#top level tkinter config
App = tk.Tk()
App.geometry(static_geometry)
#App.geometry(dynamic_geometry)
App.title("ELOAD GUI")

Chroma_6312A = ELOAD()

#variables grouping
chnlVal = IntVar()
modeVal = IntVar()
loadVal = IntVar()
ELOADmodeVal = IntVar()
L1SetVal = DoubleVar()
L2SetVal = DoubleVar()
actL1Val = DoubleVar()
actL2Val = DoubleVar()
actT1Val = StringVar()
actT2Val = StringVar()
actRiseVal = StringVar()
actFallVal = StringVar()
TL1 = DoubleVar()
TL2 = DoubleVar()
slewRise = DoubleVar()
slewFall = DoubleVar()
L1configlbl = StringVar()
L2configlbl = StringVar()
L1Eloadlbl = StringVar()
L2Eloadlbl = StringVar()
CCDriselbl = StringVar()
CCDfalllbl = StringVar()
connVal = StringVar()
CCSstate = StringVar()
CCDstate = StringVar()
currVal = DoubleVar()
voltVal = DoubleVar()
loadValStr = StringVar()

chnlVal.set(1)
modeVal.set(1)
loadVal.set(0)
connVal.set("Not Connected")
loadValStr.set("LOAD OFF")
L1configlbl.set(L1defaultstring)
L2configlbl.set(L2defaultstring)
L1Eloadlbl.set(L1defaultstring)
L2Eloadlbl.set(L2defaultstring)
CCDriselbl.set(CCDrise_default)
CCDfalllbl.set(CCDfall_default)
CCSstate.set("CCS")
CCDstate.set("CCD")

#Connection grouping
frame_Conn = LabelFrame(App, text = "Device Configuration")
port_lbl = Label(frame_Conn, width = 4, height=1, text = "Ports:")
stat_lbl = Label(frame_Conn, width = 4, height=1, text = "Status:")
sel_Port = ttk.Combobox(frame_Conn, width = 15, postcommand = load_Ports)
testConn_but = Button(frame_Conn,text="Connect",command=open_Conn,width = 10,height = 1)
disConn_but = Button(frame_Conn,text="Disconnect",command=dis_Conn,width = 10,height = 1)
stat_etry = Entry(frame_Conn,width = 18,textvariable=connVal, justify = 'center',background='yellow',foreground='black')

disConn_but.config(state='disabled')
frame_Conn.place(x=10)
port_lbl.grid(row=0,column=0, padx = 2, pady = 5)
sel_Port.grid(row=0,column=1, padx = 5, pady = 5)
stat_lbl.grid(row=1,column=0, padx = 2, pady = 5)
stat_etry.grid(row=1, column=1, padx = 5, pady = 5)
testConn_but.grid(row=2, column=0, padx = 2, pady = 5)
disConn_but.grid(row=2, column=1, padx = 2, pady = 5)

frame_Mode = LabelFrame(frame_Conn, text = "App mode (WIP)")
mode_auto = Radiobutton(frame_Mode, text = "Auto", variable = modeVal, value = 1, width = 20, height = 1,command=modeSet)
mode_manual = Radiobutton(frame_Mode, text = "Manual", variable = modeVal, value = 2, width = 20, height = 1,command=modeSet)
frame_Mode.grid(row=4,columnspan=2)
mode_auto.grid(row=0, columnspan=2,padx = 5, pady = 5)
mode_manual.grid(row=1, columnspan=2,padx = 5, pady = 5)

#mode_auto.config(state='disabled')
mode_manual.config(state='disabled')

#ELoad Information & control grouping
frame_ELOAD = LabelFrame(App, text="ELOAD Interface")
frame_Meas = LabelFrame(frame_ELOAD, text="ELOAD Measured Values")
curr_lbl = Label(frame_Meas, width=10, height=1,text = "Current (A):")
volt_lbl = Label(frame_Meas, width=10, height=1,text = "Voltage (V):")
curr_etry = Entry(frame_Meas, width=8, textvariable=currVal,justify='center', state='disabled',disabledbackground='green',disabledforeground='white')
volt_etry = Entry(frame_Meas, width=8, textvariable=voltVal,justify='center', state='disabled',disabledbackground='green',disabledforeground='white')

##Measured & set current display
frame_ELOAD.place(x=225)
frame_Meas.grid(row=0)
curr_lbl.grid(row=0,column=0,padx=5,pady=1)
volt_lbl.grid(row=1,column=0,padx=5,pady=1)
curr_etry.grid(row=0,column=1,padx=5,pady=1)
volt_etry.grid(row=1,column=1,padx=5,pady=1)

##actual current set at ELOAD
frame_currSet = LabelFrame(frame_ELOAD, text="Actual ELOAD Set Values")
actL1Set_lbl = Label(frame_currSet, width=10, height=1,textvariable = L1Eloadlbl)
actL2Set_lbl = Label(frame_currSet, width=10, height=1,textvariable = L2Eloadlbl)
actL1Set_etry = Entry(frame_currSet, width=8, textvariable=actL1Val,justify='center',state='disabled',disabledbackground='green',disabledforeground='white')
actL2Set_etry = Entry(frame_currSet, width=8, textvariable=actL2Val,justify='center',state='disabled',disabledbackground='green',disabledforeground='white')

frame_currSet.grid(row=0,column=1)
actL1Set_lbl.grid(row=0,column=0,padx=5,pady=1)
actL2Set_lbl.grid(row=1,column=0,padx=5,pady=1)
actL1Set_etry.grid(row=0,column=1,padx=5,pady=1)
actL2Set_etry.grid(row=1,column=1,padx=5,pady=1)

##used to set current
frame_currSet = LabelFrame(frame_ELOAD, text="Configure ELOAD Here")
L1Set_lbl = Label(frame_currSet, width=10, height=1,textvariable = L1configlbl)
L2Set_lbl = Label(frame_currSet, width=10, height=1,textvariable = L2configlbl)
L1Set_etry = Entry(frame_currSet, width=8, textvariable=L1SetVal,justify='center')
L2Set_etry = Entry(frame_currSet, width=8, textvariable=L2SetVal,justify='center')

frame_currSet.grid(row=1,column=0,sticky='N')
L1Set_lbl.grid(row=0,column=0,padx=5,pady=1)
L2Set_lbl.grid(row=1,column=0,padx=5,pady=1)
L1Set_etry.grid(row=0,column=1,padx=5,pady=1)
L2Set_etry.grid(row=1,column=1,padx=5,pady=1)

L1Set_etry.config(state=OFFstate)
L2Set_etry.config(state=OFFstate)

##used to set dynamic current parameters
frame_dynSet = LabelFrame(frame_ELOAD, text="CCD settings")
L1Time_lbl = Label(frame_dynSet, width=10, height=1,text = "T1 (ms):")
L2Time_lbl = Label(frame_dynSet, width=10, height=1,text = "T2 (ms):")
L1slew_lbl = Label(frame_dynSet, width=10, height=1,textvariable = CCDriselbl)
L2slew_lbl = Label(frame_dynSet, width=10, height=1,textvariable = CCDfalllbl)
L1Time_etry = Entry(frame_dynSet, width=8, textvariable=TL1,justify='center')
L2Time_etry = Entry(frame_dynSet, width=8, textvariable=TL2,justify='center')
L1slew_etry = Entry(frame_dynSet, width=8, textvariable=slewRise,justify='center')
L2slew_etry = Entry(frame_dynSet, width=8, textvariable=slewFall,justify='center')

frame_dynSet.grid(row=1,column=1)
L1Time_lbl.grid(row=0,column=0,padx=5,pady=1)
L2Time_lbl.grid(row=1,column=0,padx=5,pady=1)
L1slew_lbl.grid(row=2,column=0,padx=5,pady=1)
L2slew_lbl.grid(row=3,column=0,padx=5,pady=1)
L1Time_etry.grid(row=0,column=1,padx=5,pady=1)
L2Time_etry.grid(row=1,column=1,padx=5,pady=1)
L1slew_etry.grid(row=2,column=1,padx=5,pady=1)
L2slew_etry.grid(row=3,column=1,padx=5,pady=1)

L1Time_etry.config(state=OFFstate)
L2Time_etry.config(state=OFFstate)
L1slew_etry.config(state=OFFstate)
L2slew_etry.config(state=OFFstate)

##Channel selection grouping
frame_Channel = LabelFrame(frame_ELOAD, text = "Channel Select")
chnl_One = Radiobutton(frame_Channel, text = "Channel 1", variable = chnlVal, value = 1, width = 10, height = 1,command=chnlSel)
chnl_Two = Radiobutton(frame_Channel, text = "Channel 2", variable = chnlVal, value = 2, width = 10, height = 1,command=chnlSel)
chnl_Three = Radiobutton(frame_Channel, text = "Channel 3", variable = chnlVal, value = 3, width = 10, height = 1,command=chnlSel)
chnl_Four = Radiobutton(frame_Channel, text = "Channel 4", variable = chnlVal, value = 4, width = 10, height = 1,command=chnlSel)

chnl_One.config(state=OFFstate)
chnl_Two.config(state=OFFstate)
chnl_Three.config(state=OFFstate)
chnl_Four.config(state=OFFstate)

frame_Channel.grid(row=2, rowspan=1, column=0)
chnl_One.grid(row=0, padx=25, pady = 1)
chnl_Two.grid(row=1, padx=25, pady = 1)
chnl_Three.grid(row=2, padx=25, pady = 1)
chnl_Four.grid(row=3, padx=25, pady = 1)

##ELOAD mode selection (WIP)
frame_currMode = LabelFrame(frame_ELOAD, text = "Mode Select (default = CC)")
CCS_but = Button(frame_currMode, textvariable=CCSstate, width = 8, height = 1,command=lambda:Eload_Mode(1))
CCD_but = Button(frame_currMode, textvariable=CCDstate, width = 8, height = 1,command=lambda:Eload_Mode(2))
CV_but = Button(frame_currMode, text = "CV", width = 10, height = 1,command=lambda:Eload_Mode(3))
CR_but = Button(frame_currMode, text = "CR (WIP)", width = 10, height = 1,command=lambda:Eload_Mode(4))
frame_currMode.grid(row=2,column=1,rowspan=1,sticky='N',padx=5)
CCS_but.grid(row=0,column=0,padx=5,pady=5)
CCD_but.grid(row=0,column=1,padx=5,pady=5)
CV_but.grid(row=1,columnspan=2,padx=34,pady=5)
CR_but.grid(row=2,columnspan=2,padx=34,pady=5)

output_but = Button(frame_ELOAD, textvariable=loadValStr, width = 15, height=1, command=start_load)
output_but.grid(row=3,columnspan=2,padx=5, pady=5)
output_but.config(background='red',foreground='white')

CCS_but.config(state=OFFstate)
CCD_but.config(state=OFFstate)
CV_but.config(state=OFFstate)
CR_but.config(state=OFFstate)
output_but.config(state=OFFstate)

#Dynamic setting frame
frame_dynMode = LabelFrame(App, text = "Dynamic mode visualizer")
dynWaveform = PhotoImage(file=dynConfigImg)
dynWaveformlbl = Label(frame_dynMode,image=dynWaveform)
dynWaveformlbl.image = dynWaveform #needed as reference
actTime1_etry = Entry(frame_dynMode, width=10, textvariable=actT1Val,justify='center')
actTime2_etry = Entry(frame_dynMode, width=10, textvariable=actT2Val,justify='center')
actRise_etry = Entry(frame_dynMode, width=10, textvariable=actRiseVal,justify='center')
actFall_etry = Entry(frame_dynMode, width=10, textvariable=actFallVal,justify='center')

frame_dynMode.place(x=550)
dynWaveformlbl.grid(row=1, column=1, rowspan=4, columnspan=4)
actTime1_etry.grid(row=2,column=0,padx=5,pady=1,sticky='S')
actTime2_etry.grid(row=3,column=0,padx=5,pady=1)
actRise_etry.grid(row=0,column=2,padx=5,pady=1)
actFall_etry.grid(row=0,column=3,padx=5,pady=1)

actTime1_etry.config(state=OFFstate)
actTime2_etry.config(state=OFFstate)
actRise_etry.config(state=OFFstate)
actFall_etry.config(state=OFFstate)
#I_slider = Scale(App,from_=100, to=0, orient=tk.VERTICAL)
#I_slider.set(50)
#I_slider.grid(column = 2)

##Protocol control
#WIP
# currL1Set_etry.bind("<Enter>",on_enter(1))
# currL2Set_etry.bind("<Enter>",on_enter(2))
# currL1Set_etry.bind("<Leave>",on_leave(1))
# currL2Set_etry.bind("<Leave>",on_leave(2))
App.protocol("WM_DELETE_WINDOW", on_closing)

App.mainloop()
