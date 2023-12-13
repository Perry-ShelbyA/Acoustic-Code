#! /Applications/anaconda/bin/python

import serial
import sys
import glob
import time
from   datetime import date, time, datetime
import serial.tools.list_ports as port_list
import numpy as np


# ***************************************************************************
# Configuration Parameters
# Modify for each deployment as needed
SURVEYID='10009'    # Must be 5 characters not starting with a 0 and is used in the filename
USERID='WVD'        # 3 characters only
BUOYID='1003'       # 4 digits or characters, must be 4 and no special characters, numbers and letters only
REALTIMEENABLED=0   # 1 is enabled, every other value is disabled
REALTIMEPERIOD=28   # day is divided into 15 minute intervals, 0 is midnight, 1 is 00:15, 2 is 00:30, etc., MAX is 95
SDCARDSIZE=512     # 128, 256, 512, 1024, 2048 (IN GIGABYTES), any value between 128 and 2048 can be used but the embedded code will use the nearest to one of these values
MAGBYPASS=1         # 1 will cause the recorder not to wait for the magnetic bypass to start recording
BAUDRATE = 9600
PORT='COM22'   # Make sure this is the right com port for Oyster data logger
TIMEOUT=2


# ***************************************************************************

#def serial_ports():
def main():    
    
    print('\r\n\r\nProteus Technologies LLC Acoustic Recorder Configuration Application\r\n\r\n')
    print('\r\n\r\nAvailable Serial Ports on this Machine')
    ports = list(port_list.comports())
    for p in ports:
        print (p)
    
    print('Using: '+PORT)
    print('\r\n')
    
    now = datetime.now()
    print(now)
    
    if (now.month < 10.000):
        monthstr = '0'+str(now.month)
    else:
        monthstr = str(now.month)
    
    if (now.day < 10.000):
        daystr = '0'+str(now.day)
    else:
        daystr = str(now.day)
        
    if (now.second < 10.000):
        secondstr = '0'+str(now.second)
    else:
        secondstr = str(now.second)
        
    if (now.minute < 10.000):
        minutestr = '0'+str(now.minute)
    else:
        minutestr = str(now.minute)
        
    if (now.hour < 10.000):
        hourstr = '0'+str(now.hour)
    else:
        hourstr = str(now.hour)
        
    gprmc = '$GPRMC,'+hourstr+minutestr+secondstr+'.000'+',A,,,,,,,'+daystr+monthstr+str((now.year-2000))+",,,A,*10\r\n"
    print(gprmc)
    #print(year,':',month,day,hour,minute,seconds)
    
    #current_time = time(now.hour, now.minute, now.second)
    #datetime.combine(today, current_time)
    
    #time.time()
    #date(year=2020, month=1, day=31)
    #time(hour=13, minute=14, second=31)
    #datetime(year=2020, month=1, day=31, hour=13, minute=14, second=31)

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
        ports = glob.glob('/dev/ttyUSB*') # ubuntu is /dev/ttyUSB0
    elif sys.platform.startswith('darwin'):
        # ports = glob.glob('/dev/tty.*')
        ports = glob.glob('/dev/tty.SLAB_USBtoUART*')
    else:
        raise EnvironmentError('Unsupported platform')
    
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except serial.SerialException as e:
            if e.errno == 13:
                raise e
            pass
        except OSError:
            pass
    
    print(result)
    
    #Opens the serial port
    try:
        #serialPort = serial.Serial(port=PORT, baudrate=BAUDRATE, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=TIMEOUT, writeTimeout=TIMEOUT)
        serialPort = serial.Serial(port=PORT, baudrate=BAUDRATE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=TIMEOUT, writeTimeout=TIMEOUT)
        print("Port is open")
    
    except serial.SerialException:
        serialPort.close()
        #serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT, writeTimeout=TIMEOUT).close()
        print ("Port is closed")
        serialPort = serial.Serial(port=PORT, baudrate=BAUDRATE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=TIMEOUT, writeTimeout=TIMEOUT)
        print ("Port is open again")

    print("Port Ready to use")
    
    DONE=0
    #response=" "
    response  = np.zeros(200)
    responseD = bytearray(np.zeros(200))
    start = 's\r\n'
    startD = start.encode()
    stop  = '1\r\n'
    stopD  = stop.encode()
    
    #buoyConfig = np.zeros(100)
    buoyConfigD = bytearray(np.zeros(100))
    
    #must have no spaces between characters at all
    buoyConfig  = '$PLCFG,' + SURVEYID + ','+ USERID +','+ BUOYID +','+str(REALTIMEENABLED)+','+str(REALTIMEPERIOD)+','+str(SDCARDSIZE)+','+str(MAGBYPASS)+'*'+'\r\n'
    buoyConfigD = buoyConfig.encode()
    
    # synchronizes the Python code with the logger
    # sends an 's' for start and the logger replies with 'r' for ready
    while (DONE==0):
        serialPort.flushInput()
        serialPort.write(startD)
        response  = serialPort.read_until() # expected='\n'
        responseD = response.decode()
        print(responseD)
        rLength = len(responseD)
        if (rLength > 0):
            if (responseD[0] == 'r'):
                DONE=1

    # Send the config stream 
    # #PLCFG, ....
    DONE2=0
    while (DONE2==0):
        serialPort.flushInput()
        serialPort.write(buoyConfigD)
        response  = serialPort.read_until() # expected='\n'
        responseD = response.decode()
        rLength = len(responseD)
        if (rLength > 0):            
            print('recorder: ', responseD, '\r\n')
            DONE2=1
                
    DONE = 0
    while(DONE==0):
    
        #time.sleep(1)  # wait 1 second to send the next value, waiting for a return of 1
       
        now = datetime.now()
        if (now.month < 10.000):
            monthstr = '0'+str(now.month)
        else:
            monthstr = str(now.month)
    
        if (now.day < 10.000):
            daystr = '0'+str(now.day)
        else:
            daystr = str(now.day)
        
        if (now.second < 10.000):
            secondstr = '0'+str(now.second)
        else:
            secondstr = str(now.second)
            
        if (now.minute < 10.000):
            minutestr = '0'+str(now.minute)
        else:
            minutestr = str(now.minute)
            
        if (now.hour < 10.000):
            hourstr = '0'+str(now.hour)
        else:
            hourstr = str(now.hour)
            
        gprmc = '$GPRMC,'+hourstr+minutestr+secondstr+'.000,A,,,,,,,'+daystr+monthstr+str((now.year-2000))+",,,A,*10\r\n"
        print(gprmc)
        gprmcB = bytearray(np.zeros(100))
        #gprmcB = '$GPRMC,110554.000,A,,,,,,,110522,,,A,*10\r\n'.encode()
        gprmcB = gprmc.encode()   # convert from unicode to byte array
        
        serialPort.flushOutput()
        serialPort.flushInput()
        serialPort.write(gprmcB)
        
        #response = serialPort.readline()
        response  = serialPort.read_until()  # can add size= too        
        responseD = response.decode()
        rLength   = len(responseD)
        if (rLength > 0):            
            print('recorder: ', responseD)
        
        print('Embedded Recorder MUST respond back with parsed time! Hit 0 to retry or time is not Sync_d')
        userResponse = input("Enter 1 to Start Acquisition: ")
        if (int(userResponse) == 1): 

            serialPort.flushInput()
            serialPort.flushOutput()
            
            serialPort.write(stopD)
            response  = serialPort.read_until() # expected='\n'
            responseD = response.decode()
            print(responseD)
            rLength = len(responseD)
            if (rLength > 0):
                if (responseD[0] == 'r'):
                    DONE=1
            
    print('Remember to start the recorder with the magnet when before deploying!!!!!!!')
        
# config has finished so this will display messages from the recorder
# To quit, Debug Menu, Stop
    while(DONE==1):
        response = serialPort.readline()
        print(response)
        
    serialPort.close()

if __name__ == "__main__":
    main()
    #quit()
    #exit()
    print("Program End")
    sys.exit("System Exiting")

