import CTFServiceWrapper as PyServiceWrap
import ScsiCmdWrapper as ScsiPyWrap

import os, sys
import time
import os
from time import localtime, strftime
from argparse import ArgumentParser,SUPPRESS
import json
import socket
import argparse
import subprocess
import array
from collections import OrderedDict 

keyFileName = "secureDriveKeys.bin"

productionResult     = 'Unknown'
logFilePath          = ''
logFileTimestamp     = ''
botfile              = '' 
hwDict               = dict()
enableRelayControl   = 0
sctp_delay_between_data_chunk = 0
skip_commands_during_device_init = 0
relayPortDef         = list()
powerCycleHW         = None
relayComPort         = ''
enablecp210xcontrol  = 0
cp210xComport        = ''
enableDMC            = None
enableSecureProduction = None
useEngineeringKeys = None
securityProductionFilePath = None
enableB0 = None
enableHotCountReadandRestore = None
jumptoROMviaSCTP = False

SECTOR_SIZE = 512
SINGLE_SECTOR_BUFFER = 512
SINGLE_SECTOR = 0x01
READ_DATA = 0

global pGPIOParams

from enum import Enum
class DriveMode(Enum):
    ROM = 0
    DLE = 1
    FW = 2
    
def ExecuteSCTPCommand(cdb, buf, direction):
    sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(cdb, buf, direction)

    return sctpCommand

def ReadFile(buf, fileid, sectorcount, options=0):
        
    LengthInBytes = sectorcount * SECTOR_SIZE
    Buffer = PyServiceWrap.Buffer.CreateBuffer(LengthInBytes , patternType=PyServiceWrap.ALL_1, isSector=False)
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()

    diagCmd.cdb = [0] * 16

    diagCmd.cdb[0] = 0x8A
    diagCmd.cdb[1] = 0
    diagCmd.cdb[2] = (options & 0xFF)
    diagCmd.cdb[3] = (options >> 8) & 0xFF
    diagCmd.cdb[4] = fileid & 0xFF
    diagCmd.cdb[5] = (fileid >> 8 ) & 0xFF
    diagCmd.cdb[6] = 0
    diagCmd.cdb[7] = 0
    diagCmd.cdb[8] = sectorcount & 0xFF
    diagCmd.cdb[9] = (sectorcount >> 8 ) & 0xFF
    diagCmd.cdb[10] = (sectorcount >> 16) & 0xFF
    diagCmd.cdb[11] = (sectorcount >> 24) & 0xFF
    diagCmd.cdb[12] = LengthInBytes & 0xFF
    diagCmd.cdb[13] = (LengthInBytes >> 8 ) & 0xFF
    diagCmd.cdb[14] = (LengthInBytes >> 16) & 0xFF
    diagCmd.cdb[15] = (LengthInBytes >> 24) & 0xFF

    diagCmd.cdbLen = 16

    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, Buffer, PyServiceWrap.DIRECTION_OUT,True, None, 200000, PyServiceWrap.SEND_IMMEDIATE)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()
    except PyServiceWrap.CmdException as ex :
        print ex.GetFailureDescription()
        #self.logger.SmallBanner("DIAG: READ_FILE FAILED", "FATAL")
        #raise ValidationError.CVFGenericExceptions("SctpUtils", "READ_FILE Command failed - %s" % ex)
    #self.logger.SmallBanner("DIAG: READ_FILE SUCCESS")
    return Buffer

def WriteFile(buf, fileid, sectorcount, option=0,timeOut=1000):
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
    options = option
    fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
    fbcccdb.cdb = [0]*16
    fbcccdb.cdbLen = 16

    fbcccdb.cdb[0] = 0x8B
    fbcccdb.cdb[1] = 0
    fbcccdb.cdb[2] = options & 0xFF
    fbcccdb.cdb[3] = (options >> 8) & 0xFF
    fbcccdb.cdb[4] = (fileid & 0xFF)
    fbcccdb.cdb[5] = (fileid >> 8) & 0xFF
    fbcccdb.cdb[6] = 0
    fbcccdb.cdb[7] = 0
    fbcccdb.cdb[8] = (sectorcount & 0xFF)
    fbcccdb.cdb[9] = (sectorcount >> 8) & 0xFF
    fbcccdb.cdb[10] = (sectorcount >> 16) & 0xFF
    fbcccdb.cdb[11] = (sectorcount >> 24) & 0xFF

    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_IN)
        sctpCommand.Execute()
        sctpstatus = sctpCommand.GetStatusFrame()
        #self.returnSctpStaus= sctpstatus.Status				
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()
    except PyServiceWrap.CmdException as ex:
        print ex.GetFailureDescription()
        #self.logger.SmallBanner("DIAG: WRITE_FILE FAILED", "FATAL")
        #raise ValidationError.CVFGenericExceptions("SctpUtils", "WRITE_FILE Command failed - %s" % ex)
    #self.logger.SmallBanner("DIAG: WRITE_FILE SUCCESS")
    
def ReadEFUSE():
    """
    Description: readEFUSE used to read EFUSE.
    Parameters: None
    Returns: EFUSE Buffer
    Exceptions: None
    """
    secCount = 1

    opcode = 0xD8
    subOpcode = 0xA

    lengthInBytes = secCount * SECTOR_SIZE
    buf = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_0, isSector=False)
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
    diagCmd.cdb = [0] * 16
    diagCmd.cdb[0] = opcode
    diagCmd.cdb[1] = (subOpcode & 0xFF)
    diagCmd.cdb[2] = (subOpcode >> 8) & 0xFF	
    diagCmd.cdb[8] = (secCount & 0xFF)
    diagCmd.cdb[9] = (secCount >> 8) & 0xFF
    diagCmd.cdb[10] = (secCount >> 16) & 0xFF
    diagCmd.cdb[11] = (secCount >> 24) & 0xFF		

    diagCmd.cdbLen = len(diagCmd.cdb)

    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()
        buf.Dump()
    except PyServiceWrap.CmdException as ex:
        print("DIAG: READ_EFUSE FAILED", "FATAL")
        #raise ValidationError.TestFailError("SctpUtils", "READ_EFUSE Diag Command Failed - %s" % ex)
    #self.logger.SmallBanner("DIAG: READ_EFUSE SUCCESS")
    return buf

def GetCardGeometry():
    """
    Description: GetCardGeometry gives information related to card.
    Parameters: None
    Returns:
            @return: card information is returned
    Exceptions: None
    """
    # Notes: do not call this function from test. Info provided by this diag
    # can be accessed using global vars. eg. self.globalVars.fwCardBio.numOfDiesPerChip
    secCount = 1
    opcode = 0xB8
    CDB_LENGTH = 16
    #print "Hi"
    
    lengthInBytes = secCount * SECTOR_SIZE
    buf = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_0, isSector=False)
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
    diagCmd.cdb = [0] * CDB_LENGTH
    diagCmd.cdb[0] = opcode
    diagCmd.cdbLen = len(diagCmd.cdb)
    #print "Hi1"
    try:
        #print "Hi4"
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()
        buf.Dump()
        #print "Hi2"
    except PyServiceWrap.CmdException as ex:
        print("DIAG: GET_CARD_GEOMETRY FAILED", "FATAL")
        #raise ValidationError.TestFailError("SctpUtils", "GET_CARD_GEOMETRY Diag Command Failed - %s" % ex)
    #self.logger.SmallBanner("DIAG: GET_CARD_GEOMETRY SUCCESS")

    return buf    
    
def ReadFMU(buf, chip, die, plane, blockNumber, wordline, page, FMUOffset, stringline, count, option):
    """
    WIP
    Description: Read FMU info
    Parameters:
            @option:

    Returns:
            @return:
    Exceptions: None
    """
    opcode = 0xB1

    buf = PyServiceWrap.Buffer.CreateBuffer(32, patternType=PyServiceWrap.ALL_0, isSector=True)
    #{ U_08 opcode; U_08 chip; U_08 die; U_08 plane;
            #U_16 block; U_08 wordLine; U_08 page; U_08 fmuInPage; U_08 stringLine; U_16 count; U_08 reserved1[2]; U_16 options; }
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
    diagCmd.cdb = [0] * 16
    diagCmd.cdb[0] = opcode
    diagCmd.cdb[1] = chip
    diagCmd.cdb[2] = die
    diagCmd.cdb[3] = plane
    diagCmd.cdb[4] = blockNumber & 0xFF
    diagCmd.cdb[5] = (blockNumber >> 8) & 0xFF
    diagCmd.cdb[6] = wordline
    diagCmd.cdb[7] = page 
    diagCmd.cdb[8] = FMUOffset
    diagCmd.cdb[9] = stringline
    diagCmd.cdb[10] = (count & 0xFF)
    diagCmd.cdb[11] = (count >> 8) & 0xFF
    diagCmd.cdb[14] = (option & 0xFF)
    diagCmd.cdb[15] = (option >> 8) & 0xFF	
    diagCmd.cdbLen = len(diagCmd.cdb)
	
    print(diagCmd.cdb)

    try:
	print("Try Read")
	sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
        print("Try Read2")
	sctpCommand.Execute()
        print("Try Read3")
        sctpCommand.HandleOverlappedExecute()
        print("Try Read4")
        sctpCommand.HandleAndParseResponse()
        print("Try Read5")
    except PyServiceWrap.CmdException as ex:
        print("DIAG: ReadFMU FAILED", "FATAL")
        #print ex.GetFailureDescription()
	
    print("Read Data")	
    #buf.Dump()
    buf.WriteToFile("ReadOutput.bin", 32*512)
        
    return buf

def WriteFMU(buf , chip, die, plane, blockNumber, wordline, page, FMUOffset, string, count, option):
    """
    WIP
    Description: Write FMU info
    Parameters:
            @option:

    Returns
            @return:
    Exceptions: None
    """
    opcode = 0xB2
    if not buf:
        buf = PyServiceWrap.Buffer.CreateBuffer(32, patternType=PyServiceWrap.ALL_1, isSector=True)
		
	buf.Fill(0xa5)
	buf.WriteToFile("WriteInput.bin", 32*512)
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
    diagCmd.cdb = [0] * 16
    diagCmd.cdb[0] = opcode
    diagCmd.cdb[1] = chip
    diagCmd.cdb[2] = die
    diagCmd.cdb[3] = plane

    diagCmd.cdb[4] = blockNumber & 0xFF
    diagCmd.cdb[5] = (blockNumber >> 8) & 0xFF
    diagCmd.cdb[6] = wordline
    diagCmd.cdb[7] =  page
    diagCmd.cdb[8] = FMUOffset
    diagCmd.cdb[9] = string
    
    diagCmd.cdb[10] = (count & 0xFF)
    diagCmd.cdb[11] = (count >> 8) & 0xFF
    diagCmd.cdb[14] = (option & 0xFF)
    diagCmd.cdb[15] = (option >> 8) & 0xFF	
    
    

    diagCmd.cdbLen = len(diagCmd.cdb)
    print(diagCmd.cdb)

    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_IN)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()
    except PyServiceWrap.CmdException as ex:
        #self.logger.SmallBanner("DIAG: WriteFMU FAILED", "FATAL")
        print("DIAG: WriteFMU FAILED", "FATAL")
		#raise ValidationError.TestFailError("SctpUtils", "WriteFMU Diag Command Failed - %s" % ex)
    #self.logger.SmallBanner("DIAG: WriteFMU SUCCESS")
    return buf


def CreateIdentifyDrive(buf):

    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()

    diagCmd.cdb = [0xEC, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    diagCmd.cdbLen = 16

    sctpCommand = ExecuteSCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
    return sctpCommand
    
def SendDiagnostic(dataBuffer, cdbData, direction, sectors, opcode=None, commandName = "Diagnostic command", bIsStatusPhase = True, returnStatus = False):
   """
   """
   diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
   diagCmd.cdb = cdbData
   diagCmd.cdbLen = 16

   if direction == 0:
      direction = PyServiceWrap.DIRECTION_OUT
   elif direction == 1:
      direction = PyServiceWrap.DIRECTION_IN
   else:
      direction = PyServiceWrap.DIRECTION_NONE

   try:
	    
      sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, dataBuffer, PyServiceWrap.DIRECTION_OUT)
      sctpCommand.Execute()
      #vtfContainer.logger.Info("", "[SendDiagnostic] %s issued"%commandName)
      status = sctpCommand.GetStatusFrame().Status
   except: # TestError.CVFExceptionTypes , exc:
      status = sctpCommand.GetStatusFrame().Status
      #vtfContainer.logger.Warning("","[SendDiagnostic] FBCC command %s (0x%X) failed" %(commandName, opcode))
      #vtfContainer.logger.Info("","\n %s"%exc)
      if not returnStatus:
	 raise TestError.TestFailError("", "[SendDiagonostic] Failed with exception") 
   
   if not returnStatus:
      return dataBuffer
   else:
      return status
#end of SendDiagnostic 

def GetListOfRwFiles():
   """
   Name : GetListOfRwFiles()
   
   Description : This function calls "Get FIle List diag(0x88)", gives list of Read write Files list from the file system.
                
   Arguments : 
             vtfContainer - vtfContainer Object
             
   Returns : 
            rwFileList : Read write Files from the file system          
            
   opcode = 0x88
   
   option = 1
   """
   commandName = "Get List of Read Write Files"
   opcode = 0x3B
   configurationDataBuffer = PyServiceWrap.Buffer.CreateBuffer(SINGLE_SECTOR, patternType=PyServiceWrap.ALL_0, isSector=True)
   #buf = pyServiceWrap.Buffer.CreateBuffer(32, patternType=pyServiceWrap.ALL_0, isSector=True)
   bytesPerSector = 512
   option = 1
   rwFileList = []
   #opcodeLo = ByteUtil.LowByte(opcode)
   #opcodeHi = ByteUtil.HighByte(opcode)
   
   #optionLo = ByteUtil.LowByte(option)
   #optionHi = ByteUtil.HighByte(option)
   
   cdb = [opcode,0,0,0,
          0,0,0,0,
          0,0,0,0,
          0,0,0,0 ]
   
   configurationDataBuffer =  SendDiagnostic(configurationDataBuffer, cdb, READ_DATA, SINGLE_SECTOR, opcode, commandName)
   
   for offset in range(0, bytesPerSector):      
      #Getting the file number of the file
      fileNo=configurationDataBuffer.GetOneByteToInt(offset)
      if fileNo==0x00:
         break
      else:
         rwFileList.append(fileNo)
   #Just for debugging only(Temporary Fix)
   rwFileList.remove(149)  
   rwFileList.remove(225)
   rwFileList.remove(212)
   
   return rwFileList 
   

def GetSMARTReport():
    """
    Description: This function gives SMART related information.
    Parameters: None
    Returns:
           @return: smartReport dict
    Exceptions: None
    """
    secCount = 1
    opcode = 0xDA
    subopcode = 0x17
    CDB_LENGTH = 16
    lengthInBytes = secCount * SECTOR_SIZE
    buf = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_0, isSector=False)
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
    diagCmd.cdb = [0] * CDB_LENGTH
    diagCmd.cdb[0] = opcode
    diagCmd.cdb[2] = subopcode
    diagCmd.cdbLen = len(diagCmd.cdb)

    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()
    except PyServiceWrap.CmdException as ex:
        print ex
        #self.logger.SmallBanner("DIAG: GET_SMART_REPORT FAILED", "FATAL")
        raise ValidationError.TestFailError("SctpUtils", "GET_SMART_REPORT Diag Command Failed - %s" % ex)
    #self.logger.SmallBanner("DIAG: GET_SMART_REPORT SUCCESS")

    smartReport = dict()
    smartReport['DB version'] = buf.GetFourBytesToInt(0)
    # reserved smartReport['Reserved']
    smartReport['errorMode'] = buf.GetFourBytesToInt(24)
    smartReport['maxEraseCountEnhanced'] = buf.GetFourBytesToInt(28)
    smartReport['maxEraseCountIs'] = buf.GetFourBytesToInt(32)
    smartReport['maxEraseCountMlc'] = buf.GetFourBytesToInt(36)
    smartReport['minEraseCountEnhanced'] = buf.GetFourBytesToInt(40)
    smartReport['minEraseCountIs'] = buf.GetFourBytesToInt(44)
    smartReport['minEraseCountMlc'] = buf.GetFourBytesToInt(48)
    smartReport['avgEraseCountEnhanced'] = buf.GetFourBytesToInt(52)
    smartReport['avgEraseCountIs'] = buf.GetFourBytesToInt(56)
    smartReport['avgEraseCountMlc'] = buf.GetFourBytesToInt(60)
    smartReport['readReclaimCountEnhanced'] = buf.GetFourBytesToInt(64)
    smartReport['readReclaimCountIs'] = buf.GetFourBytesToInt(68)
    smartReport['readReclaimCountMlc'] = buf.GetFourBytesToInt(72)
    smartReport['badBlockManufactory'] = buf.GetFourBytesToInt(76)
    smartReport['badBlockRuntimeEnhanced'] = buf.GetFourBytesToInt(80)
    smartReport['badBlockRuntimeIs'] = buf.GetFourBytesToInt(84)
    smartReport['badBlockRuntimeMlc'] = buf.GetFourBytesToInt(88)
    smartReport['patchTrialCount'] = buf.GetFourBytesToInt(92)
    # smartReport['patchReleaseDate'] = self.utils.GetDataFromBufferForGivenBytesToInt(buf, 96, 107)
    smartReport['patchReleaseTime'] = buf.GetEightBytesToInt(108)
    smartReport['cumulativeWriteDataSizeIn100MB'] = buf.GetFourBytesToInt(116)
    smartReport['powerFailuresCounterReqRecovery'] = buf.GetFourBytesToInt(120)
    smartReport['numberOfOccurrencesOfVccVoltageDrops'] = buf.GetFourBytesToInt(124)
    smartReport['minimalValueForAllVoltageDrops'] = buf.GetFourBytesToInt(128)
    smartReport['numberOfOccurrencesOfVccVoltageDroops'] = buf.GetFourBytesToInt(132)
    smartReport['numberOfFailuresRecoverOldHostData'] = buf.GetFourBytesToInt(136)
    smartReport['healthDeviceLevelSlc'] = buf.GetFourBytesToInt(140)
    smartReport['healthDeviceLevelMlc'] = buf.GetFourBytesToInt(144)
    smartReport['preEolState'] = buf.GetFourBytesToInt(148)
    smartReport['numOfGrownDefectWorstPlane'] = buf.GetFourBytesToInt(152)
    smartReport['totalRecoveryOperationAfterVdet'] = buf.GetFourBytesToInt(156)
    smartReport['lastRecoveryOperationAfterVdet'] = buf.GetFourBytesToInt(160)
    smartReport['cumulativeInitializationCount'] = buf.GetFourBytesToInt(164)
    smartReport['totalSparesWorstPlane'] = buf.GetTwoBytesToInt(168)
    smartReport['minSparesWorstPlane'] = buf.GetTwoBytesToInt(170)
    smartReport['criticalSystemBlocksState'] = buf.GetFourBytesToInt(172)
    smartReport['cumulativeReadDataSizeIn100MB'] = buf.GetFourBytesToInt(176)
    smartReport['cumulativeBurstWriteDataSizeIn100MB'] = buf.GetFourBytesToInt(180)
    smartReport['cumulativeHybridWriteDataSizeIn100MB'] = buf.GetFourBytesToInt(184)
    smartReport['hybridWrittenDataThresholdCrossed'] = buf.GetFourBytesToInt(188)
    smartReport['avgEraseCountHybrid'] = buf.GetFourBytesToInt(192)

    return smartReport

def LengthOfFileInBytes(fileId):			   
   #sectorCount = Constants.FS_CONSTANTS.SECTOR_SIZE_TO_GET_LENGTH_OF_FILE
   buff = PyServiceWrap.Buffer.CreateBuffer(SINGLE_SECTOR, patternType=PyServiceWrap.ALL_0, isSector=True)

   diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
   
   
   cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
   
   cdb[0] = 0x33
   cdb[1] = fileId
   cdb[2] = 0x00

   '''''
   cdb[3] = 0
   cdb[4] = (fileId & 0xFF)
   cdb[5] = (fileId >> 8) & 0xFF
   cdb[6] = (fileId >> 16) & 0xFF
   cdb[7] = (fileId >> 24) & 0xFF
   cdb[8] = sectorCount & 0x000000FF
   cdb[9] = (sectorCount >> 8 )& 0x000000FF
   cdb[10] = (sectorCount >> 16) & 0x000000FF
   cdb[11] = (sectorCount >> 24) & 0x000000FF
   cdb[12] = cdb[13] = cdb[14] = cdb[15] = 0
   '''
   diagCommand.cdb = cdb
   diagCommand.cdbLen = 16
   try:
      sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, buff, PyServiceWrap.DIRECTION_OUT)
      sctpCommand.Execute()

      fileSizeInBytes = buff.GetFourBytesToInt(0)
      fileSizeInSectors = fileSizeInBytes / 512


      return fileSizeInSectors 			
   except PyServiceWrap.CmdException as exc :
      print exc.GetFailureDescription()

def main():   
    SECTOR_SIZE = 512
    DriverType = "SCSI"
    ExecuteBit = 0x01

    # session = PyServiceWrap.Session.GetSessionObject(PyServiceWrap.SCSI_Protocol, PyServiceWrap.DRIVER_TYPE.WIN_USB, hwDict)
# #logger = SetupLogger(session)
# #SetupConfigParams(session)
    # session.Init()

    options = 1
#fileid = 212
    sectorCount = 1
    sectorSize = 4096
    dataSize = sectorCount * sectorSize

# fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
# fbcccdb.cdb = [0]*16
# fbcccdb.cdbLen = 16

# fbcccdb.cdb[0] = 0x8A
# fbcccdb.cdb[1] = 0
# fbcccdb.cdb[2] = options & 0xFF
# fbcccdb.cdb[3] = (options >> 8) & 0xFF
# fbcccdb.cdb[4] = (fileid & 0xFF)
# fbcccdb.cdb[5] = (fileid >> 8) & 0xFF
# fbcccdb.cdb[6] = 0
# fbcccdb.cdb[7] = 0
# fbcccdb.cdb[8] = (sectorCount & 0xFF)
# fbcccdb.cdb[9] = (sectorCount >> 8) & 0xFF
# fbcccdb.cdb[10] = (sectorCount >> 16) & 0xFF
# fbcccdb.cdb[11] = (sectorCount >> 24) & 0xFF

# buf = PyServiceWrap.Buffer.CreateBuffer(dataSize, PyServiceWrap.ALL_1, False)
# #buf.Dump()	
# print("Hi")
# sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_OUT)
# try:
    # sctpCommand.Execute()
    # sctpCommand.HandleOverlappedExecute()
    # sctpCommand.HandleAndParseResponse()
# except PyServiceWrap.CmdException as ex:
    # print ex.GetFailureDescription()
# buf.Dump()
# print("worked")


#ReadProductConfigurationFile()

    # tmpBuff = PyServiceWrap.Buffer.CreateBuffer(1, PyServiceWrap.ALL_0, True)

    # pIdentifyDrive = CreateIdentifyDrive(tmpBuff)

    # try:
        # pIdentifyDrive.Execute()
        # pIdentifyDrive.HandleOverlappedExecute()
        # pIdentifyDrive.HandleAndParseResponse()
        # print("Drive Identified and connected")
        # print(pIdentifyDrive)
        # tmpBuff.Dump()
    # except PyServiceWrap.CmdException as ex:
        # print ex.GetFailureDescription()
        # raise Exception("ROM Mode check failed")
    
#ReadProductConfigurationFile()
################################################################ file read section ###########################
# options=0
# sectorcount=8
# fileid=42

# LengthInBytes = sectorcount * SECTOR_SIZE
# diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
# Buffer = PyServiceWrap.Buffer.CreateBuffer(LengthInBytes , PyServiceWrap.ALL_1, isSector=False)

# diagCmd.cdb = [0] * 16

# diagCmd.cdb[0] = 0x8A
# diagCmd.cdb[1] = 0
# diagCmd.cdb[2] = (options & 0xFF)
# diagCmd.cdb[3] = (options >> 8) & 0xFF
# diagCmd.cdb[4] = fileid & 0xFF
# diagCmd.cdb[5] = (fileid >> 8 ) & 0xFF
# diagCmd.cdb[6] = 0
# diagCmd.cdb[7] = 0
# diagCmd.cdb[8] = sectorcount & 0xFF
# diagCmd.cdb[9] = (sectorcount >> 8 ) & 0xFF
# diagCmd.cdb[10] = (sectorcount >> 16) & 0xFF
# diagCmd.cdb[11] = (sectorcount >> 24) & 0xFF
# diagCmd.cdb[12] = LengthInBytes & 0xFF
# diagCmd.cdb[13] = (LengthInBytes >> 8 ) & 0xFF
# diagCmd.cdb[14] = (LengthInBytes >> 16) & 0xFF
# diagCmd.cdb[15] = (LengthInBytes >> 24) & 0xFF

# diagCmd.cdbLen = 16

# try:
    # testhandle=PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, Buffer, PyServiceWrap.DIRECTION_OUT,None, None, 200000, PyServiceWrap.SEND_IMMEDIATE)
    # testhandle.Execute()
    # testhandle.HandleOverlappedExecute()
    # testhandle.HandleAndParseResponse()
    # buffer.Dump()
# except PyServiceWrap.CmdException as ex:
    # print ex.GetFailureDescription()
    # print("DIAG: READ_FILE FAILED", "FATAL")
#########################################################################################
    #ReadEFUSE()
    #GetCardGeometry()

    # RWFiles=GetListOfRwFiles()
    # print RWFiles
    # fileChooseToWrite=42
    # #print fileChooseToWrite
    # for x in RWFiles:
        # SIZ = LengthOfFileInBytes(x)
        # print SIZ
    # fileSize = LengthOfFileInBytes(fileChooseToWrite)
    # fileBuffer = PyServiceWrap.Buffer.CreateBuffer(fileSize, 0, True)
    # Buffer = ReadFile(fileBuffer, fileChooseToWrite, fileSize)
    # Buffer.Dump()
    # exit(99)
#WriteFile(Buffer, fileChooseToWrite, fileSize)
if __name__ == "__main__":
    originalArgs = sys.argv
    main()
