import logging
logger = logging.getLogger(__name__)

import ngFECSendCommand as sendCommands

port = 64100
host = 'localhost'
n = 5

#not the most efficient function...
def getCounterSize(regs, crate, rm, slot, isBridge=False, isIgloo=False):
   for reg in regs:
      if reg[3] == True:
         print reg[0]
         if isBridge:
            get = "get HB{0}-{1}-{2}-{3}".format(crate, rm, slot, reg[0])
         if isIgloo:
            get = "get HB{0}-{1}-{2}-iTop_{3}".format(crate, rm, slot, reg[0])
         vals = []
         cmds = []
         for i in range(1024):
            cmds.append(get)
         output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
         for entry in output:
            result = output[0]['result'].replace('0x', '')
            result = int(result, 16)
            vals += [result]
         for i in range(0, 99999999999999):
            if 2**i > max(vals):
               print "max return of register is: {0}; a size of {1}".format(max(vals), i)
               break


def checkOutput_ro(output, regs):

   testpass = True
   #load up the numbers into an array
   vals = []
   for entry in output:
      result = entry['result']
      if "ERROR" in result:
         logger.error('trouble with get command: {0}'.format(entry))
         testpass = False
         result = -1
      else :
         result = entry['result'].replace('0x', '')
         result = int(result, 16)
      vals.append(result)

   #check
   for i in range(0, len(regs)) :
      nums = vals[i:len(output):len(regs)]
      for j,num in enumerate(nums):
         if ((num<regs[i][1]) or (num>regs[i][2])):
            logger.error('unexpected return from get command: {0}; expected range [{1}, {2}]'.format(output[i+j*len(regs)], regs[i][1], regs[i][2]))
            testpass = False
      if regs[i][3]:
         isdup = False
         unique = nums
         for entry in nums:
            count = unique.count(entry)
            if count > 1:
               isdup = True
               break
         if isdup:
            thereturn = output[i:len(output):len(regs)]
            logger.error("counter may be stuck: {0}".format(thereturn))
            testpass = False

   return testpass


def registerTest_ro_bridge(crate, rm, slot):
   logger.info('beginning read-only tests for the bridge, will repeat operations {0} times.'.format(n))

   # [name, min, max, iscounter?]
   regs  = [
      ["B_AddrMatchCnt1", 0xadd0, 0xadd0, False],
      ["B_AddrMatchCnt2", 0xbad, 0xbad, False],      
      ["B_BkPln_GEO", int(slot), int(slot), False],
      ["B_BkPln_RES_QIE", 0, 0, False],  
      ["B_BkPln_Spare_1_Counter", 0xbadadd0, 0xbadadd0, False],
      ["B_BkPln_Spare_2_Counter", 0xbadadd0, 0xbadadd0, False],
      ["B_BkPln_Spare_3_Counter", 0xbadadd0, 0xbadadd0, False],
      ["B_BkPln_WTE", 0, 0, False],
      ["B_CLOCKCOUNTER", 0, (2**12)-1, True],
      ["B_FIRMVERSION_MAJOR", 4, 4, False],
      ["B_FIRMVERSION_MINOR", 2, 2, False],
      ["B_ID1", 0x4842524d, 0x4842524d, False],
      ["B_ID2", 0x42726467, 0x42726467, False],
      ["B_ONES", 0xffffffff, 0xffffffff, False],
      ["B_ONESZEROES", 0xaaaaaaaa, 0xaaaaaaaa, False],
      ["B_RESQIECOUNTER", 0, (2**24)-1, True],
      #["B_SHT_ident", 0, -1], # returns two words
      #["B_SHT_rh_f", 0, -1], # returns decimal
      #["B_SHT_temp_f", 0. -1], # returns decimal
      ["B_WTECOUNTER", 0, (2**24)-1, True],
      ["B_ZEROES", 0, 0, False],
      ["B_bc0_status_count", 0, (2**21)-1, True],
      ["B_bc0_status_max", 0xdec, 0xdec, False],
      ["B_bc0_status_min", 0xdec, 0xdec, False],
      ["B_bc0_status_missing", 0, 0, False],
      ["B_bc0_status_shift", 0, 0, False]
   ]
   #getCounterSize(regs, crate, rm, slot, isBridge=True, isIgloo=False)
   
   cmds = []
   for i in range(0, n):
      for reg in regs:
         cmds.append("get HB{0}-{1}-{2}-{3}".format(crate, rm, slot, reg[0])) 

   output = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass = checkOutput_ro(output, regs)
   return output, testpass


def registerTest_ro_igloo(crate, rm, slot):
   logger.info('beginning read-only tests for the igloos, will repeat operations {0} times.'.format(n))

   # [name, min, max, iscounter]
   regs = [
      ["ChAlignStatus", 0, 0, False],
      ["Clk_count", 0, (2**16)-1, True],
      #["DataFromSERDES", 0, -1, False],
      ["FPGA_MAJOR_VERSION", 1, 1, False],
      ["FPGA_MINOR_VERSION", 3, 3, False],
      ["FPGA_TopOrBottom", 0, 1, False],
      ["OnesRegister", 0xffffffff, 0xffffffff, False],
      ["Spy32bits", 0, (2**32)-1, True],
      #["Spy96bits", 0, -1, True], # returns 3 words
      #["StatFromSERDES_busy", 0, -1, False],
      #["StatFromSERDES_i2c_counter", 0, -1, False],
      ["StatusReg_BRIDGE_SPARE", 0, 0, False],
      ["StatusReg_InputSpyFifoFull", 0, 1, False],
      ["StatusReg_InputSpyFifoEmpty", 0, 1, False],
      ["StatusReg_InputSpyWordNum", 0, 1, False],
      ["StatusReg_PLL320MHzLock", 1, 1, False],
      ["StatusReg_QieDLLNoLock", 0, 0, False],
      ["WTE_count", 0, (2**32)-1, True],
      ["ZerosRegister", 0, 0, False],
      ["bc0_gen_error", 0, 0, False],
      ["bc0_gen_locked", 0, 1, False],
      ["bc0_gen_warning", 0, 0, False],
      ["bc0_status_count_a", 0, (2**22)-1, True],
      ["bc0_status_count_b", 0, (2**22)-1, True],
      ["bc0_status_max_a", 0xdeb, 0xdeb, False],
      ["bc0_status_max_b", 0xdeb, 0xdeb, False],
      ["bc0_status_min_a", 0xdeb, 0xdeb, False],
      ["bc0_status_min_b", 0xdeb, 0xdeb, False],
      ["bc0_status_missing_a", 0, 0, False],
      ["bc0_status_missing_b", 0, 0, False],
      ["bc0_status_shift_a", 0, 0, False],
      ["bc0_status_shift_b", 0, 0, False],
      #["inputSpy", 0, -1], # returns 7 words
   ]
   #getCounterSize(regs, crate, rm, slot, isBridge=False, isIgloo=True)
   
   # do tests for top igloo
   output_iTop = []
   cmds = []
   for i in range(0, n):
      for reg in regs:
         cmds.append("get HB{0}-{1}-{2}-{3}_{4}".format(crate, rm, slot, "iTop", reg[0]))
   output_iTop = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass_iTop = checkOutput_ro(output_iTop, regs)

   #do tests for bottom igloo
   output_iBot = []
   cmds = []
   for i in range(0, n):
      for reg in regs:
         cmds.append("get HB{0}-{1}-{2}-{3}_{4}".format(crate, rm, slot, "iBot", reg[0]))
   output_iBot = sendCommands.send_commands(cmds=cmds, script=False, control_hub=host, port=port)
   testpass_iBot = checkOutput_ro(output_iBot, regs) 
   
   #concatenate
   output = output_iTop + output_iBot
   testpass = testpass_iTop and testpass_iBot
   return output, testpass


#def registerTest_ro_qie(crate, rm, slot):
#   logger.info('there are no read-only tests for the qies')
   
#   output = []
#   testpass = true
#   return output, testpass


