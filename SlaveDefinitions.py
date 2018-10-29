"""
This is Modbus RTU Communication Module on serial bus.
Tested on ModbusMaster-Master Library on Arduino: https://github.com/4-20ma/ModbusMaster
The module supports all 10 functions of the library.
The module uses on PySerial 3.0 : https://pythonhosted.org/pyserial/index.html

Functions available :
    ModbusBegin(Baudrate,comPort,changeFlag,byteSize,stopBits,parityBits)
    ModbusRead(slaveId)
    ModbusReadNewData()

Developed by:Karim Hamdy
"""



import serial
import time
import sys
import glob

"""
Global variables and lists declaration
"""
global totalBytesCounter,timeOut,remBytes,receivNewData
global globalCounter
receivNewData = 0
inputArraySize=8;
firstSerialData = []
secSerialData = []
inputSlaveid =0
inputFuncode =  []
inputDataAddr =  []
inputRawdata = []
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
for m in range(100):
    """
    Lists initialization with a limit of 100 elements
    """
    firstSerialData.append(0)
    secSerialData.append(0)
    inputFuncode.append(0)
    inputDataAddr.append(0)
    inputRawdata.append(0)
#---------------------------------------------------------------------------------------------------
def readChecknewData():
        """
        The function reads new data stream from the serial bus to the list:secSerialData.
        Then compares this data with the data already recieved.
        If the new data is different, The function returns '1',if not, it returns '0'

        """
        global totalBytesCounter
        global inputArraySize,firstSerialData,secSerialData,inputSlaveid,inputFuncode,inputDataAddr,inputRawdata
        totalBytesCounter=0                                             #The code uses totalBytesCounter variable to identify the total number new recieved bytes
        """
        The number of bytes sent as a single message vary according to the function sent as follow :
        8 Byte wide message for all the commands except 'Writing Multiple Coils or registers' and 'Read Write Multiple Registers', They vary according to the byte count
        secSerialData[1][0] Holds the function type of the message in decimal.
        """
        for i in range(8):
            secSerialData[i] = serialRead()
        if(secSerialData[1][0] == 16 or secSerialData[1][0] == 15):
            for totalBytesCounter in range(secSerialData[6][0]-1):
                secSerialData[8+totalBytesCounter] = serialRead()
            inputArraySize=8+totalBytesCounter
            for i in range(inputArraySize):
                if(secSerialData[i] == firstSerialData[i]):
                    continue
                else:      
                    return 1
                    break
        elif(secSerialData[1][0] == 23):                                #Reading the serial data according to the function type and the byte count(if any).
            q=0                                                         #Then compares the recieved data with the old data.
            for q in range(3):
                secSerialData[8+q] = serialRead()
            for q in range(secSerialData[10][0]):
                secSerialData[11+q] = serialRead()
            inputArraySize=11+q
            totalBytesCounter=3+secSerialData[10][0]
            for i in range(inputArraySize):
                if(secSerialData[i] == firstSerialData[i]):
                    continue
                else:      
                    return 1
                    break
        else:
            totalBytesCounter=0
            for i in range(8):
                if(secSerialData[i] == firstSerialData[i]):
                    continue
                else:
                    return 1
        return 0
    




#--------------------------------------------------------------------------------------------------

def ModbusConStatus():                                                                       #Returns '1' on opening communication with the port successfully
    global ser
    return ser.is_open
#---------------------------------------------------------------------------------------------------    
def serialRead():
    return ser.read(1)
#---------------------------------------------------------------------------------------------------
def serialClose():
    ser.close()
#---------------------------------------------------------------------------------------------------

def getUARTFrameReady():
    """
    On parsing the data, The number of Sent serial Bytes Is variable according to the function type.
    This functions ignores two bytes in the serial stream, Those two bytes are the Error checking bytes.
    This is implemented because i didnot implement CRC16 Error Checking function, So if the Module didnot
    read the Error checking bytes,It would ignore them.
    The bus needs to ignore them to correctly recieve the next batch of bytes.
    """
    serialRead()
    serialRead()
#---------------------------------------------------------------------------------------------------
def parseData(Id,code,dataAddr,data):
    readData = 1
    if(code == 1):
        functionName = "Read Coil"#
        print(functionName," from adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",number of coils ",data[0],data[1])
        return 0
    elif(code == 2):
        functionName = "Read discrete inputs"#
        print(functionName," from adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",number of inputs ",data[0],data[1])
        return 0
    elif(code == 3):
        functionName = "Read Holding registers"#
        print(functionName," from adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",number of registers ",data[0],data[1])
        return 0
    elif(code == 4):
        functionName = "Read input registers"#
        print(functionName," from adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",number of registers ",data[0],data[1])
        return 0
    elif(code == 5):
        functionName = "Write single coil"#
        readData=0
        print(functionName," to adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",data = ",(data[0][0])&1)
        return 0
    elif(code == 6):
        functionName = "write single register"#
        readData=0
        print(functionName," to adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",data = ",data[1][0]&1)
        return 0
    elif(code == 15):
        functionName = "Write Multiple Coils"#
        readData=0
        print(functionName," from adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",number of registers ",data[0],data[1])
        for m in range(data[2][0]):
            print("data  ",data[m+3])
        return 1
    elif(code == 16):
        functionName = "write multiple registers"
        readData=0
        print(functionName," from adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",number of registers ",data[0],data[1])
        for m in range(data[2][0]):
            print("data  ",data[m+3])
        return 1
    elif(code == 22):
        functionName = "Mask Write Register"
        readData=0
        print(functionName," to adress in HEX:","{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",AND mask = ",data[0],data[1],",OR mask = ",data[2],data[3])##feha kalam
        return 1
    elif(code == 23):
        functionName = "Read Write Multiple Registers"#feha kalam
        readData=0
        print(functionName," Read adress in HEX:", "{0:x}".format(dataAddr[0][0]),"{0:x}".format(dataAddr[1][0]),",Read Quantity = ",data[0],data[1],", Write adress in hex:","{0:x}".format(data[2][0]),"{0:x}".format(data[3][0]),",Write Quantity = ",data[4],data[5])##feha kalam
        for m in range(data[6][0]):
            print("data  ",data[m+3])
        return 1
    else:
        print("inputSlaveid = ",Id,"inputFuncode = ",code,"inputDataAddr = ",dataAddr,"inputRawdata = ",data)

#---------------------------------------------------------------------------------------------------

def readData ():
    """
    The function reads new data stream from the serial bus to the list:firstSerialData.
    The data stream byte-size is variable according to the function type.
    The function returns number of Error Checking bytes to ignore.
    """
    global inputArraySize,firstSerialData,secSerialData,inputSlaveid,inputFuncode,inputDataAddr,inputRawdata
    for i in range(8):
        firstSerialData[i] = serialRead()
    if(firstSerialData[1][0] == 16 or firstSerialData[1][0] == 15):                 #Reads additional bytes stream according to the function type and the Byte-Count(if any)
        for m in range(firstSerialData[6][0]-1):
            firstSerialData[8+m] = serialRead()
        return 1
    elif(firstSerialData[1][0] == 22):
        return 1  
    elif(firstSerialData[1][0] == 23):
        q=0
        for p in range(3):
            firstSerialData[8+p] = serialRead()
        for q in range(firstSerialData[10][0]):
            firstSerialData[11+q] = serialRead()
        return 1
    else:
        return 0

#---------------------------------------------------------------------------------------------------

def printData ():
    global inputArraySize,firstSerialData,secSerialData,inputSlaveid,inputFuncode,inputDataAddr,inputRawdata
    n=0
        
    if(firstSerialData[1][0] == 16 or firstSerialData[1][0] == 15):            
        for n in range(8+firstSerialData[6][0]-1):
            print("data = ",firstSerialData[n])
            
    elif(firstSerialData[1][0] == 23):
        for n in range(11+firstSerialData[10][0]):
            print("data = ",firstSerialData[n])
    else:
        for n in range(8):
            print("data = ",firstSerialData[n])

#--------------------------------------------------------------------------------------------
def updateParameters():
    """
    The function Takes the data from the list :firstSerialData and resaves the data in appropiate variables.
    Those variables will be used later on to identify the slave defined,function code and so on.
    According to the protocol, The data is sent as follows: SlaveID,Function Code,Data address, Data Quantity ,Byte Count(if any),Data bytes ,Error checking bytes.
    """
    global inputArraySize,firstSerialData,secSerialData,inputSlaveid,inputFuncode,inputDataAddr,inputRawdata
    
    inputSlaveid =  firstSerialData[0][0]                               #Slave Id, [0] to convert to decimal
    

    inputFuncode =  firstSerialData[1][0]                               #Function type of recieved message
    inputDataAddr =  [firstSerialData[2],firstSerialData[3]]
    """
    The number of bytes sent as a single message vary according to the function sent as follow :
    8 Byte wide message for all the commands except 'Writing Multiple Coils or registers' and 'Read Write Multiple Registers', They vary according to the byte count
    """
    
    if(firstSerialData[1][0] == 16 or firstSerialData[1][0] == 15 ):    #Reading data according to the function type. 
        inputRawdata[0] = firstSerialData[4][0]
        inputRawdata[1] = firstSerialData[5][0]
        for m in range ((firstSerialData[6][0])+1):
            inputRawdata[(m+2)] = firstSerialData[(m+6)]
    elif(firstSerialData[1][0] == 23):
        inputRawdata[0] = firstSerialData[4][0]
        inputRawdata[1] = firstSerialData[5][0]
        inputRawdata[2] = firstSerialData[6]
        inputRawdata[3] = firstSerialData[7]
        inputRawdata[4] = firstSerialData[8][0]
        inputRawdata[5] = firstSerialData[9][0]
        inputRawdata[6] = firstSerialData[10]                           #bytecount is on firstSerialData[10]
        
        for j in range ((firstSerialData[10][0])+1):
            inputRawdata[(j+6)] = firstSerialData[(j+10)]
    else:
        for l in range(4):
            inputRawdata[l] = [firstSerialData[4+l][0]]        
#---------------------------------------------------------------------------------------------------
def ModbusRead(slaveIdUser):
    '''
    the funtion reads data from Serial stream, Then identifies the slaveID of serial stream.
    The function returns 1 on correct SlaveId identification, or returns 0 on incorrect SlaveId.
    '''
    global totalBytesCounter,timeOut,remBytes,receivNewData,globalCounter,j
    while(True):
        time.sleep(1)
        print("Listening to Serial bus.. ")

        remBytesIncorrectID=readData()                                      #Reading Data from the serial bus,Then recording the data in the List:firstSerialData                                                                

        updateParameters()                                                  #Updating the variables of the slaveID, Function Code, Raw input data and Address dat

        if(slaveIdUser == inputSlaveid):                                        #begin Parsing the data only if the Command is sent to the user-defined slaveID.
            print("Correct slave ID, Connected parsing data ...")
            remBytes = parseData(inputSlaveid,inputFuncode,inputDataAddr,inputRawdata)              #parsing the data, Printing the command, Finally returns number of remaining serial Bytes to ignore
                                                                                      #This is implemented because i didnot implement CRC16 Error Checking function, So if the Module didnot                                                                                            #reed the Error checking bytes,It would ignore them.
            print("------------------------------------------------------------------------------")

            return 1
        else:
            print("Incorrect slaveID communication...", end='')
            if(remBytesIncorrectID > 0):
                for j in range(remBytesIncorrectID):
                    getUARTFrameReady()
                return 0                                                     
        

#---------------------------------------------------------------------------------------------------

def ModbusReadNewData():
    global receivNewData,j,totalBytesCounter,totalBytesCounter,firstSerialData,secSerialData
    global inputSlaveid,inputFuncode,inputDataAddr,inputRawdata,remBytes
    while(True):
        time.sleep(1)
        if(remBytes > 0):                                                   #If the there still remains 2 bytes of Error checking,Ignore them.
            for j in range(remBytes):
                getUARTFrameReady()
        receivNewData = readChecknewData()                                  #Re-read the Serial bus for new data. The function returns '1' on identifying that new and different data is recieved.
     
        if(receivNewData==1):
            for j in range(8+totalBytesCounter+1):
                firstSerialData[j] = secSerialData[j]                       #On recieving new and different data, move the data to list:firstSerialData and restart the process once again.
                
            updateParameters()
            remBytes =parseData(inputSlaveid,inputFuncode,inputDataAddr,inputRawdata)
            print("-------------------------------------------------------------------------------")        
            check = input("Continue Listening to Modbus frame? Enter ""n"" to close communication channel : ")
            if(check == "n"):
                break;
        else:
            print("Same Data has been recieved.")
            check = input("Continue Listening to Modbus frame? Enter ""n"" to close communication channel : ")
            if(check == "n"):
                break;
            
    print("Serial Communication channel has closed.")
    serialClose()
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
def ModbusBegin(Baudrate,comPort,changeFlag,byteSize,stopBits,parityBits):              #Begins serial communication with the provided settings in the parameters
    global ser
    ser = serial.Serial()
    ser.baudrate = Baudrate
    ser.port = comPort
    if(changeFlag == 1):
        ser.bytesize = byteSize
        ser.stopbits = stopBits
        ser.parity = parityBits
    ser.open()
#---------------------------------------------------------------------------------------------------



def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
