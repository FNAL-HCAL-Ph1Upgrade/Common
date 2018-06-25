import logging
logger = logging.getLogger(__name__)

import ngFECSendCommand as sendCommands

port = 64100
host = 'localhost'
n = 5

import random
random.seed(1)
from random import randint

def getRegisterSize(regs, crate, rm, slot, isBridge=False, isIgloo=False, isQIE=False):
   for reg in regs:
      print reg
      isgood = True
      for i in range(64):
         tempint = 2**i
         if isBridge:
            cmdput = "put HB{0}-{1}-{2}-{3} {4}".format(crate, rm, slot, reg[0], tempint)
            cmdget = "get HB{0}-{1}-{2}-{3}".format(crate, rm, slot, reg[0])
         if isIgloo:
            cmdput = "put HB{0}-{1}-{2}-iTop_{3} {4}".format(crate, rm, slot, reg[0], tempint)
            cmdget = "get HB{0}-{1}-{2}-iTop_{3}".format(crate, rm, slot, reg[0])
         if isQIE:
            QIE = 1 + (int(slot)-1)*16
            cmdput = "put HB{0}-{1}-QIE{2}_{3} {4}".format(crate, rm, QIE, reg[0], tempint)
            cmdget = "get HB{0}-{1}-QIE{2}_{3}".format(crate, rm, QIE, reg[0])
         output = []
         output += sendCommands.send_commands(cmds=cmdput, script=False, control_hub=host, port=port)
         output += sendCommands.send_commands(cmds=cmdget, script=False, control_hub=host, port=port)         
         for (put, get) in zip(output[::2], output[1::2]):
            getvar = int(get['result'], 16)
            if not getvar == tempint:
               print "register size is {0} bits. put {1}. get {2}".format(i, put, get)
               isgood = False
               break
         if not isgood:
            break

def checkOutput_rw(output):
   testpass = True
   for i, (put, get) in enumerate(zip(output[::2], output[1::2])):
      if not 'OK' in put['result']:
         logger.error('trouble with put command: {0}'.format(put))
         testpass = False
         continue
      if "ERROR" in get['result']:
         logger.error('trouble with get command: {0}'.format(get))
         testpass = False
         continue
      putvar = ' '.join(put['cmd'].split()[2:]).replace('0x', '')
      getvar = get['result'].replace('0x', '')
      if not putvar==getvar:
         logger.error('put!=get: {0}, {1}'.format(put, get))
         testpass = False
   return testpass


def registerTest_rw_bridge(crate, rm, slot):
   logger.info("beginning read-write tests for the bridge, will repeat operations {0} times.".format(n))

   # [name, size]
   regs = [
      #["B_Bottom_RESET_N", -1],
      #["B_Bottom_TRST_N", -1],
      ["B_I2CBUSID", 4],
      #["B_Igloo_VDD_Enable", -1],
      ["B_JTAGSEL", 1],
      ["B_JTAG_Select_Board", 4],
      ["B_JTAG_Select_FPGA", 1],
      ["B_SCRATCH", 32],
      #["B_SHT_softreset", -1],
      #["B_SHT_user", -1],
      #["B_Thermometer", -1],
      #["B_Top_RESET_N", -1],
      #["B_Top_TRST_N", -1]
   ] 
   #getRegisterSize(regs, crate, rm, slot, isBridge=True, isIgloo=False, isQIE=False)

   cmds = []
   for reg in regs:
      getcmd = "get HB{0}-{1}-{2}-{3}".format(crate, rm, slot, reg[0])
      for i in range(n):
         tempint = hex(randint(0, (2**reg[1])-1))
         putcmd = "put HB{0}-{1}-{2}-{3} {4}".format(crate, rm, slot, reg[0], tempint)
         cmds.append(putcmd)
         cmds.append(getcmd)

   output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass = checkOutput_rw(output)
   return output, testpass


def registerTest_rw_igloo(crate, rm, slot):
   logger.info("beginning read-write tests for the igloos, will repeat operations {0} times.".format(n))
   
   # [name, size]
   regs = [
      ["AddrToSERDES", 16],
      ["BX_forSpy", 12],
      ["CntrReg_CImode", 1],
      ["CntrReg_InputSpyRst", 1],
      ["CntrReg_WrEn_InputSpy", 1],
      ["CntrReg_bit25", 1],
      ["CntrReg_bit27", 1],
      ["CntrReg_bit30", 1],
      ["CntrReg_bit31", 1],
      ["CntrReg_type2_Rst", 1],
      ["CntrReg_type3_Rst", 1],
      ["CtrlToSERDES_i2c_go", 1],
      ["CtrlToSERDES_i2c_write", 1],
      ["DataToSERDES", 32],
      #["FiberID1", -1],
      ["LinkTestMode", 8],
      ["SpyAtFixedBX", 1],
      ["StartCapID", 2],
      #["UniqueID", -1],
      ["bc0_gen_disable", 1],
      ["scratch", 32]
   ]
   #getRegisterSize(regs, crate, rm, slot, isBridge=False, isIgloo=True, isQIE=False)

   cmds =[]
   for reg in regs:
      for igloo in ["iTop", "iBot"]:
         getcmd = "get HB{0}-{1}-{2}-{3}_{4}".format(crate, rm, slot, igloo, reg[0])
         for i in range(n):
            tempint = hex(randint(0, (2**reg[1])-1))
            putcmd = "put HB{0}-{1}-{2}-{3}_{4} {5}".format(crate, rm, slot, igloo, reg[0], tempint)
            cmds.append(putcmd)
            cmds.append(getcmd)

   output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass = checkOutput_rw(output)
   return output, testpass


def registerTest_rw_qie(crate, rm, slot):
   logger.info("beginning read-write tests for the qies, will repeat operations {0} times.".format(n))

   # [name, size]
   regs = [
      ["CapID0pedestal", 4],
      ["CapID1pedestal", 4],
      ["CapID2pedestal", 4],
      ["CapID3pedestal", 4],
      ["ChargeInjectDAC", 3],
      ["CkOutEn", 1],
      ["DiscOn", 1],
      ["FixRange", 1],
      ["Gsel", 5],
      ["Hsel", 1],
      ["Idcset", 5],
      ["Lvds", 1],
      ["PedestalDAC", 6],
      ["PhaseDelay", 7],
      ["RangeSet", 2],
      ["TDCMode", 1],
      ["TGain", 1],
      ["TimingIref", 3],
      ["TimingThresholdDAC", 8],
      ["Trim", 2]
      #["HB{0}-{1}-Qie[{2}-{3}]_ck_ph", -1] QIE->Qie?
   ]
   #getRegisterSize(regs, crate, rm, slot, isBridge=False, isIgloo=False, isQIE=True)

   QIEstart = 1 + (int(slot)-1)*16
   QIEend = QIEstart + 16-1
   cmds = []
   for reg in regs:
      getcmd = "get HB{0}-{1}-QIE[{2}-{3}]_{4}".format(crate, rm, QIEstart, QIEend, reg[0])  
      for i in range(n):
         putcmd = "put HB{0}-{1}-QIE[{2}-{3}]_{4} ".format(crate, rm, QIEstart, QIEend, reg[0])
         for j in range(16):
            putcmd += "{0} ".format(hex(randint(0, (2**reg[1])-1)))
         cmds.append(putcmd)
         cmds.append(getcmd)      

   output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass = checkOutput_rw(output)
   return output, testpass


