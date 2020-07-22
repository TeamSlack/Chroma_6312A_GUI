import pyvisa,time

class ELOAD:
    connectState = 0
    mode_string = ""
    High_setting = False
    
    @classmethod
    def get_port_list(cls):
        cls.rm = pyvisa.ResourceManager()
        port_list = cls.rm.list_resources()
        return (port_list)
    
    @classmethod
    def connect(cls,port_name):
        cls.eload = cls.rm.open_resource(port_name)
        cls.eload.query('*IDN?')
        cls.eload.write('CONF:REM ON')
        cls.set_load_mode(1)
        cls.connectState = 1
        return cls.connectState
    
    @classmethod
    def disconnect(cls):
        cls.connectState = 0
        cls.eload.write('CONF:REM OFF')
        cls.eload.close()
        cls.rm.close()
        
    @classmethod
    def set_channel(cls,chnl):
        try:
            cls.eload.write(chnl)
        except:
            None
            
    @classmethod
    def set_load_mode(cls,mode="CCL",H_mode=False):
        if type(mode) == int:
            if mode == 1:
                if H_mode == False:
                    eload_mode = 'CCL'
                else:
                    eload_mode = 'CCH'
                cls.mode_string = "STAT"
            elif mode == 2:
                if H_mode == 0:
                    eload_mode = 'CCDL'
                elif H_mode == 1:
                    eload_mode = 'CCDH'
                cls.mode_string = "DYN"
            elif mode == 3:
                eload_mode = 'CV'
            elif mode == 4:
                eload_mode = 'CR'
            else:
                raise Exception("Mode is checking int type. Current mode {} does not exist".format(mode))
        elif type(mode) == str:
            if mode.upper() == "CCL":
                if H_mode == False:
                    eload_mode = 'CCL'
                else:
                    eload_mode = 'CCH'
                cls.mode_string = "STAT"
            elif mode.upper() == "CCDL":
                if H_mode == 0:
                    eload_mode = 'CCDL'
                elif H_mode == 1:
                    eload_mode = 'CCDH'
                cls.mode_string = "DYN"
            elif mode.upper() == "CV":
                eload_mode = 'CV'
            elif mode.upper() == "CR":
                eload_mode = 'CR'
            else:
                raise Exception("Mode is checking str type. Current mode {} does not exist".format(mode))    
        else:
            raise Exception("Unknown input is given to the function, check data passed to \'mode\' of function")
        cls.High_setting = H_mode
        cls.eloadActMode = eload_mode
        cls.eload.write("MODE {}".format(eload_mode))
    
    @classmethod
    def config_output(cls,op_mode, L1=0, L2=0):
        if op_mode.upper() == 'READ':
            
            if cls.eloadActMode == "CCL" or cls.eloadActMode == "CCH" or cls.eloadActMode == "CCDL" or cls.eloadActMode == "CCDH":
                read_mode = "CURR"
                queryString = 'CURR:{}:L1?; L2?'.format(cls.mode_string)
            elif cls.eloadActMode == "CV":
                queryString = 'VOLT:L1?; L2?'.format(cls.mode_string)
                
            queryVal = cls.eload.query(queryString)
            queryVal = queryVal.split(';')
            L1val = queryVal[0]
            L2val = queryVal[1].strip('\n')
            return [L1val,L2val]
        elif op_mode.upper() == 'WRITE':
            if cls.eloadActMode == "CCL" or cls.eloadActMode == "CCH" or cls.eloadActMode == "CCDL" or cls.eloadActMode == "CCDH":
                read_mode = "CURR"
                setString = "CURR:{}:L1 {}; L2 {}".format(cls.mode_string,L1,L2)
            elif cls.eloadActMode == "CV":
                setString = "VOLT:L1 {}; L2 {}".format(L1,L2)

            cls.eload.write(setString)
        else:
            raise Exception("Read / Write only. Current mode {} does not exist".format(mode))
    
    @classmethod
    def dynamic_config(cls, op_mode, TL1=0.025, TL2=0.025, rise=1, fall=1, return_mode='STD'):
        if cls.High_setting == False:
            rise, fall = str(rise)+"mA/us", str(fall)+"mA/us"
        else:
            rise, fall = str(rise)+"A/us", str(fall)+"A/us"
        
        dynamic_command = ["CURR:DYN:T1 {}; T2 {}".format(str(TL1)+"ms",str(TL2)+"ms"),"CURR:DYN:RISE {}; FALL {}".format(rise,fall), "CURR:DYN:T1?; T2?", "CURR:DYN:RISE?; Fall?"]
        setting_storage = []
        
        if op_mode.upper() == 'WRITE':
            for command in dynamic_command[:2]:
                cls.eload.write(command)
                
        elif op_mode.upper() == 'READ':
            for command in dynamic_command[2:4]:
                x = cls.eload.query(command)
                setting_storage.append(x)
            if return_mode.upper() == 'STD':
                Time = setting_storage[0].split(';')
                T1val, T2val = Time[0],Time[1].strip('\n')
                Slew = setting_storage[1].split(';')
                RiseVal, FallVal = Slew[0],Slew[1].strip('\n')
                return [T1val,T2val,RiseVal,FallVal]
            elif return_mode.upper() == 'ORI':
                return setting_storage
            else:
                raise Exception("STD / ORI only. Current operation {} does not exist".format(return_mode))
        else:
            raise Exception("Read / Write only. Current mode {} does not exist".format(op_mode))
        
    @classmethod
    def load_state(cls,state):
        if state.upper() == 'ON':
            cls.eload.write('LOAD ON')
        elif state.upper() == 'OFF':
            cls.eload.write('LOAD OFF')
        else:
            raise Exception('Invalid state. Use ON or OFF only')
        
    @classmethod
    def read_load(cls,places):
        load_val = cls.eload.query('MEAS:CURR?;VOLT?')
        load_val = load_val.split(';')
        curr = str(round(float(load_val[0]),places))
        volt = str(round(float(load_val[1]),places))
        return [curr,volt]

# class highlvlELOAD(ELOAD):
#     
#     @classmethod
#     def automate(cls, visa_manager, port_name="ASRL86::INSTR", mode="CCL"):
#         cls.connect(port_name)
#     
    
###debug###    
# Chroma_6312A = ELOAD()
# eload_port = Chroma_6312A.get_port_list()
# print(eload_port)
# x = Chroma_6312A.connect(eload_port[1])
# print(x)
# Chroma_6312A.set_load_mode('ccdl')
# for i in range(10):
#     x,y = Chroma_6312A.read_load(4)
#     print(x,y)
# Chroma_6312A.mode_string
# Chroma_6312A.config_output('write',1,0.4)
# Chroma_6312A.config_output('read')
# Chroma_6312A.dynamic_config('write',"500","100","20","40")
# T1,T2,rise,fall = Chroma_6312A.dynamic_config('read')
# print(T1,T2,rise,fall)
# Chroma_6312A.load_state('ON')
# time.sleep(5)
# Chroma_6312A.disconnect()

# Chroma_6312A = highlvlELOAD
# Chroma_6312A.automate()

    
    