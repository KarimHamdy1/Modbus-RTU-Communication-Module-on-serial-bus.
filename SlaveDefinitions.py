import serial
"""
Global variables and lists declaration
"""
global totalBytesCounter,timeOut,remBytes,receivNewData
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

def commStatus():                                                                       #Returns '1' on opening communication with the port successfully
    global ser
    return ser.is_open
    
def serialRead():
    return ser.read(1)

def serialClose():
    ser.close()


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


