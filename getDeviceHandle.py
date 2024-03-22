import os, sys, datetime
import CTFServiceWrapper
import CTFServiceWrapper as PyServiceWrap
import ScsiCmdWrapper as sw
#import SATAWrapper as sw
g_Verbose = 0

class getDeviceHandleClass(object):

    def OpenAndEnumerateDevice(self):
        hwDict = dict()
        hwDict={'SerialCommunication':'HIDAndCOMPorts'}     #change "enable_auto_relay_control" =1 in cvf.ini
        try:
            SessionObject = PyServiceWrap.Session.GetSessionObject(PyServiceWrap.SCSI_Protocol, PyServiceWrap.DRIVER_TYPE.WIN_USB, hwDict)
            #SessionObject = PyServiceWrap.Session.GetSessionObject(PyServiceWrap.ATA_Protocol, PyServiceWrap.DRIVER_TYPE.SD_AHCI, hwDict)
            configParser = SessionObject.GetConfigInfo()
            configParser.SetValue("sctp_diagnostic_command_frame_size", 512)
            SessionObject.Init()
            print 'Device Opened and Enumerated'
        except PyServiceWrap.CmdException as ex:
            print 'Session Init Failed'
            print ex.GetFailureDescription() 
        return SessionObject
    
    def __EnableForceDownloadMode(self):
        try:
            #fd = sw.EnableForceDownloadMode(10000, PyServiceWrap.SEND_IMMEDIATE)  
            print 'Enabled force download'            
        except:
            print 'Enable force download failed'
    
    def IdentifyDrive(self):

        sectorcount = 1   
        buf = PyServiceWrap.Buffer.CreateBuffer(sectorcount, PyServiceWrap.ALL_0, True)
        fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
        fbcccdb.cdb = [0]*16
        fbcccdb.cdb[0] = 0xEC
        fbcccdb.cdb[8] = (sectorcount & 0xFF)
        fbcccdb.cdb[9] = (sectorcount >> 8) & 0xFF
        fbcccdb.cdb[10] = (sectorcount >> 16) & 0xFF
        fbcccdb.cdb[11] = (sectorcount >> 24) & 0xFF
        fbcccdb.cdbLen = 16  
    
        #sctpCommand = ExecuteSCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_OUT)
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_OUT, True, None, 10000)
        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        except PyServiceWrap.CmdException as ex:
            print ex.GetFailureDescription()
        
        return buf  
    
    def isDriveInMode(self):
        print "Executing Identify Drive...."   
        tmpBuff = self.IdentifyDrive()
       
        maxLba = self.__GetMaxLba(tmpBuff)
    
        if (maxLba is 31):
            print "Drive is in ROM mode."
            return 0
    
        print "Drive is not in ROM mode."
        return 2 
    
    def __GetMaxLba(self, buf):
        maxLba =  self.__GetMax28BitLba(buf)
    
        if ( maxLba == 0xFFFFFFE ):
            maxLba = self.__GetMax48BitLba(buf)
            if(maxLba < 0xFFFFFE):
                return 0xFFFFFE
            else:
                return maxLba
    
        return maxLba

    def __GetMax28BitLba(self, buf):
        TOTAL_LBAS_OFF    = 0x78
        number_of_lba_addressable_sectors = buf.GetFourBytesToInt(TOTAL_LBAS_OFF)
    
        if (0 == number_of_lba_addressable_sectors):
           print "****** ERROR: The number of sectors addressable in LBA mode is 0."" Max LBA is undefined."
        if(number_of_lba_addressable_sectors > 0):
            return number_of_lba_addressable_sectors - 1 
        else:
            return 0
    
    
    def __GetMax48BitLba(self, buf):
        high_bytes = buf.GetFourBytesToInt(0xCC, sw.DetectByteSwapOrder(buf))
    
        if (high_bytes > 0):
            print "****** ERROR: The number of sectors addressable using 48-bit LBA does not fit in 32 bit."
            return 0
        number_of_lba_addressable_sectors = buf.GetFourBytesToInt(0xC8, sw.DetectByteSwapOrder(buf))
    
        if (0 == number_of_lba_addressable_sectors):
            print "****** ERROR: The number of sectors addressable using 48-bit LBA is 0."" Max 48-bit LBA is undefined. "
    
        if(number_of_lba_addressable_sectors > 0):
            return number_of_lba_addressable_sectors - 1 
        else:
            return 0
    
    def __JumpToIdle(self):
        self.__ExecuteInvalidateFlash()
        self.ExecutePowerCycle()

    def __ExecuteInvalidateFlash(self):
        print "Executing Invalidate flash"
        fbcccdb = PyServiceWrap.DIAG_FBCC_CDB()
        fbcccdb.cdb = [0]*16
        fbcccdb.cdb[0] = 0x90
        fbcccdb.cdb[2] = 0x02
        fbcccdb.cdbLen = 16  
    
        #sctpCommand = ExecuteSCTPCommand(fbcccdb, None, PyServiceWrap.DIRECTION_NONE)
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(fbcccdb, None, PyServiceWrap.DIRECTION_NONE, True, None, 10000)
    
        try:
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse() 
        except PyServiceWrap.CmdException as ex:
            print ex.GetFailureDescription()
    
    def ExecutePowerCycle(self):    
        array = [0xdd, 0x4c, 0x02, 0xd8, 0x0f, 0xf5, 0x0a, 0x70, 0x5e, 0x7f, 0x5a, 0x84, 0xc6, 0xf7, 0x4b, 0x6b, \
            0xd2, 0x42, 0x71, 0x28, 0x46, 0x42, 0x7b, 0x89, 0x7d, 0x8c, 0x55, 0x7c, 0x3a, 0x5a, 0x30, 0x39, \
            0x10, 0x25, 0x42, 0xeb, 0x4e, 0x10, 0x90, 0x8f, 0x4b, 0x45, 0x6f, 0x88, 0x4f, 0xf2, 0x9f, 0x61, \
            0x5d, 0xec, 0x18, 0xd2, 0x2b, 0x71, 0x60, 0xf4, 0xbe, 0x58, 0xcb, 0x04, 0x87, 0xf7, 0xcf, 0x94, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
            00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  
        
        powercycle = PyServiceWrap.PowerCycle(shutdownType=PyServiceWrap.SHUTDOWN_TYPE.UNGRACEFUL, pModelPowerParamsObj=None, pGPIOMap=None, isAsync=True, sendType=PyServiceWrap.SEND_IMMEDIATE) 
    
    def ExecuteWritePortCommand(self, buf, portAddress, byteCount, options, jumpAddress):

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

        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(fbcccdb, buf, PyServiceWrap.DIRECTION_IN)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()		    
    
        except PyServiceWrap.CmdException as ex:
            print ex.GetFailureDescription()
            raise Exception("DownloadAndExecute Failed")
    
    def __DownloadAndExecute(self, botPath):
        driveMode = self.isDriveInMode()
        if (driveMode == 2):
            self.__JumpToIdle()
            driveMode = self.isDriveInMode()
            if (driveMode == 2):
                print "Drive is not in ROM"
                raise Exception("Drive is not in ROM")
    
        result = 0
        FwChunkSize  = 512
        ObjBOTParser = PyServiceWrap.BOTFileParser()
        BotFilePath = botPath
        ret = ObjBOTParser.Open(BotFilePath)
        if ret == 1:
            GiveUp("Invalid Bot file path!! Specifiy proper path in cvf.ini")
        if ret > 1:
            GiveUp("Invalid Bot file")
        pDLEParamsSection = ObjBOTParser.GetBotSection(PyServiceWrap.BOT_DLEFORMAT)
        dleF = ObjBOTParser.FindSection(PyServiceWrap.BOT_DLEFORMAT)
        loadAddress = dleF.GetLoadAddress()
        dataSize = dleF.GetDataSize()
        jumpAddress = dleF.GetJumpAddress()
        options = 0x02
    
        inputBuff = PyServiceWrap.Buffer.CreateBuffer(dataSize,PyServiceWrap.ALL_0,False)
        inputBuff.Copy(0,pDLEParamsSection.GetData(),0,dataSize)
    
        self.ExecuteWritePortCommand(inputBuff, loadAddress, dataSize, options, jumpAddress)
        genSleep = PyServiceWrap.GenericSleep(1,0)
        
        try:
            genSleep.Execute()
            genSleep.HandleOverlappedExecute()
            genSleep.HandleAndParseResponse()
        
        except PyServiceWrap.CmdException as ex:
            print ex.GetFailureDescription()    
        print "Entered in DLE Mode"
        return
    
    def EnterDleMode(self, dlemode, botFilePath):
        #sessionObject = self.OpenAndEnumerateDevice()
        self.__EnableForceDownloadMode()
        print 'In ROM Mode'
       
        if dlemode == 1:
            self.__DownloadAndExecute(botFilePath)
        
        return
    
    def sendDiagnostics(self, cdb, cdbLen, buf, ioDirection):
        #get session handle
        #sessionObject = self.OpenAndEnumerateDevice()
        
        if ioDirection == 0:
            direction = PyServiceWrap.DIRECTION_OUT
        else:
            direction = PyServiceWrap.DIRECTION_IN
        
        try:
            if g_Verbose:
                print direction
            diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
            diagCmd.cdb = cdb
            diagCmd.cdbLen = cdbLen
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, direction, True, None, 100000)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse() 
            if g_Verbose:
                print 'Diag Command Executed'
        except PyServiceWrap.CmdException as ex:
            print 'FBCC Failed'
            print ex.GetFailureDescription() 
    
        #buf.WriteToFile("DiagOutput.bin", 8*512)
        #print 'Check DiagOutput.bin File'
        
        return buf

'''
obj = diagCmdRequestClass()
obj.OpenAndEnumerateDevice()
obj.EnterDleMode("C:\WDLABS\crex_mc\crex-fw-fwcode\output\crex_sata_x3_bics5\BOT\IXS00aE0101002001M13DEADBEEF_decrypt.bot")

#Read EC40 WL
numOfSectors = 1
seq = [0xC2, 0xF1, 0xFD, 0xDE, 0x13, 0x88, 0xC1, 0xEC, 0xA1, 0x40, 0xD0, 0x47, 0xA0]
seqbuf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
for idx, sq in enumerate(seq):
    seqbuf.SetByte(idx, sq)
cdb = [0x95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
obj.sendDiagnostics(cdb, len(cdb), seqbuf, ioDirection = 1)

numOfSectors = 36
buf = PyServiceWrap.Buffer.CreateBuffer(numOfSectors, patternType=PyServiceWrap.ALL_0, isSector=True)
cdb = [0x94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
retbuf = obj.sendDiagnostics(cdb, len(cdb), buf, 0)
retbuf.WriteToFile("DiagOutput.bin", numOfSectors*512)
'''