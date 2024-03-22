import CTFServiceWrapper as PyServiceWrap
import os, sys
import time
import os
import ScsiCmdWrapper as scsiWrap

#constants
SECTOR_SIZE=512

class GenericLib(object):
    def Session_Init(self):
        hwDict = dict()
        session = PyServiceWrap.Session.GetSessionObject(PyServiceWrap.SCSI_Protocol, PyServiceWrap.DRIVER_TYPE.WIN_USB, hwDict)
        session.Init()
        
    def get_byte(self,pos,data):
        return data&(1<<pos) and 1 or 0
        
    def GetByte(self, pos, val):
        assert type(pos) == int, "pos type must be integer"
        assert type(val) == int, "val type must be integer"

        return (val >> (pos * 8)) & 0xFF

    def GetParam(self,fim, CE, die, param_addr):
    
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
        diagCmd.cdb[6] = self.GetByte(0, param_addr)#(param_addr>>0) & 1#GetByte(0, param_addr)
        diagCmd.cdb[7] = self.GetByte(1, param_addr)#(param_addr>>1) & 1#GetByte(1, param_addr)
        diagCmd.cdbLen = len(diagCmd.cdb)
    
        buf = PyServiceWrap.Buffer.CreateBuffer(1, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            print "GetParam: PASS"
        except PyServiceWrap.CmdException as ex:
            print "GetParam: FAIL", ex.GetFailureDescription()
    
        paramValue = buf.GetOneByteToInt(0)
        print("Get Param Value::",paramValue) 
        return paramValue
            
    def SetParam(self,fim, CE, die, param_addr, param_val):
    
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
        diagCmd.cdb[6] = self.GetByte(0, param_addr)#(param_addr>>0) & 1#GetByte(0, param_addr)
        diagCmd.cdb[7] = self.GetByte(1, param_addr)#(param_addr>>1) & 1#GetByte(1, param_addr)
        diagCmd.cdb[8] = param_val
        diagCmd.cdbLen = len(diagCmd.cdb)
        
        buf = PyServiceWrap.Buffer.CreateBuffer(1, patternType = PyServiceWrap.ALL_0, isSector = True)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            print "SetParam: PASS"
        except PyServiceWrap.CmdException as ex:
            print "SetParam: FAIL", ex.GetFailureDescription()
            exit(-1)
        
        paramValue = self.GetParam(fim, CE, die, param_addr)
        
        return paramValue     
        
    def DisableBurstMode(self,trLen,switch=1):
        """
        Description: Disable Burst mode.
        Parameters:switch : 1 Disable
                            0 Enable
        Returns: None
        Exceptions: None
        """
        secCount = trLen
    
        opcode = 0xC2
        subopcode = 0x0
        SECTOR_SIZE = 512
    
    
        lengthInBytes = secCount * SECTOR_SIZE
        #buf = pyServiceWrap.Buffer.CreateBuffer(lengthInBytes, patternType=pyServiceWrap.ALL_0, isSector=False)
        #Buffer = PyServiceWrap.Buffer.CreateBuffer(dataSize = sectorCount, patternType=PyServiceWrap.ALL_0, isSector=True)
        diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
        diagCmd.cdb = [0] * 16
        diagCmd.cdb[0] = opcode
        diagCmd.cdb[1] = subopcode
        diagCmd.cdb[2] = switch
        diagCmd.cdb[3] = (lengthInBytes >> 8) & 0xFF
        diagCmd.cdbLen = len(diagCmd.cdb)
    
        sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd)
        sctpCommand.Execute()
        sctpCommand.HandleOverlappedExecute()
        sctpCommand.HandleAndParseResponse()

    def ToAddr(self,die, block, wl, string, column):
        
        plane = block & 0x1
        block_no = block/2        
        g_Verbose =1
    
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
            while(len(block_b)<13):
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
            add4= block_b[7:]+plane_b[2]+wl_b[2]
            addr4_h = int(add4, 2)
            add5= die_b[2:]+block_b[2:7]
            addr5_h = int(add5, 2)
            
    
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
                #print("Address Byte 6= \t {}".format(hex(self.add6_h)))
                print("Block number in hex( w/ plane bit)= {}".format(blk_pl_h))
                print("Decimal= {}".format(blk_pl_i))
                print("Physical block No. in hex (NanoNT)= {}".format(blk_phy_h))
                print("Decimal= {}".format(blk_phy_i))
        return [addr1_h, addr2_h, addr3_h, addr4_h, addr5_h]

#lbatophy to be moved to scsi library        
    def LbaToPhysical(self,lba):
    
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
    
        diagCmd.cdb[2] = self.GetByte(0, options)
        diagCmd.cdb[3] =self.GetByte(1, options)
        diagCmd.cdb[4] =self.GetByte(0, lba)
        diagCmd.cdb[5] =self.GetByte(1, lba)
        diagCmd.cdb[6] =self.GetByte(2, lba)
        diagCmd.cdb[7] =self.GetByte(3, lba)
        diagCmd.cdbLen = len(diagCmd.cdb)
    
        try:
            sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)
            sctpCommand.Execute()
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
            print "LBA TranslateToPhysical: PASS"
        except PyServiceWrap.CmdException as ex:
            print "LBA TranslateToPhysical: Fail", ex
            exit(-1)
        
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
    
        if buf.GetOneByteToInt(0x12) > 1:
            if buf.GetOneByteToInt(0x12)%2:
                die = (buf.GetOneByteToInt(0x12) / 2) + (PhyLocDict["fimChannel"]+1)%2
            else:
                die = (buf.GetOneByteToInt(0x12) / 2) -  PhyLocDict["fimChannel"]
        die = LogDietoPhyDie[PhyLocDict["die"]]
        PhyLocDict["die"] = die
        
        block = buf.GetTwoBytesToInt(0x14)*2 + buf.GetOneByteToInt(0x13)
        wordline = buf.GetOneByteToInt(0x1F)
        string = buf.GetOneByteToInt(0x20)
    
        self.ToAddr(die, block, wordline, string, 0)
    
        return PhyLocDict  
		
	def Read_FMU(self):
		buf = PyServiceWrap.Buffer.CreateBuffer(0x20, patternType=PyServiceWrap.ALL_1, isSector=True)
		#0x20 is no of sectors
		diagCmd = PyServiceWrap.DIAG_FBCC_CDB()
		numOfSectors=0x20

		#all the addresses provided here is physical addresses
		diagCmd.cdb = [0] * 16
		diagCmd.cdb[0] = 0xB1#opcode
		diagCmd.cdb[1] = 0x0 #chip
		diagCmd.cdb[2] = 0x0 #die
		diagCmd.cdb[3] = 0x0 #plane
		diagCmd.cdb[4] =0x0 #Block (LSB) 
		diagCmd.cdb[5] = 0x0 #Block (MSB) 
		diagCmd.cdb[6] = 0x0 #WL
		diagCmd.cdb[7] = 0x0 #page
		diagCmd.cdb[8] = 0x0 #FMUOffset use 0 -3
		diagCmd.cdb[9] = 0   #string
		diagCmd.cdb[10] = 0x4# fmu Count (LSB) 
		diagCmd.cdb[11] = 0x0 # fmu Count (LSB) 
		diagCmd.cdb[14] = 0x00 #options (LSB)  
		diagCmd.cdb[15] = 0x12#Options (MSB) 
		diagCmd.cdbLen = 16
		print diagCmd.cdb    
		sctpCommand = PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, buf, PyServiceWrap.DIRECTION_OUT)        
		sctpCommand.Execute()
		#added by anitha
		sctpCommand.HandleOverlappedExecute()
		sctpCommand.HandleAndParseResponse()   
		buf.WriteToFile("buf.bin",32*512)
		print("FBCC passed")
		
		
    def ReadLbaExt(self,lba, trLen,maximumLba):
        isAsync=True
        lun = 0
        hwDict = dict()
        sendType = PyServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE
        uasSpecificParams = scsiWrap.UAS_SPECIFIC_COMMAND_PARAMETERS()
        #write10Params = scsiWrap.WRITE12_ADDITIONAL_COMMAND_PARAMETERS()
        #read10AdditionalCommandParameters = scsiWrap.READ10_ADDITIONAL_COMMAND_PARAMETERS()
        #Enable CTF Library Traces when required.
        uasSpecificParams = scsiWrap.UAS_SPECIFIC_COMMAND_PARAMETERS()
        # Specifies the relative scheduling of the command
        uasSpecificParams.uiCommandPriority = 1#val#
        # Specifies the type of the task attribute
        uasSpecificParams.uiTaskAttribute = 0#val#
        # Specifies the user mentioned tag
        uasSpecificParams.uiTtag = 1#val#
        # Specifies if the user mentioned tag is to be used
        uasSpecificParams.bIsUseTag = False #val#
        uasSpecificCommandParameters = uasSpecificParams
        rdbuffer = None
        g_Verbose = 1
        startLba = lba
        sectorCount = trLen

        scsiWrap.ReInitDevices(False, True)		
        maxLba = maximumLba
		
        scsiWrap.SetNcqQueueDepth (qDepth = 1)
		
        count =0
        while startLba < maxLba:
            ScsiRead10 = scsiWrap.ScsiRead16(startLba, sectorCount, rdbuffer, lun, isAsync, sendType, uasSpecificCommandParameters, read16AdditionalCommandParameters = scsiWrap.READ16_ADDITIONAL_COMMAND_PARAMETERS())
            count = count+1
            startLba += sectorCount
            print("count:",count)
            #Buff = ScsiWrite10.GetBuffer()
            #ScsiStatus = ScsiWrite10.GetSptdInfo().ScsiStatus
            #phyaddr = self.LbaToPhysical(startLba)
            #print("LBA information:",phyaddr) 
            #ScsiRead10.GetBuffer().PrintToLog() # this method Works to dump
        print("Exit While")

    def WriteLbaExt(self,lba, trLen,maximumLba):
        isAsync=True
        lun = 0
        hwDict = dict()
        sendType = PyServiceWrap.CMD_SEND_TYPE.SEND_IMMEDIATE
        #sendType = PyServiceWrap.CMD_SEND_TYPE.SEND_QUEUED
        uasSpecificParams = scsiWrap.UAS_SPECIFIC_COMMAND_PARAMETERS()
        #write16Params = scsiWrap.WRITE12_ADDITIONAL_COMMAND_PARAMETERS()
        #write10AdditionalCommandParameters = scsiWrap.WRITE10_ADDITIONAL_COMMAND_PARAMETERS()
        # Enable CTF Library Traces when required.
        #uasSpecificParams = scsiWrap.UAS_SPECIFIC_COMMAND_PARAMETERS()
        # Specifies the relative scheduling of the command
        uasSpecificParams.uiCommandPriority = 1#val#
        # Specifies the type of the task attribute
        uasSpecificParams.uiTaskAttribute = 0#val#
        # Specifies the user mentioned tag
        uasSpecificParams.uiTtag = 1#val#
        # Specifies if the user mentioned tag is to be used
        uasSpecificParams.bIsUseTag = False #val#
        uasSpecificCommandParameters = uasSpecificParams
        writeBuffer = None
        g_Verbose = 1
        startLba = lba
        sectorCount = trLen
        
        scsiWrap.ReInitDevices(False, True)
		
        maxLba = maximumLba
        count =0        
        
        scsiWrap.SetNcqQueueDepth (qDepth = 1)
		
        while startLba < maxLba:
            ScsiWrite16 = scsiWrap.ScsiWrite16(startLba, sectorCount, writeBuffer, lun, isAsync, sendType, uasSpecificCommandParameters, write16AdditionalCommandParameters = scsiWrap.WRITE16_ADDITIONAL_COMMAND_PARAMETERS())		
            count = count+1
            startLba += sectorCount
            print("count:",count)
            #Buff = ScsiWrite10.GetBuffer()
            #ScsiStatus = ScsiWrite10.GetSptdInfo().ScsiStatus
            #phyaddr = self.LbaToPhysical(startLba)
            #print("LBA :",phyaddr) 
            #ScsiWrite10.GetBuffer().PrintToLog() # this method Works to dump
        print("Exit While")

	
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
        LengthInBytes = sectorcount * SECTOR_SIZE #SECTOR_SIZE=512B
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
            PyServiceWrap.SCTPCommand.SCTPCommand(diagCmd, Buffer, PyServiceWrap.DIRECTION_OUT,True, None, 200000, PyServiceWrap.SEND_IMMEDIATE)
        except PyServiceWrap.CmdException as ex:
            print("DIAG: READ_FILE FAILED", "FATAL")
            exit(-1)
        print("DIAG: READ_FILE SUCCESS")
        return Buffer
    
    def WriteFile(self, buf, fileid, sectorcount, option=0,timeOut=1000):
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
            self.returnSctpStaus= sctpstatus.Status
            sctpCommand.HandleOverlappedExecute()
            sctpCommand.HandleAndParseResponse()
        
        except PyServiceWrap.CmdException as ex:
            print("DIAG: WRITE_FILE FAILED", "FATAL")
            exit(-1)
        print("DIAG: WRITE_FILE SUCCESS")