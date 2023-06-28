import tkinter as tk
from tkinter import filedialog
import time

class textSeq:
    
    def __init__(self, mainFrame,cmdSet):
        self.sett1Val=0
        self.sett2Val=0
        self.riseVal=0
        self.fallVal=0
        self.T1Val=0
        self.T2Val=0
        self.duration=0
        self.mode="CCL"
        self.chl="CHAN 1"
        self.mainFrame = mainFrame
        self.cmd = cmdSet
        self.steps=0.0;
        
    def getVals(self,txtBox,duration=1):
        self.mode = self.cmd.mode
        self.chnl = self.cmd.chnl
        self.duration=duration
        self.sett1Val = self.mainFrame.sett1Val.get()
        self.sett2Val = self.mainFrame.sett2Val.get()
        #if self.cmd.dynstate == False:
        if self.cmd.currstate == True or self.cmd.resstate == True:
            self.riseVal = self.mainFrame.riseVal.get()
            self.fallVal = self.mainFrame.fallVal.get()
            if self.cmd.dynstate == False:
                self.Vals = "{};{};{};{};{};{};{}".format(self.mode,self.chnl,self.sett1Val,self.sett2Val,self.riseVal,self.fallVal,self.duration)
            else:
                self.T1Val = self.mainFrame.T1Val.get()
                self.T2Val = self.mainFrame.T2Val.get()                
                self.Vals = "{};{};{};{};{};{};{};{};{}".format(self.mode,self.chnl,self.sett1Val,self.sett2Val,self.riseVal,self.fallVal,self.T1Val,self.T2Val,self.duration)
        else:   
            self.Vals = "{};{};{};{};{}".format(self.mode,self.chnl,self.sett1Val,self.sett2Val,self.duration)
        
        txtBox.insert(tk.INSERT, self.Vals+'\n')
        self.steps+=1.0
        print(self.steps)
        
    def remVals(self,txtBox):
        txtBox.delete(self.steps,tk.END)
        if self.steps > 0:
            self.steps-=1.0
        #stop newline insertion at 1st line
        if self.steps > 1.0:
            txtBox.insert(tk.INSERT, '\n')
        print(self.steps)
            
    def runSeq(self,txtBox):
        strtIdx=1.0
        endIdx = ""
        duration = 0.0
        cmdStringlen = 0
        while(strtIdx < self.steps+1):
            endIdx="{} lineend".format(strtIdx)
            print(txtBox.get(strtIdx,endIdx)) #debug
            cmdString = txtBox.get(strtIdx,endIdx).split(';')
            print(cmdString, len(cmdString)) #debug
            
            #breakdown the command for device setting
            self.cmd.set_load_state('OFF')
            self.cmd.set_mode(cmdString[0],1)
            self.cmd.set_channel(cmdString[1],1)
            cmdStringlen = len(cmdString)
            if cmdStringlen > 7: #for dynamic
                self.cmd.set_T_val(float(cmdString[6]),float(cmdString[7]))
            if cmdStringlen > 5: #for CC & CR
                self.cmd.set_slew_val(cmdString[0],float(cmdString[4]),float(cmdString[5]))
            #CV will come here
            self.cmd.set_load_val(cmdString[0],float(cmdString[2]),float(cmdString[3]))
            self.cmd.set_load_state('ON')            
            duration = float(cmdString[cmdStringlen-1])*1    
            strtIdx += 1.0
            print(time.strftime("%M:%S",time.gmtime()))
            time.sleep(duration)
        self.cmd.set_load_state('OFF')
        
    def saveSeq(self,txtBox,app):
        strtIdx=1.0
        endIdx = ""
        
        seqSaveFile = filedialog.asksaveasfile(mode='w+', defaultextension=".txt", filetypes=(("text","*.txt"),("all files","*.*")))
        if seqSaveFile is None:  
            pass
        else:
            while(strtIdx < self.steps+1):
                endIdx="{} lineend".format(strtIdx)
                cmdString = txtBox.get(strtIdx,endIdx)
                print(cmdString)
                seqSaveFile.write(cmdString+'\n')
                strtIdx += 1.0
            seqSaveFile.close()
            
    def openSeq(self,txtBox,app):
        
        seqLoadFile = filedialog.askopenfile(mode='r', filetypes=(("text","*.txt"),("all files","*.*")))
        if seqLoadFile is None:
            pass
        else:
            cmdStringArray = seqLoadFile.readlines()
            print(cmdStringArray)
        seqLoadFile.close()
        
        for cmds in cmdStringArray:
            txtBox.insert(tk.INSERT,cmds)
            self.steps+=1.0
        
