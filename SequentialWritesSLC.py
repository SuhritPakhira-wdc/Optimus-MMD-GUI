import CTFServiceWrapper as PyServiceWrap
import os, sys
import time
import os
import ScsiCmdWrapper as scsiWrap
import GenericLib as generic

raw_input("Start ATB/go-logic and press Enter continue")
print "Call Write method"
#SCSI_write obj

obj = generic.GenericLib()

obj.Session_Init()

lba = 0x0
trLen = 80
MaxLba = 0x10000 # 1 Meta Blocks in SLC


obj.WriteLbaExt(lba, trLen,MaxLba)