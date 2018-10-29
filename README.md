# Modbus-RTU-Communication-Module-on-serial-bus.

This is Modbus Diagnostic Slave, Simple command line based Modbus slave simulator and test utility.

Protocol Configuration:Modbus RTU over Serial

Tested on ModbusMaster-Master Library on Arduino: https://github.com/4-20ma/ModbusMaster

The module depends on PySerial 3.0 : https://pythonhosted.org/pyserial/index.html

Functions available :
    ModbusBegin(Baudrate,comPort,changeFlag,byteSize,stopBits,parityBits)
    ModbusRead(slaveId)
    ModbusReadNewData()
    
Developed by:Karim Hamdy, Email:karimhamdymo@gmail.com
