import CTFServiceWrapper as PyServiceWrap
import os, sys
import time
import os
import ScsiCmdWrapper as scsiWrap
import GenericLib as generic


obj = generic.GenericLib()
obj.Session_Init()

lba = 0x0
trLen = 240
MaxLba = 0x10000

obj.ReadLbaExt(lba, trLen,MaxLba)



