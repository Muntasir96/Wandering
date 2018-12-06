# Created between November 13 and November 20 2018

# Built upon wanderServerv1 with a few minor changes - sending the location name to server and adding a location column to excel

################################################# Import libraries #################################################
import sys
import os.path

import time
start = time.time()
import datetime

import telnetlib

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

import winsound

import xlsxwriter

import subprocess
import multiprocessing
################################################# Ready the output file #################################################

inc = 2 # The app will read telnet signals every <inc> seconds

def readyDL(): # This will ready the data logging file and fill it in the intial information
    global inc
    dt = datetime.datetime.now()
    dtnm = str(dt)[0:19]
    test =  str(datetime.datetime.now())[0:19]
    zdt = datetime.datetime.strptime(test, '%Y-%m-%d %H:%M:%S').strftime('%m-%d-%Y_%H.%M.%S')

    print(zdt)
    filecount = int(open(r"C:\Users\wandering\Desktop\WanderProj\DataLog\counter.txt","r").read())

    zeroos = '0'
    if (filecount < 10):
        zeroos = '000'
    elif (filecount < 100):
        zeroos = '00'

    save_path = r"C:\Users\wandering\Desktop\WanderProj\DataLog"
    oname = 'rfidinfo_' + zeroos + str(filecount) + '_' + zdt + '.txt'
    completeName = os.path.join(save_path, oname)
    f = open(completeName,"w+")

    f.write("The file number is " + zeroos + str(filecount) + "\n")
    f.write("The date is " + zdt[0:10] + "\n")
    f.write("The start time is " + zdt[11:] + "\n")
    f.write("This program didn't finish properly!\n")

    f.write("The geographical zone will be determined every " + str(inc) + " seconds\n")
    f.write("\n")
    return (f, completeName, filecount, oname)

(f, completeName, filecount, oname) = readyDL() # f is the actual new file, completeName is the name of the file with the pathe file, file count is the counter number, and oname is the name of the output data log file without the path name  


def replace_line(file_name, line_num, text): # replaces a line in a text file with a text
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()



################################################# ZONE LOG #################################################

xlcount = 1 # this is used to start counting the rows on an  excel file

def readyZL(): # This will ready the data logging file and fill it in the intial information
    dt = datetime.datetime.now()
    dtnm = str(dt)[0:19]
    test =  str(datetime.datetime.now())[0:19]
    zdt = datetime.datetime.strptime(test, '%Y-%m-%d %H:%M:%S').strftime('%m-%d-%Y_%H.%M.%S')
    filecount = int(open(r"C:\Users\wandering\Desktop\WanderProj\DataLog\counter.txt","r").read())

    zeroos = '0'
    if (filecount < 10):
        zeroos = '000'
    elif (filecount < 100):
        zeroos = '00'

    save_path = r"C:\Users\wandering\Desktop\WanderProj\ZoneLog"
    oname = 'rfidinfo_' + zeroos + str(filecount) + '_' + zdt + '.txt'
    xname = 'ZoneInfo' + oname[8:-4] + '.xlsx'
    complexName = os.path.join(save_path, xname)
    workbook = xlsxwriter.Workbook(complexName)
    worksheet = workbook.add_worksheet("Log")
    bold = workbook.add_format({'bold':True})
    worksheet.write('A1', 'DATE', bold)
    worksheet.write('B1', 'TIME', bold)
    worksheet.write('C1', 'ZONE', bold)
    worksheet.write('D1', 'LOCATION', bold)
    worksheet.set_column('A:A',20)
    worksheet.set_column('B:B',20)
    worksheet.set_column('C:C',20)
    worksheet.set_column('D:D',35)
    return worksheet,workbook



worksheet,workbook = readyZL() # worksheet is the worksheet object for the current excel zone log file and workbook is the entire file

def zonelog(date, time, zone, loc): # this simply adds a row to the current excel file being worked on
    global xlcount
    global worksheet
    worksheet.write(xlcount, 0, date)
    worksheet.write(xlcount, 1, time)
    worksheet.write(xlcount, 2, zone)
    worksheet.write(xlcount, 3, loc)
    xlcount = xlcount + 1


################################################# TIME MECH #################################################
def addSecs(tm, secs): # this file is used to give a resulting time after adding X seconds
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()

tb = 150 # this program will create a new data log and zone log file every <tb> seconds
tdate = datetime.datetime.today().strftime('%Y-%m-%d')
print("dates is " + tdate)
tnow = datetime.datetime.now().time()
tend = addSecs(tnow,tb)


################################################# DATA LOG #################################################
def datalog(lines, f, dist, time, zone): # this is a very lengthy function that is used to extract data from the command strings emmitted by the tag. The information will be included in the data logging files
    for packet in lines:
        packet = packet[2:-1]
        if len(packet) >= 26:
            #print(packet)
            f.write("==========================================================================================" + "\n")
            f.write("This packet is " + packet + " which is read by the " + dist + " base reader at around " + time + " at the " + zone + " zone" + "\n")
            f.write("\n")
            res = "\n" + "The first field is: "
            spacing = "\n" + "       "
            StartByte = packet[0:2]
            if (StartByte == 'AA'):
                res = res + StartByte + spacing + "This packet communication type is Tag to Host" + "\n"
            elif(StartByte == '55'):
                res = res + StartByte + spacing + "This packet communication type is Host to Tag" + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
            else:
                res = res + StartByte + spacing + "This packet communication type is unknown" + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
                
            PacketLength = packet[2:4]
            thePLen = int(PacketLength,16)
            res = res + "The second field is: " + PacketLength + spacing +  "Packet Length (in bytes) is: " + str(thePLen) + "\n"
            res = res + "\n"
            PacketType = packet[4:6]
            if (PacketType == '00'):
                res = res + "The third field is: " + PacketType + spacing + "This packet type is Reader command" + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
            elif (PacketType == '02'):
                res = res + "The third field is: " + PacketType + spacing + "This packet type is Tag Command" + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
            elif (PacketType == '04'):
                res = res + "The third field is: " + PacketType + spacing + "This packet type is Tag Data" + "\n"
                res = res + "\n"
            else:
                res = res + "The third field is: " + PacketType + spacing + "This packet type is unknown" + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
    
            TagID = packet[6:10]
            res = res + "The fourth field is: " + TagID + spacing + "The ID of this Tag is " + TagID + "\n"
            res = res + "\n"
    
            ReaderID = packet[10:14]
            res = res + "The fifth field is: " + ReaderID + spacing + "The ID of this Reader is " + ReaderID + "\n"
            res = res + "\n"
    
            PacketNum = packet[14:16]
            res = res + "The sixth field is: " + PacketNum + spacing + "The serial packer number is " + str(int(PacketNum,16)) + "\n"
            res = res + "\n"
    
            TagPacketType = packet[16:18]
            if (TagPacketType == '30'):
                res = res + "The seventh field is: " + TagPacketType + spacing + "This is a beacon packet " + "\n"
                res = res + "\n"
            elif (TagPacketType == '31'):
                res = res + "The seventh field is: " + TagPacketType + spacing + "This is a Acknowledgement packet " + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
            elif (TagPacketType == '32'):
                res = res + "The seventh field is: " + TagPacketType + spacing + "This is a Data Dump packet " + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
            else:
                res = res + "The seventh field is: " + TagPacketType + spacing + "This is an unknown packet " + "\n"
                res = res + "This packet is not of interest " + "\n"
                f.write(res)
                continue
    
            PackControlHeader = packet[18:20]
            res = res + "The eighth field is: " + PackControlHeader + spacing + "The following field(s) are present in this packet: "
            fieldList = ["Network","GPIO","Alarm","Trigger","User Memory","Data Logging","RTLS","Extension"]
            binStr= bin(int(PackControlHeader,16))[2:]
            idx = 0
            first = True
            for i in binStr:
                comma = ", "
                if first == True:
                    comma = ""
                if i == "1":
                    res = res + comma + fieldList[idx]
                    first = False
                idx = idx + 1
            res = res + "\n\n"


            pidx = 20 
            sp1 = "                "
            sp2 = "                    "
            if len(binStr) < 8:
                     continue
            if binStr[0] == "1":
                NetworkFieldByte = packet[pidx:pidx+2]
                if len(NetworkFieldByte) < 2:
                    continue
                pidx = pidx + 2
                res = res + "The Network field is: " + NetworkFieldByte + spacing + "The following report(s) are: "
                nList = ["Current Time Report","Transmit Interval Report", "Transmit Power Report","Battery Voltage","Current Mode","RFU","RFU","Extension"]
                nbinStr= bin(int(NetworkFieldByte,16))[2:]
                nbinStr = nbinStr.rjust(8,'0')
                idx = 0
                first = True
                for i in nbinStr:
                    comma = ", "
                    if first == True:
                        comma = ""
                    if i == "1":
                        res = res + comma + nList[idx]
                        first = False
                    idx = idx + 1
                res = res + "\n\n"
                if len(nbinStr) < 8:
                    continue
                if nbinStr[0] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Current Time byte is " + Nbyte
                    res = res + "\n\n"
                if nbinStr[1] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    intervals = [".5 seconds","1 second","2 seconds","5 seconds","10 seconds","20 seconds","30 seconds", "1 minute", "2 minutes", "5 minutes" , "10 minutes", "15 minutes" ,"30 minutes","45 minutes"]
                    res = res + "The Transmit Interval byte is " + Nbyte + " which means that the tag is emitting data every "
                    tidx = int(Nbyte,16) - 1
                    if tidx > 13:
                       res = res + "45 minutes or more"
                    else:
                       res = res + intervals[tidx]
                    res = res + "\n\n"
                if nbinStr[2] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    powers = ["-25 dBm", "-15 dBm", "-10 dBm", "-7 dBm", "-5 dBm", "-3 dBm", "-1 dBm", "0 dBm"]
                    tidx = int(Nbyte, 16)
                    res = res + "The Transmit Power byte is " + Nbyte + " which means that the Transmit Power of this tag is "
                    if tidx > 7:
                       res = res + "undefined"
                    else: 
                       res = res + powers[tidx]
                    res = res + "\n\n"
                if nbinStr[3] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Battery Voltage byte is " + Nbyte + " which means that the voltage level is "
                    bdict = {"F8":"3.3", "F0":"3.2", "E0":"3.1", "D0":"3.0", "C8":"2.95", "C0":"2.9", "B8":"2.85", "B0":"2.8", "A0":"2.75", "98":"2.7", "90":"2.65", "88":"2.6", "78":"2.5", "68":"2.4", "58":"2.3", "40":"2.2"}
                    if Nbyte in bdict:
                        res = res + bdict[Nbyte]
                    else:
                        y = 43095.36 + (2.496044 - 43095.36)/(1 + (float(int(Nbyte,16))/15116.6)**2.653468)
                        res = res + "around " + str(round(y,1))
                    res = res + "\n\n"
                if nbinStr[4] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Current Mode byte is " + Nbyte
                    res = res + "\n\n"
                if nbinStr[5] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "This byte is " + Nbyte + "and its functions are reserved for future use"
                    res = res + "\n\n"
                if nbinStr[6] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "This byte is " + Nbyte + "and its functions are reserved for future use"
                    res = res + "\n\n"
                if nbinStr[7] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Network Extension byte is " + Nbyte
                    res = res + "\n\n"            
            
            if binStr[1] == "1":
                GPIOByte = packet[pidx:pidx+2]
                if len(GPIOByte) < 2:
                    continue
                pidx = pidx + 2
                res = res + "The GPIO field is: " + GPIOByte + spacing + "The following report(s) are: "
                nList = ["Analog/Digital Config Report","I/O Config Report", "Digital Report","Analog Reference","Analog Report","RFU","RFU","RFU"]
                nbinStr= bin(int(GPIOByte,16))[2:]
                nbinStr = nbinStr.rjust(8,'0')
                idx = 0
                first = True
                for i in nbinStr:
                    comma = ", "
                    if first == True:
                        comma = ""
                    if i == "1":
                        res = res + comma + nList[idx]
                        first = False
                    idx = idx + 1
                res = res + "\n\n"
                if len(nbinStr) < 8:
                     continue
                if nbinStr[0] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Analog/Digital Config byte is " + Nbyte
                    pins = ["A7","A6","A5","A4","A3","A2","A1","A0"]
                    tbinStr = bin(int(Nbyte,16))[2:]
                    tbinStr = tbinStr.rjust(8,'0')
                    idx = 0
                    first = True
                    for i in tbinStr:
                        comma = ", "
                        if first == True:
                            comma = ""
                        if i == "1":
                            if first == True:
                                res = res + " which means the following pins are on: "
                            res = res + comma + pins[idx]
                            first = False
                        idx = idx + 1
                    if first == True:
                        res = res + " which means none of the pins are on"
                    res = res + "\n\n"
                if nbinStr[1] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The I/O Config byte is " + Nbyte 
                    pins = ["A7","A6","A5","A4","A3","A2","A1","A0"]
                    tbinStr = bin(int(Nbyte,16))[2:]
                    tbinStr = tbinStr.rjust(8,'0')
                    idx = 0
                    first = True
                    for i in tbinStr:
                        comma = ", "
                        if first == True:
                            comma = ""
                        if i == "1":
                            if first == True:
                                res = res + " which means the following pins are on: "
                            res = res + comma + pins[idx]
                            first = False
                        idx = idx + 1
                    if first == True:
                        res = res + " which means none of the pins are on"
                    res = res + "\n\n"
                if nbinStr[2] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Digital byte is " + Nbyte 
                    pins = ["D7","D6","D5","D4","D3","D2","D1","D0"]
                    tbinStr = bin(int(Nbyte,16))[2:]
                    tbinStr = tbinStr.rjust(8,'0')
                    idx = 0
                    first = True
                    for i in tbinStr:
                        comma = ", "
                        if first == True:
                            comma = ""
                        if i == "1":
                            if first == True:
                                res = res + " which means the following pins are on: "
                            res = res + comma + pins[idx]
                            first = False
                        idx = idx + 1
                    if first == True:
                        res = res + " which means none of the pins are on"
                    res = res + "\n\n"
                if nbinStr[3] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Analog Reference byte is " + Nbyte
                    pins = ["A7","A6","A5","A4","A3","A2","A1","A0"]
                    tbinStr = bin(int(Nbyte,16))[2:]
                    tbinStr = tbinStr.rjust(8,'0')
                    idx = 0
                    first = True
                    for i in tbinStr:
                        comma = ", "
                        if first == True:
                            comma = ""
                        if i == "1":
                            if first == True:
                                res = res + " which means the following pins are on: "
                            res = res + comma + pins[idx]
                            first = False
                        idx = idx + 1
                    if first == True:
                        res = res + " which means none of the pins are on"
                    res = res + "\n\n"
                if nbinStr[4] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "The Analog byte is " + Nbyte
                    pins = ["A7","A6","A5","A4","A3","A2","A1","A0"]
                    tbinStr = bin(int(Nbyte,16))[2:]
                    tbinStr = tbinStr.rjust(8,'0')
                    idx = 0
                    first = True
                    for i in tbinStr:
                        comma = ", "
                        if first == True:
                            comma = ""
                        if i == "1":
                            if first == True:
                                res = res + " which means the following pins are on: "
                            res = res + comma + pins[idx]
                            first = False
                        idx = idx + 1
                    if first == True:
                        res = res + " which means none of the pins are on"
                    res = res + "\n\n"
                if nbinStr[5] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "This byte is " + Nbyte + "and its functions are reserved for future use"
                    res = res + "\n\n"
                if nbinStr[6] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "This byte is " + Nbyte + "and its functions are reserved for future use"
                    res = res + "\n\n"
                if nbinStr[7] == "1":
                    Nbyte = packet[pidx:pidx+2]
                    if len(Nbyte) < 2:
                        continue
                    pidx = pidx+2
                    res = res + "This byte is " + Nbyte + "and its functions are reserved for future use"
                    res = res + "\n\n" 
         
            RSSI = packet[-2:]
            res = res + "The last field is: " + RSSI + spacing + "The signal strength is " + str(int(RSSI,16)) + "\n"
            res = res + "\n" 
    
            f.write(res)


################################################# START THE PROGRAM #################################################
input("\nPress any key to continue \n")


################################################# READY THE TELNET MODULES #################################################
ip0 = "192.168.1.129" # the bedroom base reader or SAFE
ip1 = "192.168.1.127" # the hallway base reader or WARNING
ip2 = "192.168.1.126" # the front door base reader or DANGER
port = 10001 # dont change this

tn0 = telnetlib.Telnet(ip0,port) # starting connection to base reader 0
dummy = tn0.read_very_eager()
tn0.close()
tn0 = telnetlib.Telnet(ip0,port)

tn1 = telnetlib.Telnet(ip1,port) # starting connection to base reader 1
dummy = tn1.read_very_eager()
tn1.close()
tn1 = telnetlib.Telnet(ip1,port)


tn2 = telnetlib.Telnet(ip2,port) # starting connection to base reader 2
dummy = tn2.read_very_eager()
tn2.close()
tn2 = telnetlib.Telnet(ip2,port)


################################################# RUN THE APP #################################################

danger = 0
recent = "empty"
rL = -1
buffer = 10
cmd = "py myFlask.py " # this is the command line that will call the server file
p = subprocess.Popen(cmd+'NO_SIGNAL') 

class IntervalW(Label): # THE MAIN APP
    def update(self, *args): # THIS METHOD WILL RUN EVERY <inc> seconds
        tn_read0 = str(tn0.read_very_eager()) # gets a list of commands from base reader 0 from the past <inc> seconds
        tn_read1 = str(tn1.read_very_eager()) # gets a list of commands from base reader 1 from the past <inc> seconds
        tn_read2 = str(tn2.read_very_eager()) # gets a list of commands from base reader 2 from the past <inc> seconds

        packets0 = tn_read0.split("r") # splits the string into a list
        packets1 = tn_read1.split("r")
        packets2 = tn_read2.split("r")
        print("=================================================")
        print("safe: " + str(len(packets0)))
        print("warning: " + str(len(packets1)))
        print("danger: " + str(len(packets2)))
        
        test =  str(datetime.datetime.now())[0:19]
        zdt = datetime.datetime.strptime(test, '%Y-%m-%d %H:%M:%S').strftime('%m-%d-%Y_%I:%M:%S')
        zone = "NA"
        global danger # getting the global files from outside this function to reader the datalog and zonelog files
        global rL
        global recent
        global buffer
        global tnow
        global tb
        global tend
        global tdate
        global f
        global workbook 
        global worksheet
        global completeName
        global filecount
        global xlcount
        global p
        if(len(packets0) == 1 and len(packets1) == 1 and len(packets2) == 1): # there is no signals from any base readers (length 1 means no signal according to my split)
            zone = "none"
            recent = "-"
            if rL == 0:
                self.text = "     NO SIGNAL" + "\n" +"LAST SEEN: " + recent + "\n" + time.asctime()
                self.font_size = 55
                self.color = (0,1,0.5,1)
            elif rL == 1:
                self.text = "     NO SIGNAL" +"\n" + "LAST SEEN: " + recent + "\n" + time.asctime()
                self.font_size = 55
                self.color = (1,1,0.5,1)
            elif rL == 2:
                self.text = "     NO SIGNAL" + "\n" +"LAST SEEN: " + recent + "\n" + time.asctime()
                self.font_size = 55
                self.color = (1,0.5,0,1)
            else:
                self.text = "    NO SIGNAL" + "\n" + time.asctime()
                self.font_size = 55
                self.color = (1.5,0.5,0.5,1)
                p.kill()
                p = subprocess.Popen(cmd+"3NO_SIGNAL")
        elif(len(packets0) == max(len(packets0),len(packets1),len(packets2))): # base reader bedroom has the most packets
            zone = "safe"
            recent = "BEDROOM"
            rL = 0
            self.text = "          " + recent + "\n" + time.asctime()
            self.font_size = 55
            self.color = (0,1,0,1)
            if danger >= 0:
                danger = danger - 1
            p.kill() # kills the current subprocess
            p = subprocess.Popen(cmd+"0BEDROOM") # new supprocess opens another python file myFlask.py that sends the message to the local server
        elif(len(packets2) == max(len(packets0),len(packets1),len(packets2))):# base reader front door has the most packets
            zone = "danger"
            recent = "FRONT DOOR"
            rL = 2
            self.text = "        " + recent + "!\n" + time.asctime()
            self.font_size = 55
            self.color = (1,0,0,1)
            if danger <= 5:
                danger = danger + 1
            p.kill()
            p = subprocess.Popen(cmd+"2FRONT_DOOR")# new supprocess opens another python file myFlask.py that sends the message to the local server

        else: # base reader hallway has the most packets
            zone = "warning"
            recent = "HALLWAY"
            rL = 1
            self.text = "         " + recent + "\n" + time.asctime()
            self.font_size = 55
            self.color = (1,1,0,1)
            if danger >= 0:
                danger = danger - 1
            p.kill()
            p = subprocess.Popen(cmd+"1HALLWAY")# new supprocess opens another python file myFlask.py that sends the message to the local server
        if danger >= 5:
            danger = 0
            print("notification")
            plays = subprocess.Popen([sys.executable, 'PlaySound.py'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT) # plays a sound
            notif = subprocess.Popen([sys.executable, 'Notification.py'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT) # turns on alert notification



        print("Danger queue is: " + str(danger))
        print("Current zone is: " + zone)

        tnow = datetime.datetime.now().time() # finish up the current data long and zone log files if <tb> seconds passed and then open up anotehr file
        dnow = datetime.datetime.today().strftime('%Y-%m-%d')
        if (tend >= tnow or tdate != dnow): 
            datalog(packets0,f, "safe", zdt[11:], zone)
            datalog(packets1,f, "warning", zdt[11:], zone)
            datalog(packets2,f, "danger", zdt[11:], zone)
            zonelog(zdt[:10],zdt[11:], zone, recent)
            tdate = dnow
        else:
            f.close()
            workbook.close()
            dt = datetime.datetime.now()
            dtnm = str(dt)[0:19]\

            test =  str(datetime.datetime.now())[0:19]
            endTime = datetime.datetime.strptime(test, '%Y-%m-%d %H:%M:%S').strftime('%m-%d-%Y_%H.%M.%S')
            eline = "The end time is " + endTime[11:] + "\n"
            replace_line(completeName,3,eline)

            fc = open(r"C:\Users\wandering\Desktop\WanderProj\DataLog\counter.txt","w+")
            fc.write(str(filecount+1))
            fc.close()

            (f, completeName, filecount, oname) = readyDL()
            worksheet,workbook = readyZL()
            xlcount = 1
            tend = addSecs(tnow,tb)



class WanderApp(App): # call the file
    def build(self):
        self.title = 'Wandering Emulation V3'
        base = IntervalW()
        Clock.schedule_interval(base.update, inc)
        return base



if __name__ == "__main__":
    WanderApp().run()


################################################# CLOSE THE PROGRAM #################################################

# close all the files


f.close()
workbook.close()

dt = datetime.datetime.now()
dtnm = str(dt)[0:19]\

test =  str(datetime.datetime.now())[0:19]
endTime = datetime.datetime.strptime(test, '%Y-%m-%d %H:%M:%S').strftime('%m-%d-%Y_%H.%M.%S')
eline = "The end time is " + endTime[11:] + "\n"
replace_line(completeName,3,eline)

fc = open(r"C:\Users\wandering\Desktop\WanderProj\DataLog\counter.txt","w+")
fc.write(str(filecount+1))

fc.close()

print("The output file is: ", oname)

end = time.time()
elapsed = end - start
print("This program took " + str(round(elapsed,2)) + " seconds to run")