import logging
logger = logging.getLogger(__name__)

import ngFECSendCommand as sendCommands

port = 64000
host = 'localhost'


def checkOutput_setDefaults(output):
   for entry in output:
      if not 'OK' in entry['result']:
         logger.warning('trouble with put command: {0}'.format(entry))


def registerTest_setDefaults_bridge(crate, rm, slot):
   logger.info('setting defaults for the bridge')

   # [register, default value]
   regs = [
      ["B_Bottom_RESET_N", 1],
      ["B_Bottom_TRST_N", 1],
      ["B_I2CBUSID", 0],
      ["B_Igloo_VDD_Enable", 1],
      ["B_JTAGSEL", 0],
      ["B_JTAG_Select_Board", 0],
      ["B_JTAG_Select_FPGA", 0],
      ["B_SCRATCH", 0],
      ["B_SHT_softreset", 0],
      ["B_SHT_user", 0],
      #["B_Thermometer", 0],
      ["B_Top_RESET_N", 1],
      ["B_Top_TRST_N", 1]
   ]

   cmds = []
   for reg in regs:
      cmds.append("put HB{0}-{1}-{2}-{3} {4}".format(crate, rm, slot, reg[0], reg[1]))

   output = sendCommands.send_commands(cmds=cmds, script=True, port=port, control_hub=host)
   checkOutput_setDefaults(output)
   
   return output


def registerTest_setDefaults_igloo(crate, rm, slot):
   logger.info('setting defaults for the igloos')
  
   # [register, default value] 
   regs = [
      ["AddrToSERDES", 0],
      ["BX_forSpy", 0],
      ["CntrReg_CImode", 0],
      ["CntrReg_InputSpyRst", 0],
      ["CntrReg_WrEn_InputSpy", 0],
      ["CntrReg_bit25", 0],
      ["CntrReg_bit27", 0],
      ["CntrReg_bit30", 0],
      ["CntrReg_bit31", 0],
      ["CntrReg_type2_Rst", 0],
      ["CtrlToSERDES_i2c_go", 0],
      ["CtrlToSERDES_i2c_write", 0],
      ["DataToSERDES", 0],
      ["FiberID1", 0],
      ["LinkTestMode", 0],
      ["SpyAtFixedBX", 0],
      ["StartCapID", 0],
      #["UniqueID", 0],
      ["bc0_gen_disable", 0],
      ["scratch", 0]
   ]

   cmds = []
   for reg in regs:
      for igloo in ["iBot", "iTop"]:
         cmds.append("put HB{0}-{1}-{2}-{3}_{4} {5}".format(crate, rm, slot, igloo, reg[0], reg[1])  )

   output = sendCommands.send_commands(cmds=cmds, script=True, port=port, control_hub=host)
   checkOutput_setDefaults(output)

   return output


def registerTest_setDefaults_qie(crate, rm, slot):

   logger.info('setting defaults for the qies')

   # [register, default value]
   regs = [
      ["CapID0pedestal", 0],
      ["CapID1pedestal", 0],
      ["CapID2pedestal", 0],
      ["CapID3pedestal", 0],
      ["ChargeInjectDAC", 0],
      ["CkOutEn", 1],
      ["DiscOn", 1],
      ["FixRange", 0],
      ["Gsel", 0],
      ["Hsel", 0],
      ["Idcset", 0],
      ["Lvds", 1],
      ["PedestalDAC", 38],
      ["PhaseDelay", 0],
      ["RangeSet", 0],
      ["TDCMode", 0],
      ["TGain", 0],
      ["TimingIref", 0],
      ["TimingThresholdDAC", 255],
      ["Trim", 2]
   ]

   QIEstart = 1 + (int(slot)-1)*16
   QIEend = QIEstart + 16-1
   cmds = []
   for reg in regs:
      cmds.append("put HB{0}-{1}-QIE[{2}-{3}]_{4} 16*{5}".format(crate, rm, QIEstart, QIEend, reg[0], reg[1]))
   output = sendCommands.send_commands(cmds=cmds, script=True, port=port, control_hub=host)
  
   checkOutput_setDefaults(output)
   return output


