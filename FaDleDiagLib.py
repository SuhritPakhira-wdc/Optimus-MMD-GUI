import os, sys
#import CTFServiceWrapper
import CTFServiceWrapper as PyServiceWrap
import ScsiCmdWrapper as sw
#from ScsiCmdWrapper import AtaRegister,ATA_COMMAND_DIRECTION,GetByte,DrvLba,GetDeviceFromSession,AtaOpcode
import getDeviceHandle as dg
import csv
from enum import Enum
from enum import IntEnum
import datetime as datetime_
import subprocess
import time

MODEL_NUMBER_OFFSET = 0x36
MODEL_NUMBER_LENGTH = 40

#Diag opcode constants
CMD1 = 0xC1
CMD2 = 0xC2
CMD3 = 0xC3
CMD4 = 0xC4
CMD5 = 0xC5
CMD6 = 0xC6
CMD7 = 0xC7
CMD8 = 0xC8
CMD9 = 0xC9
CMDEND = 0xEE

ADDR1 = 0xA1
ADDR2 = 0xA2
ADDR3 = 0xA3
ADDR4 = 0xA4
ADDR5 = 0xA5
ADDR6 = 0xA6

WAIT_RB = 0xB0

#Data in to NAND
DATA_IN = 0xD1
DATA_IN_R = 0xD2 #Repeat
DATA_IN_E = 0xD3

#data out from NAND
DATA_OUT = 0xD0

# 0x10c5 is maximum =  4293 * 1000 * 1000 32 bit DELAY
DELAY = 0xDE


#Global variables
x3_page_size = 18336
fmu_size = x3_page_size/4
ldpc_max_decode = 600 #Todo find actual 2SB max bits
sata_sector_size = 512
numOfSectorsSP = (x3_page_size/sata_sector_size) + 1
numOfSectorsSPSeq = numOfSectorsSP + 1
no_of_fmus = 4
g_Verbose = 1

#Flash command constants
CmdReadAddr = 0x00
CmdAccessLP = 0x01
CmdAccessMP = 0x02
CmdAccessUP = 0x03
CmdReadColAddr = 0x05
CmdAutoProgram = 0x10
CmdAutoProgramDummy = 0x11
CmdCacheProgram = 0x15
CmdNextCellOnWL = 0x1A
CmdArrayRead = 0x30
CmdMulPlaneRead = 0x32
CmdDynRead = 0x5D
CmdLoadAddr = 0x60
CmdStatus6A = 0x6A
CmdStatus70 = 0x70
CmdStatus72 = 0x72
CmdStatus77 = 0x77
CmdWriteData = 0x80
CmdWriteColAddr = 0x85
CmdAutoErase = 0xD0
CmdRegRead = 0xE0
CmdManualPOR = 0xFD
CmdResetAll = 0xFF

class BlkType(Enum):
    SLC = 0
    TLC = 1

class PlaneType(Enum):
    single = 0
    dual = 1

class PageType(IntEnum):
     SLC = 0
     LP = 1
     MP = 2
     UP = 3
     TLC = 4

class FlashInfoClass(object):
    def __init__(self):
        self.fim = 0
        self.ce = 0
        self.die = 0
        self.block_no1 = 0 #Referred for Single plane
        self.wl = 0
        self.string = 0
        self.block_no2 = 0 #Referred for Dual plane
        self.PageType = PageType.SLC

class CustomShiftClass(object):
    def __init__(self):
        self.AShift = 0
        self.BShift = 0
        self.CShift = 0
        self.DShift = 0 #Referred for Single plane
        self.EShift = 0
        self.FShift = 0
        self.GShift = 0
  
class FlashAttributesClass(object):
    def __init__(self):
        self.BlkType = BlkType.SLC
        self.PlaneType = PlaneType.single
        self.FDReset = 1
        self.ErrorInjection = 0
        self.ParamAddr = 0
        self.ParamValue = 0
        self.Pattern = 0xAA55 
        self.Payload = None #Higher precedence over pattern, can't mix pattern and payload for dual plane operation. 
        self.isVerbose = 1
        self.FlashReset = 1
        self.isFBC = 1

class csvWriterClass(object):
    def __init__(self):
        self.operation = ""
        self.fim = 0
        self.ce = 0
        self.die = 0
        self.block = 0
        self.string = 0
        self.wl = 0
        self.pagetype = PageType.SLC.name
        self.voltage = 0
        self.population = 0
        self.result = "Pass"
        self.fbc_fmu = [0,0,0,0]
        self.program_loop_count = 0

    def WriteRows(self, writer):
        tup = (self.operation, self.fim, self.ce, self.die, self.block, self.string, self.wl, self.pagetype, self.voltage, self.population, self.result, self.fbc_fmu[0], self.fbc_fmu[1], self.fbc_fmu[2], self.fbc_fmu[3], self.program_loop_count)
        writer.writerow(tup)
    
    def CreateCsvFile(self, csvfilename):
        self.outFile = None
        if csvfilename == None:
            csvfilename = "FATool_Log_" + str(datetime_.datetime.now().strftime("%d%m%Y-%H%M%S")) + ".csv" 
            self.outFile = open(os.path.join(os.getcwd(),  csvfilename), 'ab+')
            self.writer = csv.writer(self.outFile, delimiter=',')
            title = ('Operation', 'FIM', 'CE', 'Die','Block', 'String', 'WL', 'Page type', 'Voltage', 'Population', 'Result', 'FMU0 FBC', 'FMU1 FBC', 'FMU2 FBC', 'FMU3 FBC', 'Program/Erase Loop Count')
            self.writer.writerow(title)            
        else:
            csvfilenam_h = csvfilename.split(".")
            self.outFile = open(os.path.join(os.getcwd(),  csvfilenam_h[0] + "_" + str(datetime_.datetime.now().strftime("%d%m%Y-%H%M%S")) + ".csv"), 'wb+') 
            self.writer = csv.writer(self.outFile, delimiter=',')
            title = ('Operation', 'FIM', 'CE', 'Die','Block', 'String', 'WL', 'Page type', 'Voltage', 'Population', 'Result', 'FMU0 FBC', 'FMU1 FBC', 'FMU2 FBC', 'FMU3 FBC', 'Program/Erase Loop Count')
            self.writer.writerow(title)
                                
        
        return [self.outFile, self.writer]
        

class diagCmdLibClass(object):
        
    def __init__(self, dHandle = 0, dlemode = 0, csvfilename = None, botFilepath = "", ):
        if dHandle == 1:
            self.diagobj = dg.getDeviceHandleClass()
            self.diagobj.OpenAndEnumerateDevice()
            if dlemode == 1:
                if botFilepath == "":
                    print "Provide botfile path"
                else:
                    self.diagobj.EnterDleMode(dlemode, botFilepath)
                    
        csvobj = csvWriterClass()
        retlist = csvobj.CreateCsvFile(csvfilename)
        
        self.outCsvFile = retlist[0]
        self.writer = retlist[1]

    # Deleting (Calling destructor)
    def __del__(self):
        self.outCsvFile.close()
        #if g_Verbose:
        print('Destructor called.')
    
    def ToAddr(self, die, block, wl, string, column):
        
        plane = block & 0x1
        block_no = int(block/2)

        #die_i= int(die, 16)
        #block_i= int(block, 16)
        #plane_i= int(plane, 16)
        #string_i= int(string, 16)
        #column_i= int(column, 16)
        #wl_i= int(wl, 16)

        die_b= bin(die)
        block_b= bin(block_no)
        plane_b= bin(plane)
        string_b= bin(string)
        column_b= bin(column)
        wl_b= bin(wl)

        #BiCs5 address conversion
        while(len(die_b)<5):        #length of die 2+3
            die_b = die_b[:2] +'0'+die_b[2:]
        while(len(string_b)<4):     #length of string 2+2
            string_b = string_b[:2] +'0'+string_b[2:]
        while(len(column_b)<17):    #length of column 2+15
            column_b = column_b[:2] +'0'+column_b[2:]

        if die<0 or die>7:  #Die input check
            print("Die: Invalid Value")
        elif column<0 or column>32767:  #column input check
            print("Column: Invalid Value")
        elif plane<0 or plane>1:    #plane input check
            print("Plane: Invalid Value")
        elif string<0 or string>3:  #string input check
            print("String: Invalid Value")
        elif (wl<0 or wl>111):
            print("Word Line: Invalid Value")
        elif (block_no<0 or block_no>4095):
            print("Block: Invalid Value")
        else:
            while(len(block_b)<14):
                block_b = block_b[:2] +'0'+block_b[2:]
            blk_phy_b= die_b[2:] + block_b[2:] + plane_b[2:]
            blk_pl_b= block_b[2:] + plane_b[2:]

            while(len(wl_b)<9):
                wl_b = wl_b[:2] +'0'+wl_b[2:]
            add1= column_b[9:]
            addr1_h = int(add1, 2)
            add2= column_b[2:9]
            addr2_h = int(add2, 2)
            add3= wl_b[3:]+string_b[2:]
            addr3_h = int(add3, 2)
            add4= block_b[8:]+plane_b[2]+wl_b[2]
            addr4_h = int(add4, 2)
            add5= die_b[3:]+block_b[2:8]
            addr5_h = int(add5, 2)
            add6= die_b[2] # extrac last bit from 6th cycle.
            addr6_h = int(add6, 2)
			
			
			
            blk_phy_i = int(blk_phy_b, 2)
            blk_phy_h= hex(blk_phy_i)
            blk_pl_i = int(blk_pl_b, 2)
            blk_pl_h= hex(blk_pl_i)

            if g_Verbose:
                print("Address Byte 1= \t {}".format(hex(addr1_h)))
                print("Address Byte 2= \t {}".format(hex(addr2_h)))
                print("Address Byte 3= \t {}".format(hex(addr3_h)))
                print("Address Byte 4= \t {}".format(hex(addr4_h)))
                print("Address Byte 5= \t {}".format(hex(addr5_h)))
                print("Address Byte 6= \t {}".format(hex(addr6_h)))
                #print("Block number in hex( w/ plane bit)= {}".format(blk_pl_h))
                #print("Decimal= {}".format(blk_pl_i))
                #print("Physical block No. in hex (NanoNT)= {}".format(blk_phy_h))
                #print("Decimal= {}".format(blk_phy_i))
            return [addr1_h, addr2_h, addr3_h, addr4_h, addr5_h, addr6_h]
    
    def ReadEC40WL(self):
        print("ReadEC40WL")

        seq = [CMD2, 0xF1, 0xFD, DELAY, 0x0, 0x1, CMDEND, CMD2, 0xF1, 0x70, CMDEND, CMD1, 0xEC, ADDR1, 0x40, WAIT_RB, DATA_OUT, 0x47, 0xA0, CMDEND]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        numOfSectors = 36
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        retbuf.WriteToFile("Read_EC40WL.bin", numOfSectors*512)
        return retbuf
    
    def EraseUserrom0(self):
        
        print("EraseUserrom0")

        #Erase Userrom Plane-0
        seq = [CMD2, 0xF1, 0xFD, DELAY, 0x13, 0x88, WAIT_RB, CMDEND, CMD6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD6, 0xF1, 0x99, 0x5A, 0xBE, 0xA2, 0x60, ADDR3, 0x00, 0x00, 0x00, CMD1, 0xD0, DELAY, 0x27, 0x10, WAIT_RB, 0xEE, CMD1, 0xFF, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return
    
    def ProgramUserrom0(self, urompayload):
        #Program Userrom Plane-0

        print("ProgramUserrom0")

        seq = [CMD2, 0xF1, 0xFD, DELAY, 0x13,  0x88, WAIT_RB, CMDEND, CMD3, 0x61, 0x40, 0x8F, CMDEND, CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMDEND, CMD6, 0xF1, 0x5A, 0xBE, 0xC3, 0xA2, 0x80, ADDR5, 0x00, 0x00, 0x90, 0x01, 0x00, DELAY, 0x0, 0x5, DATA_IN_E, 0x47, 0xA0, CMDEND, 0xC1, 0x10, 0xDE, 0x27, 0x10, WAIT_RB, CMDEND, CMD1, 0xFF, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        with open(urompayload, "rb") as fptr:
            urpstr = fptr.read()
        seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        numOfSectors = 37
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        #seqbuf.FillFromFile("userrom_writeseq_payload.bin", False)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return

    def FBC_per_FMU_change(self, buf, fbc_count): 
        """
        Description: FBC_Count_Func
        Parameters:
            @param: buf = Takes PyServiceWrap.Buffer.CreateBuffer 
            @param: pattern = 2 byte pattern
        Returns: fbc_fmu list
        Exceptions: None
        """
        fmu_index = 0
        
        while fmu_index < no_of_fmus:
            idx = 100
            fbc_count_fmu = 0
            while idx < fmu_size and fbc_count_fmu < fbc_count:
                retdata = buf.GetTwoBytesToInt(idx + (fmu_size * fmu_index) )
                buf.SetTwoBytes(idx + (fmu_size * fmu_index), 0)  
                idx = idx + 2
                while(retdata):
                    fbc_count_fmu += 1
                    retdata &= retdata-1
            fmu_index += 1
        
        return buf
    

    def FBC_Count_Func(self, buf, pattern, payload): 
        """
        Description: FBC_Count_Func
        Parameters:
            @param: buf = Takes PyServiceWrap.Buffer.CreateBuffer 
            @param: pattern = 2 byte pattern
        Returns: fbc_fmu list
        Exceptions: None
        """
        fmu_index = 0
        fbc_fmu = [0, 0, 0, 0]

        if not payload == None:
            while fmu_index < no_of_fmus:
                idx = 0
                fbc_count = 0
                while idx < fmu_size:
                    retdata = buf.GetTwoBytesToInt(idx + (fmu_size * fmu_index) ) 
                    payloaddata = payload.GetTwoBytesToInt(idx + (fmu_size * fmu_index) ) 
                    idx = idx + 2
                    if not retdata == payloaddata:
                        diff = payloaddata ^ retdata
                        while(diff):
                            fbc_count += 1
                            diff &= diff-1
                if g_Verbose:
                    print( "FMU" + str(fmu_index) + " FBC " + str(fbc_count))
                fbc_fmu[fmu_index] = fbc_count
                fmu_index += 1           
        elif not pattern == None:    
            while fmu_index < no_of_fmus:
                idx = 0
                fbc_count = 0
                while idx < fmu_size:
                    retdata = buf.GetTwoBytesToInt(idx + (fmu_size * fmu_index) )  
                    idx = idx + 2
                    if not retdata == pattern:
                        diff = pattern ^ retdata
                        while(diff):
                            fbc_count += 1
                            diff &= diff-1
                if g_Verbose:
                    print( "FMU" + str(fmu_index) + " FBC " + str(fbc_count))
                fbc_fmu[fmu_index] = fbc_count
                fmu_index += 1
        else:
            raise AssertionError("Either pattern or AttrObj.payload must be valid one")

        
        return fbc_fmu
    
    def Manual_POR_FDh(self, fim, ce, die):
        
        die_no = 0xF0 | (die + 1) 

        seq = [CMD2, die_no, 0xFD, DELAY, 0x0, 0x1, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        #seqbuf.Dump()
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return
    
    def Flash_CMD_Reset(self, fim, ce, die):
        die_no = 0xF0 | (die + 1) 
        seq = [CMD2, die_no, 0xFF, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return

    #[Todo] : CreateBuffer cleanup
    def SLC_Read_Page(self, FIObj, AttrObj):
        """
        Description: SLC_Read_Page
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: retbuf, Read data of FIObj.block_no1
        Exceptions: None
        """
        if AttrObj.isVerbose:
            print("SLC_Read_Page")

        #defaults
        AttrObj.BlkType = BlkType.SLC
        AttrObj.PlaneType = PlaneType.single
        FIObj.PageType = PageType.SLC

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)  
		
        print("CE = " + str(FIObj.ce) + ", FIM = " + str(FIObj.fim) + ", Die = " + str(FIObj.die) + ", Block = " + str(FIObj.block_no1)) 
		
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        seq = [CMD2, die_no, CmdStatus70, CMD3, die_no, 0xA2, CmdReadAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdArrayRead, WAIT_RB, CMD2, die_no, CmdStatus70, CMD1, CmdReadColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]        
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die) 
        
        PayloadBuf = None
        if AttrObj.isFBC:
            if not AttrObj.Payload == None:
                PayloadBuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
                #filebuf.FillFromFile(AttrObj.Payload, False)
                fptr =  open(AttrObj.Payload, "rb")
                if fptr:
                    urpstr = fptr.read(x3_page_size)
                    seq = [int(hex(ord(st)),16) for st in urpstr]
                    for idx, sq in enumerate(seq):
                        PayloadBuf.SetByte(idx, sq)                   

        if AttrObj.isFBC:
            fbc_fmu = self.FBC_Count_Func(retbuf, AttrObj.Pattern, PayloadBuf)
        else:
            fbc_fmu = [0,0,0,0]

        if AttrObj.isVerbose:
            retbuf.WriteToFile("SLC_Read_Page.bin", x3_page_size) 

        if self.outCsvFile:
            csvobj = csvWriterClass()
            csvobj.fim = FIObj.fim
            csvobj.ce = FIObj.ce
            csvobj.die = FIObj.die
            csvobj.block = FIObj.block_no1
            csvobj.wl = FIObj.wl
            csvobj.string = FIObj.string
            
            csvobj.pagetype = FIObj.PageType.name
            csvobj.operation = 'SLC_Read_Page'
            csvobj.fbc_fmu = fbc_fmu
           
            if fbc_fmu[0] > ldpc_max_decode or fbc_fmu[1] > ldpc_max_decode or fbc_fmu[2] > ldpc_max_decode  or fbc_fmu[3] > ldpc_max_decode:
                 csvobj.result = "Fail"

            csvobj.WriteRows(self.writer)

        return retbuf    

    def SLC_Read_DualPlane(self, FIObj, AttrObj):
        """
        Description: SLC_Read_Page
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: retbuf(data of FIObj.block_no1) and retbuf1(data of FIObj.block_no2)
        Exceptions: None
        """ 
        if AttrObj.isVerbose:
            print("SLC_Read_DualPlane")

        AttrObj.BlkType = BlkType.SLC
        AttrObj.PlaneType = PlaneType.dual
        FIObj.PageType = PageType.SLC

        plane0 = FIObj.block_no1%2
        plane1 = FIObj.block_no2%2

        if plane0 == plane1:
            print("Block number's not meeting for dual plane program operation")

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)

        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        b1_addr = self.ToAddr(FIObj.die, FIObj.block_no2, FIObj.wl, FIObj.string, 0)

        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        seq = [CMD2, die_no, CmdStatus70, CMD3, die_no, 0xA2, CmdLoadAddr, ADDR4, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdLoadAddr, ADDR4, b1_addr[2], b1_addr[3], b1_addr[4], b0_addr[5], CMD1, CmdArrayRead, WAIT_RB, CMD1, CmdReadColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)

        PayloadBuf = None
        if AttrObj.isFBC:
            if not AttrObj.Payload == None:
                PayloadBuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
                #filebuf.FillFromFile(AttrObj.Payload, False)
                fptr =  open(AttrObj.Payload, "rb")
                if fptr:
                    urpstr = fptr.read(x3_page_size)
                    seq = [int(hex(ord(st)),16) for st in urpstr]
                    for idx, sq in enumerate(seq):
                        PayloadBuf.SetByte(idx, sq)         

        if AttrObj.isFBC:
            b0_fbc_fmu = self.FBC_Count_Func(retbuf, AttrObj.Pattern, PayloadBuf)
        else:
            b0_fbc_fmu = [0, 0, 0, 0]

        if AttrObj.isVerbose:
            retbuf.WriteToFile("SLC_Read_DualPlane1.bin", x3_page_size)

        seq = [CMD1, CmdReadColAddr, ADDR5, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]

        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf1 = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die) 

        #retbuf.Append(retbuf1)
        
        PayloadBuf = None
        if AttrObj.isFBC:
            if not AttrObj.Payload == None:
                PayloadBuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
                if fptr:
                    urpstr = fptr.read(x3_page_size)
                    seq = [int(hex(ord(st)),16) for st in urpstr]
                    for idx, sq in enumerate(seq):
                        PayloadBuf.SetByte(idx, sq)
                    
        if AttrObj.isFBC:
            b1_fbc_fmu = self.FBC_Count_Func(retbuf1, AttrObj.Pattern, PayloadBuf)
        else:
            b1_fbc_fmu = [0, 0, 0, 0]

        if AttrObj.isVerbose:
            retbuf1.WriteToFile("SLC_Read_DualPlane2.bin", x3_page_size)  

        if self.outCsvFile:
             
            csvobj1 = csvWriterClass()
            csvobj2 = csvWriterClass()

            csvobj1.fim = csvobj2.fim = FIObj.fim
            csvobj1.ce = csvobj2.ce = FIObj.ce
            csvobj1.die = csvobj2.die = FIObj.die
            csvobj1.wl= csvobj2.wl = FIObj.wl
            csvobj1.string = csvobj2.string = FIObj.string
            csvobj1.operation = csvobj2.operation = 'SLC_Read_DualPlane'
            csvobj1.pagetype = csvobj2.pagetype = FIObj.PageType.name
            
            csvobj1.block = FIObj.block_no1
            csvobj2.block = FIObj.block_no2
            
            csvobj1.fbc_fmu = b0_fbc_fmu
            if b0_fbc_fmu[0] > ldpc_max_decode or b0_fbc_fmu[1] > ldpc_max_decode or b0_fbc_fmu[2] > ldpc_max_decode  or b0_fbc_fmu[3] > ldpc_max_decode:
                 csvobj1.result = "Fail"

            csvobj2.fbc_fmu = b0_fbc_fmu
            if b1_fbc_fmu[0] > ldpc_max_decode or b1_fbc_fmu[1] > ldpc_max_decode or b1_fbc_fmu[2] > ldpc_max_decode  or b1_fbc_fmu[3] > ldpc_max_decode:
                 csvobj2.result = "Fail"

            csvobj1.WriteRows(self.writer)
            csvobj2.WriteRows(self.writer)

        return [retbuf, retbuf1]  
                                                            
    def TLC_Read_Page(self, FIObj, AttrObj):
        """
        Description: TLC_Read_Page
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: retbuf, Read data of FIObj.block_no1
        Exceptions: None
        """
        if AttrObj.isVerbose:
            print("TLC_Read_Page")
            
        global g_Verbose
        g_Verbose = AttrObj.isVerbose
        
        AttrObj.BlkType = BlkType.TLC
        AttrObj.PlaneType = PlaneType.single

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)
		
        print("CE = " + str(FIObj.ce) + ", FIM = " + str(FIObj.fim) + ", Die = " + str(FIObj.die) + ", Block = " + str(FIObj.block_no1))
		
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
       
        if AttrObj.FDReset == 1:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)
        
        
        seq = [CMD4, die_no, CmdDynRead, int(FIObj.PageType), CmdReadAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdArrayRead, WAIT_RB, CMD1, CmdReadColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]        
        
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        
        PayloadBuf = None
        if AttrObj.isFBC:
            if not AttrObj.Payload == None:
                PayloadBuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
                #filebuf.FillFromFile(AttrObj.Payload, False)
                fptr =  open(AttrObj.Payload, "rb")
                if fptr:
                    urpstr = fptr.read(x3_page_size)
                    seq = [int(hex(ord(st)),16) for st in urpstr]
                    for idx, sq in enumerate(seq):
                        PayloadBuf.SetByte(idx, sq)                    
        
        if AttrObj.isFBC:
            fbc_fmu = self.FBC_Count_Func(retbuf, AttrObj.Pattern, PayloadBuf)
        else:
            fbc_fmu = [0,0,0,0]        

        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)

        if AttrObj.isVerbose:
            retbuf.WriteToFile("TLC_Read_Page_" + FIObj.PageType.name + ".bin", x3_page_size) 

        if self.outCsvFile:

            csvobj1 = csvWriterClass()

            csvobj1.fim = FIObj.fim
            csvobj1.ce = FIObj.ce
            csvobj1.die = FIObj.die
            csvobj1.wl = FIObj.wl
            csvobj1.string = FIObj.string
            csvobj1.operation = 'TLC_Read_Page'
            csvobj1.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            csvobj1.fbc_fmu = fbc_fmu
            
            if fbc_fmu[0] > ldpc_max_decode or fbc_fmu[1] > ldpc_max_decode or fbc_fmu[2] > ldpc_max_decode  or fbc_fmu[3] > ldpc_max_decode:
                 csvobj1.result = "Fail"
            csvobj1.WriteRows(self.writer)
        return retbuf

    def TLC_Read_DualPlane(self, FIObj, AttrObj): 
        """
        Description: TLC_Read_Page
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: retbuf(data of FIObj.block_no1) and retbuf1(data of FIObj.block_no2)
        Exceptions: None
        """
        if AttrObj.isVerbose:
            print("TLC_Read_DualPlaneNonCache")
        
        AttrObj.BlkType = BlkType.TLC
        AttrObj.PlaneType = PlaneType.dual
        
        plane0 = FIObj.block_no1%2
        plane1 = FIObj.block_no2%2

        if plane0 == plane1:
            print("Block number's not meeting for dual plane program operation")

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)

        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        b1_addr = self.ToAddr(FIObj.die, FIObj.block_no2, FIObj.wl, FIObj.string, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        seq = [CMD4, die_no, CmdDynRead, int(FIObj.PageType), CmdReadAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdMulPlaneRead, WAIT_RB, CMD3, CmdDynRead, int(FIObj.PageType), CmdReadAddr, ADDR5, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], CMD1, CmdArrayRead, WAIT_RB, CMDEND, 
        CMD1, CmdReadColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND] 
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        
        PayloadBuf = None
        if not AttrObj.Payload == None:
            PayloadBuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
            #filebuf.FillFromFile(AttrObj.Payload, False)
            fptr =  open(AttrObj.Payload, "rb")
            if fptr:
                urpstr = fptr.read(x3_page_size)
                seq = [int(hex(ord(st)),16) for st in urpstr]
                for idx, sq in enumerate(seq):
                    PayloadBuf.SetByte(idx, sq)  

        b0_fbc_fmu = self.FBC_Count_Func(retbuf, AttrObj.Pattern, PayloadBuf)

        if AttrObj.isVerbose:
            retbuf.WriteToFile("TLC_Read_Page_" + FIObj.PageType.name + "1.bin" , x3_page_size)    

        seq = [CMD1, CmdReadColAddr, ADDR5, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
        
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1) 

        buf1 = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf1 = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)        
        
        PayloadBuf = None
        if not AttrObj.Payload == None:
            PayloadBuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
            if fptr:
                urpstr = fptr.read(x3_page_size)
                seq = [int(hex(ord(st)),16) for st in urpstr]
                for idx, sq in enumerate(seq):
                    PayloadBuf.SetByte(idx, sq)  

        b1_fbc_fmu = self.FBC_Count_Func(retbuf1, AttrObj.Pattern, PayloadBuf)
        #retbuf.Append(retbuf1) #[Todo] API do validation Destructor call failing if we append buffer
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die) 

        if AttrObj.isVerbose:
            retbuf1.WriteToFile("TLC_Read_Page_" + FIObj.PageType.name + "2.bin", x3_page_size)

        if self.outCsvFile:     
            csvobj1 = csvWriterClass()
            csvobj2 = csvWriterClass()

            csvobj1.fim = csvobj2.fim = FIObj.fim
            csvobj1.ce = csvobj2.ce = FIObj.ce
            csvobj1.die = csvobj2.die = FIObj.die
            csvobj1.wl= csvobj2.wl = FIObj.wl
            csvobj1.string = csvobj2.string = FIObj.string
            csvobj1.operation = csvobj2.operation = 'TLC_Read_DualPlane'
            csvobj1.pagetype = csvobj2.pagetype = FIObj.PageType.name
            
            csvobj1.block = FIObj.block_no1
            csvobj2.block = FIObj.block_no2
            
            csvobj1.fbc_fmu = b0_fbc_fmu
            if b0_fbc_fmu[0] > ldpc_max_decode or b0_fbc_fmu[1] > ldpc_max_decode or b0_fbc_fmu[2] > ldpc_max_decode  or b0_fbc_fmu[3] > ldpc_max_decode:
                 csvobj1.result = "Fail"

            csvobj2.fbc_fmu = b1_fbc_fmu
            if b1_fbc_fmu[0] > ldpc_max_decode or b1_fbc_fmu[1] > ldpc_max_decode or b1_fbc_fmu[2] > ldpc_max_decode  or b1_fbc_fmu[3] > ldpc_max_decode:
                 csvobj2.result = "Fail"

            csvobj1.WriteRows(self.writer)
            csvobj2.WriteRows(self.writer)

        return [retbuf, retbuf1]    

    def EraseBlock_Single(self, FIObj, AttrObj):
        """
        Description: EraseBlock_Single
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        ret = True
        print("CE = " + str(FIObj.ce) + ", FIM = " + str(FIObj.fim) + ", Die = " + str(FIObj.die) + ", Block = " + str(FIObj.block_no1))         
        if AttrObj.isVerbose:
            print("EraseBlock_Single")
        
        AttrObj.PlaneType = PlaneType.single

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1) 

		
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, 0, 0, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection
            print("Get param value = \t {}".format(hex(value)))            

            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection
            print("Set param value = \t {}".format(hex(value)))

        if AttrObj.BlkType == BlkType.SLC: # SLC
            print("SLC Erase")
            seq = [CMD3, die_no, 0xA2, CmdLoadAddr, ADDR4, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, CMD1, CmdAutoErase, DELAY, 0x0, 0x1, WAIT_RB, CMDEND]
        elif AttrObj.BlkType == BlkType.TLC: # TLC:
            print("TLC Erase")
            seq = [CMD2, die_no, CmdLoadAddr, ADDR4, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, CMD1, CmdAutoErase, DELAY, 0x0, 0x1, WAIT_RB, CMDEND]
            
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        retbyte = self.StatusRead(FIObj.die, CmdStatus70)
        print('Erase Done')
        if not retbyte == 0xE0:
            for i in range(10):
                if AttrObj.BlkType == BlkType.SLC and retbyte != 0xE4:
                   retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                if AttrObj.BlkType == BlkType.TLC and retbyte != 0xE1:
                   retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                else:
                    break

        if self.outCsvFile:
            csvobj1 = csvWriterClass()
            csvobj1.operation = 'Erase_Block'
            csvobj1.fim = FIObj.fim
            csvobj1.ce = FIObj.ce
            csvobj1.die =  FIObj.die
            csvobj1.block = FIObj.block_no1
            csvobj1.pagetype = AttrObj.BlkType.name
            csvobj1.block = FIObj.block_no1
            
            if retbyte != 0xE0:
                ret = False
                csvobj1.result = "Fail"
                csvobj1.program_loop_count = self.GetLoopCount(FIObj.die, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5])
                    
            csvobj1.WriteRows(self.writer) 
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)
        return ret

    def EraseBlock_Dual(self, FIObj, AttrObj):
        """
        Description: EraseBlock
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        ret = True 

        if AttrObj.isVerbose:
            print("EraseBlock Dual")
        
        #SLC Error Injection : 0x5D, 0x17 value
        #TLC Error Injection 0x5C : Value = 0x17        

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)        
        
        
        # condition plane check
        if AttrObj.PlaneType == PlaneType.dual: 
            plane0 = FIObj.block_no1%2
            plane1 = FIObj.block_no2%2

            if plane0 == plane1:
                print("Block number's not meeting for dual plane program operation")

        if not FIObj.block_no1 == None:
            b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, 0, 0, 0)
            
        if not FIObj.block_no2 == None:
            b1_addr = self.ToAddr(FIObj.die, FIObj.block_no2, 0, 0, 0)

        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)
        
        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection
            print("Get param value = \t {}".format(hex(value)))            

            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection
            print("Set param value = \t {}".format(hex(value)))
        
        if AttrObj.BlkType == BlkType.SLC: # SLC
            if AttrObj.PlaneType == PlaneType.dual: #dual plane
                seq = [CMD3, die_no, 0xA2, CmdLoadAddr, ADDR4, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, CMD1, CmdLoadAddr, ADDR4, b1_addr[2], b1_addr[3], b1_addr[4], b0_addr[5], CMD1, CmdAutoErase, DELAY, 0x0, 0x1, WAIT_RB, CMDEND]
        elif AttrObj.BlkType == BlkType.TLC: # TLC:
            if AttrObj.PlaneType == PlaneType.dual: #dual plane:
                seq = [CMD2, die_no, CmdLoadAddr, ADDR4, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, CMD1, CmdLoadAddr, ADDR4, b1_addr[2], b1_addr[3], b1_addr[4], b0_addr[5], CMD1, CmdAutoErase, DELAY, 0x0, 0x1, WAIT_RB, CMDEND]
        
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        retbyte = self.StatusRead(FIObj.die, CmdStatus70)
        retbyte = self.StatusRead(FIObj.die, CmdStatus70)
        if not retbyte == 0xE0:
            for i in range(10):
                if AttrObj.BlkType == BlkType.SLC and retbyte != 0xE4:
                   retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                if AttrObj.BlkType == BlkType.TLC and retbyte != 0xE1:
                   retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                else:
                    break
        
        if self.outCsvFile:
            csvobj1 = csvWriterClass()
            csvobj1.operation = 'Erase_Block'
            csvobj1.fim = FIObj.fim
            csvobj1.ce = FIObj.ce
            csvobj1.die = FIObj.die
            csvobj1.block = FIObj.block_no1
            csvobj1.pagetype = AttrObj.BlkType.name

            if AttrObj.PlaneType == PlaneType.dual:
                csvobj2 = csvWriterClass()
                csvobj2.operation = 'Erase_Block'
                csvobj2.fim = FIObj.fim
                csvobj2.ce = FIObj.ce
                csvobj2.die = FIObj.die
                csvobj2.block = FIObj.block_no2
                csvobj2.pagetype = AttrObj.BlkType.name
            
            if retbyte != 0xE0:
                ret = False
                if AttrObj.BlkType == BlkType.SLC:
                    plane = (self.StatusRead(FIObj.die, 0x72) & 0x6)
                if AttrObj.BlkType == BlkType.TLC:
                    plane = (self.StatusRead(FIObj.die, 0x71) & 0x6)
                
                if plane & 0x02: #plane0 fails
                    if FIObj.block_no1%2 == 0: #checking even plane
                        csvobj1.result =  "Fail"
                        csvobj1.program_loop_count = self.GetLoopCount(FIObj.die, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5])
                    elif FIObj.block_no2%2 == 0:
                        csvobj2.result =  "Fail"
                        csvobj2.program_loop_count(self.GetLoopCount(FIObj.die, b1_addr[2], b1_addr[3], b1_addr[4], b0_addr[5]))
                
                if plane & 0x04: #plane1 fails
                    if FIObj.block_no1%2 == 1: #checking odd plane
                        csvobj1.result =  "Fail"
                        csvobj1.program_loop_count = self.GetLoopCount(FIObj.die, b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5])
                    elif FIObj.block_no2%2 == 1:
                        csvobj2.result =  "Fail"
                        csvobj2.program_loop_count = self.GetLoopCount(FIObj.die, b1_addr[2], b1_addr[3], b1_addr[4], b0_addr[5])

            csvobj1.WriteRows(self.writer) 
            if AttrObj.PlaneType == PlaneType.dual:
                csvobj2.WriteRows(self.writer)
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)

        return ret

    def TLC_Program_Single_Plane_NonCache(self, FIObj, AttrObj):
        """
        Description: TLC_Program_Single_Plane_NonCache
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
            @Note: 3 * 18336 payload file should be given
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        #Error Injection : Parameter Address 0x64 : Value = 0x2D
        ret = True 
        if AttrObj.isVerbose:
            print("TLC_Program_Single_Plane_NonCache")

        AttrObj.BlkType = BlkType.TLC
        AttrObj.PlaneType = PlaneType.single
        FIObj.PageType = PageType.TLC

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)
		
        print("CE = " + str(FIObj.ce) + ", FIM = " + str(FIObj.fim) + ", Die = " + str(FIObj.die) + ", Block = " + str(FIObj.block_no1))
		
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection #0x104
            print("Get param value = \t {}".format(hex(value)))            

            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection  #0x26
            print("Set param value = \t {}".format(hex(value)))

        #lower page
        seq = [CMD3, die_no, CmdAccessLP, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdNextCellOnWL, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)

        if not AttrObj.Payload == None:
            fptr =  open(AttrObj.Payload, "rb")
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        elif not AttrObj.Pattern == None:    
            idx = 0
            while idx < numOfSectorsSPSeq * 512:
                seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
                idx = idx + 2
        else:
            raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")
            
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        #seqbuf.Dump()        
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        #middle page
        seq = [CMD3, die_no, CmdAccessMP, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdNextCellOnWL, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        #seqbuf.Dump()        
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        #upper page
        seq = [CMD3, die_no, CmdAccessUP, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgram, DELAY, 0x0, 0x5, WAIT_RB, CMD2, 0xF1, 0x70, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        #seqbuf.Dump()
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        #print(cdb)
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        retbyte = self.StatusRead(FIObj.die, CmdStatus70)
        if not retbyte == 0xE0:
            for i in range(10):
                if retbyte != 0xE1:
                    retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                else:
                    break

        if self.outCsvFile:
            csvobj1 = csvWriterClass()
            
            csvobj1.operation = 'TLC_Program_Single_Plane_NonCache'
            csvobj1.fim = FIObj.fim
            csvobj1.ce = FIObj.ce
            csvobj1.die = FIObj.die
            csvobj1.wl = FIObj.wl
            csvobj1.string = FIObj.string
            csvobj1.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            
            if retbyte != 0xE0:
                ret = False
                csvobj1.result = "Fail"
                csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
            csvobj1.WriteRows(self.writer)
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)

        return ret
    
    def TLC_Program_Single_Plane_NonCache_OneCmd(self, FIObj, AttrObj):
        """
        Description: TLC_Program_Single_Plane_NonCache
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass

        Returns: True = Success, False = Fail
        Exceptions: None
        """
        #Error Injection : Parameter Address 0x64 : Value = 0x2D
        ret = True 
        if AttrObj.isVerbose:
            print("TLC_Program_Single_Plane_NonCache")

        AttrObj.BlkType = BlkType.TLC
        AttrObj.PlaneType = PlaneType.single
        FIObj.PageType = PageType.TLC

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)

        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)

        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection #0x104
            print("Get param value = \t {}".format(hex(value)))            

            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection  #0x26
            print("Set param value = \t {}".format(hex(value)))

        #lower page
        seq = [CMD2, die_no, 0xFD, DELAY, 0x0, 0x1, WAIT_RB, CMD3, die_no, CmdAccessLP, CmdWriteColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdNextCellOnWL, DELAY, 0x0, 0x5, WAIT_RB, CMD3, die_no, CmdAccessMP, CmdWriteColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdNextCellOnWL, DELAY, 0x0, 0x5, WAIT_RB, CMD4, die_no, 0xB2, CmdAccessUP, CmdWriteColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgram, DELAY, 0x0, 0x5, WAIT_RB, CMD2, 0xF1, 0x70, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)

        if not AttrObj.Payload == None:
            fptr =  open(AttrObj.Payload, "rb")
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        elif not AttrObj.Pattern == None:    
            idx = 0
            while idx < numOfSectorsSPSeq * 512:
                seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
                idx = idx + 2
        else:
            raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        for i in range(10):
            retbyte = self.StatusRead(FIObj.die, CmdStatus70)

        if self.outCsvFile:
            csvobj1 = csvWriterClass()

            csvobj1.operation = 'TLC_Program_Single_Plane_NonCache'
            csvobj1.fim = FIObj.fim
            csvobj1.ce = FIObj.ce
            csvobj1.die = FIObj.die
            csvobj1.wl = FIObj.wl
            csvobj1.string = FIObj.string
            csvobj1.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            
            if retbyte != 0xE0:
                ret = False
                csvobj1.result = "Fail"
                csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
            csvobj1.WriteRows(self.writer)

        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)

        return ret

        
    def SLC_Program_Single_Plane_NonCache(self, FIObj, AttrObj):
		"""
		Description: SLC_Program_Single_Plane_NonCache
		Parameters:
			@param: FlashInfoClass object
			@param: FlashAttributesClass
		Returns: True = Success, False = Fail
		Exceptions: None
		"""
		#Error Injection : Parameter Address 0x63 : Value = 0x2D
		ret = True 

		if AttrObj.isVerbose:
			print("SLC_Program_Single_Plane_NonCache")
		
		AttrObj.BlkType = BlkType.SLC
		AttrObj.PlaneType = PlaneType.single
		FIObj.PageType = PageType.SLC

		if FIObj.die<0 or FIObj.die>7:  #Die input check
			print("Die: Invalid Value")        
		die_no = 0xF0 | (FIObj.die + 1)
		
		print("CE = " + str(FIObj.ce) + ", FIM = " + str(FIObj.fim) + ", Die = " + str(FIObj.die) + ", Block = " + str(FIObj.block_no1))
		
		b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
		
		if AttrObj.FDReset:
			self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)
		
		if AttrObj.ErrorInjection == 1:
			value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection
			print("Get param value = \t {}".format(hex(value)))            
		
			value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection
			print("Set param value = \t {}".format(hex(value)))        

		seq = [CMD3, die_no, 0xA2, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgram, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
		seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

		seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
		
		if not AttrObj.Payload == None:
			with open(AttrObj.Payload, "rb") as fptr:
				urpstr = fptr.read(x3_page_size)
			seq = seq + [int(hex(ord(st)),16) for st in urpstr]
		elif not AttrObj.Pattern == None:
			idx = 0
			while idx < numOfSectorsSPSeq * 512:
				seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
				idx = idx + 2
		else:
			raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")
			
		for idx, sq in enumerate(seq):
			seqbuf.SetByte(idx, sq)
		#seqbuf.Dump()
		cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
		self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

		retbyte = self.StatusRead(FIObj.die, CmdStatus70)
		if not retbyte == 0xE0:
			for i in range(10):
				if retbyte != 0xE4:
					retbyte = self.StatusRead(FIObj.die, CmdStatus70)
				else:
					break

		if self.outCsvFile:    
			csvobj1 = csvWriterClass()
			
			csvobj1.operation = 'SLC_Program_Single_Plane_NonCache'
			csvobj1.fim = FIObj.fim
			csvobj1.ce = FIObj.ce
			csvobj1.die = FIObj.die
			csvobj1.wl = FIObj.wl
			csvobj1.string = FIObj.string
			csvobj1.pagetype = FIObj.PageType.name
			csvobj1.block = FIObj.block_no1
			
			if retbyte != 0xE0:
				ret = False 
				csvobj1.result = "Fail"
				csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
			csvobj1.WriteRows(self.writer)
		
		if AttrObj.FlashReset:
			self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)

		return ret

    def SLC_Program_Dual_Plane_NonCache(self, FIObj, AttrObj):
        """
        Description: SLC_Program_Dual_Plane_NonCache
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
            @Note: 2 * 18336 bytes payload file should be given
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        ret = True 
        if AttrObj.isVerbose:
            print("SLC_Program_Dual_Plane_NonCache")

        AttrObj.BlkType = BlkType.SLC
        AttrObj.PlaneType = PlaneType.dual
        FIObj.PageType = PageType.SLC

        plane0 = FIObj.block_no1%2
        plane1 = FIObj.block_no2%2

        if plane0 == plane1:
            print("Block number's not meeting for dual plane program operation")

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)
        
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        b1_addr = self.ToAddr(FIObj.die, FIObj.block_no2, FIObj.wl, FIObj.string, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection #x63
            print("Get param value = \t {}".format(hex(value)))            

            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection
            print("Set param value = \t {}".format(hex(value)))

        #first plane transfer
        seq = [CMD3, die_no, 0xA2, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgramDummy, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)

        if not AttrObj.Payload == None:
            fptr =  open(AttrObj.Payload, "rb")
            if fptr:
                urpstr = fptr.read(x3_page_size)
                seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        elif not AttrObj.Pattern == None:    
            idx = 0
            while idx < numOfSectorsSPSeq * 512:
                seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
                idx = idx + 2
        else:
            raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")
                
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        #Second plane transfer
        seq = [CMD2, 0xA2, CmdWriteData, ADDR6, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], b1_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgram, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr] 
            
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        retbyte = self.StatusRead(FIObj.die, 0x70)
        if not retbyte == 0xE0:
            for i in range(10):
                if retbyte != 0xE4:
                   retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                else:
                    break
                   
        if self.outCsvFile:

            csvobj1 = csvWriterClass()
            csvobj2 = csvWriterClass()

            csvobj1.fim = csvobj2.fim = FIObj.fim
            csvobj1.ce = csvobj2.ce = FIObj.ce
            csvobj1.die = csvobj2.die = FIObj.die
            csvobj1.wl= csvobj2.wl = FIObj.wl
            csvobj1.string = csvobj2.string = FIObj.string
            csvobj1.operation = csvobj2.operation = 'SLC_Program_Dual_Plane_NonCache'
            csvobj1.pagetype = csvobj2.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            csvobj2.block = FIObj.block_no2
            
            if retbyte != 0xE0:
                ret = False
                plane = (self.StatusRead(FIObj.die, 0x72) & 0x6)
                
                if plane & 0x02: #plane0 fails
                    if FIObj.block_no1%2 == 0: #checking even plane
                        csvobj1.result = "Fail"
                        csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
                    elif FIObj.block_no2%2 == 0:
                        csvobj2.result = "Fail"
                        csvobj2.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
                
                    if plane & 0x04: #plane1 fails
                        if FIObj.block_no1%2 == 1: #checking odd plane
                            csvobj1.result = "Fail"
                            csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2) 
                        elif FIObj.block_no2%2 == 1:
                            csvobj2.result = "Fail"
                            csvobj2.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2) 

            csvobj1.WriteRows(self.writer)
            csvobj2.WriteRows(self.writer)

        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die) 

        return ret

    def SLC_Program_Single_Plane_Cache(self, FIObj, AttrObj):
        """
        Description: This function used to program single plane SLC program
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        ret = True 
        if AttrObj.isVerbose:
            print("SLC_Program_Single_Plane_Cache")
        
        AttrObj.BlkType = BlkType.SLC
        AttrObj.PlaneType = PlaneType.single
        FIObj.PageType = PageType.SLC

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)
        
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)
        
        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection
            print("Get param value = \t {}".format(hex(value)))            
        
            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection
            print("Set param value = \t {}".format(hex(value)))        

        seq = [CMD3, die_no, 0xA2, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdCacheProgram, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]

        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)

        if not AttrObj.Payload == None:
            with open(AttrObj.Payload, "rb") as fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        elif not AttrObj.Pattern == None:    
            idx = 0
            while idx < numOfSectorsSPSeq * 512:
                seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
                idx = idx + 2
        else:
            raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")
            
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        retbyte = self.StatusRead(FIObj.die, 0x70)
        if not retbyte == 0xE0:
            for i in range(10):
                if retbyte != 0xE4:
                   retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                else:
                    break

        if self.outCsvFile: 

            csvobj1 = csvWriterClass()
            
            csvobj1.operation = 'SLC_Program_Single_Plane_Cache'
            csvobj1.fim = FIObj.fim
            csvobj1.ce = FIObj.ce
            csvobj1.die = FIObj.die
            csvobj1.wl = FIObj.wl
            csvobj1.string = FIObj.string
            csvobj1.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            
            if retbyte != 0xE0:
                ret = False
                csvobj1.result = "Fail"
                csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
                   
            csvobj1.WriteRows(self.writer)
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die) 

        return ret

    def SLC_Program_Dual_Plane_Cache(self, FIObj, AttrObj):
        """
        Description: This function used to program single plane SLC program
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
            @Note: 2 * 18336 bytes payload file should be given
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        ret = True 
        if AttrObj.isVerbose:
            print("SLC_Program_Dual_Plane_Cache")

        AttrObj.BlkType = BlkType.SLC
        AttrObj.PlaneType = PlaneType.dual
        FIObj.PageType = PageType.SLC

        plane0 = FIObj.block_no1%2
        plane1 = FIObj.block_no2%2

        if plane0 == plane1:
            print("Block number's not meeting for dual plane program operation")

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)
        
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        b1_addr = self.ToAddr(FIObj.die, FIObj.block_no2, FIObj.wl, FIObj.string, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection #0x104
            print("Get param value = \t {}".format(hex(value)))            

            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection  #0x26
            print("Set param value = \t {}".format(hex(value)))

         #first plane transfer
        seq = [CMD3, die_no, 0xA2, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgramDummy, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)

        if not AttrObj.Payload == None:
            fptr =  open(AttrObj.Payload, "rb")
            if fptr:
                urpstr = fptr.read(x3_page_size)
                seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        elif not AttrObj.Pattern == None:    
            idx = 0
            while idx < numOfSectorsSPSeq * 512:
                seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
                idx = idx + 2
        else:
            raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")
                
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        #Second plane transfer
        seq = [CMD2, 0xA2, CmdWriteData, ADDR6, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], b1_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdCacheProgram, WAIT_RB, CMD2, die_no, 0x70, DATA_OUT, 0x0, 0x02, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr] 
            
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        retbyte = self.StatusRead(FIObj.die, CmdStatus70)
        if not retbyte == 0xE0:
            for i in range(10):
                if retbyte != 0xE4:
                    retbyte = self.StatusRead(FIObj.die, CmdStatus70)
                else:
                    break

        if self.outCsvFile:

            csvobj1 = csvWriterClass()
            csvobj2 = csvWriterClass()

            csvobj1.fim = csvobj2.fim = FIObj.fim
            csvobj1.ce = csvobj2.ce = FIObj.ce
            csvobj1.die = csvobj2.die = FIObj.die
            csvobj1.wl= csvobj2.wl = FIObj.wl
            csvobj1.string = csvobj2.string = FIObj.string
            csvobj1.operation = csvobj2.operation = 'SLC_Program_Dual_Plane_Cache'
            csvobj1.pagetype = csvobj2.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            csvobj2.block = FIObj.block_no2
            
            if retbyte != 0xE0:
                ret = False
                plane = (self.StatusRead(FIObj.die, 0x72) & 0x6)
                
                if plane & 0x02: #plane0 fails
                    if FIObj.block_no1%2 == 0: #checking even plane
                        csvobj1.result = "Fail"
                        csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
                    elif FIObj.block_no2%2 == 0:
                        csvobj2.result = "Fail"
                        csvobj2.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
                
                    if plane & 0x04: #plane1 fails
                        if FIObj.block_no1%2 == 1: #checking odd plane
                            csvobj1.result = "Fail"
                            csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2) 
                        elif FIObj.block_no2%2 == 1:
                            csvobj2.result = "Fail"
                            csvobj2.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)               
                            
            csvobj1.WriteRows(self.writer)
            csvobj2.WriteRows(self.writer)

        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)         
        return ret

    def TLC_Program_Dual_Plane_NonCache(self, FIObj, AttrObj):
        """
        Description: TLC_Program_Dual_Plane_NonCache
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
            @Note: 6 * 18336 bytes payload should be given
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        ret = True 
        if AttrObj.isVerbose:
            print("TLC_Program_Dual_Plane_NonCache")

        AttrObj.BlkType = BlkType.TLC
        AttrObj.PlaneType = PlaneType.dual
        FIObj.PageType = PageType.TLC

        plane0 = FIObj.block_no1%2
        plane1 = FIObj.block_no2%2

        if plane0 == plane1:
            print("Block number's not meeting for dual plane program operation")

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)
        
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)
        b1_addr = self.ToAddr(FIObj.die, FIObj.block_no2, FIObj.wl, FIObj.string, 0)
        
        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        if AttrObj.ErrorInjection == 1:
            value = self.GetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr) #EF injection #0x104
            print("Get param value = \t {}".format(hex(value)))            

            value = self.SetParam(FIObj.fim, FIObj.ce, FIObj.die, AttrObj.ParamAddr, AttrObj.ParamValue) #EF injection  #0x26
            print("Set param value = \t {}".format(hex(value)))

        #lower page
        seq = [CMD3, die_no, CmdAccessLP, CmdWriteData, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgramDummy, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)

        if not AttrObj.Payload == None:
            fptr =  open(AttrObj.Payload, "rb")
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        elif not AttrObj.Pattern == None:    
            idx = 0
            while idx < numOfSectorsSPSeq * 512:
                seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
                idx = idx + 2
        else:
            raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")
            
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        #2nd plane, lower page
        seq = [CMD2, CmdAccessLP, CmdWriteData, ADDR6, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], b1_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdNextCellOnWL, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        elif not AttrObj.Pattern == None:    
            idx = 0
            while idx < numOfSectorsSPSeq:
                seqbuf.SetTwoBytes(idx, AttrObj.Pattern)
                idx = idx + 2
        else:
            raise AssertionError("Either data_pattern or AttrObj.payload must be valid one")

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        
        #middle page
        seq = [CMD2, CmdAccessMP, CmdWriteData, ADDR6,  b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgramDummy, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        #middle page
        seq = [CMD2, CmdAccessMP, CmdWriteData, ADDR6, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], b1_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdNextCellOnWL, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        #upper page
        seq = [CMD2, CmdAccessUP, CmdWriteData, ADDR6,  b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgramDummy, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        #upper page
        seq = [CMD2, CmdAccessUP, CmdWriteData, ADDR6, b1_addr[0], b1_addr[1], b1_addr[2], b1_addr[3], b1_addr[4], b1_addr[5], DELAY, 0x0, 0x1, DATA_IN_E, 0x47, 0xA0, CMD1, CmdAutoProgram, DELAY, 0x0, 0x5, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        if not AttrObj.Payload == None:
            if fptr:
                urpstr = fptr.read(x3_page_size)
            seq = seq + [int(hex(ord(st)),16) for st in urpstr]

        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        retbyte = self.StatusRead(FIObj.die, CmdStatus70)
        if not retbyte == 0xE0:
            for i in range(10):
                if retbyte != 0xE1:
                    retbyte = self.StatusRead(FIObj.die, CmdStatus70)        
                else:
                    break

        if self.outCsvFile:
            csvobj1 = csvWriterClass()
            csvobj2 = csvWriterClass()

            csvobj1.fim = csvobj2.fim = FIObj.fim
            csvobj1.ce = csvobj2.ce = FIObj.ce
            csvobj1.die = csvobj2.die = FIObj.die
            csvobj1.wl= csvobj2.wl = FIObj.wl
            csvobj1.string = csvobj2.string = FIObj.string
            csvobj1.operation = csvobj2.operation = 'TLC_Program_Dual_Plane_NonCache'
            csvobj1.pagetype = csvobj2.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            csvobj2.block = FIObj.block_no2
            
            if retbyte != 0xE0:
                ret = False
                plane = (self.StatusRead(FIObj.die, 0x71) & 0x6)
                
                if plane & 0x02: #plane0 fails
                    if FIObj.block_no1%2 == 0: #checking even plane
                        csvobj1.result = "Fail"
                        csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
                    elif FIObj.block_no2%2 == 0:
                        csvobj2.result = "Fail"
                        csvobj2.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2) 
                
                if plane & 0x04: #plane1 fails
                    if FIObj.block_no1%2 == 1: #checking odd plane
                        csvobj1.result = "Fail"
                        csvobj1.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
                    elif FIObj.block_no2%2 == 1:
                        csvobj2.result = "Fail"
                        csvobj2.program_loop_count = self.ProgGetLoopCount(FIObj.die, 0x77, 0x2)
            
            csvobj1.WriteRows(self.writer)
            csvobj2.WriteRows(self.writer)
        
        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)              

        return ret


    def StatusRead(self, die, stacmd):
        if g_Verbose:
            print("StatusRead")
        
        die_no = 0xF0 | (die + 1)
        
        seq = [CMD2, die_no, stacmd, DATA_OUT, 0x0, 0x02, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        numOfSectors = 1
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)   
        if stacmd == 0x77:
            retbyte = retbuf.GetTwoBytesToInt(0)
        else:
            retbyte = retbuf.GetOneByteToInt(0)
        #if stacmd == 0x70: 
        #    retbyte = 0xE1
        #if stacmd == 0x71:  
        #    retbyte = 0xE6
        if g_Verbose:  
            print("Status {}".format(hex(stacmd)) + "return = {}".format(hex(retbyte)) )
            retbuf.WriteToFile("status.bin", numOfSectors*512) 
        return retbyte

    def GetLoopCount(self, die, addr1_h, addr2_h, addr3_h, addr4_h):
        if g_Verbose:
            print("GetLoopCount")

        die_no = 0xF0 | (die + 1)

        seq = [CMD2, die_no, CmdStatus6A, ADDR4, addr1_h, addr2_h, addr3_h, addr4_h, DATA_OUT, 0x0, 0x02, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        numOfSectors = 1
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)   
        retbyte = retbuf.GetOneByteToInt(0)
        
        if g_Verbose:
            print("Get loop count {0x6A}" + "return = {}".format(hex(retbyte)) )
            retbuf.WriteToFile("GetLoop.bin", numOfSectors*512) 
        return retbyte
    
    def ProgGetLoopCount(self, die, stacmd, addr1_h):
        
        if g_Verbose:
            print("GetLoopCount")
    
        die_no = 0xF0 | (die + 1)
    
        seq = [CMD2, die_no, stacmd, ADDR1, addr1_h, DATA_OUT, 0x0, 0x02, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
    
        numOfSectors = 1
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)   
        retbyte = retbuf.GetOneByteToInt(0) & 0x7F
        
        if g_Verbose:
            print("Program Get loop count {}".format(hex(stacmd)) + " return = {}".format(hex(retbyte)) )
            retbuf.WriteToFile("GetProgLoop.bin", numOfSectors*512) 
        
        return retbyte    

    def ReadEC40WL_old(self):
        #Read EC40WL
        #seq = [0xC2, 0xF1, 0xFD, 0xEE, 0xDE, 0x13, 0x88, 0xC1, 0xEC, 0xA1, 0x40, 0xD0, 0x47, 0xA0, 0xEE]
        seq = [0xC2, 0xF1, 0xFD, 0xDE, 0x13, 0x88, 0xC1, 0xEC, 0xA1, 0x40, 0xD0, 0x47, 0xA0]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        numOfSectors = 36
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        retbuf.WriteToFile("Read_EC40WL.bin", numOfSectors*512)
        return retbuf
    
    def EraseUserrom0_old(self):
        #Erase Userrom Plane-0
        seq = [0xC2, 0xF1, 0xFD, 0xDE, 0x13, 0x88, 0xC6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, 0xA1, 0x00, 0xD1, 0x00, 0x01, 0x01, 0xC6, 0xF1, 0x99, 0x5A, 0xBE, 0xA2, 0x60, 0xA3, 0x00, 0x00, 0x00, 0xC1, 0xD0, 0xDE, 0x27, 0x10, 0xC1, 0xFF]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return
    
    def ProgramUserrom0_old(self, urompayload):
        #Program Userrom Plane-0
        seq = [0xC2, 0xF1, 0xFD, 0xDE, 0x13, 0x88, 0xC6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, 0xA1, 0x00, 0xD1, 0x00, 0x01, 0x01, 0xC5, 0xF1, 0x5A, 0xBE, 0xA2, 0x80, 0xA5, 0x00, 0x00, 0x90, 0x01, 0x00, 0xD3, 0x47, 0xA0, 0xC1, 0x10, 0xDE, 0x27, 0x10, 0xC1, 0xFF]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        with open(urompayload, "rb") as fptr:
            urpstr = fptr.read()
        seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        numOfSectors = 37
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        #seqbuf.FillFromFile("userrom_writeseq_payload.bin", False)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return

    def ReadFile(self, buf, fileid, sectorcount, options=0):
        """
        Description: This function will read file based on file ID into buffer
        Parameters:
            @param: buf - Buffer which gets filled
            @param: fileid - File ID
            @param: sectorcount - Number of sector count
            @param: options - To set options
        Returns: None
        Exceptions: None
        """
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()

        diagCmd.cdb = [0] * 16

        diagCmd.cdb[0] = 0x8A
        diagCmd.cdb[1] = 0
        diagCmd.cdb[2] = GetByte(0, options)
        diagCmd.cdb[3] = GetByte(1, options)
        diagCmd.cdb[4] = GetByte(0, fileid)
        diagCmd.cdb[5] = GetByte(1, fileid)
        diagCmd.cdb[6] = 0
        diagCmd.cdb[7] = 0
        diagCmd.cdb[8] = GetByte(0, sectorcount)
        diagCmd.cdb[9] = GetByte(1, sectorcount)
        diagCmd.cdb[10] = GetByte(2, sectorcount)
        diagCmd.cdb[11] = GetByte(3, sectorcount)
        diagCmd.cdb[12] = 0
        diagCmd.cdb[13] = 0
        diagCmd.cdb[14] = 0
        diagCmd.cdb[15] = 0

        diagCmd.cdbLen = 16
        try:
            PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT,
                                                  True, None, 200000, PyServiceWrap.SEND_IMMEDIATE)
        except PyServiceWrap.CmdException as ex:
            # self.logger.SmallBanner("DIAG: READ_FILE FAILED", "FATAL")
            print "Exception"
            #raise ValidationError.CVFGenericExceptions("SctpUtils", "READ_FILE Command failed - %s" % ex)
        #self.logger.SmallBanner("DIAG: READ_FILE SUCCESS")
        return buf

    def WriteFile(self, buf, fileid, sectorcount, timeOut=1000):
        """
        Description: This function will write file based on file ID into buffer
        Parameters:
            @param: buf - Buffer which gets filled
            @param: fileid - File ID
            @param: sectorcount - Number of sector count
            @param: options - To set options
        Returns: None
        Exceptions: None
        """
        options = 0
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()

        diagCmd.cdb = [0] * 16

        diagCmd.cdb[0] = 0x8B
        diagCmd.cdb[1] = 0
        diagCmd.cdb[2] = GetByte(0, options)
        diagCmd.cdb[3] = GetByte(1, options)
        diagCmd.cdb[4] = GetByte(0, fileid)
        diagCmd.cdb[5] = GetByte(1, fileid)
        diagCmd.cdb[6] = 0
        diagCmd.cdb[7] = 0
        diagCmd.cdb[8] = GetByte(0, sectorcount)
        diagCmd.cdb[9] = GetByte(1, sectorcount)
        diagCmd.cdb[10] = GetByte(2, sectorcount)
        diagCmd.cdb[11] = GetByte(3, sectorcount)
        diagCmd.cdb[12] = 0
        diagCmd.cdb[13] = 0
        diagCmd.cdb[14] = 0
        diagCmd.cdb[15] = 0
        diagCmd.cdbLen = 16

        try:
            #PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_IN,
           #            True, None, 200000, PyServiceWrap.SEND_IMMEDIATE)
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_IN)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
             print("exception")
   
    def RequestSense(self):
        """
        Description: Memory allocation ( This function use to create Singleton object of OrthogonalTestManager)
        Parameters: None
        Returns: None
        Exceptions: None
        """
        sectorCount = 4
        opcode = 0x03

        lengthInBytes = sectorCount * 512
        buf = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_1, isSector=False)

        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[8] = GetByte(0, sectorCount)
        diagCmd.cdb[9] = GetByte(1, sectorCount)
        diagCmd.cdb[10] = GetByte(2, sectorCount)
        diagCmd.cdb[11] = GetByte(3, sectorCount)

        diagCmd.cdbLen = len(diagCmd.cdb)
        self.diagobj.sendDiagnostics(diagCmd.cdb, diagCmd.cdbLen, buf, ioDirection = 1)
        return buf
        
    def AtaIdentifyDrive(self, sectorcount=1):
        """
        Description: Memory allocation ( This function use to create Singleton object of OrthogonalTestManager)
        Parameters: None
        Returns: None
        Exceptions: None
        """
        opcode = 0xEC
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount * 512, patternType=PyServiceWrap.ALL_1, isSector=False)
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16

        diagCmd.cdb[0] = opcode
        diagCmd.cdb[8] = GetByte(0, sectorcount)
        diagCmd.cdb[9] = GetByte(1, sectorcount)
        diagCmd.cdb[10] = GetByte(2, sectorcount)
        diagCmd.cdb[11] = GetByte(3, sectorcount)

        diagCmd.cdbLen = len(diagCmd.cdb)

        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
              print "Exceprion"
             #self.logger.SmallBanner("DIAG: IDENTIFY_DRIVE FAILED", "FATAL")
             #raise ValidationError.TestFailError("SctpUtils", "IDENTIFY_DRIVE Diag Command Failed - %s" % ex)
        #self.logger.SmallBanner("DIAG: IDENTIFY_DRIVE SUCCESS")

        modelNumber = buf.GetString(MODEL_NUMBER_OFFSET, MODEL_NUMBER_LENGTH).lower()
        if "wdc" not in modelNumber and "sandisk" not in modelNumber:
            print"Model Number is Wrong:"
            #self.logger.Error("Model Number is Wrong: %s" % modelNumber.upper())
        #self.logger.Info("Model Number is : %s" % modelNumber.upper())
        return buf

    def SLC_program(self, urompayload):
        #Program Userrom Plane-0
        seq = [0xC2, 0xF1, 0xFD, 0xDE, 0x13, 0x88, 0xC6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, 0xA1, 0x00, 0xD1, 0x00, 0x01, 0x01, 0xC5, 0xF1, 0x5A, 0xBE, 0xA2, 0x80, 0xA5, 0x00, 0x00, 0x90, 0x01, 0x00, 0xD3, 0x47, 0xA0, 0xC1, 0x10, 0xDE, 0x27, 0x10, 0xC1, 0xFF]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        with open(urompayload, "rb") as fptr:
            urpstr = fptr.read()
        seq = seq + [int(hex(ord(st)),16) for st in urpstr]
        numOfSectors = 37
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        #seqbuf.FillFromFile("userrom_writeseq_payload.bin", False)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return


    def MemcelCVDParam(self):
    
        opcode = 0xD6
        subopcode = 0x20
        sectorcount = 4
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount * 512, patternType=PyServiceWrap.ALL_1, isSector=False)
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        #'''
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = subopcode
        diagCmd.cdb[3] = 4
        #diagCmd.cdb[16] = 4
        #'''
        #diagCmd.cdb = [0xD6,0x20,00,04,00,00,00,00,00,00,00,00,00,00,00,00,04,00]
        diagCmd.cdbLen = len(diagCmd.cdb)
        
        #retbuf = self.diagobj.sendDiagnostics(diagCmd, diagCmd.cdbLen, buf, ioDirection = 0)    
        #'''
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
             print("exception")         
        #'''
        return buf
    
    def Param(self,Param,Param_or_fetature,Die,num):
    
        opcode = 0xBB
        sectorcount = 4
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount * 512, patternType=PyServiceWrap.ALL_1, isSector=False)
        #'''
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = Param
        diagCmd.cdb[2] = Param_or_fetature
        diagCmd.cdb[3] = Die
        diagCmd.cdb[4] = 0x10
        #diagCmd.cdb[16] = 4
        '''
        cdb = [0]*16
        cdb[0] = opcode
        cdb[1] = Paramcdb = [0xD6,0x20,00,04,00,00,00,00,00,00,00,00,00,00,00,00,04,00]
        cdb[2] = Param_or_fetature
        cdb[3] = Die
        cdb[4] = num   
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0) 
        '''
        try:
            print("try")  
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            print("try-1")
        except PyServiceWrap.CmdException as ex:
            print("exception-1")         
        #'''
        print(buf)
        return buf

    def FlushCVDDeltaList(self):
    
        opcode = 0xD6
        subopcode = 0x21
        sectorcount = 4
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount * 512, patternType=PyServiceWrap.ALL_1, isSector=False)
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        #'''
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = subopcode
        diagCmd.cdb[3] = 1
        #diagCmd.cdb[16] = 4
        #'''
        #diagCmd.cdb = [D6,21,00,01,00,00,00,00,00,00,00,00,00,00,00,00,01,00]
        diagCmd.cdbLen = len(diagCmd.cdb)
        
        #retbuf = self.diagobj.sendDiagnostics(diagCmd, diagCmd.cdbLen, buf, ioDirection = 0)    
        #'''
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
             print("exception")         
        #'''
        return buf

    def CVDDiag(self):
    
        DiagNum = int(raw_input("Enter \n 1: Get Memcell CVD read params \n 2: Flush CVD delta List \n 3: Flush CVD cache \n  4: Trigger Force TRT update \n  5: Trigger Force TRT compaction \n  6: Get all active TRT for thermal regions \n 7: Get TRT CVD read params \n "))
        opcode = 0xD6
        subopcode = (0x1F + DiagNum)
        print(subopcode)
        sectorcount = 4
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount * 512, patternType=PyServiceWrap.ALL_1, isSector=False)
        buf.Dump()
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        #'''
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = subopcode
        diagCmd.cdb[3] = 1
        #diagCmd.cdb[16] = 4
        #'''
        #diagCmd.cdb = D6,22,00,01,00,00,00,00,00,00,00,00,00,00,00,00,01,00
        diagCmd.cdbLen = len(diagCmd.cdb)
        print(diagCmd.cdb)
        #retbuf = self.diagobj.sendDiagnostics(diagCmd, diagCmd.cdbLen, buf, ioDirection = 0)    
        #'''
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
             print("exception")         
        #'''
        buf.Dump()
        return buf

    def SecurityOnProductionEnd(self): 
        opcode = 0x46 #0x42
        sectorcount = 2
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount * 512, patternType=PyServiceWrap.ALL_1, isSector=False)
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        #'''
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
             print("exception")         
        #'''
        buf.Dump()
        return buf

    def WriteFMU(self):
    
        opcode = 0xB2
        sectorcount = 4
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount * 512, patternType=PyServiceWrap.ALL_1, isSector=False)
        #'''
        chip = input("Enter Chip no.:")
        Die = input("Enter Die no.:")
        plane = input("Enter plane no.:")
        Block_LSB = input("Enter Block LSB no.:")
        Block_MSB = input("Enter Block MSB no.:")
        Page_LSB = input("Enter Page LSB no.:")
        Page_MSB = input("Enter Page MSB no.:")
        FMU_Offset =input("Enter FMU offset in page (=0-3 for SLC , must be 0 for TLC):")
        string = input("Enter String no.:")
        Count_LSB = input("Enter Count LSB no.:")
        Count_MSB = input("Enter Count MSB no.:")
        Option_LSB =input("Enter Option LSB no.:")
        Option_MSB =input("Enter Option MSB no.:")
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = int(opcode)
        diagCmd.cdb[1] = int(chip)
        diagCmd.cdb[2] = int(Die)
        diagCmd.cdb[3] = int(plane)
        diagCmd.cdb[4] = int(Block_LSB)
        diagCmd.cdb[5] = int(Block_MSB)
        diagCmd.cdb[6] = int(Page_LSB)
        diagCmd.cdb[7] = int(Page_MSB)
        diagCmd.cdb[8] = int(FMU_Offset)
        diagCmd.cdb[9] = int(string)
        diagCmd.cdb[10] =int(Count_LSB)
        diagCmd.cdb[11] =int(Count_MSB)
        diagCmd.cdb[14] =int(Option_LSB)
        diagCmd.cdb[15] =int(Option_MSB)
        #diagCmd.cdb[16] = 4
        '''
        cdb = [0]*16
        cdb[0] = opcode
        cdb[1] = Paramcdb = [0xD6,0x20,00,04,00,00,00,00,00,00,00,00,00,00,00,00,04,00]
        cdb[2] = Param_or_fetature
        cdb[3] = Die
        cdb[4] = num   
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0) 
        '''
        try:
            print("try")  
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            print("try-1")
        except PyServiceWrap.CmdException as ex:
            print("exception-1")         
        #'''
        print(buf)
        return buf
    
    def ReadFBBList(self, option = 0):
    
        special_opt = 0
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0]*16
        diagCmd.cdb[0] = 0xAA
        diagCmd.cdb[1] = special_opt
        diagCmd.cdb[2] = (option) & 0xFF
        diagCmd.cdb[3] = (option >>8) & 0xFF
        diagCmd.cdbLen = len(diagCmd.cdb)
        
        if option == 0:
            FBBCount = (self.ReadFBBList(1)).GetTwoBytesToInt(0)
            #print FBBCount
    
        buf = PyServiceWrap.Buffer.CreateBuffer(8, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            #print "ReadFBBList: PASS"
        except PyServiceWrap.CmdException as ex:
            print "ReadFBBList: FAIL", ex.GetFailureDescription()
            exit()
        
        if option == 0 and FBBCount != 0:
            fbbFileName = "FBBList.csv"
            with open(fbbFileName, 'wb') as fbbFile:
                csvWriter = csv.writer(fbbFile, delimiter=',')
                csvWriter.writerow(['Count', 'FIM', 'CE', 'Die', 'Plane', 'Block'])
                for cnt in range(FBBCount):
                    csvWriter.writerow([cnt]+[(buf.GetTwoBytesToInt(cnt*4)>>shft)&0xF for shft in range(0,16,4)]+[hex(buf.GetTwoBytesToInt(cnt*4+2))])
                fbbFile.close()
            print "FBB List dumped to", fbbFileName
            
        if option == 0 and FBBCount == 0:
            print "FBB Count is 0"
            
        return buf
        
    def ReadGBBList(self, option = 0):

        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0]*16
        diagCmd.cdb[0] = 0xB3
        diagCmd.cdb[1] = 0
        diagCmd.cdb[2] = (option) & 0xFF
        diagCmd.cdb[3] = (option >>8) & 0xFF
        diagCmd.cdbLen = len(diagCmd.cdb)
        
        if option == 0:
            GBBCount = (self.ReadGBBList(1)).GetFourBytesToInt(0) 
            #print GBBCount
    
        buf = PyServiceWrap.Buffer.CreateBuffer(8, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            #print "ReadGBBList: PASS"
        except PyServiceWrap.CmdException as ex:
            print "ReadGBBList: FAIL", ex.GetFailureDescription() 
            exit()
            
        if option == 0 and GBBCount != 0:
            gbbFileName = "GBBList.csv"
            with open(gbbFileName, 'wb') as gbbFile:
                csvWriter = csv.writer(gbbFile, delimiter=',')
                csvWriter.writerow(['Count', 'FIM', 'CE', 'Die', 'Plane', 'Block'])
                for cnt in range(GBBCount):
                    csvWriter.writerow([cnt]+[(buf.GetTwoBytesToInt(cnt*4)>>shft)&0xF for shft in range(0,16,4)]+[hex(buf.GetTwoBytesToInt(cnt*4+2))])
                gbbFile.close()
            print "GBB List dumped to", gbbFileName
        if option == 0 and GBBCount == 0:
            print "GBB Count is 0"
            
        return buf
        
    def LbaToPhysical(self, lba):

        opcode = 0x87
        inputAddressMode = 1
        inputAddressType = 0
        pageAddressFormat = 1
        sectorcount = 1
        
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount, patternType=PyServiceWrap.ALL_0, isSector=True)
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = 0
        options = 0
    
        options |= (inputAddressMode << 0)
        options |= (inputAddressType << 1)
        options |= (pageAddressFormat << 10)
       
        diagCmd.cdb[2] = GetByte(0, options)
        diagCmd.cdb[3] = GetByte(1, options)
        diagCmd.cdb[4] = GetByte(0, lba)
        diagCmd.cdb[5] = GetByte(1, lba)
        diagCmd.cdb[6] = GetByte(2, lba)
        diagCmd.cdb[7] = GetByte(3, lba)
        diagCmd.cdbLen = len(diagCmd.cdb)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            print "LBA TranslateToPhysical: PASS"
        except PyServiceWrap.CmdException as ex:
            print "LBA TranslateToPhysical: Fail", ex
        
        PhyLocDict = {}
        PhyLocDict["lba"] = buf.GetFourBytesToInt(0x4)
        PhyLocDict["fimChannel"] = buf.GetOneByteToInt(0x21)
        PhyLocDict["chip"] = buf.GetOneByteToInt(0x11)
        PhyLocDict["die"] = buf.GetOneByteToInt(0x12)
        PhyLocDict["plane"] = buf.GetOneByteToInt(0x13)
        PhyLocDict["block_P"] = buf.GetTwoBytesToInt(0x14) * 2 + buf.GetOneByteToInt(0x13)
        #PhyLocDict["wordLine"] = buf.GetTwoBytesToInt(0x16)
        #PhyLocDict["string"] = buf.GetOneByteToInt(0x17)
        
        PhyLocDict["wordLine"] = buf.GetOneByteToInt(0x1F)
        PhyLocDict["string"] = buf.GetOneByteToInt(0x20)

        #phyAddr.wlInBlock=db.GetByte(0x16)  
        #phyAddr.pageInWl=db.GetByte(0x17)

        PhyLocDict["page"] = buf.GetTwoBytesToInt(0x16)
        PhyLocDict["fmuInPage"] = buf.GetOneByteToInt(0x18)
        PhyLocDict["isBinary"] = buf.GetOneByteToInt(0x19)
        PhyLocDict["isErased"] = buf.GetOneByteToInt(0x1A)
        PhyLocDict["lfmuSequenceLength"] = buf.GetFourBytesToInt(0x1B)
        PhyLocDict["TLCpage"] = 0
        if PhyLocDict["isBinary"]  == 0:
            PhyLocDict["TLCpage"] = buf.GetTwoBytesToInt(0x16)%3 + 1
        
        #print PhyLocDict

        #Logical die to physical die
        LogDietoPhyDie = {}
        LogDietoPhyDie[0] = 0
        LogDietoPhyDie[1] = 1
        LogDietoPhyDie[2] = 0
        LogDietoPhyDie[3] = 1
        LogDietoPhyDie[4] = 2
        LogDietoPhyDie[5] = 3
        LogDietoPhyDie[6] = 2
        LogDietoPhyDie[7] = 3

        #if buf.GetOneByteToInt(0x12) > 1:
        #    if buf.GetOneByteToInt(0x12)%2:
        #        die = (buf.GetOneByteToInt(0x12) / 2) + (PhyLocDict["fimChannel"]+1)%2
        #    else
        #        die = (buf.GetOneByteToInt(0x12) / 2) -  PhyLocDict["fimChannel"]
        #die = LogDietoPhyDie[PhyLocDict["die"]]
        #PhyLocDict["die"] = die
        
        block = buf.GetTwoBytesToInt(0x14)*2 + buf.GetOneByteToInt(0x13)
        wordline = buf.GetOneByteToInt(0x1F)
        string = buf.GetOneByteToInt(0x20)

        self.ToAddr(die, block, wordline, string, 0)

        return PhyLocDict
    
    def GetParamSeq(self, FIObj, param_addr):
        
        if g_Verbose:
            print("GetParamSeq")        

        if param_addr > 0xFF:
            msb_addr = 1
        else:
            msb_addr = 0
        lsb_addr = param_addr & 0xFF
        
        die_no = 0xF0 | (FIObj.die + 1)
        
        seq = [CMD2, die_no, 0x56, ADDR1, 0x01, DATA_IN, 0x0, 0x1, 0x36, CMDEND, CMD1, 0x55, ADDR1, 0xff, DATA_IN, 0x0, 0x1, msb_addr, CMDEND, CMD1, 0, ADDR1, lsb_addr, CMD1, 0x5f,  DELAY, 0x0, 0x1, DATA_OUT, 0x0, 0x2, CMDEND]
        #seq = [CMD5, 0xF1, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        numOfSectors = 1
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)   
        retbyte = retbuf.GetOneByteToInt(0)
        
        if g_Verbose:  
            print("GetParamSeq {}".format(hex(param_addr)) + "return = {}".format(hex(retbyte)) )
            #retbuf.WriteToFile("GetParamSeq.bin", numOfSectors*512) 
                
        return retbyte
    
    def SetParamSeq(self, FIObj, param_addr, param_val):
        
        if g_Verbose:
            print("SetParamSeq")        
        
        if param_addr > 0xFF:
            msb_addr = 1
        else:
            msb_addr = 0
        lsb_addr = param_addr & 0xFF
    
        die_no = 0xF0 | (FIObj.die + 1)
        
        seq = [CMD2, die_no, 0x56, ADDR1, 0xff, DATA_IN, 0x0, 0x1, msb_addr, CMDEND, CMD1, 0x56, ADDR1, lsb_addr, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x1, param_val, CMD1, 0x56, ADDR1, 0xff, DATA_IN, 0x0, 0x1, 0, CMDEND]
        #seq = [CMD5, 0xF1, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMDEND]
        
        #seq = [cmd2, 0xF1, 0x56, addr1, 0x01, data, 0x0, 0x1, 36, cmd1, 0x55, addr1, 0xff, 0x0, cmd1, 0, addr1, paddr, cmd1, 0x5f, data_in, 0x0, 0x1, cmdend]
        #seq = [CMD5, 0xF1, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        retbyte = self.GetParamSeq(FIObj, param_addr)
        
        return retbyte

    def GetParam(self, fim, CE, die, param_addr):
    
        opcode = 0xBB
        setget = 1
        Param = 0
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = fim
        diagCmd.cdb[2] = CE
        diagCmd.cdb[3] = setget
        diagCmd.cdb[4] = Param
        diagCmd.cdb[5] = die
        diagCmd.cdb[6] = param_addr
        diagCmd.cdb[7] = param_addr >> 8
        diagCmd.cdbLen = len(diagCmd.cdb)

        buf = PyServiceWrap.Buffer.CreateBuffer(1, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            #print "GetParam: PASS"
        except PyServiceWrap.CmdException as ex:
            print "GetParam: FAIL", ex.GetFailureDescription()
       
        paramValue = buf.GetOneByteToInt(0)
        
        print("GetParam = \t {}".format(hex(param_addr)) + " Value = \t {}".format(hex(paramValue)) )
        
        return paramValue
        
    def GetParam_Set(self, fim, CE, die, param_addr):
    
        opcode = 0xBB
        setget = 1
        Param = 0
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = fim
        diagCmd.cdb[2] = CE
        diagCmd.cdb[3] = setget
        diagCmd.cdb[4] = Param
        diagCmd.cdb[5] = die
        diagCmd.cdb[6] = param_addr
        diagCmd.cdb[7] = param_addr >> 8
        diagCmd.cdbLen = len(diagCmd.cdb)

        buf = PyServiceWrap.Buffer.CreateBuffer(1, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            #print "GetParam: PASS"
        except PyServiceWrap.CmdException as ex:
            print "GetParam: FAIL", ex.GetFailureDescription()
       
        paramValue = buf.GetOneByteToInt(0)
        
        return paramValue
       
    def SetParam(self, fim, CE, die, param_addr, param_val):
        
        paramValue = self.GetParam(fim, CE, die, param_addr)
        
        opcode = 0xBB
        setget = 0
        Param = 0
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = fim
        diagCmd.cdb[2] = CE
        diagCmd.cdb[3] = setget
        diagCmd.cdb[4] = Param
        diagCmd.cdb[5] = die
        diagCmd.cdb[6] = param_addr
        diagCmd.cdb[7] = param_addr >> 8
        diagCmd.cdb[8] = param_val
        diagCmd.cdbLen = len(diagCmd.cdb)
        
        buf = PyServiceWrap.Buffer.CreateBuffer(1, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            #print "SetParam: PASS"
        except PyServiceWrap.CmdException as ex:
            print "SetParam: FAIL", ex.GetFailureDescription()
        
        paramValue = self.GetParam_Set(fim, CE, die, param_addr)
        
        print("SetParam = \t {}".format(hex(param_addr)) + " Value = \t {}".format(hex(paramValue)) )
        
        return paramValue
     
    def ParseFADLog(self, fadFilePath, faSchemaPath):
        
        xPlorerFADPath = "C:\\xTools\\app\\xfaddecoder\\"
        if os.path.exists(xPlorerFADPath):
            cwd = os.getcwd()
            os.chdir(xPlorerFADPath)
            xplFadCmd = "xfaddecoder-cli.bat --product=C-Rex-SATA --fad-path="+fadFilePath+" --sdb-path="+faSchemaPath+" --output-format=FAD_SUMMARY"
            result = subprocess.Popen(xplFadCmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            #output = result.stdout.read().replace('\n', '').replace('\r', '')
            time.sleep(2)
            #output.split(':')[-1].strip()
            os.chdir(cwd)
        else:
            print "xPlorer tool is Missing"
        return

    def FALogDump(self, option = 0, faSchemaPath = None):
        
        opcode = 0xD7
        
        sector_cnt = 1
        if option == 0:
            sector_cnt = (self.FALogDump(1)).GetFourBytesToInt(0)
            #print sector_cnt

        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = 0
        diagCmd.cdb[2] = 0
        diagCmd.cdb[3] = 0
        diagCmd.cdb[4] = GetByte(0, option)
        diagCmd.cdb[5] = GetByte(1, option)
        diagCmd.cdb[6] = 0
        diagCmd.cdb[7] = 0
        diagCmd.cdb[8] = GetByte(0, sector_cnt)
        diagCmd.cdb[9] = GetByte(1, sector_cnt)
        diagCmd.cdb[10] = GetByte(2, sector_cnt)
        diagCmd.cdb[11] = GetByte(3, sector_cnt)
        diagCmd.cdbLen = len(diagCmd.cdb)
        
        buf = PyServiceWrap.Buffer.CreateBuffer(sector_cnt, patternType=PyServiceWrap.ALL_0, isSector=True)
        
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
            print "FA Error Log dump: Failed", ex
        
        if option == 0:
            fadFile = "Yoda_FADump.FAD"
            buf.WriteToFile(fadFile, sector_cnt*512)
            print "FA Error Log dumped to", fadFile
        
        if faSchemaPath != None:
            time.sleep(2)
            cwd = os.getcwd()
            fadFilePath = '"'+os.path.join(cwd,fadFile)+'"'
            self.ParseFADLog(fadFilePath, faSchemaPath)
            print "\n\nFA Error Log Parsed to", fadFile[:-4]+".csv"
        return buf
		
    def EnterUserMode(self, fim, ce):
       
        #Read NandStatus
        #seq = [cmd2, 0xF1, 0xFD, DELAY, 0x0, 0x1, cmdend, cmd2, 0xF1, 0x70, cmdend, cmd1, 0xEC, addr1, 0x40, WAIT_RB, DATA_OUT, 0x47, 0xA0, cmdend]
        seq = [CMD4, 0xF1, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return

    def MBRefresh(self, FIObj, AttrObj):
        """
        Description: EraseBlock_Single
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: True = Success, False = Fail
        Exceptions: None
        """
        ret = True
        
        
        AttrObj.PlaneType = PlaneType.single

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)        
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, 0, 0, 0)
        
        
        seq = [CMD3, die_no, 0xA2, CmdLoadAddr, ADDR3, b0_addr[2], b0_addr[3], b0_addr[4], DELAY, 0x0, 0x1, CMD1, CmdAutoErase, DELAY, 0x0, 0x1, WAIT_RB, CMD1, CmdResetAll, WAIT_RB, CMDEND]
        seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        return ret


    def TestModeEntry(self, fim, ce):
        
        #Read NandStatus
        #seq = [cmd2, 0xF1, 0xFD, DELAY, 0x0, 0x1, cmdend, cmd2, 0xF1, 0x70, cmdend, cmd1, 0xEC, addr1, 0x40, WAIT_RB, DATA_OUT, 0x47, 0xA0, cmdend]
        seq = [CMD5, 0xF1, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return
        
    def TempPara(self, fim, ce, die):
	
        if die<0 or die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (die + 1)
		
        #Read NandStatus
        #seq = [CMD1, 0x55, ADDR1, 0x03, DATA_IN, 0x00, 0x01, 0x00, CMDEND, CMD1, 0x55, ADDR1, 0x04, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0x05, DATA_IN, 0x00, 0x01, 0x0A, CMDEND]
        seq = [CMD2, die_no, 0x55, ADDR1, 0x03, DATA_IN, 0x00, 0x01, 0x00, CMDEND, CMD1, 0x55, ADDR1, 0x04, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0x05, DATA_IN, 0x00, 0x01, 0x02, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        return  

    def DistRead(self, fim, ce, die, block_no, wl, string, SLC_Flag):
        #Read NandStatus
        #seq = [cmd2, 0xBC, 0x00, ADDR5, 0x00, 0x00, 0x09, 0x00, 0x40, cmd1, 0xAE, cmd1, 0x3D, cmdend, cmd1, 0x05, ADDR5, 0x00, 0x00, 0x09, 0x00, 0x40, cmd1, 0xE0, DELAY, 0x01, 0x2C, DATA_OUT, 0x40, 0x00, cmdend]
        if die<0 or die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (die + 1)
        b0_addr = self.ToAddr(die, block_no, wl, string, 0)
        if SLC_Flag == 1:
            seq = [CMD4, die_no, 0xA2, 0xBC, 0x00, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xAE, WAIT_RB, CMD2, 0xA2, 0x3D, WAIT_RB, CMDEND, CMD1, 0x05, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xE0, DELAY, 0x01, 0x2C, DATA_OUT, 0x47, 0xA0, CMDEND]
            print(" -> SLC read should be happen with SLC Sequence")
        elif SLC_Flag == 2:
			#print("DistRead")
			#print(b0_addr)
			seq = [CMD3, die_no, 0xBC, 0x00, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xAE, WAIT_RB, CMD1, 0x3D, WAIT_RB, CMDEND, CMD1, 0x05, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xE0, DELAY, 0x01, 0x2C, DATA_OUT, 0x47, 0xA0, CMDEND]
			print("# -> TLC read should be happen with TLC Sequence")
        else:
            seq = [CMD4, die_no, 0xDD, 0xBC, 0x00, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xAE, WAIT_RB, CMD1, 0x3D, WAIT_RB, CMDEND, CMD1, 0x05, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xE0, DELAY, 0x01, 0x2C, DATA_OUT, 0x47, 0xA0, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        numOfSectors = 36
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        #retbuf.WriteToFile("DistRead1.bin", numOfSectors*512)
        return retbuf
    def NextDistRead(self, fim, ce, die, block_no, wl, string, SLC_Flag): 
       
        if die<0 or die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (die + 1)        
        b0_addr = self.ToAddr(die, block_no, wl, string, 0)
        if SLC_Flag == 1:
            seq = [CMD3, die_no, 0xA2, 0x3D, CMD1, 0x05, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xE0, DELAY, 0x01, 0x2C, DATA_OUT, 0x47, 0xA0, CMDEND]
        else:
            seq = [CMD2, die_no, 0x3D, CMD1, 0x05, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0xE0, DELAY, 0x01, 0x2C, DATA_OUT, 0x47, 0xA0, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        numOfSectors = 36
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Updated
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        #retbuf.WriteToFile("DistRead2.bin", numOfSectors*512)
        return retbuf
    
    def Exit_DistRead(self, fim, ce, die):       
        die_no = 0xF0 | (die + 1)
        seq = [CMD2, die_no, 0xA5, WAIT_RB, CMD2, 0x41, 0x35, WAIT_RB, CMD1, 0xA8, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
     
    def TestModeExit(self, fim, ce, die):       
        die_no = 0xF0 | (die + 1)        
        #execute Reset Command 
        seq = [CMD2, die_no, 0xFF, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
     
    def default_Tempara(self, fim, ce, die):        
        die_no = 0xF0 | (die + 1)

        seq = [CMD2, die_no, 0x55, ADDR1, 0x03, DATA_IN, 0x00, 0x01, 0x00, CMDEND, CMD1, 0x55, ADDR1, 0x04, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0x05, DATA_IN, 0x00, 0x01, 0x00, CMDEND]
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
    
    def countSetBits(self, num):
        setBits = [0]
        # convert given number into binary
        # output will be like bin(11)=0b1101
        if num:
            binary = bin(num)
            # now separate out all 1's from binary string
            # we need to skip starting two characters
            # of binary string i.e; 0b
            setBits = [ones for ones in binary[2:] if ones=='1']
        return (len(setBits))
    
    def Count_1stinfile(self,readbuf):
        #file = open("DistRead10.bin", "rb")
        byte =  readbuf.GetOneByteToInt(0)#file.read(1)
        #print(byte)		
        count = 0 
        for i in range(1, 18336): 
            count = count + self.countSetBits(byte)    
            byte =  readbuf.GetOneByteToInt(i)
        return count
    
    def getCVD(self, fim, ce, die, block_no, wl, string, SLC_Flag, vt_Shift, csvWriter, isVerbose):
        vlt = 0
        prev_count=0
        count = 0
        global g_Verbose
        g_Verbose = isVerbose
        
        Loop_Count = 6.98/vt_Shift
        
        #outFileName = "SLC_GetCVDTest_0xAA55wl4.csv"
        #ouputcsv = open(outFileName, 'wb')
        #file = input("Capture GoLogic if needed and then press 1:" )
        #readbuf = obj.NandStatus()
        if SLC_Flag == 3:
            self.TestModeEntry(fim, ce, die)
            self.TempPara(fim, ce, die)
            readbuf = self.DistRead(fim, ce, die, block_no, wl, string, SLC_Flag)
            readbuf.WriteToFile("NDWL.bin", 36*512)
        else:
            self.EnterUserMode(fim, ce)
            self.TempPara(fim, ce, die)
            readbuf = self.DistRead(fim, ce, die, block_no, wl, string, SLC_Flag)
            readbuf.WriteToFile("TLCDistReadfromhexfile.bin", 36*512)
        count = self.Count_1stinfile(readbuf)
        if prev_count:
			csvWriter.writerow(["user_WL", fim, ce, die, wl, string, count, block_no, vlt, count-prev_count])
        else:
            csvWriter.writerow(["user_WL", fim, ce, die, wl, string, count, block_no, vlt, 0])
        
        for i in range(1, int(Loop_Count)): #int(Loop_Count)
            #print(i)
            prev_count=count
            readbuf = self.NextDistRead(fim, ce, die, block_no, wl, string, SLC_Flag)
            readbuf.WriteToFile("NextTLCDistReadfromhexfile.bin", 36*512)
            #print(count)
            count = self.Count_1stinfile(readbuf)
            vlt = vlt + vt_Shift
            if prev_count:
                csvWriter.writerow(["user_WL", fim, ce, die, wl, string, count, block_no, vlt, count-prev_count])
            
            #readbuf.Dump()
            #print("2nd")
            #print(count)
             
        if SLC_Flag == 3:
            self.Exit_DistRead(fim, ce, die)
        else:
            self.TestModeExit(fim, ce, die)
        self.default_Tempara(fim, ce, die)

    def csv_parameter(self, ret, offsetstart, offsetend):
        j=0
        parameter = [0]*((offsetend-offsetstart)+1)
        for i in range(offsetstart, offsetend+1):
            byte = chr(ret.GetOneByteToInt(i)) #file.read(1)
            parameter[j] = byte
            j=j+1
        return parameter 
    
    def csv_parameter_date(self, ret, offsetstart, offsetend):
        j=0
        parameter = [0]*((offsetend-offsetstart)+3)
        for i in range(offsetstart, offsetend+1):
            byte = chr(ret.GetOneByteToInt(i))  
            parameter[j] = byte
            j=j+1
            if j==2 or j==5: 
                parameter[j] = '/'
                j=j+1    
        return parameter  

    def csv_parameter_time(self, ret, offsetstart, offsetend):
        j=0
        parameter = [0]*((offsetend-offsetstart)+3)
        for i in range(offsetstart, offsetend+1):
            byte = chr(ret.GetOneByteToInt(i))  
            parameter[j] = byte
            j=j+1
            if j==2 or j==5: 
                parameter[j] = ':'
                j=j+1    
        return parameter         
   
    def WaferInfo(self, ce, fim, die):
         
        
        if die==0:   
            ad5=0x00
        elif die==1:
            ad5=0x20
        elif die==2:
            ad5=0x40
        elif die==3:
            ad5 =0x60
        elif die==4:
            ad5=0x80
        elif die==5:
            ad5=0xA0
        elif die==6:
            ad5=0xC0
        elif die==7:
            ad5=0xE0
        else:
            print("Die: Invalid Value")
            
        if die<0 or die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (die + 1)
		
        self.Manual_POR_FDh(fim, ce, die)
        
        seq = [CMD5, die_no, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD3, 0x5A, 0xBE, 0x00, ADDR5, 0x00, 0x00, 0x36, 0x02, ad5, CMD1, 0x30, WAIT_RB, CMD1, 0x05, ADDR5, 0x00, 0x00, 0x36, 0x02, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
       
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
    
        numOfSectors = 36
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        WaferInformation = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        WaferInformation[0] = ce
        WaferInformation[1] = fim
        WaferInformation[2] = die
        WaferInformation[3] = self.csv_parameter(retbuf, 0x112, 0x11E) #lotID
        WaferInformation[4] = self.csv_parameter(retbuf, 0x129, 0x12A) # Wafer ID
        WaferInformation[5] = self.csv_parameter(retbuf, 0x12B, 0x12C)  #X coordinate
        WaferInformation[6] = self.csv_parameter(retbuf, 0x12D, 0x12E)  #Y cordinate
        WaferInformation[7] = self.csv_parameter_date(retbuf, 0x026, 0x02B)  # Sorted Date
        WaferInformation[8] = self.csv_parameter_time(retbuf, 0x02C, 0x031)  # Sorted time
        WaferInformation[9] = self.csv_parameter(retbuf, 0x135, 0x138) #Parameter Version
        WaferInformation[10] = self.csv_parameter(retbuf, 0x13A, 0x13C)  #DSversion
        retbuf.WriteToFile("Reg_Waferinformation" + "_" + str(ce) + "_" + str(fim) + "_" + str(die) + "_" + str(datetime_.datetime.now().strftime("%d%m%Y-%H%M%S")) + ".bin", 36*512)
        
        #retbuf.WriteToFile("Waferinformation.bin", 36*512)
         
       # print (WaferInformation)
       # outFileName = "readstamp.csv"
        cwd = os.getcwd()
        os.chdir(cwd+str("\WaferInfoLatest"))
        ouputcsv = open("readstamp" + "CE" + str(ce) + "Fim" + str(fim) + "Die" + str(die) + ".csv", 'wb')
        csvWriter = csv.writer(ouputcsv, delimiter=',')
        csvWriter.writerow(["CE", "FIM", "Die", "Lot Number", "Wafer ID", "X coordinate", "Y coordinate", "Sorted Date(YY/MM/DD)", "Sorted Time (Hours(HH):Minutes(XX):Seconds(SS))", "Parameter Version", "DS Version"])
        csvWriter.writerow([WaferInformation[0], WaferInformation[1], WaferInformation[2], ''.join(WaferInformation[3]), ''.join(WaferInformation[4]), ''.join(WaferInformation[5]) , ''.join(WaferInformation[6]), ''.join(WaferInformation[7]), ''.join(WaferInformation[8]),''.join(WaferInformation[9]), ''.join(WaferInformation[10])])
        print("Wafer information read operation done")
        ouputcsv.close()
        os.chdir(cwd)
        time.sleep(5)
        
        return
   
    def Memceldata(self, fim, die):

        if die==0:   
            ad5=0x00
        elif die==1:
            ad5=0x20
        elif die==2:
            ad5=0x40
        elif die==3:
            ad5 =0x60
        elif die==4:
            ad5=0x80
        elif die==5:
            ad5=0xA0
        elif die==6:
            ad5=0xC0
        elif die==7:
            ad5=0xE0
        else:
            print("Die: Invalid Value")

        if die<0 or die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (die + 1)
		
        seq = [CMD5, die_no, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD3, 0x5A, 0xBE, 0x00, ADDR5, 0x00, 0x00, 0x88, 0x00, ad5, CMD1, 0x30, WAIT_RB, CMD1, 0x05, ADDR5, 0x00, 0x00, 0x88, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

        numOfSectors = 36
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        
        retbuf.WriteToFile("Memceldata.bin", 36*512)
    
        return retbuf
        
    def RegFuseRead(self, fim, ce, die, avpgm):        
        if die==0:   
                ad5=0x00
        elif die==1:
                ad5=0x20
        elif die==2:
                ad5=0x40
        elif die==3:
                ad5 =0x60
        elif die==4:
                ad5=0x80
        elif die==5:
                ad5=0xA0
        elif die==6:
                ad5=0xC0
        elif die==7:
                ad5=0xE0
        else:
                print("Die: Invalid Value")
        
        die_no = 0xF0 | (die + 1)
        
        print "Regfuse dump fim" + "-" + str(fim) + "-" + "die " + str(die)
        
        #self.Manual_POR_FDh(fim, 0, die)
        
        # retbyte = self.StatusRead(fim, die, CmdStatus70)
        # if not retbyte == 0xE0:
            # for i in range(10):
                # retbyte = self.StatusRead(fim, die, CmdStatus70)        
                    
        #seq = [CMD4, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD3, 0x5A, 0xBE, 0x00, WAIT_RB, CMD1, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
        
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD2, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #FwSeq
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0, DATA_IN, 0, 1, 1, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2,
        #CMD2, die_no, 0x56, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x56, ADDR1, 1, DATA_IN, 0, 1, 6, CMD1, 0xAA, WAIT_RB, CMD2, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #FwSeq
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0, DATA_IN, 0 ,1, 1, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2,  
        #CMD1, 0x56, ADDR1, 0xFF, DATA_IN, 0x0, 0x1, 0, CMD1, 0x56, ADDR1, 0x1, DATA_IN, 0, 1, 6, CMD1, 0x56, ADDR1, 3, DATA_IN, 0, 1, 0xFF, CMD1, 0x56, ADDR1, 0xFF,
        #DATA_IN, 0, 1, 0, CMD1, 0x0, ADDR1, 0x63, CMD2, 0xEA, 0x57, ADDR1, 63, DATA_IN, 0, 1,  0x98, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 2,
        #CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0, DATA_IN, 0, 1, 1, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2,
        #CMD2, die_no, 0x56, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x56, ADDR1, 1, DATA_IN, 0, 1, 6, CMD1, 0xAA, WAIT_RB, CMD2, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        
        # Only AVPGM Seq
        if 0:
            #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0, DATA_IN, 0 ,1, 1, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2,  
            #CMD1, 0x56, ADDR1, 0xFF, DATA_IN, 0x0, 0x1, 0, CMD1, 0x56, ADDR1, 0x1, DATA_IN, 0, 1, 6, CMD1, 0x56, ADDR1, 3, DATA_IN, 0, 1, 0xFF, CMD1, 0x56, ADDR1, 0xFF,
            #DATA_IN, 0, 1, 0, CMD1, 0x0, ADDR1, 0x63, CMD2, 0xEA, 0x57, ADDR1, 63, DATA_IN, 0, 1,  0x98, CMD1, 0xFF, CMDEND]
            
            #seq = [CMD1, 0xFF, WAIT_RB, CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0, DATA_IN, 0 ,1, 1, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2,  
            #CMD2, die_no, 0x56, ADDR1, 0xFF, DATA_IN, 0x0, 0x1, 0, CMD1, 0x56, ADDR1, 0x1, DATA_IN, 0, 1, 6, CMD1, 0x56, ADDR1, 3, DATA_IN, 0, 1, 0xFF, CMD1, 0x56, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x0, ADDR1, 0x63, CMD2, 0xEA, 0x57, ADDR1, 0x63, DATA_IN, 0, 1,  0x90, CMD1, 0x56, ADDR1, 0xFF, DATA_IN, 0 , 1, 0,
            #CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2, CMDEND]
            
            seq = [CMD2, die_no, 0xFF, WAIT_RB, CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0 ,1, 0, CMD1, 0x55, ADDR1, 0x63, DATA_IN, 0, 1,  0x9D, CMD1, 0x55, ADDR1, 0xFF, DATA_IN, 0 , 1, 0, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2, CMDEND]
            
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            print "Avpgm 9D set"
        
        
        #AVPGM Seq
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0, DATA_IN, 0 ,1, 1, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2,  
        #CMD1, 0x56, ADDR1, 0xFF, DATA_IN, 0x0, 0x1, 0, CMD1, 0x56, ADDR1, 0x1, DATA_IN, 0, 1, 6, CMD1, 0x56, ADDR1, 3, DATA_IN, 0, 1, 0xFF, CMD1, 0x56, ADDR1, 0xFF,
        #DATA_IN, 0, 1, 0, CMD1, 0x0, ADDR1, 0x63, CMD2, 0xEA, 0x57, ADDR1, 63, DATA_IN, 0, 1,  0x98, CMD1, 0xFF,
        #CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0x01, DATA_IN, 0, 1, 2, CMD1, 0x55, ADDR1, 0xFF, DATA_IN, 0 , 1, 0,
        #CMD2, 0xAA, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #NanoSeq
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0x01, DATA_IN, 0, 1, 2, CMD2, 0x9E, 0x55, ADDR1, 0xFF, DATA_IN, 0 , 1, 0,
        #CMD1, 0xAA, WAIT_RB, CMD4, 0xE9, 0x4c, die_no, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #AppNote
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, 
        #CMD3, 0x9E, 0x4D, 0x55, ADDR1, 0x1, DATA_IN, 0, 1, 1, CMD1, 0xAA, WAIT_RB, CMD1, 0xE9,
        #CMD3, 0x4c, die_no, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #FwSeq
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0x00, 0x01, 0x00, CMD1, 0x55, ADDR1, 0, DATA_IN, 0, 1, 1, CMD2, die_no, 0x70, WAIT_RB, DATA_OUT, 0, 0x2,
        #CMD2, die_no, 0x56, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x56, ADDR1, 1, DATA_IN, 0, 1, 6, CMD1, 0xAA, WAIT_RB, CMD2, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #Design manual 246
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x55, ADDR1, 0xFF, DATA_IN, 0, 1, 0xF,  CMD1, 0xCA, WAIT_RB, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x55, ADDR1, 1, DATA_IN, 0, 1, 6, CMD1, 0xAA, WAIT_RB, CMD2, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #NNT RegFuses
        #seq = [CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x55, ADDR1, 0x01, DATA_IN, 0, 1, 0xF,  CMD1, 0x55, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0xCA, WAIT_RB, CMD3, 0x5C, 0xC5, 0x55, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x55, ADDR1, 1, DATA_IN, 0, 1, 2, CMD1, 0x55, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0xAA, WAIT_RB, CMD2, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMD1, 0xFF, CMDEND]
        
        #FwSeqf
        seq = [CMD2, die_no, 0xFF, WAIT_RB, CMD4, 0x5C, 0xC5, die_no, 0x56, ADDR1, 0xFF, DATA_IN, 0, 1, 0, CMD1, 0x56, ADDR1, 1, DATA_IN, 0, 1, 6, CMD1, 0xAA, WAIT_RB, CMD3, die_no, 0x4c, 0x05, ADDR5, 0x00, 0x00, 0x00, 0x00, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
        
        print ad5
        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, fim, ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
    
        numOfSectors = 36
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        retbuf.WriteToFile("Regfuse_FwSeq_" + str(fim) + "_" + str(die) + "_"  + str(avpgm) + "_" + str(datetime_.datetime.now().strftime("%d%m%Y-%H%M%S")) +  ".bin", 36*512)
        
        time.sleep(5)
         
        #print "try5"
       # outFileName = "readstamp.csv"
        return
        
    def ReadUserrom(self,plane):
        print("ReadUserrom")
        if plane==0:
            seq = [CMD2, 0xF1, 0xFD, DELAY, 0x13, 0x88, WAIT_RB, CMDEND, CMD6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD4, 0x5A, 0xBE, 0xA2, 0x00, ADDR5, 0x00, 0x00, 0x90, 0x01, 0x00, WAIT_RB, DATA_OUT, 0x47, 0xA0, CMDEND]

            seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

            numOfSectors = 36
            buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
            cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
            retbuf.WriteToFile("ReadUserrom_P0.bin", numOfSectors*512)
            #return retbuf
        elif plane==1:
            seq = [CMD2, 0xF1, 0xFD, DELAY, 0x13, 0x88, WAIT_RB, CMDEND, CMD6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD4, 0x5A, 0xBE, 0xA2, 0x00, ADDR5, 0x00, 0x00, 0x90, 0x03, 0x00, WAIT_RB, DATA_OUT, 0x47, 0xA0, CMDEND]
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

            numOfSectors = 36
            buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
            cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
            retbuf.WriteToFile("ReadUserrom_P1.bin", numOfSectors*512)
            #return retbuf
        else:
            #seq = [CMD4, 0x61, 0x40, 0x8F, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD3, 0x5A, 0xBE, 0x00, ADDR5, 0x00, 0x00, 0x36, 0x02, ad5, CMD1, 0x30, WAIT_RB, CMD1, 0x05, ADDR5, 0x00, 0x00, 0x36, 0x02, ad5, CMD1, 0xE0, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
            seq = [CMD1, 0xF1, DELAY, 0x13, 0x88, WAIT_RB, CMDEND, CMD6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD4, 0x5A, 0xBE, 0xA2, 0x00, ADDR5, 0x00, 0x00, 0x88, 0x00, 0x00, CMD1, 0x30, WAIT_RB, CMD1, 0x05, ADDR5, 0x00, 0x00, 0x88, 0x00, 0x00, CMD1, 0xE0,WAIT_RB, DATA_OUT, 0x47, 0xA0, CMDEND]
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

            numOfSectors = 36
            buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
            cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
            retbuf.WriteToFile("ReadUserrom_P0.bin", numOfSectors*512)
            #return retbuf
            
            seq = [CMD1, 0xF1, DELAY, 0x13, 0x88, WAIT_RB, CMDEND, CMD6, 0x61, 0x40, 0x8F, 0x5C, 0xC5, 0x55, ADDR1, 0x00, DATA_IN, 0x00, 0x01, 0x01, CMD4, 0x5A, 0xBE, 0xA2, 0x00, ADDR5, 0x00, 0x00, 0x88, 0x02, 0x00, CMD1, 0x30, WAIT_RB, CMD1, 0x05, ADDR5, 0x00, 0x00, 0x88, 0x02, 0x00, CMD1, 0xE0, WAIT_RB, DATA_OUT, 0x47, 0xA0, CMDEND]
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

            numOfSectors = 36
            buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
            cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
            retbuf.WriteToFile("ReadUserrom_P1.bin", numOfSectors*512)
			
    def GetBER(self, die, plane, block, fmu, blockType):
    
        opcode = 0xD6
        setget = 1
        Param = 0
        #print "FADLE"
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = 0xD6 #opcode
        diagCmd.cdb[1] = 0x0F #Sub-opcode
        diagCmd.cdb[2] = 0x00 #option 
        diagCmd.cdb[3] = 0x01 #sector count
        diagCmd.cdb[4] = die #Logical Die
        diagCmd.cdb[5] = plane 
        diagCmd.cdb[6] = block #Block (LSB) 
        diagCmd.cdb[7] = block >> 8 #Block (MSB) 
        diagCmd.cdb[8] = fmu #FMU in block (LSB)
        diagCmd.cdb[9] = fmu >> 8 #FMU in block (MSB)
        diagCmd.cdb[10] = blockType # SLC = 0 TLC = 1 
        diagCmd.cdb[11] = 0x0 #Read Attributes
        diagCmd.cdb[12] = 0x0
        diagCmd.cdb[13] = 0x0
        diagCmd.cdb[14] = 0x0 #options (LSB)   #0x20 - page, #0 raw
        diagCmd.cdb[15] = 0x0 #Options (LSB)    #0x13 - page, #0x12 raw SLC, #0x10 raw MLC
        
        diagCmd.cdbLen = len(diagCmd.cdb)
		
        buf = PyServiceWrap.Buffer.CreateBuffer(1, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            #print "GetParam: PASS"
        except PyServiceWrap.CmdException as ex:
            print "GetBER: FAIL", ex.GetFailureDescription()
       
        BERValue = buf.GetFourBytesToInt(16)
        #csvWriter.writerow([die, plane, block, fmu, blockType, paramValue])
        print("GetBER = \t {}".format(hex(fmu)) + " Value = \t {}".format(hex(BERValue)) )
        buf.WriteToFile("GetBER.bin", 1*512)
        return BERValue
    	
    def TLC_Read_Page_CustomShifts_SB1(self, FIObj, AttrObj, CustomShifts):
        """
        Description: TLC_Read_Page
        Parameters:
            @param: FlashInfoClass object
            @param: FlashAttributesClass
        Returns: retbuf, Read data of FIObj.block_no1
        Exceptions: None
        """
        if AttrObj.isVerbose:
            print("TLC_Read_Page_CustomShifts")

        global g_Verbose
        g_Verbose = AttrObj.isVerbose
        
        
        AttrObj.BlkType = BlkType.TLC
        AttrObj.PlaneType = PlaneType.single

        if FIObj.die<0 or FIObj.die>7:  #Die input check
            print("Die: Invalid Value")        
        die_no = 0xF0 | (FIObj.die + 1)
        
        b0_addr = self.ToAddr(FIObj.die, FIObj.block_no1, FIObj.wl, FIObj.string, 0)

        if AttrObj.FlashReset:
            self.Flash_CMD_Reset(FIObj.fim, FIObj.ce, FIObj.die)

        if AttrObj.FDReset:
            self.Manual_POR_FDh(FIObj.fim, FIObj.ce, FIObj.die)

        
        if FIObj.PageType == PageType.LP:
            sf_addr0 = 0
            sf_addr1 = 0
            sf_addr2 = CustomShifts.DShift
            sf_addr3 = 0
	    
            numOfSectorsSPSeq = 2

            """ seq = [CMD1, 0xD5, ADDR2, FIObj.die, 0x8A, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, sf_addr0, sf_addr1, sf_addr2, sf_addr3, WAIT_RB,
            CMD1, 0xD5, ADDR2, FIObj.die, 0x93, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, 0xF6, 0xF6, 0xF2, 0, WAIT_RB,        
            CMD1, 0xD5, ADDR2, FIObj.die, 0x95, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, 0xA, 0xA, 0xE, 0, WAIT_RB,
            CMD1, 0xD5, ADDR2, FIObj.die, 0x8A, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, sf_addr0, sf_addr1, sf_addr2, sf_addr3, WAIT_RB,
            CMD6, die_no, CmdDynRead, 0x26, 0xC2, int(FIObj.PageType), CmdReadAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, 0x31, WAIT_RB, 
            CMD1, CmdReadColAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND] """ 

            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x89, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
        
            idx = 512
            seqbuf.SetByte(idx, sf_addr0)
            seqbuf.SetByte(idx+1, sf_addr1)
            seqbuf.SetByte(idx+2, sf_addr2)
            seqbuf.SetByte(idx+3, sf_addr3)
        
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_LP" + "_.bin", numOfSectorsSPSeq*512)
            print("Cus LP" + str(hex(sf_addr0)) + str(hex(sf_addr1)) + str(hex(sf_addr2)) + str(hex(sf_addr3)))
            ###################################################
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x93, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
        
            idx = 512
            seqbuf.SetByte(idx, 0xF6)
            seqbuf.SetByte(idx+1, 0xF6)
            seqbuf.SetByte(idx+2, 0xF2)
            seqbuf.SetByte(idx+3, 0)
        
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_LP" + "_.bin", numOfSectorsSPSeq*512)
            ################################
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x95, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
        
            idx = 512
            seqbuf.SetByte(idx, 0xA)
            seqbuf.SetByte(idx+1, 0xA)
            seqbuf.SetByte(idx+2, 0xE)
            seqbuf.SetByte(idx+3, 0)
        
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            #seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_LP" + "_.bin", numOfSectorsSPSeq*512)
            ##############################################################################

            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x89, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
        
            idx = 512
            seqbuf.SetByte(idx, sf_addr0)
            seqbuf.SetByte(idx+1, sf_addr1)
            seqbuf.SetByte(idx+2, sf_addr2)
            seqbuf.SetByte(idx+3, sf_addr3)
        
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_LP" + "_.bin", numOfSectorsSPSeq*512)
            print("Cus LP" + str(hex(sf_addr0)) + str(hex(sf_addr1)) + str(hex(sf_addr2)) + str(hex(sf_addr3)))

        if FIObj.PageType == PageType.MP:
            sf_addr0 = CustomShifts.AShift
            sf_addr1 = CustomShifts.CShift
            sf_addr2 = 0
            sf_addr3 = CustomShifts.FShift
	    
            numOfSectorsSPSeq = 2
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x89, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
        
            idx = 512
            seqbuf.SetByte(idx, sf_addr0)
            seqbuf.SetByte(idx+1, sf_addr1)
            seqbuf.SetByte(idx+2, sf_addr2)
            seqbuf.SetByte(idx+3, sf_addr3)
        
            for idx, sq in enumerate(seq):
	            seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            #seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_MP" + "_.bin", numOfSectorsSPSeq*512)
            print("Cus MP" + str(hex(sf_addr0)) + str(hex(sf_addr1)) + str(hex(sf_addr2)) + str(hex(sf_addr3)))

        if FIObj.PageType == PageType.UP:
            sf_addr0 = int(CustomShifts.BShift)
            sf_addr1 = int(CustomShifts.EShift)
            sf_addr2 = int(CustomShifts.GShift)
            sf_addr3 = 0
	    
            #sf_addr0 = 0
            #sf_addr1 = 0
            #sf_addr2 = CustomShifts.DShift
            #sf_addr3 = 0
            
            numOfSectorsSPSeq = 2
            
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x8A, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
            
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
            
            idx = 512
            seqbuf.SetByte(idx, sf_addr0)
            seqbuf.SetByte(idx+1, sf_addr1)
            seqbuf.SetByte(idx+2, sf_addr2)
            seqbuf.SetByte(idx+3, sf_addr3)
            
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            #seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_UP" + "_.bin", numOfSectorsSPSeq*512)
            print("Cus UP" + str(hex(sf_addr0)) + str(hex(sf_addr1)) + str(hex(sf_addr2)) + str(hex(sf_addr3)))
            ###################################################
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x93, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
            
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
            
            idx = 512
            seqbuf.SetByte(idx, 0xF6)
            seqbuf.SetByte(idx+1, 0xF6)
            seqbuf.SetByte(idx+2, 0xF2)
            seqbuf.SetByte(idx+3, 0)
            
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_UP" + "_.bin", numOfSectorsSPSeq*512)
            ################################
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x95, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
            
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
            
            idx = 512
            seqbuf.SetByte(idx, 0xA)
            seqbuf.SetByte(idx+1, 0xA)
            seqbuf.SetByte(idx+2, 0xE)
            seqbuf.SetByte(idx+3, 0)
            
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_UP" + "_.bin", numOfSectorsSPSeq*512)
            ##############################################################################
            '''
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x8A, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
            
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
            
            idx = 512
            seqbuf.SetByte(idx, sf_addr0)
            seqbuf.SetByte(idx+1, sf_addr1)
            seqbuf.SetByte(idx+2, sf_addr2)
            seqbuf.SetByte(idx+3, sf_addr3)
            
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_UP" + "_.bin", numOfSectorsSPSeq*512)
            print("Cus UP" + str(hex(sf_addr0)) + str(hex(sf_addr1)) + str(hex(sf_addr2)) + str(hex(sf_addr3)))	     """

	    '''
	    '''
            #Upper page page
            numOfSectorsSPSeq = 2
            seq = [CMD2, die_no, 0xD5, ADDR1, int(FIObj.die), ADDR1, 0x8A, DATA_IN_E, 0x0, 0x4, CMDEND]
            seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]
        
            seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSPSeq, patternType=PyServiceWrap.ALL_0, isSector=True)
        
            idx = 512
            seqbuf.SetByte(idx, sf_addr0)
            seqbuf.SetByte(idx+1, sf_addr1)
            seqbuf.SetByte(idx+2, sf_addr2)
            seqbuf.SetByte(idx+3, sf_addr3)
        
            for idx, sq in enumerate(seq):
                seqbuf.SetByte(idx, sq)
            cdb = [0x95, 0, FIObj.fim, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
            seqbuf.WriteToFile("TLC_Read_Page_CustomShifts_UP" + "_.bin", numOfSectorsSPSeq*512)
            print("Cus UP" + str(hex(sf_addr0)) + str(hex(sf_addr1)) + str(hex(sf_addr2)) + str(hex(sf_addr3)))
	    '''

        #seq =  [CMD6, die_no, CmdDynRead, 0x26, 0xC2, int(FIObj.PageType), CmdReadAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, 0x31, WAIT_RB, 
        #CMD1, CmdReadColAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]

        seq =  [CMD5, die_no, CmdDynRead, 0x26,  int(FIObj.PageType), CmdReadAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0x30, WAIT_RB, 
        CMD1, CmdReadColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]

        # seq = [CMD2, die_no, 0xD5, ADDR2, FIObj.die, 0x8A, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, sf_addr0, sf_addr1, sf_addr2, sf_addr3, CMD1, 0xD5, ADDR2, FIObj.die, 0x93, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, 0xF6, 0xF6, 0xF2, 0, CMD1, 0xD5, ADDR2, FIObj.die, 0x95, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, 0xA, 0xA, 0xE, 0, CMD1, 0xD5, ADDR2, FIObj.die, 0x8A, DELAY, 0x0, 0x1, DATA_IN, 0x0, 0x4, sf_addr0, sf_addr1, sf_addr2, sf_addr3, CMD6, die_no, CmdDynRead, 0x26, 0xC2, int(FIObj.PageType), CmdReadAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, 0x31, WAIT_RB, CMD1, CmdReadColAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]       
        # seq = seq + [0 for i in range(0, 512-len(seq)) if 512 > len(seq)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        retbuf.WriteToFile("TLC_SB1_HB_" + str(FIObj.die) + "-" + str(FIObj.block_no1) + "-" + FIObj.PageType.name + "_Cus.bin", 18336)
	
        time.sleep(10)
	
        #self.StatusRead(FIObj.fim, FIObj.die, CmdStatus70)
        
        #seq1 = [CMD2, die_no, 0x3F, DELAY, 0x0, 0x1, CMD1, CmdReadColAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]        
        seq1 =  [CMD6, die_no, CmdDynRead, 0x26, 0xC2, int(FIObj.PageType), CmdReadAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, 0x30, WAIT_RB, 
        CMD1, CmdReadColAddr, ADDR6, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], b0_addr[5], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
        seq1 = seq1 + [0 for i in range(0, 512-len(seq1)) if 512 > len(seq1)]

        seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        for idx, sq in enumerate(seq1):
            seqbuf.SetByte(idx, sq)
        cdb = [0x95, 0, FIObj.fim, FIObj.ce, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        buf2 = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        retbuf2 = self.diagobj.sendDiagnostics(cdb, len(cdb), buf2, ioDirection = 0)
        retbuf2.WriteToFile("TLC_SB1_SB1_" + str(FIObj.die) + "-" + str(FIObj.block_no1) + "-" + FIObj.PageType.name + "_Cus.bin", 18336)
        #self.StatusRead(FIObj.fim, FIObj.die, CmdStatus70)

        # seq = [CMD4, die_no, CmdDynRead, int(FIObj.PageType), CmdReadAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, CmdArrayRead, WAIT_RB, 
        # CMD1, CmdReadColAddr, ADDR5, b0_addr[0], b0_addr[1], b0_addr[2], b0_addr[3], b0_addr[4], CMD1, CmdRegRead, DELAY, 0x0, 0x1, DATA_OUT, 0x47, 0xA0, CMDEND]
        
        # seqbuf = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)
        # for idx, sq in enumerate(seq):
	    #     seqbuf.SetByte(idx, sq)
        
        # seqbuf.Dump()
        # cdb = [0x95, 0, FIObj.fim, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)
        
        # buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
        # cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # retbuf = self.diagobj.sendDiagnostics(cdb, len(cdb), buf, ioDirection = 0)
        
        #self.StatusRead(FIObj.fim, FIObj.die, CmdStatus70)
        
        #### Get Feature #####  
        # if FIObj.PageType == PageType.UP:
            # seq = [CMD1, 0xD4, ADDR2, FIObj.die, 0x8A, DELAY, 0x0, 0x1, DATA_OUT, 0x0, 0x4, DELAY, 0x0, 0x1, CMDEND]
        # else: 
            # seq = [CMD1, 0xD4, ADDR2, FIObj.die, 0x89, DELAY, 0x0, 0x1, DATA_OUT, 0x0, 0x4, DELAY, 0x0, 0x1, CMDEND]

        # seqbuf1 = PyServiceWrap.Buffer.CreateBuffer(1, patternType=PyServiceWrap.ALL_0, isSector=True)                
        # for idx, sq in enumerate(seq):
            # seqbuf1.SetByte(idx, sq)
        # cdb = [0x95, 0, FIObj.fim, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # self.diagobj.sendDiagnostics(cdb, len(cdb), seqbuf1, ioDirection = 1)
        
        # numOfSectors = 1
        # buf2 = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
        # cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # retbuf2 = self.diagobj.sendDiagnostics(cdb, len(cdb), buf2, ioDirection = 0)   
       
        # print("\r\n Return 0 {}".format(hex(retbuf2.GetOneByteToInt(0))) + "\r\n 1 {} ".format(hex(retbuf2.GetOneByteToInt(1))) + "\r\n 2{}  ".format(hex(retbuf2.GetOneByteToInt(2))) + "\r\n 3{} ".format(hex(retbuf2.GetOneByteToInt(3))) )
        
        #retbuf2.Dump()
        
        PayloadBuf = None
        if AttrObj.isFBC:
            if not AttrObj.Payload == None:
                PayloadBuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectorsSP, patternType=PyServiceWrap.ALL_0, isSector=True)
                #filebuf.FillFromFile(AttrObj.Payload, False)
                fptr =  open(AttrObj.Payload, "rb")
                if fptr:
                    urpstr = fptr.read(x3_page_size)
                    seq = [int(hex(ord(st)),16) for st in urpstr]
                    for idx, sq in enumerate(seq):
                        PayloadBuf.SetByte(idx, sq)                    
        
        if AttrObj.isFBC:
            fbc_fmu = self.FBC_Count_Func(retbuf, AttrObj.Pattern, PayloadBuf)
        else:
            fbc_fmu = [0,0,0,0]        

        #if AttrObj.FlashReset:
        #    self.Flash_CMD_Reset(FIObj.fim, FIObj.ce)

        if AttrObj.isVerbose:
            retbuf.WriteToFile("TLC_Read_Page_" + FIObj.PageType.name + ".bin", x3_page_size) 

        if self.outCsvFile:

            csvobj1 = csvWriterClass()

            csvobj1.fim = FIObj.fim
            csvobj1.ce = FIObj.ce
            csvobj1.die = FIObj.die
            csvobj1.wl = FIObj.wl
            csvobj1.string = FIObj.string
            csvobj1.operation = 'TLC_Read_Page'
            csvobj1.pagetype = FIObj.PageType.name
            csvobj1.block = FIObj.block_no1
            csvobj1.fbc_fmu = fbc_fmu
            
            if fbc_fmu[0] > ldpc_max_decode or fbc_fmu[1] > ldpc_max_decode or fbc_fmu[2] > ldpc_max_decode  or fbc_fmu[3] > ldpc_max_decode:
                 csvobj1.result = "Fail"
            csvobj1.WriteRows(self.writer)
            
        return retbuf2
    