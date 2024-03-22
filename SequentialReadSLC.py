import CTFServiceWrapper as PyServiceWrap
import os, sys
import time
import os
import ScsiCmdWrapper as scsiWrap
import GenericLib as generic
#import diagCmdLib as dgcmd

#obj_FA = dgcmd.diagCmdLibClass(1)

obj = generic.GenericLib()
obj.Session_Init()
lba = 0x0
trLen = 80
MaxLba = 0x10000

#obj.SetParam(1,1,1,0x5D,0x10)
#obj.SetParam(0,0,0,0x3F,0x02)

#obj_FA.FALogDump()

obj.ReadLbaExt(lba, trLen, MaxLba)

#physcalAdd = obj.LbaToPhysical(lba)

#print physcalAdd


