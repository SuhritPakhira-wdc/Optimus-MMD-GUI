import CTFServiceWrapper as PyServiceWrap
import os, sys
import time
import os
import ScsiCmdWrapper as scsiWrap
import GenericLib as generic


raw_input("Start ATB/go-logic and press Enter continue")
print "Call Write method"

obj = generic.GenericLib()

obj.Session_Init()

lba = 0x0
trLen = 240
MaxLba = 0x20000

obj.DisableBurstMode(trLen,1)
obj.WriteLbaExt(lba, trLen,MaxLba)
