"""
This is Modbus RTU Communication Module on serial bus.
Tested on ModbusMaster-Master Library on Arduino: https://github.com/4-20ma/ModbusMaster
The module supports all 10 functions of the library.
The module depends on PySerial 3.0 : https://pythonhosted.org/pyserial/index.html
Developed by:Karim Ahmed Hamdy, Email:karimhamdymo@gmail.com
"""

from SlaveDefinitions import *
import serial
import time    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
print("Modbus Diagnostic Slave, Simple command line based Modbus slave simulator and test utility.")
print("Protocol Configuration:Modbus RTU over Serial.")
print("-------------------------------------------------------------------------------------------")

while(True):
    Baudrate = input("Enter the baudrate : ")                   
    if(Baudrate.isdigit()==False):
        print("Enter numerical digits for the baudrate")
        continue
    break;

while(True):
    comPort = input("Enter the number of com port or enter (p) to list available ports : ")
    if(comPort== 'p'):                                                  #The module uses another script in the pySerial libray to identify the available ports
        exec(open('list_ports.py').read())                              #Executes lists_ports.py to identify the available ports
        continue
    if(comPort.isdigit()==False):
        print("Please enter number of com port or enter (p) to list available ports")
        continue
    break;

while(True):
    slaveId=input("Enter the slave id : ")                              #User input of Slave ID, This is crucial to Modbus communication, As the module ignores the commands sent 
    if(slaveId.isdigit()==False):                                       #to other slaves.
        print("Enter numerical digits for the Slave Id")
        continue
    break;
serByteSize=8;serStopBits=1;serParityBits='E'                           #Default settings for communication
slaveId = int(slaveId)
Baudrate = int(Baudrate)
while(True):
        global timeOut
        comPort = 'COM'+str(comPort)
        print("Default Settings are : 8-Byte wide bytesize, 1 Stop bit, No parity bits, Master poll timeout:1 second ")
        change = input("do you want to change the settings? <y | n>")
        if(change == 'y'):
            serByteSize = int(input("Enter the Byte size (5 | 6 | 7 | 8):"))
            serStopBits = int(input("Enter the number of stop bits (1 | 2):"))
            parity = input("Enter the type of parity bit (None (n), Even (e), Mark (m), Space (s)):")
            if(parity == 'n'):
                serParityBits = 'N'
            elif(parity == 'e'):
                serParityBits = 'E'
            elif(parity == 'm'):
                serParityBits = 'M'
            elif(parity == 's'):
                serParityBits = 'S'
            timeOut = int(input("Enter the Master Poll timeout (seconds) :"))    
            print("Applied new Configurations.")
            ModbusBegin(Baudrate,comPort,1,serByteSize,serStopBits,serParityBits)       #Start of serial communication, With "1" sent as a parameter to identify that there are new settings.
        try:
                if(change != 'y'):                                      #Start of the serial communication with default settings.
                        timeOut=1
                        ModbusBegin(Baudrate,comPort,0,serByteSize,serStopBits,serParityBits)
        except serial.serialutil.SerialException:                       #Catching the SerialException error, Triggered when opening unavailable ports.
                while(True):    
                        comPort = input("Unable to open Port, Please re-enter the number of com port or enter (p) to list available ports : ")
                        if(comPort== 'p'):
                                exec(open('list_ports.py').read())
                                continue
                        if(comPort.isdigit()==False):
                                print("Please enter number of com port or enter (p) to list available ports")
                                continue
                        break;
                
                continue
        break;
                
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
print("Connection to port",comPort," is ", end='')
if(commStatus() == 1):
    print("successful")
    print("-------------------------------------------------------------------------------------------")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
while(True):
    global inputArraySize,firstSerialData,secSerialData,inputSlaveid,inputFuncode,inputDataAddr,inputRawdata
    print("Listening to Serial bus.. ")

    remBytesIncorrectID=readData()                                      #Reading Data from the serial bus,Then recording the data in the List:firstSerialData                                                                
    updateParameters()                                                  #Updating the variables of the slaveID, Function Code, Raw input data and Address data

    if(slaveId == inputSlaveid):                                        #begin Parsing the data only if the Command is sent to the user-defined slaveID.
        print("Correct slave adress, Connected parsing data ...")
        remBytes = parseData(inputSlaveid,inputFuncode,inputDataAddr,inputRawdata)              #parsing the data, Printing the command, Finally returns number of remaining serial Bytes to ignore
                                                                                                #This is implemented because i didnot implement CRC16 Error Checking function, So if the Module didnot
                                                                                                #reed the Error checking bytes,It would ignore them.
        print("-------------------------------------------------------------------------------------------")
        break
    else:
        print("Incorrect slaveID communication...", end='')
        if(remBytesIncorrectID > 0):
            for j in range(remBytesIncorrectID):
                getUARTFrameReady()
        time.sleep(timeOut)                                             ## putting Master poll time delay.
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
while(True):
    time.sleep(timeOut)
    if(remBytes > 0):                                                   #If the there still remains 2 bytes of Error checking,Ignore them.
        for j in range(remBytes):
            getUARTFrameReady()

    receivNewData = readChecknewData()                                  #Re-read the Serial bus for new data. The function returns '1' on identifying that new and different data is recieved.
 
    if(receivNewData==1):
        for j in range(8+totalBytesCounter+1):
            firstSerialData[j] = secSerialData[j]                       #On recieving new and different data, move the data to list:firstSerialData and restart the process once again.
            
        updateParameters()
        remBytes =parseData(inputSlaveid,inputFuncode,inputDataAddr,inputRawdata)
        print("-------------------------------------------------------------------------------------------")        
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



