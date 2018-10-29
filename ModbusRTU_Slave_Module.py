from SlaveDefinitions import *


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------


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
        print(serial_ports())                              #identify the available ports
        continue
    if(comPort.isdigit()==False):
        print("Please enter number of com port or enter (p) to list available ports")
        continue
    break;

while(True):
    slaveIdInput=input("Enter the slave id : ")                              #User input of Slave ID, This is crucial to Modbus communication, As the module ignores the commands sent 
    if(slaveIdInput.isdigit()==False):                                       #to other slaves.
        print("Enter numerical digits for the Slave Id")
        continue
    break;
serByteSize=8;serStopBits=1;serParityBits='E'                           #Default settings for communication
slaveId = int(slaveIdInput)
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
                                print(serial_ports())
                                continue
                        if(comPort.isdigit()==False):
                                print("Please enter number of com port or enter (p) to list available ports")
                                continue
                        break;
                
                continue
        break;
                
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
print("Connection to port",comPort," is ", end='')
if(ModbusConStatus() == 1):
    print("successful")
    print("-----------------------------------------------------------------------------------")

else:
    print("Not successful, Most likely it is already in use or unavailable.")
    print("Serial Communication channel has closed.")
    serialClose()
    sys.exit()
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

correctIdFlag = ModbusRead(slaveId)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

if (correctIdFlag ==1):
    ModbusReadNewData()
else:
    serialClose()
    sys.exit()


