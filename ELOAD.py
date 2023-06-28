import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ELOAD_SCPI import *
from ELOAD_SEQ import *

class portSelectPanel(tk.Frame):
    def __init__(self, app, mainPanel, xtraPanel, geometryLst, cmdset):
        tk.Frame.__init__(self,app)
        self.app = app
        self.cmd = cmdset
        self.geometryLst = geometryLst
        self.mainPanel = mainPanel
        self.xtraPanel = xtraPanel
        self.portFrame = tk.LabelFrame(self, text="Eload Setup")
        self.portFrame.grid(row=0,column=0, padx=5)
        
        #Labels
        self.portLbl = tk.Label(self.portFrame, text="Select port: ", height=1)
        self.portLbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        #Combobox
        self.portCombo = ttk.Combobox(self.portFrame, width=15, postcommand=self.get_port_list)
        self.portCombo.grid(row=0, column=1, padx=5, pady=5)
        
        #Buttons
        self.connPort = tk.Button(self.portFrame, text="Connect", height=1, width=8, command=self.open_port)
        self.connPort.grid(row=0, column=2, padx=5, pady=5)
        
        self.disconnPort = tk.Button(self.portFrame, text="Disconnect", height=1, width=8, command=self.close_port)
        self.disconnPort.grid(row=0, column=3, padx=5, pady=5)
        
        self.disconnPort['state'] = 'disabled'
        
        self.mainPanel.modeSelect('CCL',0)
        
    def get_port_list(self):
        self.portCombo['values'] = self.cmd.list_ports()
        
    def open_port(self):
        if self.portCombo.current() != -1:
            self.cmd.connect(self.portCombo.get())
            self.mainPanel.modeSelect('CCL',0)
            self.xtraPanel.checkEloadVals()
            self.disconnPort['state'] = 'normal'
            self.portCombo['state'] = 'disabled'
        else:
            messagebox.showinfo("Incomplete configurtion", "Select a port & ELOAD config first")
                
    def close_port(self):
        self.portCombo['state'] = 'normal'
        ongoing_sched = self.app.tk.call('after','info')
        #cancel ongoing 'after' schedule
        if ongoing_sched != "":
            self.app.after_cancel(ongoing_sched)
        self.cmd.disconnect()
        
#For functions on the invidiual ELOAD modules
class ELOADSub(tk.Frame):   
    def __init__(self, app, cmdset, mainPanel):
        tk.Frame.__init__(self,app)
        self.cmd = cmdset
        self.mainPanel = mainPanel
        self.SubFrame = tk.LabelFrame(self, text="ELOAD Sub")
        self.SubFrame.grid(row=0,column=0, padx=2)
        
        #Variables
        self.loadState = tk.StringVar()
        self.readVVal = tk.DoubleVar()
        self.readIVal = tk.DoubleVar()
        self.loadState.set("LOAD OFF")
        
        #Labels
        self.volt = tk.Label(self.SubFrame, text="V: ", height=1)
        self.volt.grid(row=0, column=0, padx=5, pady=5)
        
        self.curr = tk.Label(self.SubFrame, text="A: ", height=1)
        self.curr.grid(row=1, column=0, padx=5, pady=5)
        
        #Entries
        self.voltEtry = tk.Entry(self.SubFrame, textvariable=self.readVVal, width=10, justify='center', state='disabled')
        self.voltEtry.grid(row=0, column=1, padx=5, pady=5)
        
        self.currEtry = tk.Entry(self.SubFrame, textvariable=self.readIVal, width=10, justify='center', state='disabled')
        self.currEtry.grid(row=1, column=1, padx=5, pady=5)
        
        #Buttons
        self.AB = tk.Button(self.SubFrame, text="A/B", height=1, width=5, command=lambda: self.A_B())
        self.AB.grid(row=2, column=0, padx=5, pady=5)
        
        self.outputBut = tk.Button(self.SubFrame, textvariable=self.loadState, height=1, width=8, command=self.configLoadState)
        self.outputBut.grid(row=2, column=1, padx=5, pady=5)
        
    def configLoadState(self):
        if self.outputBut['relief'] == 'sunken':
            self.outputBut['relief'] = 'raised'
            self.cmd.set_load_state('OFF')
            self.loadState.set('LOAD OFF')
            for button in self.mainPanel.buttonList:
                button['state'] = 'normal'
        else:
            for button in self.mainPanel.buttonList:
                button['state'] = 'disabled'
            self.outputBut['relief'] = 'sunken'
            self.cmd.set_load_state('ON')
            self.loadState.set('LOAD ON')
            
    def A_B(self):
        if self.AB['relief']=="raised":
            self.AB['relief']="sunken"
            self.cmd.ABState('B')
            self.cmd.setOutAB()
        else:
            self.AB['relief']="raised"
            self.cmd.ABState('A')
            self.cmd.setOutAB()

#For main functions on the ELOAD control module
class ELOADMain(tk.Frame):
    def __init__(self, app, cmdSet, geometryLst):
        tk.Frame.__init__(self,app)
        self.MainFrame = tk.LabelFrame(self, text="ELOAD Main")
        self.MainFrame.grid(row=0, column=0, padx=5)
        
        #Variable definition
        self.app = app
        self.cmd = cmdSet
        self.geometryLst = geometryLst
        self.sett1lbl = tk.StringVar()
        self.sett2lbl = tk.StringVar()
        self.riselbl = tk.StringVar()
        self.falllbl = tk.StringVar()        
        self.riseVal = tk.DoubleVar()
        self.fallVal = tk.DoubleVar()
        self.sett1Val = tk.DoubleVar()
        self.sett2Val = tk.DoubleVar()
        self.T1Val = tk.DoubleVar()
        self.T2Val = tk.DoubleVar()
        self.modeVal = tk.StringVar()
        self.chnlVal = tk.IntVar()
        self.chnlVal.set(1)
        self.modeVal.set('CCL')
        
        #Labels
        self.sett1 = tk.Label(self.MainFrame, textvariable=self.sett1lbl, height=1)
        self.sett1.grid(row=0, column=0, padx=5, pady=2)
        
        self.sett2 = tk.Label(self.MainFrame, textvariable=self.sett2lbl, height=1)
        self.sett2.grid(row=1, column=0, padx=5, pady=2)
        
        self.T1 = tk.Label(self.MainFrame, text='T1 (ms): ', height=1)
        self.T2 = tk.Label(self.MainFrame, text='T2 (ms): ', height=1)
        self.rise = tk.Label(self.MainFrame, textvariable=self.riselbl, height=1)
        self.fall = tk.Label(self.MainFrame, textvariable=self.falllbl, height=1)
        
        #Entries
        self.sett1Etry = tk.Entry(self.MainFrame, textvariable=self.sett1Val, width=10, justify='center')
        self.sett1Etry.grid(row=0, column=1, padx=5, pady=2)
        
        self.sett2Etry = tk.Entry(self.MainFrame, textvariable=self.sett2Val, width=10, justify='center')
        self.sett2Etry.grid(row=1, column=1, padx=5, pady=2)
        
        self.T1Etry = tk.Entry(self.MainFrame, textvariable=self.T1Val, width=10, justify='center')
        self.T2Etry = tk.Entry(self.MainFrame, textvariable=self.T2Val, width=10, justify='center')
        self.riseEtry = tk.Entry(self.MainFrame, textvariable=self.riseVal, width=10, justify='center')
        self.fallEtry = tk.Entry(self.MainFrame, textvariable=self.fallVal, width=10, justify='center')
        
        self.miscWidgetList = [self.T1, self.T2, self.T1Etry, self.T2Etry, self.rise, self.fall, self.riseEtry, self.fallEtry]

        #Sub Frames
        self.chnlFrame = tk.LabelFrame(self.MainFrame, text="CHAN")
        self.chnlFrame.grid(row=4, column=0, sticky=tk.N)
        
        self.modeFrame = tk.LabelFrame(self.MainFrame, text="MODE")
        
        #Buttons
        self.setVal = tk.Button(self.MainFrame, text="Set", height=5, width=3, command=lambda: self.setEloadVal())
        
        self.CCLmode = tk.Button(self.modeFrame, text="CCL", height=1, width=5, command=lambda: self.modeSelect('CCL',0))
        self.CCLmode.grid(row=0, column=0, padx=5, pady=5)
        
        self.CCHmode = tk.Button(self.modeFrame, text="CCH", height=1, width=5, command=lambda: self.modeSelect('CCH',1))
        self.CCHmode.grid(row=1, column=0, padx=5, pady=5)
                
        self.CCDLmode = tk.Button(self.modeFrame, text="CCDL", height=1, width=5, command=lambda: self.modeSelect('CCDL',2))
        self.CCDLmode.grid(row=0, column=1, padx=5, pady=5)

        self.CCHLmode = tk.Button(self.modeFrame, text="CCDH", height=1, width=5, command=lambda: self.modeSelect('CCDH',3))
        self.CCHLmode.grid(row=1, column=1, padx=5, pady=5)
        
        self.CVmode = tk.Button(self.modeFrame, text="CV", height=1, width=12, command=lambda: self.modeSelect('CV',4))
        self.CVmode.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        self.CRLmode = tk.Button(self.modeFrame, text="CRL", height=1, width=5, command=lambda: self.modeSelect('CRL',5))
        self.CRLmode.grid(row=3, column=0, padx=5, pady=5)
        
        self.CRHmode = tk.Button(self.modeFrame, text="CRH", height=1, width=5, command=lambda: self.modeSelect('CRH',6))
        self.CRHmode.grid(row=3, column=1, padx=5, pady=5)
        
        self.buttonList = [self.CCLmode, self.CCHmode, self.CCDLmode, self.CCHLmode, self.CVmode, self.CRLmode, self.CRHmode]
        
    def modeSelect(self, mode, butNo):
        self.modeVal.set(mode)
        if 'H' in mode or 'CR' in mode:
            self.riselbl.set('Rise (A/us): ')
            self.falllbl.set('Fall (A/us): ')
        else:
            self.riselbl.set('Rise (mA/s): ')
            self.falllbl.set('Fall (mA/s): ')
            
        if 'CC' in mode:
            self.cmd.CCstate(True)
            self.cmd.CRstate(False)
        elif 'CR' in mode:
            self.cmd.CRstate(True)
            self.cmd.CCstate(False)
        else:
            self.cmd.CCstate(False)
            self.cmd.CRstate(False)
            self.cmd.dynamicState(False)
        
        if 'CV' not in mode:
            if 'CC' in mode or 'CR' in mode:
                self.rise.grid(row=2, column=0, padx=5, pady=2)
                self.fall.grid(row=3, column=0, padx=5, pady=2)
                self.riseEtry.grid(row=2, column=1, padx=5, pady=2)
                self.fallEtry.grid(row=3, column=1, padx=5, pady=2)
                self.setVal.grid(row=0, column=2, rowspan=4, padx=5, pady=5)
                if 'D' in mode:
                    self.cmd.dynamicState(True)
                    if self.cmd.seqstate == False:
                        self.app.geometry(self.geometryLst[3])
                    else:
                        self.app.geometry(self.geometryLst[8])
                    self.T1.grid(row=2, column=2, padx=5, pady=2)
                    self.T2.grid(row=3, column=2, padx=5, pady=2)
                    self.T1Etry.grid(row=2, column=3, padx=5, pady=2)
                    self.T2Etry.grid(row=3, column=3, padx=5, pady=2)
                    self.modeFrame.grid(row=4, column=1, columnspan=4, sticky=tk.N)
                    self.setVal.grid(row=0, column=4, rowspan=4, padx=5, pady=5)
                    for button in self.buttonList:
                        if button['text'] == 'CV':
                            button['width'] = 33
                        else:
                            button['width'] = 15
                else:
                    self.cmd.dynamicState(False)
                    if self.cmd.seqstate == False:
                        self.app.geometry(self.geometryLst[1])
                    else:
                        self.app.geometry(self.geometryLst[7])
                    self.modeFrame.grid(row=4, column=1, columnspan=2, sticky=tk.N)
                    for widget in self.miscWidgetList[:4]:
                        widget.grid_forget()
                    for button in self.buttonList:
                        if button['text'] == 'CV':
                            button['width'] = 12
                        else:
                            button['width'] = 5
        else:
            if self.cmd.seqstate == False:
                self.app.geometry(self.geometryLst[2])
            else:
                self.app.geometry(self.geometryLst[9])
            self.setVal['height']=2
            for widget in self.miscWidgetList:
                widget.grid_forget()
            for button in self.buttonList:
                if button['text'] == 'CV':
                    button['width'] = 12
                else:
                    button['width'] = 5
                
        if self.buttonList[butNo]['relief'] == 'raised':
            self.buttonList[butNo]['relief'] = 'sunken'
            for button in self.buttonList:
                if button == self.buttonList[butNo]:
                    continue
                else:
                    button['relief'] = 'raised'
            self.sett1lbl.set("%s1 :" %mode)
            self.sett2lbl.set("%s2 :" %mode)
            self.cmd.set_mode(mode)
            
    def setEloadVal(self):
        msg1, msg2, msg3, msg4, msg5, msg6 = "","","","","",""
        mode = self.modeVal.get()
        if "CC" and "L" in mode: #considers CCL & CCDL modes
            if self.sett1Val.get() > 6.00:
                msg1 = "{} exceeds L setting limit, set to max value".format(self.sett1lbl.get())
                self.sett1Val.set(6.0000)
            if self.sett2Val.get() > 6.00:
                msg2 = "{} exceeds L setting limit, set to max value".format(self.sett2lbl.get())
                self.sett2Val.set(6.0000)
            if self.riseVal.get() > 100:
                msg3 = "{} exceeds rise setting limit, set to max value".format(self.riselbl.get())
                self.riseVal.set(100)
            if self.fallVal.get() > 100:
                msg4 = "{} exceeds fall setting limit, set to max value".format(self.falllbl.get())
                self.fallVal.set(100)
        elif mode == 'CV':
            if self.sett1Val.get() > 80.00:
                msg1 = "{} exceeds voltage setting limit, set to max value".format(self.sett1lbl.get())
                self.sett1Val.set(80.0000)
            if self.sett2Val.get() > 80.00:
                msg2 = "{} exceeds voltage setting limit, set to max value".format(self.sett2lbl.get())
                self.sett1Val.set(80.0000)
        elif mode == 'CRL':
            if self.sett1Val.get() > 100.00:
                msg1 = "{} exceeds resistance setting limit, set to max value".format(self.sett1lbl.get())
                self.sett1Val.set(100.0000)
            if self.sett2Val.get() > 100.00:
                msg2 = "{} exceeds voltage setting limit, set to max value".format(self.sett2lbl.get())
                self.sett1Val.set(100.0000)
            if self.riseVal.get() > 100:
                msg3 = "{} exceeds rise setting limit, set to max value".format(self.riselbl.get())
                self.riseVal.set(100)
            if self.fallVal.get() > 100:
                msg4 = "{} exceeds fall setting limit, set to max value".format(self.falllbl.get())
                self.fallVal.set(100)
        
        if "D" in mode: #considers only when in dynamic mode
            if self.T1Val.get() > 50000:
                msg4 = "T1 exceeds time setting limit, set to max value"
                self.T1Val.set(50000)
            if self.T2Val.get() > 50000:
                msg5 = "T2 exceeds time setting limit, set to max value"
                self.T2Val.set(50000)
            Tval1 = self.T1Val.get()
            Tval2 = self.T2Val.get()
            self.cmd.set_T_val(Tval1,Tval2)
            
        if mode != "CV": #considered in all modes except CV
            rise = self.riseVal.get()
            fall = self.fallVal.get()
            self.cmd.set_slew_val(mode,rise,fall)
        
        msgs = [msg1,msg2,msg3,msg4,msg5,msg6]
        msgStr = []
        for msg in msgs:
            if msg != "":
                msgStr.append(msg)
        msgStr = '\n'.join(msgStr)
        
        val1 = self.sett1Val.get()
        val2 = self.sett2Val.get()

        self.cmd.set_load_val(mode,val1,val2)

    
        if msgStr != "":
            messagebox.showinfo("FYI",msgStr)
            
        del msgs
        del msgStr
     

        
#For additional functions
class ELOADXtra(tk.Frame):
    def __init__(self, app, mainPanel, subPanelList, geometryLst, cmdSet, seqcmdSet, numOfPanels=1,):
        self.app = app
        self.mainPanel = mainPanel
        self.panelLst = subPanelList
        self.geometryLst = geometryLst
        self.cmd = cmdSet
        self.seqcmd = seqcmdSet
        self.numOfPanels = numOfPanels
        tk.Frame.__init__(self,app)
        self.AddFrame = tk.LabelFrame(self, text="Additional Functions")
        self.AddFrame.grid(row=0, column=0, padx=5)    
             
        #Buttons
        self.ExpOut = tk.Button(self.AddFrame, text="Exp", height=1, width=15, command=lambda : self.addFuncON(1))
        self.ExpOut.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.seqBut = tk.Button(self.AddFrame, text="Sequence", height=1, width=15, command=lambda : self.addFuncON(2))
        self.seqBut.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
    def addFuncOFF(self, mode):
        if mode == 1:
            self.ExpOut['relief'] = "raised"
            self.seqBut['state'] = "normal"
            self.destroyExpFrame()
            for button in self.mainPanel.buttonList:
                button['state'] = 'normal'
        elif mode == 2:
            self.seqBut['relief'] = "raised"
            self.ExpOut['state'] = "normal"
            self.cmd.seqState(False)
            self.destroySeqFrame()
            
        self.mainPanel.setVal['state'] = 'normal'
        
        if self.cmd.dynstate == False:
            if self.cmd.currstate == True or self.cmd.resstate == True:
                self.app.geometry(self.geometryLst[1])
            else:
                self.app.geometry(self.geometryLst[2])
        else:
            self.app.geometry(self.geometryLst[3])               

            
    def addFuncON(self, mode):
        self.mainPanel.setVal['state'] = 'disabled'
        if mode == 1:
            if self.ExpOut['relief'] == "raised":
                self.ExpOut['relief'] = "sunken"
                self.seqBut['state'] = "disabled"
                self.genExpFrame()
                if self.cmd.dynstate == True:
                        self.app.geometry(self.geometryLst[5])
                else:
                    if self.cmd.currstate == False and self.cmd.resstate == False:
                        self.app.geometry(self.geometryLst[6])
                    else:
                        self.app.geometry(self.geometryLst[4])                
                for button in self.mainPanel.buttonList:
                    button['state'] = 'disabled'    
            else:
                self.addFuncOFF(mode)
        elif mode == 2:
            if self.seqBut['relief'] == "raised":
                self.seqBut['relief'] = "sunken"
                self.ExpOut['state'] = "disabled"
                self.cmd.seqState(True)
                self.genSeqFrame()
                if self.cmd.dynstate == True:
                    self.app.geometry(self.geometryLst[8])
                else:
                    if self.cmd.currstate == False and self.cmd.resstate == False:
                        self.app.geometry(self.geometryLst[9])
                    else:
                        self.app.geometry(self.geometryLst[7])                
            else:
                self.addFuncOFF(mode)
                
    def genSeqFrame(self):
        self.seqFrame = tk.LabelFrame(self.app, text="Sequence")
        self.seqFrame.grid(row=1, rowspan=2, column=self.numOfPanels+2, padx=5, sticky=tk.N)
        
        #Variable definition
        self.duration = tk.DoubleVar() 
        self.duration.set(1.0)
        
        #label
        self.infolbl = tk.Label(self.seqFrame, bg="yellow", text="INFO ON FORMAT: \nSTEP: [MODE];[CHAN];[Sett1];[Sett2];[RISE];[FALL];[T1];[T2];[Duration]\no Set values at \"ELOAD MAIN\" panel\no RISE & FALL not in CV\no T1 & T2 only in dynamic mode\no Set duration at every step, default = 1min", justify="left", wraplength=370)
        self.infolbl.grid(row=0, column=0, columnspan=7)
        
        self.durationlbl = tk.Label(self.seqFrame, text="Duration(mins):", justify="left")
        self.durationlbl.grid(row=1, column=0, columnspan=3)
        
        #Textbox
        self.seqBox = tk.Text(self.seqFrame, height=10, width=30)
        self.seqBoxScroll = tk.Scrollbar(self.seqFrame, command=self.seqBox.yview, orient="vertical")
        self.seqBox.configure(yscrollcommand=self.seqBoxScroll.set)
        self.seqBox.grid(row=2, rowspan=6, column=0, columnspan=5)
        self.seqBoxScroll.grid(row=2,rowspan=6,column=5, sticky=tk.W, ipady=60)
        
        #Entries
        self.durationEtry = tk.Entry(self.seqFrame, textvariable=self.duration, width=10, justify='center')
        self.durationEtry.grid(row=1, column=3, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        #Buttons
        self.AddStp = tk.Button(self.seqFrame, text="+ Step", command=lambda: self.seqcmd.getVals(self.seqBox,self.duration.get()))
        self.AddStp.grid(row=2, column=6, padx=5, ipadx=19, pady=5,sticky=tk.W)
        
        self.RmvStp = tk.Button(self.seqFrame, text="- Step",command=lambda: self.seqcmd.remVals(self.seqBox))
        self.RmvStp.grid(row=3, column=6, padx=5, ipadx=20, pady=5, sticky=tk.W)
        
        self.StrtSeq = tk.Button(self.seqFrame, text="Run", bg='#97dc91', command=lambda: self.seqcmd.runSeq(self.seqBox))
        self.StrtSeq.grid(row=4, column=6, padx=5, ipadx=25, pady=5,sticky=tk.W)
        
        self.SaveSeq = tk.Button(self.seqFrame, text="Save",command=lambda: self.seqcmd.saveSeq(self.seqBox,self.app))
        self.SaveSeq.grid(row=5, column=6, padx=5, ipadx=24, pady=5, sticky=tk.W)
        
        self.OpenSeq = tk.Button(self.seqFrame, text="Load",command=lambda: self.seqcmd.openSeq(self.seqBox,self.app))
        self.OpenSeq.grid(row=6, column=6, padx=5, ipadx=24, pady=5, sticky=tk.W)
        
    def genExpFrame(self):
        self.ExpCtrlFrame = tk.LabelFrame(self.app, text="Exponential")
        self.ExpCtrlFrame.grid(row=1, rowspan=2, column=self.numOfPanels+2, padx=5, sticky=tk.N)
        
        #variables
        self.expButTxt = tk.StringVar()
        self.startCurrVal = tk.DoubleVar()
        self.endCurrVal = tk.DoubleVar()
        self.durationVal = tk.DoubleVar()
        self.expButTxt.set("Exponential OFF")
        
        #Labels
        self.startCurr = tk.Label(self.ExpCtrlFrame, text="Start current : ", height=1)
        self.startCurr.grid(row=0, column=0, padx=5, pady=5)
        
        self.endCurr = tk.Label(self.ExpCtrlFrame, text="End current  : ", height=1)
        self.endCurr.grid(row=1, column=0, padx=5, pady=5)
        
        self.duration = tk.Label(self.ExpCtrlFrame, text="Duration       : ", height=1)
        self.duration.grid(row=2, column=0, padx=5, pady=5)
        
        #Entries
        self.startCurrEtry = tk.Entry(self.ExpCtrlFrame, textvariable=self.startCurrVal, width=10, justify='center')
        self.startCurrEtry.grid(row=0, column=1, padx=5, pady=5)
        
        self.endCurrEtry = tk.Entry(self.ExpCtrlFrame, textvariable=self.endCurrVal, width=10, justify='center')
        self.endCurrEtry.grid(row=1, column=1, padx=5, pady=5)
        
        self.durationEtry = tk.Entry(self.ExpCtrlFrame, textvariable=self.durationVal, width=10, justify='center')
        self.durationEtry.grid(row=2, column=1, padx=5, pady=5)
        
        #Buttons
        self.ExpBut = tk.Button(self.ExpCtrlFrame, textvariable=self.expButTxt, height=1, width=20, command= lambda: self.triggerExpOut())
        self.ExpBut.grid(row=3, columnspan=2, column=0, padx=5, pady=5)
        
    def destroyExpFrame(self):
        widget_list = self.ExpCtrlFrame.grid_slaves()
        for widget in widget_list:
            widget.destroy()
        self.ExpCtrlFrame.destroy()
        
    def destroySeqFrame(self):
        widget_list = self.seqFrame.grid_slaves()
        for widget in widget_list:
            widget.destroy()
        self.seqFrame.destroy()
        
    def triggerExpOut(self):
        I_initial = self.startCurrVal.get()
        I_end = self.endCurrVal.get()
        t_end = self.durationVal.get()
        if I_initial != 0.0 and I_end != 0.0 and t_end != 0.0:
            if self.expButTxt.get() == 'Exponential OFF':
                self.cmd.expState(True)
                self.expButTxt.set("Exponential ON")
                self.ExpBut['relief'] = 'sunken'
                self.cmd.expOutput(I_initial, I_end, t_end)
                self.cmd.expState(False)
            else:
                self.cmd.expState(False)
                self.expButTxt.set("Exponential OFF")
                self.ExpBut['relief'] = 'raised'
                self.cmd.set_load_state('OFF')
        else:
            messagebox.showwarning("Warning!", "Start current, End current and Duration cannot be 0")
            
    def checkEloadVals(self):
        print("I'm here")
        print(self.panelLst)
        ELOADcurrVal,ELOADvoltVal = self.cmd.read_load(4)

        if len(ELOADcurrVal) < 6:
            ELOADcurrVal = ELOADcurrVal.ljust(6,'0')
        if len(ELOADvoltVal) < 6:
            ELOADvoltVal = ELOADvoltVal.ljust(6,'0')
        
        for panel in self.panelLst:
            print(panel, ELOADcurrVal, ELOADvoltVal) #debug use
            panel.readVVal.set(ELOADvoltVal[:6])
            panel.readIVal.set(ELOADcurrVal[:6])
        
        self.app.after(1000,lambda: self.checkEloadVals())

class genChnlBut:
    def __init__(self,chnlframe,cmdSet,rowNum,chanNum,chnlVariable):
        
        self.cmd = cmdSet
        self.value = chnlVariable
        self.chanStr = "CHAN %s" %str(chanNum)

        #self.chnlRad = tk.Radiobutton(chnlframe, text=self.chanStr, variable=self.value, value=chanNum, command=self.printVal_debug)
        self.chnlRad = tk.Radiobutton(chnlframe, text=self.chanStr, variable=self.value, value=chanNum, command=lambda: self.cmd.set_channel(self.chanStr))      
        self.chnlRad.grid(row=rowNum, column=0, padx=5, pady=5)
        
    #debug
    def printVal_debug(self):
        print(self.value.get())
        
#--------------------------------------Description-------------------------------------------------------
#CreatUI(Var 1, Var 2)
#Var 1: define the title for the app window
#Var 2: number of channels - for defining the number of channels on the ELOAD
    
def CreateUI(title, numOfChnls=1):

    def on_closing(panelLst,chnlLst, geoLst, cmdSet):
        #gets all running 'after' schedules
        ongoing_sched = app.tk.call('after','info')
        #cancel ongoing 'after' schedule
        if ongoing_sched != "":
            app.after_cancel(ongoing_sched)
        del panelLst
        del chnlLst
        del geoLst
        cmdSet.fulldisconnect()
        app.destroy()
        
    #---------------------------------Start of ELOAD GUI generation-------------------------------------
    #ELOADCMD = ELOAD()
    #ELOADCMD.ELOADconfig(numOfChnls)
    app = tk.Tk()
    app.title(title)
    #app.resizable(0,0)
    
    #app.geometry(ELOADCMD.geoList[2])
    
    #app.iconbitmap('conti_black_white.ico')

    MainPanel = ELOADMain(app, ELOADCMD, ELOADCMD.geoList)
    MainPanel.grid(row=1, rowspan=2, column=numOfChnls+1, sticky=tk.N)
    
    SEQCMD = textSeq(MainPanel,ELOADCMD)
       
    subPanelList = []
    for panel in range(numOfChnls):
        subPanelList.append(ELOADSub(app,ELOADCMD, MainPanel))
        subPanelList[panel].grid(row=1, column=panel, sticky=tk.N)
       
    XtraPanel = ELOADXtra(app, MainPanel, subPanelList, ELOADCMD.geoList, ELOADCMD, SEQCMD, numOfChnls)
    XtraPanel.grid(row=2, column=0, sticky=tk.N)
    
    radButList = []
    for chnls in range(1,numOfChnls+1):
        if chnls == 2 & numOfChnls == 2:
            chnls += 1
        radButList.append(genChnlBut(MainPanel.chnlFrame,ELOADCMD,chnls-1,chnls,MainPanel.chnlVal))
    
    portPanel = portSelectPanel(app, MainPanel, XtraPanel, ELOADCMD.geoList, ELOADCMD)
    portPanel.grid(row=0, column=0, columnspan=numOfChnls+2, sticky=tk.W)
    
    app.protocol("WM_DELETE_WINDOW", lambda: on_closing(subPanelList, radButList, ELOADCMD.geoList, ELOADCMD))

CreateUI("Chroma 6310A",2)

    
    
