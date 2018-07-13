import logging
logger = logging.getLogger(__name__)

import ngFECSendCommand as sendCommands

host = 'localhost'

import random
random.seed(1)
from random import randint

def getRegisterSize(regs, crate, rm, slot, port, isBridge=False, isIgloo=False, isQIE=False):
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

def checkOutput_rw(output,list_regs,n):
   testpass = True#truth value for all rw tests
   #reg_truth = 1   #pass status per register, initialized to passing
   stat_val = []  #list of pass/fail values per register
   
   result_dict = {}#dictionary where per register test info will be stored
   
   for i, (put, get) in enumerate(zip(output[::2], output[1::2])):
      reg_check = True#Each register considered true until otherwise noted
      pass_stat = 1#defaults to passing
      
      if not 'OK' in put['result']:
         logger.error('trouble with put command: {0}'.format(put))
         testpass  = False
         reg_check = False
         continue
      if "ERROR" in get['result']:
         logger.error('trouble with get command: {0}'.format(get))
         testpass  = False
         reg_check = False
         continue
      putvar = ' '.join(put['cmd'].split()[2:]).replace('0x', '')
      getvar = get['result'].replace('0x', '')
      if not putvar==getvar:
         logger.error('put!=get: {0}, {1}'.format(put, get))
         testpass  = False
         reg_check = False
      if not reg_check:
         pass_stat = 0

      stat_val.append(pass_stat)

   for i in range(len(list_regs)):
      reg_truth = 1#defaults to passing
      l_per_reg  = stat_val[i+i*(n-1):n+i*n]#finds the values that correspond to each register
      pass_count = sum(l_per_reg)
      if pass_count !== n:
         reg_truth = 0

      #result_dict[list_regs[i]] = reg_truth#does this on per register basis, no counting per iteration
      result_dict[list_regs[i]] = [reg_truth,pass_count,n-pass_count]#this has the number info
      
   return testpass, result_dict


def registerTest_rw_bridge(crate, rm, slot, port, n):
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
   regs_list = []
   for reg in regs:
      regs_list.append("reg_"+reg[0])
      getcmd = "get HB{0}-{1}-{2}-{3}".format(crate, rm, slot, reg[0])
      for i in range(n):
         tempint = hex(randint(0, (2**reg[1])-1))
         putcmd = "put HB{0}-{1}-{2}-{3} {4}".format(crate, rm, slot, reg[0], tempint)
         cmds.append(putcmd)
         cmds.append(getcmd)
         
   output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass, regs_status_dict  = checkOutput_rw(output,regs_list,n)
   return output, testpass, regs_status_dict


def registerTest_rw_igloo(crate, rm, slot, port, n):
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

   reg_list = []
   cmds =[]
   for reg in regs:
      for igloo in ["iTop", "iBot"]:
         reg_list.append("reg_"+igloo+"_"+reg[0])
         getcmd = "get HB{0}-{1}-{2}-{3}_{4}".format(crate, rm, slot, igloo, reg[0])
         for i in range(n):
            tempint = hex(randint(0, (2**reg[1])-1))
            putcmd = "put HB{0}-{1}-{2}-{3}_{4} {5}".format(crate, rm, slot, igloo, reg[0], tempint)
            cmds.append(putcmd)
            cmds.append(getcmd)
            
   output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass, reg_dict_status = checkOutput_rw(output,reg_list,n)
   return output, testpass, reg_dict_status


def registerTest_rw_qie(crate, rm, slot, port, n):
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
   reg_list = []
   for reg in regs:
      reg_list.append("reg_"+reg[0])
      getcmd = "get HB{0}-{1}-QIE[{2}-{3}]_{4}".format(crate, rm, QIEstart, QIEend, reg[0])  
      for i in range(n):
         putcmd = "put HB{0}-{1}-QIE[{2}-{3}]_{4} ".format(crate, rm, QIEstart, QIEend, reg[0])
         for j in range(16):
            putcmd += "{0} ".format(hex(randint(0, (2**reg[1])-1)))#adding random number to put command
         cmds.append(putcmd)
         cmds.append(getcmd)

   output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass, reg_status_list = checkOutput_rw(output,reg_list,n)
   return output, testpass, reg_status_list


