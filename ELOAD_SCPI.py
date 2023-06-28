import pyvisa, time

class ELOAD:
    
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.dynamicState()
        self.CCstate()
        self.CRstate()
        self.expState()
        self.seqState()
        self.ABState()
        self.mode = 'CCL'
        self.chnl = 'CHAN 1'
        self.setStringA = ""
        self.setStringB = ""

    def list_ports(self):
        self.port_list = self.rm.list_resources()
        return(self.port_list)
    
    def connect(self,port_name,baudrate=9600):
        try:
            self.instrVISA = self.rm.open_resource(port_name)
            self.instrVISA.baud_rate = baudrate
            self.Write_command('CONF:REM ON')
        except:
            None
        print('connected')
        
    def disconnect(self):
        self.Write_command('CONF:REM OFF')
        self.set_load_state('OFF')
        try:
            self.instrVISA.close()
        except:
            None
            
    def fulldisconnect(self):
        self.disconnect()
        try:
            self.rm.close()
        except:
            None
        
#----------------------------------------General Write read command------------------------------------
    def Query_command(self,command):
        self.response=self.instrVISA.query(command)
        #print("Query command = ",self.instrVISA.query(command)) #[Debug only]
        return self.response

    def Write_command(self,command):
        try:
            self.instrVISA.write(command)
        except:
            None
        print("Write command =", command) #[Debug only]

#-----------------------------------------------Set command--------------------------------------------
    #bypass is used for setting when sequence is used.
    #1 = no bypass command
    #0 = bypass the command
    def set_channel(self,chnl='CHAN 1',bypass=0):
        try:
            if self.seqstate == False or bypass == 1:
                self.Write_command(chnl)

            self.chnl = chnl
        except TypeError:
            print('Error in \"set_channel\" function: Please pass only strings')
        
    def set_mode(self, mode='CCL',bypass=0):
        try:
            if self.seqstate == False or bypass == 1:
                self.Write_command("MODE %s" %mode)

            self.mode = mode
        except TypeError:
            print('Error in \"set_mode\" function: Please pass only strings')

    def set_load_state(self,state):
        if state.upper() == 'ON':
            self.Write_command('LOAD ON')
        elif state.upper() == 'OFF':
            self.Write_command('LOAD OFF')
        else:
            raise Exception('Invalid state. Use ON or OFF only')
        
    def set_load_val(self,mode,val1,val2,extern=0):
        
        if extern==1:
            if "CC" and "L" in mode: #considers CCL & CCDL modes
                if val1 > 6.00:
                    val1 = 6.0000
                if val2 > 6.00:
                    val2 = 6.0000
            elif mode == 'CV':
                if val1 > 80.00:
                    val1 = 80.0000
                if val2 > 80.00:
                    val2 = 80.0000
            elif mode == 'CRL':
                if val1 > 100.00:
                    val1 = 100.0000
                if val2 > 100.00:
                    val2 = 100.0000
        
        if mode == 'CV':
            setString = "VOLT:L1 {};L2 {}".format(val1,val2)
        elif mode == 'CRL' or mode == 'CRH':
            setString = "RES:L1 {};L2 {}".format(val1,val2)
        else:
            if 'D' in mode:
                modeString = 'DYN'
            else:
                modeString = 'STAT'
            setString = "CURR:{}:L1 {};L2 {}".format(modeString,val1,val2)
        
        #Get the command string for A & B
        temp_String1 = setString.split(';')
        temp_String2 = temp_String1[0].split(':')
        
        self.setStringA = temp_String1[0]
        self.setStringB = ':'.join(temp_String2[0:len(temp_String2)-1])+":"+temp_String1[1]
        #print(self.setStringA, self.setStringB) #debug only
        
        self.Write_command(setString)
        if self.ABstate == "A":
            self.Write_command(self.setStringA)
        elif self.ABstate == "B":
            self.Write_command(self.setStringB)
            
        del temp_String1
        del temp_String2
        
    def set_T_val(self,T1,T2,extern=0):
        
        if extern==1:
            if T1 > 100.00:
                T1 = 100.0000
            if T2 > 100.00:
                T2 = 100.0000
            
        setString = "CURR:DYN:T1 {};T2 {}".format(("%sms"%T1),("%sms"%T2))
        self.Write_command(setString)
        
    def set_slew_val(self,mode,rise,fall,extern=0):
        
        if extern==1:
            if ("CC" and "L" in mode) or mode == 'CRL':
                if rise > 100:
                    rise= 100
                if fall > 100:
                    fall = 100
        
        if 'D' in mode:
            modeString = 'DYN'
        else:
            modeString = 'STAT'
        if ("CC" and "H" in mode) or ("R" in mode):
            rise, fall = "%sA/us"%rise,"%sA/us"%fall
        elif "CC" and "L" in mode:
            rise, fall = "%smA/us"%rise,"%smA/us"%fall
            
        if 'CC' not in mode:
            setString = "RES:RISE {};FALL {}".format(rise,fall)
        else:
            setString = "CURR:{}:RISE {};FALL {}".format(modeString,rise,fall)
            
        self.Write_command(setString)
        
#---------------------------------------------Read command-----------------------------------------
    def read_load(self,places=4):
        if self.expstate == False:
            try:
                load_val = self.Query_command('MEAS:CURR?;VOLT?')
                load_val = load_val.split(';')
                curr = str(round(float(load_val[0]),places))
                volt = str(round(float(load_val[1]),places))
                return [curr,volt]
            except:
#                 curr = "11.5" #[Debug]
#                 volt = "2.0" #[Debug]
#                 return [curr,volt] #debug
                pass
        else:
            pass
        
    def setOutAB(self):
        if self.ABstate=='A':
            self.Write_command(self.setStringA)
        elif self.ABstate=='B':
            self.Write_command(self.setStringB)
    
#------------------------------------------Compound functions--------------------------------------
    def expOutput(self, I_initial=0, I_end=0,t_end=0):
        if I_initial > 6:
            self.set_mode('CCH')
        else:
            self.set_mode('CCL')
        self.set_load_state('ON')
        a = I_initial
        b = pow((I_end/I_initial),(1/t_end))
        t_initial = time.time()
        t_new = time.time()
        delta_t = round(t_new - t_initial,6)
        while (delta_t < t_end):
            L1 = a*pow(b,delta_t)
            setString = "CURR:STAT:L1 {}".format(L1)
            t_new = time.time()
            print(t_new)
            delta_t = round(t_new - t_initial,4)
            print(delta_t)
            self.Write_command(setString)

#------------------------------------------Data holding function-----------------------------------
    def dynamicState(self,state=False):
        self.dynstate = state
        
    def CCstate(self,state=False):
        self.currstate = state
        
    def CRstate(self,state=False):
        self.resstate = state
        
    def expState(self,state=False):
        self.expstate = state
        
    def seqState(self,state=False):
        self.seqstate = state
        
    def ABState(self,state='A'):
        self.ABstate = state
        
    def ELOADconfig(self,numOfChnls):
        xaxis = (numOfChnls)*150 + 220
        noConnGeometry = '340x95'
        initCCGeometry = '%sx350' %str(xaxis)
        initnoCCGeometry = '%sx300' %str(xaxis)
        initDGeometry = '%sx350' %str(xaxis+140)
        expandednoDGeometry = '%sx350' %str(xaxis+180)
        expandedDGeometry = '%sx350' %str(xaxis+310)
        expandednoCCGeometry = '%sx300' %str(xaxis+180)
        expandednoDseqGeometry = '%sx390' %str(xaxis+360)
        expandedseqDGeometry = '%sx390' %str(xaxis+510)
        expandednoCCseqGeometry = '%sx390' %str(xaxis+360)
        
        self.geoList = [noConnGeometry, initCCGeometry, initnoCCGeometry, initDGeometry, expandednoDGeometry, expandedDGeometry, expandednoCCGeometry,expandednoDseqGeometry,expandedseqDGeometry,expandednoCCseqGeometry]
        
#------------------------------------------Additional For Integration-----------------------------------
    def set_Chan_AB(self,chnlSelStr):
        chnlStrLen = len(chnlSelStr)
        chnl = ""
#         print(chnlStrLen) #debug
        if chnlStrLen > 6:
            chnl = chnlSelStr[:4].upper() + " " + chnlSelStr[8]
            self.set_channel(chnl)
            self.ABState(chnlSelStr[9])
#             print(self.chnl, self.ABstate) #debug


# ELOAD = ELOAD()
# ELOAD.connect("ASRL91::INSTR")
# ELOAD.set_channel('CHAN 1',1)
# ELOAD.set_mode('CV',1)
# ELOAD.ABState('B')
# ELOAD.set_load_val('CV',3,2)
# #ELOAD.Write_command("CURR:STAT:L1 2;L2 2")
# ELOAD.fulldisconnect()
