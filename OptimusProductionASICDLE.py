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
import random
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
adapter              = None
cp210xComport        = ''
enableDMC            = None
enableSecureProduction = None
useEngineeringKeys = None
securityProductionFilePath = None
enableB0 = None
enableHotCountReadandRestore = None
jumptoROMviaSCTP = False

global pGPIOParams

from enum import Enum
class DriveMode(Enum):
    ROM = 0
    DLE = 1
    FW = 2

SECTOR_SIZE = 512
DriverType = "SCSI"
ExecuteBit = 0x01

#logger.EnableCTFDiagnosticTrace()
#logger.EnableCTFProductionTrace()
#logger.EnableCTFInitTrace()
#logger.EnableCTFLibraryTrace()
#logger.EnableCTFCmdTrace()
#logger.EnableCTFModelOperationTrace()

####################################################### HELPER FUNCTIONS ###############################################
def ParseArgs(parser=None):

    global cmdlineArgs
    global deviceType
    global botfile
    global adapter
    global productName
    global enable_optimus_production
    global sctp_delay_between_data_chunk
    global skip_commands_during_device_init
    global security_production
    global is_production_requried
    global do_dle
    global production_phase_2
    global DriverType
    global hwDict
    global relayPortDef
    global enableRelayControl
    global powerCycleHW
    global relayComPort
    global enableDMC
    global enableSecureProduction
    global useEngineeringKeys
    global securityProductionFilePath
    global enableB0
    global enableHotCountReadandRestore
    global enablecp210xcontrol
    global cp210xComport
    global jumptoROMviaSCTP

    if parser == None:
        parser = argparse.ArgumentParser(description="Optimus Production Script",usage=SUPPRESS)

    # Adding TLM parameters
    parser.add_argument("--driverType", type=str,default='SD_AHCI',help=argparse.SUPPRESS)
    parser.add_argument("--launchId", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--testQueueId", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--RCPlanTestName", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--labID", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--dutID", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--TxnID", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--commitID", default=None, type=str, help=argparse.SUPPRESS)
    parser.add_argument("--TestID", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--StreamName" , type=str, help=argparse.SUPPRESS)
    parser.add_argument("--TestGroupName", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--FWVersion", type=str, help=argparse.SUPPRESS)
    parser.add_argument("--SkipTestRun", type=StrToBool, default = "False", help=argparse.SUPPRESS)
    parser.add_argument("--bot", default=None, type=str, help=argparse.SUPPRESS)
    parser.add_argument("--adapter", type=int, default = None, help=argparse.SUPPRESS)
    parser.add_argument("--productFamily", type=int, default = None, help=argparse.SUPPRESS)
    parser.add_argument("--product_name", type=str, default=None)
    parser.add_argument("--enable_optimus_production", type=str, default=None)
    parser.add_argument("--sctp_delay_between_data_chunk", type=int, default=None)
    parser.add_argument("--skip_commands_during_device_init", type=int, default=None)
    parser.add_argument("--is_production_requried", type=str, default=None)
    parser.add_argument("--do_dle", type=str, default=None)
    parser.add_argument("--production_phase_2",  type=StrToBool, default = "False",help=argparse.SUPPRESS)
    parser.add_argument("--power_cycle_hw_option", type=int, default = None, help=argparse.SUPPRESS)
    parser.add_argument("--enable_auto_relay_control", type=int, default = 0, help=argparse.SUPPRESS)
    parser.add_argument("--enable_cp210x_control", type=int, default = 0, help=argparse.SUPPRESS)
    parser.add_argument("--relay_com_port", type=str, default = None, help=argparse.SUPPRESS)    
    parser.add_argument("--cp210x_com_port", type=str, default = None, help=argparse.SUPPRESS) 
    parser.add_argument("--definition_of_relay_port", '--list',nargs='+',default=None,help=argparse.SUPPRESS)
    parser.add_argument("--enable_short_stroke", type=int, default =-1, help=argparse.SUPPRESS)
    parser.add_argument("--enableDMC", type=int, default = None, help=argparse.SUPPRESS)
    parser.add_argument("--enable_optimus_secure_production", type=int, default = None , help=argparse.SUPPRESS)
    parser.add_argument("--use_engineering_keys", type=int, default = None , help=argparse.SUPPRESS)
    parser.add_argument("--security_production_secrets_config_file", type=str, default =None, help=argparse.SUPPRESS)    
    parser.add_argument("--enable_pec", type=int, default = -1, help=argparse.SUPPRESS)
    parser.add_argument("--pec_history_directory", type=str, default ='None', help=argparse.SUPPRESS)
    parser.add_argument("--enableB0", type=int, default = None, help=argparse.SUPPRESS)
    parser.add_argument("--enableHotCountReadandRestore" , type = int, default = None, help=argparse.SUPPRESS)
    parser.add_argument("--jumptoROMviaSCTP" , type = int, default = 0, help=argparse.SUPPRESS)
    parser.add_argument("--regionsupport_in_short_stroke" , type = int, default = -1, help=argparse.SUPPRESS)
    parser.add_argument("--short_stroke_startlba" , type = int, default = 0, help=argparse.SUPPRESS)
    parser.add_argument("--short_stroke_region" , type = int, default = 0, help=argparse.SUPPRESS)
    parser.add_argument("--file42_path", type=str, default ="", help=argparse.SUPPRESS)        

    try:
        cmdlineArgs = parser.parse_args()

    except:
        #PrintHelp()
        sys.exit(2)

    DriverType = cmdlineArgs.driverType.lower()
    global botfile

    if cmdlineArgs.bot:
        botfile = cmdlineArgs.bot.lower()    
    if cmdlineArgs.product_name:
        productName = cmdlineArgs.product_name.lower() 
    if cmdlineArgs.adapter is not None:
        adapter = cmdlineArgs.adapter
    if cmdlineArgs.enable_optimus_production:
        enable_optimus_production = cmdlineArgs.enable_optimus_production.lower()
    if cmdlineArgs.sctp_delay_between_data_chunk:
        sctp_delay_between_data_chunk = cmdlineArgs.sctp_delay_between_data_chunk
    if cmdlineArgs.skip_commands_during_device_init:
        skip_commands_during_device_init = cmdlineArgs.skip_commands_during_device_init
    if cmdlineArgs.is_production_requried:
        is_production_requried = cmdlineArgs.is_production_requried.lower()
    if cmdlineArgs.do_dle:
        do_dle = cmdlineArgs.do_dle.lower()                    
    if cmdlineArgs.production_phase_2:
        production_phase_2 = cmdlineArgs.production_phase_2.lower()
        
    if cmdlineArgs.enableB0 is not None:
        print("B0 Enabled")
        enableB0 = cmdlineArgs.enableB0     

    if cmdlineArgs.enableDMC is not None:
        print("DMC Enabled")
        enableDMC = cmdlineArgs.enableDMC 

    if cmdlineArgs.enableHotCountReadandRestore is not None:
        enableHotCountReadandRestore = cmdlineArgs.enableHotCountReadandRestore

    if cmdlineArgs.enable_optimus_secure_production is not None:
        enableSecureProduction = cmdlineArgs.enable_optimus_secure_production
        
    if enableSecureProduction==1:
        print("Security Production Enabled")
        cmdlineArgs.enableDMC=1
        enableDMC=1

    if cmdlineArgs.power_cycle_hw_option:
        powerCycleHW = cmdlineArgs.power_cycle_hw_option

    if cmdlineArgs.use_engineering_keys is not None:
        useEngineeringKeys=cmdlineArgs.use_engineering_keys

    if cmdlineArgs.security_production_secrets_config_file:
        securityProductionFilePath=cmdlineArgs.security_production_secrets_config_file
        print(securityProductionFilePath)

    if cmdlineArgs.enable_auto_relay_control==1:
        hwDict['SerialCommunication']='HIDAndCOMPorts'
        relayPortDef=cmdlineArgs.definition_of_relay_port
        enableRelayControl = cmdlineArgs.enable_auto_relay_control
        if cmdlineArgs.relay_com_port:
            relayComPort = cmdlineArgs.relay_com_port.upper()  
            print(relayComPort)
        print(relayPortDef)

    if cmdlineArgs.enable_cp210x_control==1:
        hwDict['SerialCommunication']='HIDAndCOMPorts'
        enablecp210xcontrol = cmdlineArgs.enable_cp210x_control
        if cmdlineArgs.cp210x_com_port:
            cp210xComport = cmdlineArgs.cp210x_com_port 

    if cmdlineArgs.jumptoROMviaSCTP:
        jumptoROMviaSCTP = cmdlineArgs.jumptoROMviaSCTP


def PrintCommandLine(logger):

    if originalArgs:
        if logger != None:
            logger.Message("Command-line:")
            cmdLine = "" 
            for arg in originalArgs:
                cmdLine = cmdLine + arg + " " 

            logger.Message(cmdLine)


def WriteProductionStatusJSON():

    global logFilePath
    global logFileTimestamp
    global productionResult
    if(os.path.isfile(os.path.dirname(logFilePath) + '\\production_status.json')):
        os.unlink(os.path.dirname(logFilePath) + '\\production_status.json')
    data = {}
    data['ID'] = logFileTimestamp
    data['Log location'] = logFilePath
    data['Machine name'] = socket.gethostname()
    data['Status'] = productionResult
    data['Processed'] = False
    data['DUT ID'] = ""
    with open(os.path.dirname(logFilePath) + '\\production_status.json', 'w') as outfile:  
        json.dump(data, outfile) 


def SetupLogger(session):

    global logFilePath
    global logFileTimestamp
    if ( PyServiceWrap.DRIVER_TYPE.WIN_USB == session.GetDriverType()):
        logFilePath = os.path.join(os.environ['SANDISK_CTF_HOME_X64'], "Results")
    else:
        logFilePath = os.path.join(os.environ['SANDISK_CTF_HOME_X86'], "Results")

    if os.path.exists(logFilePath) == False:
        os.mkdir(logFilePath)

    logFileTimestamp = strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    logFile = "Production_" + logFileTimestamp + ".log"
    logFile = os.path.join(logFilePath, logFile)
    logger = PyServiceWrap.CTFLogger(logFile, PyServiceWrap.LOG_LEVEL_MESSAGE)
    logFilePath = logFile
    #logger.EnableCTFBufferTrace()
    #logger.EnableCTFDiagnosticTrace()
    #logger.EnableCTFCmdTrace()
    #logger.EnableCTFPeripheralHWTrace()
    #logger.EnableCTFDiagnosticErrorTrace()
    #logger.EnableCTFProductionTrace()
    return logger


def SetupConfigParams(session):

    global deviceSerialNumber
    global deviceCapacity
    global deviceVendor
    global deviceType
    global deviceAdapterType
    global enableVendorBasedSelection
    global productName
    global allowPecFallbackG
    global isSecure
    global useEngineeringKeys
    global enableSecureProduction
    global adapter
    global enableHotCountReadandRestore

    parser = session.GetConfigInfo()
    parser.SetValue("enable_auto_relay_control",enableRelayControl)
    parser.SetValue("enable_writebuf_for_sctp", 1)
    parser.SetValue("enable_microcode_download", 1)

    if adapter >= 0:
        parser.SetValue("adapter_index", adapter)

    if securityProductionFilePath is not None:
        parser.SetValue("security_production_secrets_config_file",securityProductionFilePath)        
        
    if enableSecureProduction==None:
        enableSecureProduction = parser.GetValue("enable_optimus_secure_production",0)[0]     
        if enableSecureProduction==1:
            enableDMC=1
            cmdlineArgs.enableDMC=1
            
    if enableSecureProduction==1:
        if useEngineeringKeys==None:
            useEngineeringKeys = parser.GetValue("use_engineering_keys",1)[0]

    if relayComPort is not '' and relayComPort is not None:
        parser.SetValue("relay_com_port",relayComPort)

    if enableRelayControl==1 and relayPortDef is not None and len(relayPortDef)==1:
        relayDefString = '[' + str(relayPortDef[0].replace(',',' '))+']'
        parser.SetValue("definition_of_relay_port",relayDefString)

    if sctp_delay_between_data_chunk:
        parser.SetValue("sctp_delay_between_data_chunk",sctp_delay_between_data_chunk)

    if skip_commands_during_device_init:
        parser.SetValue("skip_commands_during_device_init",skip_commands_during_device_init)

    if enablecp210xcontrol:
        parser.SetValue("device_adapter_type", "cp210x")
        parser.SetValue("cp210x_port", cp210xComport)
        
    if enableHotCountReadandRestore is None:
        enableHotCountReadandRestore = parser.GetValue("enableHotCountReadandRestore",0)[0]


def StrToBool(param):
    if param.lower() in ("yes", "true", "t", "1"):
        return True
    elif param.lower() in ("no", "false", "f", "0"):
        return False  
    raise Exception("{} cannot interpret as Bool".format(param))


def GetMaxLba(buf, logger):

    maxLba =  GetMax28BitLba(buf, logger)

    if ( maxLba == 0xFFFFFFE ):
        maxLba = GetMax48BitLba(buf, logger)

        if(maxLba < 0xFFFFFE):
            return 0xFFFFFE
        else:
            return maxLba

    return maxLba


def GetMax28BitLba(buf, logger):
    TOTAL_LBAS_OFF    = 0x78
    number_of_lba_addressable_sectors = buf.GetFourBytesToInt(TOTAL_LBAS_OFF)

    if(number_of_lba_addressable_sectors > 0):
        return number_of_lba_addressable_sectors - 1 
    else:
        return 0


def GetMax48BitLba(buf, logger):

    number_of_lba_addressable_sectors = buf.GetEightBytesToInt(0xC8,ScsiPyWrap.DetectByteSwapOrder(buf))

    if (0 == number_of_lba_addressable_sectors):
        logger.Error("****** ERROR: The number of sectors addressable using 48-bit LBA is 0."" Max 48-bit LBA is undefined. ")

    if(number_of_lba_addressable_sectors > 0):
        return number_of_lba_addressable_sectors - 1 
    else:
        return 0

def FromHexStringArrayToByteArray(hexStr):

    tmp = hexStr.decode("utf-8")
    tmpArr = array.array('B')
    count = 0
    while count + 1 < len(tmp):
        i = int(tmp[count], 16) << 4
        i |= int(tmp[count + 1], 16)
        count +=2
        tmpArr.append(i)
    if (len(tmp)%2 != 0):
        i = int(tmp[count], 16)
        tmpArr.append(i)        
    return tmpArr

def GetByte(pos, val):
    assert type(pos) == int, "pos type must be integer"
    assert type(val) == int, "val type must be integer"

    return (val >> (pos * 8)) & 0xFF

####################################################### HELPER METHODS ###################################################


def CreateWriteMultiFile(buf, sectorCount):

    options = 1
    fileid = 0
 
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
    fbcccdb.cdb[8] = (sectorCount & 0xFF)
    fbcccdb.cdb[9] = (sectorCount >> 8) & 0xFF
    fbcccdb.cdb[10] = (sectorCount >> 16) & 0xFF
    fbcccdb.cdb[11] = (sectorCount >> 24) & 0xFF

    sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_IN)

    return sctpCommand

def CreateWriteMultiFile_Format(buf, sectorCount):

    options = 1
    fileid = 0
 
    fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
    fbcccdb.cdb = [0]*16   
    fbcccdb.cdbLen = 16	
 
    fbcccdb.cdb[0] = 0x8F
    fbcccdb.cdb[1] = 0
    fbcccdb.cdb[2] = 0
    fbcccdb.cdb[3] = 0
    fbcccdb.cdb[4] = (fileid & 0xFF)
    fbcccdb.cdb[5] = (fileid >> 8) & 0xFF
    fbcccdb.cdb[6] = 0
    fbcccdb.cdb[7] = 0
    fbcccdb.cdb[8] = (sectorCount & 0xFF)
    fbcccdb.cdb[9] = (sectorCount >> 8) & 0xFF
    fbcccdb.cdb[10] = (sectorCount >> 16) & 0xFF
    fbcccdb.cdb[11] = (sectorCount >> 24) & 0xFF

    sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_IN)

    return sctpCommand

def CreateIdentifyDrive(buf):

    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()

    diagCmd.cdb = [0xEC, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    diagCmd.cdbLen = 16

    sctpCommand = ExecuteSCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
    return sctpCommand


def CreateReadFile(buf, isReadFileSize, fileid, fileSize):

    fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
    fbcccdb.cdb = [0]*16
    fbcccdb.cdbLen = 16

    if (isReadFileSize):
        sectorCount = 1
        fbcccdb.cdb[2] = 1

    else:    
        sectorCount = fileSize / 4096

        if (fileSize % 4096 == 0):
            sectorCount = sectorCount + 1
        fbcccdb.cdb[2] = 0

    fbcccdb.cdb[0] = 0x8A
    fbcccdb.cdb[1] = 0
    fbcccdb.cdb[3] = 0
    fbcccdb.cdb[4] = (fileid & 0xFF)
    fbcccdb.cdb[5] = (fileid >> 8) & 0xFF
    fbcccdb.cdb[6] = (fileid >> 16) & 0xFF
    fbcccdb.cdb[7] = (fileid >> 24) & 0xFF
    fbcccdb.cdb[8] = (sectorCount & 0xFF)
    fbcccdb.cdb[9] = (sectorCount >> 8) & 0xFF
    fbcccdb.cdb[10] = (sectorCount >> 16) & 0xFF
    fbcccdb.cdb[11] = (sectorCount >> 24) & 0xFF

    sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_OUT)
    return sctpCommand


def CreateInvalidateFlash():

    fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()

    fbcccdb.cdb = [0]*16

    fbcccdb.cdb[0] = 0x90
    fbcccdb.cdb[2] = 0x02

    fbcccdb.cdbLen = 16  

    sctpCommand = ExecuteSCTPCommand(fbcccdb, None, PyServiceWrap.DIRECTION_NONE)
    return sctpCommand


def CreateALTCommand(buf, options):

    dieOptions = 0xFFFFFFFF

    fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()

    fbcccdb.cdb = [0]*16

    fbcccdb.cdbLen = 16

    fbcccdb.cdb[0] = 0xB5
    fbcccdb.cdb[3] = 0
    fbcccdb.cdb[4] = options & 0xFF
    fbcccdb.cdb[5] = (options >> 8) & 0xFF
    fbcccdb.cdb[6] = dieOptions & 0xFF
    fbcccdb.cdb[7] = (dieOptions >> 8) & 0xFF
    fbcccdb.cdb[8] = (dieOptions >> 16) & 0xFF
    fbcccdb.cdb[9] = (dieOptions >> 24) & 0xFF	

    sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_NONE)
    return sctpCommand


def CreateRetrieveALTResultCommand(buf):

    fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()

    fbcccdb.cdb = [0]*16

    fbcccdb.cdbLen = 16
    fbcccdb.cdb[0] = 0xB5
    fbcccdb.cdb[3] = 1

    sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_OUT)
    return sctpCommand


def ExecuteInvalidateFlash(logger):

    logger.Info("Executing Invalidate flash")

    pInvalidateflash = CreateInvalidateFlash()

    try:

        pInvalidateflash.Execute()
        pInvalidateflash.HandleOverlappedExecute()
        pInvalidateflash.HandleAndParseResponse() 

    except PyServiceWrap.CmdException as ex:
        print(ex.GetFailureDescription())
        raise Exception("Invalidate flash failed")



def ExecuteWritePortCommand(buf, portAddress, byteCount, options, jumpAddress):

    fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
    fbcccdb.cdb = [0]*16


    fbcccdb.cdb[0] = 0x8C
    fbcccdb.cdb[1] =0
    fbcccdb.cdb[2] = (options & 0xFF)
    fbcccdb.cdb[3] = (options >> 8) & 0xFF
    fbcccdb.cdb[4] = (portAddress & 0xFF)
    fbcccdb.cdb[5] = (portAddress >> 8) & 0xFF
    fbcccdb.cdb[6] = (portAddress >> 16) & 0xFF
    fbcccdb.cdb[7] = (portAddress >> 24) & 0xFF
    fbcccdb.cdb[8] = (byteCount & 0xFF)
    fbcccdb.cdb[9] = (byteCount >> 8) & 0xFF
    fbcccdb.cdb[10] = (byteCount >> 16) & 0xFF
    fbcccdb.cdb[11] = (byteCount >> 24) & 0xFF
    fbcccdb.cdb[12] = (jumpAddress & 0xFF)
    fbcccdb.cdb[13] = (jumpAddress >> 8) & 0xFF
    fbcccdb.cdb[14] = (jumpAddress >> 16) & 0xFF
    fbcccdb.cdb[15] = (jumpAddress >> 24) & 0xFF

    fbcccdb.cdbLen = 16

    #sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_IN)

    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_IN,True,None,200,PyServiceWrap.SEND_IMMEDIATE)
        #sctpCommand.Execute()
        #sctpCommand.HandleOverlappedExecute()
        #sctpCommand.HandleAndParseResponse()		

    except PyServiceWrap.CmdException as ex:
        print(ex.GetFailureDescription())
        raise Exception("ExecuteWritePortCommand Failed")

def ExecuteWritePortviaWriteBuffer(buffermode, inputBuff):

    print("Starting DLE through SCSI Write Buffer")
    try:
        cmdObjScsiWriteBuffer= scsiCmdWrap.ScsiWriteBuffer(mode=buffermode, bufferId=0, bufferOffset=0, paramListLength=4096, buffer=inputBuff, lun=0, isAsync=True,sendType=PyServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE )
    except PyServiceWrap.CmdException as ex:
        print(ex.GetFailureDescription())
        raise Exception("ExecuteWritePortCommand Failed")


def ExecuteSCTPCommand(cdb, buf, direction):
    sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(cdb, buf, direction)

    return sctpCommand


def ExecutePowerCycle(logger, force_download=0):
    if force_download:
        ScsiPyWrap.ConfigureProductionMode(ScsiPyWrap.PRODUCTION_MODE.FORCE_DOWNLOAD_HOST)
        time.sleep(2)
    else:
        gpiomap = PyServiceWrap.GPIO_MAP()
        gsdCmd = PyServiceWrap.PowerCycle(shutdownType=PyServiceWrap.SHUTDOWN_TYPE.GRACEFUL, pModelPowerParamsObj=None, pGPIOMap=gpiomap)
        try:
            gsdCmd.Execute()
            gsdCmd.HandleOverlappedExecute()
            gsdCmd.HandleAndParseResponse()
            logger.Info("", "Power Cycle complete")
        except (PyServiceWrap.BufferException, PyServiceWrap.GenericException, PyServiceWrap.CmdException) as ex:
            logger.Info("", "Power Cycle  failed" )
            logger.Error("", ex.GetFailureDescription())
            return False

        #Put some delay after Power cycle.
        time.sleep(2)


def SetGPIOParams(self, logger):
    global pGPIOParams
    GenericHWUtility = PyServiceWrap.GenericHWUtilties(self.session)
    pGPIOParams = GenericHWUtility.GetGPIOPinValues()
    pGPIOParams.FORCE_DOWNLOAD = 1
    pGPIOParams.HALT = 1
    pGPIOParams.POWER_ON_OFF = 0
    pGPIOParams.UART_BOOT = 1
    pGPIOParams.DISABL_PERST = 1
    pGPIOParams.INSRT_PERST = 1
    pGPIOParams.DISABL_CLKREQ = 1
    pGPIOParams.INSRT_CLKREQ = 1
    GenericHWUtility.SetGPIOPinValues(pGPIOParams)
    logger.Info("GPIO parameters set.")

def GetPECBuffer(option, sectorCount, logger):
    
    logger.Info("Getting PEC Buffer Option %d" %option)
    secCount = sectorCount
    SECTOR_SIZE = 512
    lengthInBytes = secCount * SECTOR_SIZE
    buf = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_0, isSector=False)
    cdb = [0]*16
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()    
    diagCmd.cdb = [0xD8, 0x05, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    diagCmd.cdb[2] = GetByte(0 , option)
    diagCmd.cdb[3] = GetByte(1 , option)
    diagCmd.cdb[8] = GetByte(0 , sectorCount)
    diagCmd.cdb[9] = GetByte(1 , sectorCount)
    diagCmd.cdb[10] = GetByte(2 , sectorCount)
    diagCmd.cdb[11] = GetByte(3 , sectorCount)
    diagCmd.cdbLen = 16
    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()        
    except PyServiceWrap.CmdException as ex:
        print(ex.GetFailureDescription())
        raise Exception("Getting PEC Buffer Failed for Option %d" %option)        
    return buf 

def UpdatePEC(buf, logger):
    
    logger.Info("Updating PEC")
    secCount = (buf.GetBufferSize())/512
    cdb = [0]*16
    diagCmd = PyServiceWrap.DIAG_FBCC_CDB()    
    diagCmd.cdb = [0xDE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    diagCmd.cdb[8] = GetByte(0 , secCount)
    diagCmd.cdb[9] = GetByte(1 , secCount)
    diagCmd.cdb[10] = GetByte(2 , secCount)
    diagCmd.cdb[11] = GetByte(3 , secCount)
    diagCmd.cdbLen = 16
    try:
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_IN, True, None, 100)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()        
    except PyServiceWrap.CmdException as ex:
        print(ex.GetFailureDescription())
        raise Exception("PEC Update Failed")  
    
def RetrieveAndStorePEC(pecRestoreFilePath, logger):
    
    pecBufOption0 = GetPECBuffer(0, 1, logger)
    secCountPecOption3 = pecBufOption0.GetFourBytesToInt(0)
    pecBufOption2 = GetPECBuffer(2, 8, logger)        
    
    pecBufOption3 = GetPECBuffer(3, secCountPecOption3, logger)
    pecBufOption2.Append(pecBufOption3) 
    pecBufOption2.WriteToFile(pecRestoreFilePath,(8+secCountPecOption3)*512) 
    return pecBufOption2 
    
def GetPecRestoreFilePath(pec_history_directory, logger):
    pecBufOption4 = GetPECBuffer(4, 1, logger)
    yCoord = pecBufOption4.GetTwoBytesToInt(11)
    xCoord = pecBufOption4.GetTwoBytesToInt(9)
    waferLot = pecBufOption4.GetNBytesToSignedInt(0,7)
    waferNum = pecBufOption4.GetTwoBytesToInt(7)
    pecRestoreFileName = "\\" + str(yCoord) + str(xCoord) + str(waferLot) + str(waferNum) + ".txt"
    pecRestoreFilePath = pec_history_directory + pecRestoreFileName
    return pecRestoreFilePath

def MaxLbaToCardCapacity( maxlba ):

    if (maxlba<=0):
        return "OK"

    units = []
    units.insert(0,'K')
    units.insert(1,'M')
    units.insert(2,'G')
    units.insert(3,'T')

    kb =  float( (maxlba + 1) * 512.0 ) / 1000

    for i in range(3, -1, -1):
        capacity =  kb / pow ( float ( 1000 ), float ( i ) )

        if ( capacity - 1.0 > 0 ):
            dummy = []
            c = round(capacity)
            fCapacity = int(c)
            fCapacity = str(fCapacity)
            return fCapacity + units[i] + 'B'
    return "OK"


####################################################### CLASSES ########################################################
class OptimusProduction(object):

    # def __init__(self, self.session=None, secure=None, self.Logger=None, perform_io=False, vtfArgParser=None):
    def __init__(self, session, logger):
        print("init")
        if session == None:
            raise AssertionError("You need to provide a valid session for production to work.\n")
        else:
            self.session = session
            self.configParser = session.GetConfigInfo()

        self.installDir = os.environ['SANDISK_CTF_HOME_X64']
        #adding security related params
        self.MRKpublickeySize = 547
        self.BigRMApasswordSize = 512
        self.OEMPKSize = 512
        self.OEMPKsignatureSize = 256
        self.FFUESize = 32
        self.PRPublicKeySize = 512
        self.FFUPublicKeySize = 512
        self.FFUPKSigSize = 256
        self.TELEKSize = 32
        self.TELSKSize = 32
        self.EpochSize = 1
        self.EpochOffset = 0x62

        self.LittleRMAPasswordSize = 32
        self.PSIDPasswordSize = 32
        self.SIDPasswordSize = 32
        self.ATAMasterPasswordSize = 32
        self.ProductionRMAPasswordSize = 32
        self.MSIXChangeTableSizeRAMADDRESS = 0xf00000b0
        self.MSIXChangeTableSizeData = 0x8008c011
        self.MSIXChangeTableSizeDataLength = 4	
        ## General
        self.ErrorCount=0
        self.WarningCount=0
        
        if logger == None:
            self.Logger = self.session.GetLogger()
        else:
            self.Logger = logger

        if self.Logger == None:
            raise AssertionError("Please provide a valid logger object either through constructor or through session object.")

    #def Setup(self):
        #if self.sataself.session.GetDriverType() == PyServiceWrap.DRIVER_TYPE.SD_AHCI: 
            #self.installDir = os.environ['SANDISK_CTF_HOME_X86']
        #else :
            #self.installDir = os.environ['SANDISK_CTF_HOME_X64']
        #if globalBotFile:
            #self.BotFilePath = botFile 


    def Execute(self):

        pec_history_directory_string = ""
        if cmdlineArgs.pec_history_directory != 'None':
            pec_history_directory_string = cmdlineArgs.pec_history_directory
        elif self.session.GetConfigInfo().GetValue("pec_history_directory", 'None')[0] !='None':
            pec_history_directory_string = self.session.GetConfigInfo().GetValue("pec_history_directory", 0)[0]
        else:
            pec_history_directory_string = os.path.join(os.environ['SANDISK_CTF_HOME_X64'], "PEC")
        if pec_history_directory_string[-1] == "\\":
            pec_history_directory_string = pec_history_directory_string[:-1]
        hasGettingPecBufferFailed =0
        doPEC = 0
        if cmdlineArgs.enable_pec ==-1:
            doPEC = self.session.GetConfigInfo().GetValue("enable_pec", 1)[0]
        else:
            doPEC = cmdlineArgs.enable_pec
        if doPEC > 0:  
            driveMode = self.isDriveInMode()
            if (driveMode != DriveMode.FW):  
                hasGettingPecBufferFailed = 1
            else:
                pecRestoreFilePath = GetPecRestoreFilePath(pec_history_directory_string, self.Logger)
                pecBufOption2 = RetrieveAndStorePEC(pecRestoreFilePath, self.Logger)

        #Read HotCount value from the device before the start of production
        #HotCount will be reset to 0 during the production sequence. So, it needs to be restored after the production sequence.
        if enableHotCountReadandRestore == 1:
            self.ReadHotCount()

        #EnableForceDownloadMode(sessionID,logger)
        self.configParser.SetValue('skip_setting_device_config_during_production_in_rom_mode', 1)
        driveMode = self.isDriveInMode()
        if (driveMode == DriveMode.FW):
            self.JumpToIdle()
            driveMode = self.isDriveInMode()
            if (driveMode == DriveMode.FW):
                self.Logger.Error("Production failed. Drive is not in ROM")
                raise Exception("Drive is not in ROM Mode")


        #Crex Production :Phase 1- DLE ,FW write, PowerCyle
        self.DoDle()

        self.Logger.Info("Executing  PowerCycle")
        ExecutePowerCycle(self.Logger)

        #Set sctp diagnostic chunk size to 8 before formatting.
        chunksize = 8
        self.configParser.SetValue("sctp_diagnostic_chunk_size", chunksize)
        #Perform Post DLE.
        self.DoPostDle()

        ExecutePowerCycle(self.Logger)

        self.ExecuteVerificationFlow()
        driveMode = self.isDriveInMode()

        if (driveMode != DriveMode.FW):
            self.Logger.Error("Production failed. Drive is not in FW") 
            raise Exception("Production failed. Drive is not in FW")

        if doPEC > 0:
            pecRestoreFilePath = GetPecRestoreFilePath(pec_history_directory_string, self.Logger)
            if hasGettingPecBufferFailed ==1:
                from os import path
                if path.exists(pecRestoreFilePath):
                    pecBufOption2 = PyServiceWrap.Buffer.CreateBufferFromFile(pecRestoreFilePath)
                    UpdatePEC(pecBufOption2, self.Logger)
                else:
                    pecBufOption2 = RetrieveAndStorePEC(pecRestoreFilePath, self.Logger)
                    UpdatePEC(pecBufOption2, self.Logger)
            else:
                UpdatePEC(pecBufOption2, self.Logger)

        #Restore HotCount value to the device after production is complete
        if enableHotCountReadandRestore == 1:
            self.RestoreHotCount() 

        self.Logger.Info("Production successful. Drive is in FW")
        self.configParser.SetValue('skip_setting_device_config_during_production_in_rom_mode', 0)


    def isDriveInMode(self):

        tmpBuff = PyServiceWrap.Buffer.CreateBuffer(1, PyServiceWrap.ALL_0, True)

        self.Logger.Info("Executing Identify Drive - .")

        pIdentifyDrive = CreateIdentifyDrive(tmpBuff)

        try:
            pIdentifyDrive.Execute()
            pIdentifyDrive.HandleOverlappedExecute()
            pIdentifyDrive.HandleAndParseResponse()

        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            raise Exception("ROM Mode check failed")

        maxLba = GetMaxLba(tmpBuff, self.Logger)

        if (maxLba is 0):
            self.Logger.Info("Drive is in ROM")
            return DriveMode.ROM

        self.Logger.Info("Drive is not in ROM.")
        return DriveMode.FW


    def JumpToIdle(self):
        if jumptoROMviaSCTP:
            ExecuteInvalidateFlash(self.Logger)
        else:
            ExecutePowerCycle(self.Logger, force_download=1)


    def GetShortStroke(self):
        self.Logger.Info("Executing GetShortStroke")
        secCount = 1
        SECTOR_SIZE = 512
        lengthInBytes = secCount * SECTOR_SIZE
        buf = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_0, isSector=False)
        cdb = [0]*16
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0xD8, 0x0C, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        diagCmd.cdbLen = 16
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT, True, None, 100, PyServiceWrap.SEND_IMMEDIATE)
            #sctpCommand.Execute()
        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            raise Exception("GetShortStroke Failed ")
        
        return buf.GetTwoBytesToInt(0)

    def SetShortStroke(self, start_lba = 0, region = 0):
        self.Logger.Info("Executing SetShortStroke")
        secCount = 1
        SECTOR_SIZE = 512
        SS_SET_OPTION = 0x1
        lengthInBytes = secCount * SECTOR_SIZE
        buf = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_0, isSector=False)
        cdb = [0]*16
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = 0xD8
        diagCmd.cdb[1] = 0x0C
        diagCmd.cdb[2] = SS_SET_OPTION & 0xFF
        diagCmd.cdb[3] = (SS_SET_OPTION >> 8) & 0xFF
        diagCmd.cdb[4] = region & 0xFF
        diagCmd.cdb[5] = (region >> 8) & 0xFF
        diagCmd.cdb[6] = (region >> 16) & 0xFF
        diagCmd.cdb[7] = (region >> 24) & 0xFF
        diagCmd.cdb[8] = start_lba & 0xFF
        diagCmd.cdb[9] = (start_lba >> 8) & 0xFF
        diagCmd.cdb[10] = (start_lba >> 16) & 0xFF
        diagCmd.cdb[11] = (start_lba >> 24) & 0xFF
        diagCmd.cdb[12] = (start_lba >> 32) & 0xFF
        diagCmd.cdb[13] = (start_lba >> 40) & 0xFF
        diagCmd.cdb[14] = (start_lba >> 48) & 0xFF
        diagCmd.cdb[15] = (start_lba >> 56) & 0xFF

        diagCmd.cdbLen = 16
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, None, PyServiceWrap.DIRECTION_NONE)
            sctpCommand.Execute()
        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            raise Exception("SetShortStroke Failed ")

    def ReadHotCount(self):
        self.Logger.Info("Calling ReadHotCount")
        lengthInBytes = 24
        self.HotCountBuffer = PyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=PyServiceWrap.ALL_0, isSector=False)
        fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
        fbcccdb.cdb = [0]*16
        fbcccdb.cdbLen = 16

        fbcccdb.cdb[0] = 0x77

        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(fbcccdb, self.HotCountBuffer, PyServiceWrap.DIRECTION_OUT)

        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            raise Exception("ReadHotCount Failed")

        self.Logger.Info("ReadHotCount Done")

    def RestoreHotCount(self):
        self.Logger.Info("Calling RestoreHotCount")
        fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
        fbcccdb.cdb = [0]*16
        fbcccdb.cdbLen = 16

        fbcccdb.cdb[0] = 0x78

        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(fbcccdb, self.HotCountBuffer, PyServiceWrap.DIRECTION_IN)

        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            raise Exception("RestoreHotCount Failed")

        self.Logger.Info("RestoreHotCount Done")

    def ExecuteSecurityFWConfig(self):

        self.Logger.Info("Execute SecurityFWConfig Start")
        numberOfBytesSet = 0
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x4C

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16
        numberOfSectorsRequired= 6
        writeBuff = PyServiceWrap.Buffer.CreateBuffer(numberOfSectorsRequired)

        ATAMasterPasswordArr = FromHexStringArrayToByteArray(self.ATAMasterPassword)
        for i in range(0, self.ATAMasterPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, ATAMasterPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.ATAMasterPasswordSize

        LittleRMAPasswordArr = FromHexStringArrayToByteArray(self.LittleRMAPassword)
        for i in range(0, self.LittleRMAPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, LittleRMAPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.LittleRMAPasswordSize

        ProductionRMAPasswordArr = FromHexStringArrayToByteArray(self.ProductionRMAPassword)
        for i in range(0, self.ProductionRMAPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, ProductionRMAPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.ProductionRMAPasswordSize            

        BigRMApasswordArr = FromHexStringArrayToByteArray(self.BigRMApassword)
        for i in range(0, self.BigRMApasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, BigRMApasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.BigRMApasswordSize    

        PRPublicKeyArr = FromHexStringArrayToByteArray(self.PRPublicKey)
        for i in range(0, self.PRPublicKeySize):
            writeBuff.SetByte(i + numberOfBytesSet, PRPublicKeyArr[i])
        numberOfBytesSet = numberOfBytesSet + self.PRPublicKeySize    

        ffueArr = FromHexStringArrayToByteArray(self.FFUE)
        for i in range(0, self.FFUESize):
            writeBuff.SetByte(i + numberOfBytesSet, ffueArr[i])
        numberOfBytesSet = numberOfBytesSet + self.FFUESize

        oempkArr = FromHexStringArrayToByteArray(self.OEMPK)
        for i in range(0, self.OEMPKSize):
            writeBuff.SetByte(i + numberOfBytesSet, oempkArr[i])
        numberOfBytesSet = numberOfBytesSet + self.OEMPKSize

        oempkSignature = FromHexStringArrayToByteArray(self.OEMPKsignature)
        for i in range(0, self.OEMPKsignatureSize):
            writeBuff.SetByte(i + numberOfBytesSet, oempkSignature[i])
        numberOfBytesSet = numberOfBytesSet + self.OEMPKsignatureSize

        PSIDPasswordArr = FromHexStringArrayToByteArray(self.PSIDPassword)
        for i in range(0, self.PSIDPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, PSIDPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.PSIDPasswordSize

        SIDPasswordArr = FromHexStringArrayToByteArray(self.SIDPassword)
        for i in range(0, self.SIDPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, SIDPasswordArr[i])    
        numberOfBytesSet = numberOfBytesSet + self.SIDPasswordSize

        FFUPKArr = FromHexStringArrayToByteArray(self.FFUPK)
        for i in range(0, self.FFUPublicKeySize):
            writeBuff.SetByte(i + numberOfBytesSet, FFUPKArr[i])
        numberOfBytesSet = numberOfBytesSet + self.FFUPublicKeySize

        FFUPKSigArr = FromHexStringArrayToByteArray(self.FFUPKSig)
        for i in range(0, self.FFUPKSigSize):
            writeBuff.SetByte(i + numberOfBytesSet, FFUPKSigArr[i])
        numberOfBytesSet = numberOfBytesSet + self.FFUPKSigSize  

        EpochArr = FromHexStringArrayToByteArray(str(self.Epoch))
        for i in range(0, self.EpochSize):
            writeBuff.SetByte(i + numberOfBytesSet, EpochArr[i])
        numberOfBytesSet = numberOfBytesSet + self.EpochSize + 3

        if self.isTELEKExist:
            TELEKArr = FromHexStringArrayToByteArray(self.TELEK)
            for i in range(0, self.TELEKSize):
                writeBuff.SetByte(i + numberOfBytesSet, TELEKArr[i])
            numberOfBytesSet = numberOfBytesSet + self.TELEKSize

        if self.isTELSKExist:
            TELSKArr = FromHexStringArrayToByteArray(self.TELSK)
            for i in range(0, self.TELSKSize):
                writeBuff.SetByte(i + numberOfBytesSet, TELSKArr[i])

        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, writeBuff, PyServiceWrap.DIRECTION_IN, True,None,2000000)

        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
            self.Logger.Error("ExecuteSecurityFWConfig Failed")
            raise Exception("ExecuteSecurityFWConfig Failed")

        self.Logger.Info("Execute SecurityFWConfig Done")

    def ExecuteSecurityFWConfigVerify(self):
        self.Logger.Info("Execute SecurityFWConfigVerify Start")
        numberOfBytesSet = 0
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x4D

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16
        numberOfSectorsRequired= 6
        writeBuff = PyServiceWrap.Buffer.CreateBuffer(numberOfSectorsRequired)

        ATAMasterPasswordArr = FromHexStringArrayToByteArray(self.ATAMasterPassword)
        for i in range(0, self.ATAMasterPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, ATAMasterPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.ATAMasterPasswordSize

        LittleRMAPasswordArr = FromHexStringArrayToByteArray(self.LittleRMAPassword)
        for i in range(0, self.LittleRMAPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, LittleRMAPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.LittleRMAPasswordSize

        ProductionRMAPasswordArr = FromHexStringArrayToByteArray(self.ProductionRMAPassword)
        for i in range(0, self.ProductionRMAPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, ProductionRMAPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.ProductionRMAPasswordSize

        BigRMApasswordArr = FromHexStringArrayToByteArray(self.BigRMApassword)
        for i in range(0, self.BigRMApasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, BigRMApasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.BigRMApasswordSize


        PRPublicKeyArr = FromHexStringArrayToByteArray(self.PRPublicKey)
        for i in range(0, self.PRPublicKeySize):
            writeBuff.SetByte(i + numberOfBytesSet, PRPublicKeyArr[i])
        numberOfBytesSet = numberOfBytesSet + self.PRPublicKeySize    

        ffueArr = FromHexStringArrayToByteArray(self.FFUE)
        for i in range(0, self.FFUESize):
            writeBuff.SetByte(i + numberOfBytesSet, ffueArr[i])
        numberOfBytesSet = numberOfBytesSet + self.FFUESize

        oempkArr = FromHexStringArrayToByteArray(self.OEMPK)
        for i in range(0, self.OEMPKSize):
            writeBuff.SetByte(i + numberOfBytesSet, oempkArr[i])
        numberOfBytesSet = numberOfBytesSet + self.OEMPKSize

        oempkSignature = FromHexStringArrayToByteArray(self.OEMPKsignature)
        for i in range(0, self.OEMPKsignatureSize):
            writeBuff.SetByte(i + numberOfBytesSet, oempkSignature[i])
        numberOfBytesSet = numberOfBytesSet + self.OEMPKsignatureSize

        PSIDPasswordArr = FromHexStringArrayToByteArray(self.PSIDPassword)
        for i in range(0, self.PSIDPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, PSIDPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.PSIDPasswordSize

        SIDPasswordArr = FromHexStringArrayToByteArray(self.SIDPassword)
        for i in range(0, self.SIDPasswordSize):
            writeBuff.SetByte(i + numberOfBytesSet, SIDPasswordArr[i])
        numberOfBytesSet = numberOfBytesSet + self.SIDPasswordSize

        FFUPKArr = FromHexStringArrayToByteArray(self.FFUPK)
        for i in range(0, self.FFUPublicKeySize):
            writeBuff.SetByte(i + numberOfBytesSet, FFUPKArr[i])
        numberOfBytesSet = numberOfBytesSet + self.FFUPublicKeySize

        FFUPKSigArr = FromHexStringArrayToByteArray(self.FFUPKSig)
        for i in range(0, self.FFUPKSigSize):
            writeBuff.SetByte(i + numberOfBytesSet, FFUPKSigArr[i])
        numberOfBytesSet = numberOfBytesSet + self.FFUPKSigSize	

        EpochArr = FromHexStringArrayToByteArray(str(self.Epoch))
        for i in range(0, self.EpochSize):
            writeBuff.SetByte(i + numberOfBytesSet, EpochArr[i])
        numberOfBytesSet = numberOfBytesSet + self.EpochSize + 3

        if self.isTELEKExist:
            TELEKArr = FromHexStringArrayToByteArray(self.TELEK)
            for i in range(0, self.TELEKSize):
                writeBuff.SetByte(i + numberOfBytesSet, TELEKArr[i])
            numberOfBytesSet = numberOfBytesSet + self.TELEKSize
        if self.isTELSKExist:
            TELSKArr = FromHexStringArrayToByteArray(self.TELSK)
            for i in range(0, self.TELSKSize):
                writeBuff.SetByte(i + numberOfBytesSet, TELSKArr[i])

        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, writeBuff, PyServiceWrap.DIRECTION_IN, True,None,20000)

        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
            self.Logger.Error("Execute SecurityFWConfigVerify Failed")
            raise Exception("Execute SecurityFWConfigVerify Failed") 

        self.Logger.Info("Execute SecurityFWConfigVerify Done")

    def ExecuteSecurityTestHW(self):

        self.Logger.Info("Executing SecurityTestHW: Start")
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cdb[0] = 0x45
        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        try:
            #cdb, buf, direction, True, None, 10000
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, None, PyServiceWrap.DIRECTION_NONE,True,None,20000000)          #,True, None, 10000)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except:
            self.Logger.Error("SecurityOnProductionStart Failed")
            raise Exception("SecurityOnProductionStart Failed")
        self.Logger.Info("Executing SecurityTestHW: End")

    def ExecuteSecurityOnProductionStart(self):
        self.Logger.Info("SecurityOnProductionStart Start")
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cdb[0] = 0x41

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        #sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, None, PyServiceWrap.DIRECTION_NONE, None)
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, None, PyServiceWrap.DIRECTION_NONE, True,None,200000)
        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except:
            self.Logger.Error("SecurityOnProductionStart Failed")
            raise Exception("SecurityOnProductionStart Failed")

        self.Logger.Info("SecurityOnProductionStart Done")

    def ExecuteSecurityDLEConfig(self):
        self.Logger.Info("Execute SecurityDLEConfig Start")
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x43

        cdb[8]=0
        cdb[9]=4
        cdb[10]=0
        cdb[11]=0

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        numberOfSectorsRequired= 3
        writeBuff = PyServiceWrap.Buffer.CreateBuffer(numberOfSectorsRequired)

        MRKpublickeyArr = FromHexStringArrayToByteArray(self.MRKpublickey)
        for i in range(0, self.MRKpublickeySize):
            writeBuff.SetByte(i, MRKpublickeyArr[i])

        BigRMApasswordArr = FromHexStringArrayToByteArray(self.BigRMApassword)
        for i in range(0, self.BigRMApasswordSize):
            writeBuff.SetByte(i+self.MRKpublickeySize, BigRMApasswordArr[i])

        #sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, writeBuff, PyServiceWrap.DIRECTION_IN, None)
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, writeBuff, PyServiceWrap.DIRECTION_IN, True,None,200000)
        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except:
            self.Logger.Error("SecurityDLEConfig Failed")
            raise Exception("SecurityDLEConfig Failed")

        self.Logger.Info("Execute SecurityDLEConfig Done")

    def ExecuteSecurityDLEConfigVerify(self):
        self.Logger.Info("Execute SecurityDLEConfigVerify Start")
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x49

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        numberOfSectorsRequired= 3
        writeBuff = PyServiceWrap.Buffer.CreateBuffer(numberOfSectorsRequired)

        MRKpublickeyArr = FromHexStringArrayToByteArray(self.MRKpublickey)
        for i in range(0, self.MRKpublickeySize):
            writeBuff.SetByte(i, MRKpublickeyArr[i])

        BigRMApasswordArr = FromHexStringArrayToByteArray(self.BigRMApassword)
        for i in range(0, self.BigRMApasswordSize):
            writeBuff.SetByte(i+self.MRKpublickeySize, BigRMApasswordArr[i])

        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, writeBuff, PyServiceWrap.DIRECTION_IN, True,None,20000,PyServiceWrap.SEND_IMMEDIATE)
        except:
            self.Logger.Error("SecurityDLEConfigVerify Failed")
            raise Exception("SecurityDLEConfigVerify Failed")

        self.Logger.Info("Execute SecurityDLEConfigVerify Done")

    def ExecuteSecurityOnProductionEnd(self):

        self.Logger.Info("SecurityOnProductionEnd Start")
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x42

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, None, PyServiceWrap.DIRECTION_NONE,  True,None,20000)

        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except:
            self.Logger.Error("SecurityOnProductionEnd Failed")
            raise Exception("SecurityOnProductionEnd Failed")

        self.Logger.Info("SecurityOnProductionEnd Done")

    def CreateReadFile42(self, buf):

        options = 0
        fileid = 42
        sectorCount = 1
        fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()

        fbcccdb.cdb = [0]*16
        fbcccdb.cdbLen = 16
        fbcccdb.cdb[0] = 0x8A
        fbcccdb.cdb[1] = 0
        fbcccdb.cdb[2] = options & 0xFF
        fbcccdb.cdb[3] = (options >> 8) & 0xFF
        fbcccdb.cdb[4] = (fileid & 0xFF)
        fbcccdb.cdb[5] = (fileid >> 8) & 0xFF
        fbcccdb.cdb[6] = 0
        fbcccdb.cdb[7] = 0
        fbcccdb.cdb[8] = (sectorCount & 0xFF)
        fbcccdb.cdb[9] = (sectorCount >> 8) & 0xFF
        fbcccdb.cdb[10] = (sectorCount >> 16) & 0xFF
        fbcccdb.cdb[11] = (sectorCount >> 24) & 0xFF

        sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_OUT)

        return sctpCommand

    def CreateWriteFile42(self, buf, sectorCount=1, serial = "1234567890"):

        options = 0
        fileid = 42

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
        fbcccdb.cdb[8] = (sectorCount & 0xFF)
        fbcccdb.cdb[9] = (sectorCount >> 8) & 0xFF
        fbcccdb.cdb[10] = (sectorCount >> 16) & 0xFF
        fbcccdb.cdb[11] = (sectorCount >> 24) & 0xFF

        buf.PrintToLog()
        sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_IN)
        return sctpCommand

    def ExecuteSecurityLockDevice(self):

        print("Execute SecurityLockDevice Start")
        diagCommand = PyServiceWrap.DIAG_FBCC_CDB()
        cdb = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cdb[0] = 0x44

        diagCommand.cdb = cdb
        diagCommand.cdbLen = 16

        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCommand, None, PyServiceWrap.DIRECTION_NONE,True,None,20000000)  #chetan modified to avoid time out.

        try:
            sctpCommand.Execute()
        except PyServiceWrap.CmdException as ex:
            self.GiveUp(ex.GetFailureDescription())

        print("Execute SecurityLockDevice Done")

    def DownloadMicroCodeDMA(self,mode=0xE):
        chunkSize = 4
        headerSize=0x2E
        self.Logger.Info("Starting DLE through DownloadMicrocode")
        lba = 0

        blkSize = chunkSize * 1024
        sectorCount = blkSize/512

        buff = PyServiceWrap.Buffer.CreateBuffer(dataSize = sectorCount, patternType = PyServiceWrap.ALL_0, isSector = True)

        if mode == 0xF:
            try:
                #arg1 = buff (0), arg2 = offset(0), arg3 = paramListlength(0), arg4 = mode
                DM_Activate = ScsiPyWrap.DownloadMicrocode(None, 0, 0, mode, PyServiceWrap.SEND_NONE)
                DM_Activate.Execute()
                DM_Activate.HandleOverlappedExecute()
                DM_Activate.HandleAndParseResponse()

            except PyServiceWrap.CmdException as ex:
                print(ex.GetFailureDescription())
                raise Exception("DLE failed during DMC Activation")
            return

        pDLEParamsSection = self.ObjBOTParser.GetBotSection(PyServiceWrap.BOT_DLEFORMAT)
        dleF = self.ObjBOTParser.FindSection(PyServiceWrap.BOT_DLEFORMAT)
        filesize = dleF.GetDataSize() + headerSize
        #filesize = filesize+12
        dleloadaddress = dleF.GetLoadAddress()
        dlejumpaddress = dleF.GetJumpAddress()

        fbot = open(self.BotFilePath,"rb")
        stringbot = fbot.read()
        HdrLocation = stringbot.find("DLE Section Hdr")

        sDleHdr = stringbot[HdrLocation : HdrLocation + headerSize]

        nSectors = (filesize/512 +1) if(filesize%512) else (filesize/512)

        if(nSectors % sectorCount!=0):
            nSectors = nSectors + (sectorCount - nSectors%sectorCount)

        if (nSectors % sectorCount != 0):
            loop = nSectors / sectorCount + 1;
        else :
            loop = nSectors / sectorCount;

        db = PyServiceWrap.Buffer.CreateBuffer(dataSize = nSectors, patternType = PyServiceWrap.ALL_0, isSector = True)

        for i in range(headerSize):
            PyServiceWrap.Buffer.SetByte(db,i,ord(sDleHdr[i])) 
        db.Copy(headerSize, pDLEParamsSection.GetData(), 0, pDLEParamsSection.GetBufferSize())

        bufferid = 0
        offset = 0
        paramlistlength = 0

        j = 0
        for j in range(loop):
            i = 0
            for i in range(0, blkSize):
                buff.SetByte(i, db.GetByte(i + j*blkSize))
                i = i + 1
            try:
                offset = j * blkSize;
                paramlistlength = blkSize;

                DM_Download = ScsiPyWrap.DownloadMicrocode(buff, offset, paramlistlength, mode, PyServiceWrap.SEND_NONE)
                DM_Download.Execute()
                DM_Download.HandleOverlappedExecute()
                DM_Download.HandleAndParseResponse()

            except PyServiceWrap.CmdException as ex:
                print(ex.GetFailureDescription())
                raise Exception("DLE failed during DMC download ")
            lba = lba + sectorCount
            j = j + 1


    def GenerateLitteRMAPin(self, littleRMAPassword , deviceSerialNumber=0):
        """
        """
        cvfInstalledPath = ""
        self.Logger.Info("Generation of RMA Pin in Progress")

        try:
            obj = PyServiceWrap.SecurityGenPin()
            obj.GeneratePin(littleRMAPassword, deviceSerialNumber, 10000)
            retVal = obj.response;
            if len(retVal) > 0:
                self.Logger.Info("Generation of RMA Pin SUCCESS!!")
                return retVal
            else:
                self.Logger.Error("Unable to generate Little RMA Pin")
        except Exception as ex:
            raise Exception("Unable to generate Little RMA Pin {0}" .format(ex.message))


    def SecurityParseSecurityConfigReleaseEnv(self):
        #Keys needed for DLE:
        #Need to call fucntions in Production_release.py file here..
        self.Logger.Info("Creating release security keys")
        '''
        keysDict = mainReleaseEnvKeyExtract()

        for key,val  in keysDict.items():
            if((len(val)/2)>32 and (len(val)/2)<512):
                keysDict[key] = val+"0"*(1024-len(val))#self.padit(val,1024,0)   #for few keys which are suppsed to be 512 byte that is 1024 chars pad by zero

        keyFile = open(self.keyFile,'w')
        #START saba side
        for key,val  in keysDict.items():
            keyFile.write(key) #first line is key
            keyFile.write("\n")
            keyFile.write(val) #second line is val
            keyFile.write("\n")
        keyFile.write("1234") #dummy to simulate real file last line
        keyFile.close()
        #END saba side
        '''
        #START production side
        keysDict= OrderedDict()
        keyFile = open(self.keyFile,'rb')
        Lines = keyFile.readlines()
        for i in range(0, len(Lines),2):
            #read two lines
            if((i+1)>=len(Lines)):
                break
            keysDict[Lines[i].strip()] = Lines[i+1].strip()
            '''            
            print(Lines[i].strip())            
            print(Lines[i+1].strip())
            print("-----------------------------------****************************---------------------------")
            '''
            
        #END production side
        
        self.MRKpublickey = keysDict['MRKpublickey'] 
        self.BigRMApassword = keysDict['BigRMApublicKey'] 

        self.OEMPK = keysDict['OEMPK'] 
        self.FFUE = keysDict['FFUE']  
        self.FFUPK = keysDict['FFUPK']
        self.FFUPKSig = keysDict['FFUPKSig']
        self.PRPublicKey = keysDict['PRSPK']
        self.TELEK = keysDict['TELEK'] 
        self.isTELEKExist = True
        self.TELSK = keysDict['TELHK']
        self.isTELSKExist = True
        self.Epoch = keysDict['Epoch']

        self.LittleRMAPassword = keysDict['LittleRMAPassword'] 
        deviceSerialNumber = "00000000000000000000000000000000"  #temporarily using 32 zeros
        self.LittleRMAPassword = self.GenerateLitteRMAPin(self.LittleRMAPassword , deviceSerialNumber)
        self.PSIDPassword="3030303030303030303030303030303030303030303030303030303030303030"
        self.SIDPassword="184d1593c83825eba5ec4a4c7985a58ec8354eec4c6844eb2ae9499c58a4fcfb"
        self.ATAMasterPassword = ATAMasterPassword="2020202020202020202020202020202020202020202020202020202020202020"  #hardcode from crex_downloaded.ini as per discussion with Danny.
        self.ProductionRMAPassword =  keysDict['ProductionRMAPassword'] 
        self.OEMPKsignature =  keysDict['OEMPKSig']

        self.Logger.Info("SecurityParseSecurityConfigReleaseEnv Done ")


    def SecurityParseSecurityConfig(self):

        ssuFile = ""
        retTuple = self.configParser.GetValue("security_production_secrets_config_file", ssuFile)
        ssuFile = retTuple[0]

        # If an absolute path of the secrets file is given, use it. 
        # Otherwise use the file in cvf package
        if os.path.isfile(ssuFile) == False :
            ssuFile = os.path.join(self.installDir, "config\OptimusDownload.ini")
            if os.path.isfile(ssuFile) == False:
                self.Error("Security Production Failure!")    
                self.Error("Could not find security_production_secrets_config_file at the following paths :")
                self.Error(retTuple[0])
                self.Error(ssuFile)
                self.GiveUp("Could not find security_production_secrets_config_file. Exiting...")
            else :
                self.Info("Using security_production_secrets_config_file from cvf installation folder.")

        import ConfigParser

        config = ConfigParser.RawConfigParser()
        config.read(ssuFile)
        self.MRKpublickey = config.get('DLE Secrets', 'MRKpublickey')  
        self.BigRMApassword = config.get('DLE Secrets', 'BigRMAPublicKey')

        self.OEMPK = config.get('FW Secrets', 'OEMPK')  
        self.FFUE = config.get('FW Secrets', 'FFUE')
        self.FFUPK = config.get('FW Secrets', 'FFUPK')  
        self.FFUPKSig = config.get('FW Secrets', 'FFUPKSig')
        self.PRPublicKey = config.get('FW Secrets', 'PRSPK')
        if config.has_option('FW Secrets', 'TELEK'):
            self.isTELEKExist = True
            self.TELEK = config.get('FW Secrets', 'TELEK')
        else:
            self.isTELEKExist = False
        if config.has_option('FW Secrets', 'TELSK'):
            self.isTELSKExist = True
            self.TELSK = config.get('FW Secrets', 'TELSK')
        else:
            self.isTELSKExist = False


        Key = str(self.FFUPK)
        index = self.EpochOffset
        epoch = str(Key[index*2:index*2 + self.EpochSize*2])
        self.Epoch = int(epoch)

        self.LittleRMAPassword = config.get('FW Secrets', 'LittleRMAPassword')
        self.PSIDPassword = config.get('FW Secrets', 'PSIDPassword')
        self.SIDPassword = config.get('FW Secrets', 'SIDPassword')  
        self.ATAMasterPassword = config.get('FW Secrets', 'ATAMasterPassword')
        self.ProductionRMAPassword = config.get('FW Secrets', 'ProductionRMAPassword')
        self.OEMPKsignature = config.get('FW Secrets', 'OEMPKSig')

    def DoDle(self):
        self.CreateBotFileParser()
        if(enableSecureProduction == 1 and useEngineeringKeys!=1):
            self.CheckKeyFileSignature()
        bDoDLE = self.session.GetConfigInfo().GetValue("do_dle", True)

        if (bDoDLE):

            if cmdlineArgs.enableDMC==None:
                doDLEUsingDMC = self.session.GetConfigInfo().GetValue("enable_microcode_download", 1)[0]
            else:
                doDLEUsingDMC = cmdlineArgs.enableDMC
            
            if doDLEUsingDMC:
                self.DownloadMicroCodeDMA(0xE)
                self.DownloadMicroCodeDMA(0xF)
            else:
                self.DownloadAndExecute()

            self.do_short_stroke = 0
            if cmdlineArgs.enable_short_stroke == -1:
                self.do_short_stroke = self.session.GetConfigInfo().GetValue("enable_short_stroke", 0)[0]
            else:
                self.do_short_stroke = cmdlineArgs.enable_short_stroke
            if self.do_short_stroke == 1:
                
                # delay workaround for short stroke
                import time
                time.sleep(1)                

                self.GetShortStroke()
                self.SetShortStroke()
            else:
                pass
            
            import time
            time.sleep(1)
	    exit(-1)
            #GenericSleep genSleep(1, 0)
            #genSleep = PyServiceWrap.GenericSleep(1,0)

            #try:
                #genSleep.Execute()
                #genSleep.HandleOverlappedExecute()
                #genSleep.HandleAndParseResponse()

            #except PyServiceWrap.CmdException as ex:
                #print(ex.GetFailureDescription())
                #raise Exception("DoDle GenSleep failed ")

        bReadandVerifyEFuseData = self.session.GetConfigInfo().GetValue("do_efuse_operations", False)

        if bReadandVerifyEFuseData == 1:
            self.ReadAndVerifyeFuse()

        bDoALT = self.session.GetConfigInfo().GetValue("do_alt", False)

        if bDoALT == 1:
            self.ExeucteAddressLineTest()

        if bReadandVerifyEFuseData == 1:
            self.VerifyAndBurneFuse()

        self.Logger.Info("Starting Secure Production")

        if enableSecureProduction == 1:
            if(useEngineeringKeys==1):
                self.SecurityParseSecurityConfig()
            else:
                self.SecurityParseSecurityConfigReleaseEnv()
            self.ExecuteSecurityTestHW()
            self.ExecuteSecurityOnProductionStart()
            self.ExecuteSecurityDLEConfig()
            self.ExecuteSecurityDLEConfigVerify()

        self.Logger.Info("Executing  WriteBotFileSection(BOT_FIRMWARE).")

        #Formatted the card, now download whatever is there in bot file.
        result = self.WriteBotFileSection(PyServiceWrap.BOT_FIRMWARE)

        if result:
            self.Logger.Error("Execute WriteFile BOT_FIRMWARE Failed.")
            raise Exception("Execute WriteFile BOT_FIRMWARE Failed.")

        self.Logger.Info("Executing Secure DLE end.")


    def DoPostDle(self):

        self.Logger.Info("Executing  WriteBotFileSection(PyServiceWrap.BOT_CONFIG).")
        time.sleep(2)
        result = self.WriteBotFileSection(PyServiceWrap.BOT_CONFIG)

        if (result):
            self.Logger.Error("Execute WriteFile BOT_CONFIG Failed.")
            raise Exception("Execute WriteFile BOT_CONFIG Failed.")
        
        regionSupportInShortStroke = 0
        if cmdlineArgs.regionsupport_in_short_stroke== -1:
            regionSupportInShortStroke = self.session.GetConfigInfo().GetValue("regionsupport_in_short_stroke", 0)[0]
        else:
            regionSupportInShortStroke = cmdlineArgs.regionsupport_in_short_stroke     
        
        if self.do_short_stroke and regionSupportInShortStroke:
            self.Logger.Info("Execute Short Stroke diagnostic for region selection.")
            
            maxRegion = self.GetShortStroke()            
            self.Logger.Info("Max regions available are {}".format(maxRegion))
            
            start_lba = 0
            if cmdlineArgs.short_stroke_startlba == 0:
                start_lba = self.session.GetConfigInfo().GetValue("short_stroke_startlba", 0)[0]
            elif cmdlineArgs.short_stroke_startlba == -1 :
                readCapObj = ScsiPyWrap.ScsiReadCapacity16(sendType = PyServiceWrap.SEND_IMMEDIATE)
                maxLba = readCapObj.GetMaxLba()
                maxCapacity = MaxLbaToCardCapacity(maxLba)
                self.Logger.Info("Max LBA is {}".format(maxLba))                
                self.Logger.Info("Maximum capacity is {}".format(maxCapacity))
                ss_capacity_128=250000000
                ss_capacity_256=500000000
                
                if maxCapacity[0] == '1' or maxCapacity[0] == '4':
                    value = random.randrange(0,maxLba-ss_capacity_128+1)
                elif maxCapacity[0] == '2' or maxCapacity[0] == '8':
                    value= random.randrange(0,maxLba-ss_capacity_256+1)
                start_lba = value          
            else:
                start_lba = cmdlineArgs.short_stroke_startlba         
            
            ssRegion = 0
            if cmdlineArgs.short_stroke_region == 0:
                ssRegion = self.session.GetConfigInfo().GetValue("short_stroke_region", 0)[0]
            else:
                ssRegion = cmdlineArgs.short_stroke_region
            
            if ssRegion == -1:            
                region =  maxRegion-1
            elif ssRegion >= 0 and ssRegion < maxRegion:
                region = ssRegion
            elif ssRegion >= maxRegion:
                region = random.randint(0, maxRegion-1)            
            self.Logger.Info("Selection region is {}".format(region))
            self.Logger.Info("Configured LBA is {}".format(start_lba))            
            
            self.SetShortStroke(start_lba, region)            

        self.Logger.Info("Executing  WriteBotFileSection(PyServiceWrap.BOT_FORMAT).")
        time.sleep(2)
        result = self.WriteBotFileSection(PyServiceWrap.BOT_FORMAT)

        if (result):
            self.Logger.Error("Execute WriteFile BOT_FORMAT Failed.")
            raise Exception("Execute WriteFile BOT_FORMAT Failed.")


        if enableSecureProduction == 1:
            self.ExecuteSecurityFWConfig()
            self.ExecuteSecurityFWConfigVerify()
            #lifecycle provision bit in efuse enable
            self.ExecuteSecurityOnProductionEnd()
        
        file42_path= cmdlineArgs.file42_path
        buf = PyServiceWrap.Buffer.CreateBuffer(512,PyServiceWrap.ALL_1,False)
        
        # If an absolute path of the file42 file is given, use it. 
        # Otherwise use the BOT file
        if(file42_path != "" and (os.path.isfile(file42_path) == True)):
            self.Logger.Info("Using the file42 path provided:" + file42_path)
            buf.FillFromFile(file42_path, True)
                        
        else:  
            if (file42_path != "" and (os.path.isfile(file42_path) == False)) :
                self.Warn("The path provided does not exist." + file42_path)
                self.Logger.Info("Continuing with the default file.")
            
            pReadFile = self.CreateReadFile42(buf)
            try:
                pReadFile.Execute()
                pReadFile.HandleOverlappedExecute()
                pReadFile.HandleAndParseResponse()

            except PyServiceWrap.CmdException as ex:
                print(ex.GetFailureDescription())
                return ex.GetErrorNumber()

        serial = "221220640204"
        sectorCount = 1

        pWriteFile = self.CreateWriteFile42(buf, sectorCount, serial)
        try:

            pWriteFile.Execute()
            pWriteFile.HandleOverlappedExecute()
            pWriteFile.HandleAndParseResponse()

        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            return ex.GetErrorNum

        tbuf = PyServiceWrap.Buffer.CreateBuffer(512,PyServiceWrap.ALL_1,False)
        pReadFile = self.CreateReadFile42(tbuf)
        try:

            pReadFile.Execute()
            pReadFile.HandleOverlappedExecute()
            pReadFile.HandleAndParseResponse()

        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            return ex.GetErrorNumber()
            #tbuf.PrintToLog()
            #lock() set devie in deployed mode
            #self.ExecuteSecurityLockDevice()

        return 0


    def WriteProductConfiguration(self):

        self.ReadProductConfigurationFile()
        self.GetProductionConfiguration()
        self.UpdateProductConfigurationFile()


    def ReadProductConfigurationFile(self):

        fileId = 42

        self.Logger.Info("Executing Read File")

        buf = PyServiceWrap.Buffer.CreateBuffer(512,False)

        sFile42Size = CreateReadFile(buf1, true, fileId, 1) #Read File 42

        try:
            sFile42Size.Execute()
            sFile42Size.HandleOverlappedExecute()
            sFile42Size.HandleAndParseResponse()

        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())

        file42Size = buf.GetFourBytesToInt(0, True);
        buf1 = PyServiceWrap.Buffer.CreateBuffer(file42Size,False)

        sFile42 = CreateReadFile(buf1, false, fileId, file42Size) #Read File 42

        try:
            sFile42.Execute()
            sFile42.HandleOverlappedExecute()
            sFile42.HandleAndParseResponse()

        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())

    def VerifyEntireBOTAndKeyFileSignature(self, tempFilePath):
        Path = os.path.join(os.environ['SANDISK_CTF_HOME_X64'], "Python", "VerifyEntireBOTSignature.py")
        if(not os.path.isfile(Path)):
            self.Error("File not found "+Path)
            exit(-1)
        Path = '"' + Path + '"'
        args  = "--FileID " + str(tempFilePath)
        cmd  = " ".join([sys.executable, Path, args])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        status, err = proc.communicate()
        if err:
            raise RuntimeError( "\nCOMMAND: %s\n%s" % (cmd, err) )

        if("SUCCESS" in status):
            self.Info("Signature verification SUCCESS for->"+tempFilePath)
        else:
            self.Error("Signature verification FAIL for-->"+tempFilePath)
            exit(-1)

    def CheckKeyFileSignature(self):
        self.Info("Trying to verify key file signature")
        #Do not change the string in below Log statement, as it is used in file parsing in ActivateDLE and ExitDLE
        self.Info("Using bot_file : " + self.BotFilePath) 
        self.keyFile = os.path.dirname(self.BotFilePath)
        self.keyFile = os.path.join(self.keyFile,keyFileName)
        self.Info("Using Key_file : " + self.keyFile) 
        
        if(not os.path.isfile(self.keyFile)):
            self.GiveUp("Invalid Key file path; Please keep key file at same place you keep bot file.")

        if(enableSecureProduction == 1):
            self.VerifyEntireBOTAndKeyFileSignature(self.keyFile)
        self.Info("Successfully verified key signature")


    def CreateBotFileParser(self):
        self.Info("Trying to create BOT file parser")
        self.ObjBOTParser = PyServiceWrap.BOTFileParser()
        retTuple = self.configParser.GetValue("bot_file", "")
        self.BotFilePath = retTuple[0]
        global botfile
        if botfile:
            self.BotFilePath = botfile
        else:
            botfile = self.BotFilePath

        #Do not change the string in below Log statement, as it is used in file parsing in ActivateDLE and ExitDLE
        self.Info("Using bot_file : " + self.BotFilePath) 
        ret = self.ObjBOTParser.Open(self.BotFilePath)
        if ret == 1:
            self.GiveUp("Invalid Bot file path!! Specifiy proper path in cvf.ini")
        if ret > 1:
            self.GiveUp("Invalid Bot file")

        if(enableSecureProduction == 1):
            self.VerifyEntireBOTAndKeyFileSignature(self.BotFilePath)
        self.Info("Successfully created BOT file parser")


#------------------------Utility methods----------------------------
    # Prints and puts the error in log
    def Error(self, message):
        self.Logger.Info("[PRODUCTION ERROR]: " + message)
        self.ErrorCount = self.ErrorCount + 1

    # Prints and puts the warning in log
    def Warn(self, message):
        self.Logger.Info("[PRODUCTION WARNING]: " + message)
        self.WarningCount = self.WarningCount + 1

    # Prints and puts the info in log
    def Info(self, message):
        self.Logger.Info("[PRODUCTION INFO]: " + message)
    # Prints and puts the message in log	

    # Give up and Exit
    def GiveUp(self, message, printSettings=True):
        global restartIndicator
        if(os.path.isfile(restartIndicator)):
            os.unlink(restartIndicator)
        self.Error(message)
        if printSettings:
            self.Logger.Info("Printing the settings for you to review. Maybe something is wrong with the settings.")
            #self.PrintSettings()
        self.Logger.Info(message + " Please search [PRODUCTION ERROR/WARNING] for more information...", emphasize=3)
        if self.performIO:
            exit(99)
        else:
            raise AssertionError(message)
#------------------------Utility methods----------------------------


    def DownloadAndExecute(self):
        try:
            result = 0
            FwChunkSize  = 512

            pDLEParamsSection = self.ObjBOTParser.GetBotSection(PyServiceWrap.BOT_DLEFORMAT)
            dleF = self.ObjBOTParser.FindSection(PyServiceWrap.BOT_DLEFORMAT)
            loadAddress = dleF.GetLoadAddress()
            dataSize = dleF.GetDataSize()
            jumpAddress = dleF.GetJumpAddress()
            options = 0x02

            inputBuff = PyServiceWrap.Buffer.CreateBuffer(dataSize,PyServiceWrap.ALL_0,False)
            inputBuff.Copy(0,pDLEParamsSection.GetData(),0,dataSize)
            ExecuteWritePortCommand(inputBuff, loadAddress, dataSize, options, jumpAddress)

        except:
            self.Logger.Error("DownloadAndExecute Failed")
            raise Exception("DownloadAndExecute Failed")

        return result


    def ExecuteVerificationFlow(self):
        return 


    def ReadAndVerifyeFuse(self):
        pass


    def VerifyAndBurneFuse(self):
        pass


    def GetProductionConfiguration(self):
        pass


    def UpdateProductConfigurationFile(self):
        pass


    def WriteBotFileSection(self , botType):
        returnCode = 0
        pSection = self.ObjBOTParser.GetBotSection(botType)

        dleSec = self.ObjBOTParser.FindSection(botType)
        dataSize = dleSec.GetDataSize()

        if (None == pSection):
            return _ERROR_PRODUCTION_BOTFILE_INVALID_SECTION

        buf = PyServiceWrap.Buffer.CreateBuffer(dataSize, PyServiceWrap.ALL_0, False)
        buf.Copy(0,pSection.GetData(),0,dataSize)
        if botType==PyServiceWrap.BOT_FORMAT:
            pWriteFile = CreateWriteMultiFile_Format(buf, dataSize/512)
        else :
            pWriteFile = CreateWriteMultiFile(buf, dataSize/512)
        try:

            tpm = PyServiceWrap.ThreadPoolMgr.GetThreadPoolMgr()
            tpm.PostRequestToWorkerThread(pWriteFile,True)
        except (PyServiceWrap.CmdException,PyServiceWrap.GenericException,PyServiceWrap.FatalException) as ex:
            print(ex.GetFailureDescription())
            returnCode =  ex.GetErrorNumber() if ex.GetErrorNumber()>0 else 99
        finally:
            return returnCode


    def ExeucteAddressLineTest(self):

        self.Logger.Info("Executing Address Line Test - ExecuteALT.")

        buf1 = PyServiceWrap.Buffer.CreateBuffer(512,PyServiceWrap.ALL_0,False)

        sCreareALTCommand = CreateALTCommand(buf1, 0x4F7)

        try:
            sCreareALTCommand.Execute()
            sCreareALTCommand.HandleOverlappedExecute()
            sCreareALTCommand.HandleAndParseResponse()

        except PyServiceWrap.CmdException as ex:
            print(ex.GetFailureDescription())
            raise Exception("ExeucteAddressLineTest Failed")

        isDone = false
        retryCount = 0

        while ( not isDone and retryCount >= 5):

            self.Logger.Info("Executing Address Line Test - Retrieve ALT results.")

            buf1 = PyServiceWrap.Buffer.CreateBuffer(512,False)
            buf1.FillFromPattern(0)

            sCreareALTCommand = CreateRetrieveALTResultCommand(buf1)

            sCreareALTCommand.Execute()
            sCreareALTCommand.HandleOverlappedExecute()
            sCreareALTCommand.HandleAndParseResponse()


            altStatus = buf1.GetTwoBytesToInt(0)
            altErrorCode = buf1.GetTwoBytesToInt(2)

            if (altStatus == 0):

                self.Logger.Info("ALT state : D_ALT_IDLE_STATE ")

                #AddError(new GenericError(_ERROR_PRODUCTION_ALT_NOT_DONE,GRP_ERROR_PRODUCTION, pself.session->GetErrorManager()->GetErrorDesc((INT16)_ERROR_PRODUCTION_ALT_NOT_DONE, (INT16)GRP_ERROR_PRODUCTION).c_str()));

                #RAISE_CTF_CMD_EXCEPTION(pself.session, this)

            elif (altStatus == 1):

                self.Logger.Info("ALT state : D_ALT_START_STATE") 
                #AddError(new GenericError(_ERROR_PRODUCTION_ALT_NOT_DONE, GRP_ERROR_PRODUCTION, psession->GetErrorManager()->GetErrorDesc((INT16)_ERROR_PRODUCTION_ALT_NOT_DONE, (INT16)GRP_ERROR_PRODUCTION).c_str()));

                #RAISE_CTF_CMD_EXCEPTION(pself.session, this)

            elif (altStatus == 2):

                self.Logger.Info("ALT state : D_ALT_IN_PROGRESS_STATE")
                #AddError(new GenericError(_ERROR_PRODUCTION_ALT_NOT_DONE, GRP_ERROR_PRODUCTION, psession->GetErrorManager()->GetErrorDesc((INT16)_ERROR_PRODUCTION_ALT_NOT_DONE, (INT16)GRP_ERROR_PRODUCTION).c_str()));

                #RAISE_CTF_CMD_EXCEPTION(pself.session, this)	

            elif (altStatus == 3):

                self.Logger.Info("ALT state : D_ALT_DONE_STATE")

                isDone = true    

            else :

                self.Logger.Info("ALT state : UNKONWN State ")
                #AddError(new GenericError(_ERROR_PRODUCTION_ALT_NOT_DONE, GRP_ERROR_PRODUCTION, psession->GetErrorManager()->GetErrorDesc((INT16)_ERROR_PRODUCTION_ALT_NOT_DONE, (INT16)GRP_ERROR_PRODUCTION).c_str()));

                #RAISE_CTF_CMD_EXCEPTION(pself.session, this)	

            if (altErrorCode == 0 ):
                self.Logger.Info("ALT error Code : D_ALT_NO_ERRORS")

            else :
                self.Logger.Info("ALT error Code : %d", altErrorCode)
                #AddError(new GenericError(_ERROR_PRODUCTION_ALT_NOT_DONE, GRP_ERROR_PRODUCTION, psession->GetErrorManager()->GetErrorDesc((INT16)_ERROR_PRODUCTION_ALT_NOT_DONE, (INT16)GRP_ERROR_PRODUCTION).c_str()));

                #RAISE_CTF_CMD_EXCEPTION(psession, this)	


####################################################### END CLASSES ####################################################
####################################################### MAIN PROGRAM ###################################################
def doHWProduction(sessionObj, logger, argParser):
    global DriverType
    global cmdlineArgs
    global deviceType
    global botfile    
    global security_production
    global is_production_requried
    global hwDict
    global relayPortDef
    global enableRelayControl
    global templateFilePath
    global xplorerInstallPath
    global xplorerInputFilePath
    global xplorerDCOPath
    global powerCycleHW
    global relayComPort
    global enableDMC
    global enableSecureProduction
    global useEngineeringKeys
    global securityProductionFilePath
    global enablecp210xcontrol
    global cp210xComport
    global enableHotCountReadandRestore
    
    sessionID = ""
    configParser = sessionObj.GetConfigInfo()

    DriverType='WIN_USB'
    botfile=configParser.GetValue("bot_file","")[0]
    enableSecureProduction = int(configParser.GetValue("enable_optimus_secure_production","")[0])
    enableDMC= int(configParser.GetValue("enable_microcode_download","")[0])
    if enableSecureProduction:
        useEngineeringKeys=int(configParser.GetValue("use_engineering_keys","")[0])

    deviceAdapterType = configParser.GetValue("device_adapter_type","")[0]
    if deviceAdapterType == "cp210x":
        hwDict['SerialCommunication']='HIDAndCOMPorts'
        enablecp210xcontrol = 1
        cp210xComport = configParser.GetValue("cp210x_port","")[0]
        enableRelayControl = 0

    elif deviceAdapterType == "relay":
        hwDict['SerialCommunication']='HIDAndCOMPorts'
        enableRelayControl = 1
        relayPortDef=configParser.GetValue("definition_of_relay_port","")[0]
        enablecp210xcontrol = 0

    enableHotCountReadandRestore = configParser.GetValue("enableHotCountReadandRestore",0)[0]
    
    ParseArgs(argParser)

    try:
        SetupConfigParams(sessionObj)
        configParser = sessionObj.GetConfigInfo()          

        myProduction = OptimusProduction(sessionObj, logger)
        myProduction.Execute()

    except (PyServiceWrap.PeripheralHWException,PyServiceWrap.LoggerException, PyServiceWrap.CmdException,PyServiceWrap.GenericException,PyServiceWrap.FatalException,PyServiceWrap.IBaseExcep,PyServiceWrap.DataTrackingException,PyServiceWrap.ErrorTrackingException, PyServiceWrap.GeneralException,PyServiceWrap.BufferException, PyServiceWrap.CTFCmdBaseExcep,PyServiceWrap.CTFBaseExcep,PyServiceWrap.ConfigException) as ex:
        PrintCommandLine(logger)
        if logger != None:
            logger.Message(ex.GetFailureDescription())
        else:
            print(ex.GetFailureDescription())
            exit(99)
    
    except (PyServiceWrap.PeripheralHWException,PyServiceWrap.LoggerException, PyServiceWrap.CmdException,PyServiceWrap.GenericException,PyServiceWrap.FatalException,PyServiceWrap.IBaseExcep,PyServiceWrap.DataTrackingException,PyServiceWrap.ErrorTrackingException, PyServiceWrap.GeneralException,PyServiceWrap.BufferException, PyServiceWrap.CTFCmdBaseExcep,PyServiceWrap.CTFBaseExcep,PyServiceWrap.ConfigException) as ex:
        PrintCommandLine(logger)
        if logger != None:
            logger.Message(ex.GetFailureDescription())
        else:
            print(ex.GetFailureDescription())
            exit()

def main():
    ParseArgs()
    try:
        session = PyServiceWrap.Session.GetSessionObject(PyServiceWrap.SCSI_Protocol, PyServiceWrap.DRIVER_TYPE.WIN_USB, hwDict)
        logger = SetupLogger(session)
        SetupConfigParams(session)

        #Initialize the session.
        session.Init()

        myProduction = OptimusProduction(session, logger)
        myProduction.Execute()

        tpm = PyServiceWrap.ThreadPoolMgr.GetThreadPoolMgr()
        tpm.CleanThreadPoolMgr()

    except (PyServiceWrap.PeripheralHWException,PyServiceWrap.LoggerException, PyServiceWrap.CmdException,PyServiceWrap.GenericException,PyServiceWrap.FatalException,PyServiceWrap.IBaseExcep,PyServiceWrap.DataTrackingException,PyServiceWrap.ErrorTrackingException, PyServiceWrap.GeneralException,PyServiceWrap.BufferException, PyServiceWrap.CTFCmdBaseExcep,PyServiceWrap.CTFBaseExcep,PyServiceWrap.ConfigException) as ex:
        print(ex.GetFailureDescription())
        exit(99)

if __name__ == "__main__":
    originalArgs = sys.argv
    main()
