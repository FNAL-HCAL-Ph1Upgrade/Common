import os
import sys
import json
import time
from optparse import OptionParser
import uuid
import ngFECSendCommand as sendCommands
import logging

host = 'localhost'

from registerTest_setDefaults import registerTest_setDefaults_bridge
from registerTest_setDefaults import registerTest_setDefaults_igloo
from registerTest_setDefaults import registerTest_setDefaults_qie
from registerTest_ro import registerTest_ro_bridge
from registerTest_ro import registerTest_ro_igloo
#from registerTest_ro import registerTest_ro_qie
from registerTest_rw import registerTest_rw_bridge
from registerTest_rw import registerTest_rw_igloo
from registerTest_rw import registerTest_rw_qie

def writeToCmdLog(output, cmdlogfile):
   for item in output:
      cmdlogfile.write("%s\n" % item)

def makeOutputPath(uID):
   path = "./registerTestResults/{0}/".format(uID)
   if os.path.exists(path):
      extension = 2
      while os.path.exists( "./registerTestResults/{0}_v{1}/".format(uID, extension) ):
         extension += 1
      path = "./registerTestResults/{0}_v{1}/".format(uID, extension)
   return path

def backplanereset(crate, halfback, port):
   logger = logging.getLogger(__name__)
   logger.info('resetting backplane {0}{1}'.format(crate,halfback))   

   cmds = []
   cmds.append('put HB{0}{1}-bkp_pwr_enable 1'.format(crate,halfback))
   cmds.append('put HB{0}{1}-bkp_reset 1'.format(crate,halfback))
   cmds.append('put HB{0}{1}-bkp_reset 0'.format(crate,halfback))

   output = sendCommands.send_commands(cmds=cmds, script=False, port=port, control_hub=host)   

   for entry in output:
      result = entry['result']
      if not 'OK' in result:
         logger.critical('trouble with put command: {0}'.format(entry))
         writeToCmdLog(output, cmdlogfile)
         sys.exit()

   return output


def checktemp(crate, rm, slot, port):
   logger = logging.getLogger(__name__)
   logger.info('checking the bridge temperature')
   
   cmds = []
   cmds.append('get HB{0}-{1}-{2}-B_SHT_temp_f'.format(crate, rm, slot))

   output = sendCommands.send_commands(cmds=cmds, script=True, port=port, control_hub=host)

   for entry in output:
      result = entry['result']
      if "ERROR" in result:
         logger.critical('trouble with get command: {0}'.format(output[0]))
         writeToCmdLog(output, cmdlogfile)
         sys.exit()

   temp = result.split()
   logger.info('bridge has temperature: {0}'.format(temp[0]))
   
   return output


def checkid(crate, rm, slot, port):
   logger = logging.getLogger(__name__)
   logger.info('checking UniqueID')

   cmds = []
   cmds.append('get HB{0}-{1}-{2}-UniqueID'.format(crate, rm, slot))
   output = sendCommands.send_commands(cmds=cmds, script=True, port=port, control_hub=host)

   for entry in output:
      result = entry['result']
      if "ERROR" in result:
         logger.critical('trouble with get command: {0}'.format(output[0]))
         writeToCmdLog(output, cmdlogfile)
         sys.exit()

   uID = output[0]['result']
   uID = uID.split(" ")
   uID = uID[1]+"_"+uID[2]
   logger.info('UniqueID is: {0}'.format(uID))

   return output, uID


if __name__ == "__main__":
   parser = OptionParser()
   parser.add_option("-p", "--port",  dest="port", default = 64000, type = "int", help = "port needed for server")
   parser.add_option("-n", "--num",   dest="n",    default = 5,     type = "int", help = "number of interations")
   parser.add_option("-S", "--side",  dest="side", default = "",    type = "str", help = "which half backplane")
   parser.add_option("-c", "--crate", dest="c",    default = -1,    type = "int", help = "crate number")
   parser.add_option("-r", "--rm",    dest="r",    default = -1,    type = "int", help = "readout module number")
   parser.add_option("-s", "--slot",  dest="s",    default = -1,    type = "int", help = "slot number within the readout module")
   parser.add_option("-t", "--tester",dest="t",    default = "ninja",type= "str", help = "name of person running tests")
   parser.add_option("-C", "--comments",dest="C",  default = "n/a", type = "str", help = "comments provided by tester")
   (options, args) = parser.parse_args()

   port  = options.port
   n = options.n
   halfp = options.side

   tester_name   = options.t
   test_comments = options.C
   
   crate = options.c
   if not (crate>-1):
      logger.critical('specify a crate number!')
      logger.critical('required registerTest options: python registerTest.py --crate X --readoutmodule Y --slot Z')
      sys.exit()
   
   rm = options.r
   if not (rm==1 or rm==2 or rm==3 or rm==4):
      logger.critical('specify a proper readout module number!')
      logger.critical('required registerTest options: python registerTest.py --crate X --readoutmodule Y --slot Z')
      sys.exit()
   
   slot = options.s
   if not (slot==1 or slot==2 or slot==3 or slot==4):
      logger.critical('specify a proper slot number!')
      logger.critical('required registerTest options: python registerTest.py --crate X --readoutmodule Y --slot Z')
      sys.exit()

   tempname = str(uuid.uuid4())
   templogname = "{0}.runlog.tmp".format(tempname)
   logging.basicConfig(filename=templogname, level=logging.DEBUG)
   console = logging.StreamHandler()
   console.setLevel(logging.INFO)
   logging.getLogger('').addHandler(console)
   logger = logging.getLogger(__name__)

   logger.info("##########")
   logger.info('your temporary run log: ./{0}'.format(templogname))
   logger.info(time.ctime(time.time()))

   logger.info('begin crate {0}, rm {1}, slot {2}'.format(crate, rm, slot))

   # log all commands
   tempcmdlogname = "{0}.cmdlog.tmp".format(tempname)
   cmdlogfile = open(tempcmdlogname, 'w+') 
   logger.info('your temporary command log: ./{0}'.format(tempcmdlogname))

   # reset the backplane
   #output = []
   #if (rm==1 or rm==2):
   #   output = backplanereset(crate, "")
   #elif (rm==3 or rm==4): 
   #   output = backplanereset(crate, "")
   output = backplanereset(crate, halfp, port)
   writeToCmdLog(output, cmdlogfile)

   # check the temperature sensor
   output = checktemp(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)

   # check for the unique id
   output, uID = checkid(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)
 
   outputPath = makeOutputPath(uID)
   os.makedirs(outputPath)
   print outputPath

   # rename test log file to have uID in name
   runlog_fname = outputPath+"run.log"
   os.rename(templogname, runlog_fname)
   logger.info('the run log file has been renamed: {0}'.format(runlog_fname))
   # rename command log file to have uID in name
   runcmdlog_fname = outputPath+"cmd.log"
   os.rename(tempcmdlogname, runcmdlog_fname)
   logger.info('the command log file has been renamed: {0}'.format(runcmdlog_fname))

   # set defaults
   output, pass_setDefaults_bridge = registerTest_setDefaults_bridge(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)
   output, pass_setDefaults_igloo = registerTest_setDefaults_igloo(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)
   output, pass_setDefaults_qie = registerTest_setDefaults_qie(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)
   
   # run bridge tests
   output, pass_ro_bridge = registerTest_ro_bridge(crate, rm, slot, port, n)
   writeToCmdLog(output, cmdlogfile)
   output, pass_rw_bridge = registerTest_rw_bridge(crate, rm, slot, port, n)
   writeToCmdLog(output, cmdlogfile)
   output, pass_setDefaults_bridge = registerTest_setDefaults_bridge(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)
   
   # run igloo tests
   outlog, pass_ro_igloo, per_reg_pass_ro_iTop, per_reg_pass_ro_iBot = registerTest_ro_igloo(crate, rm, slot, port, n)
   writeToCmdLog(output, cmdlogfile)
   output, pass_rw_igloo = registerTest_rw_igloo(crate, rm, slot, port, n)
   writeToCmdLog(output, cmdlogfile)
   output, pass_setDefaults_igloo = registerTest_setDefaults_igloo(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)

   # run qie tests
   #output, pass_ro_qie = registerTest_ro_qie(crate, rm, slot)
   #writeToCmdLog(output, cmdlogfile)
   output, pass_rw_qie = registerTest_rw_qie(crate, rm, slot, port, n)
   writeToCmdLog(output, cmdlogfile)
   output, pass_setDefaults_qie = registerTest_setDefaults_qie(crate, rm, slot, port)
   writeToCmdLog(output, cmdlogfile)

   testresults = {
      "uID" : uID,
      "bridge_ro" : int(pass_ro_bridge),
      "bridge_rw" : int(pass_rw_bridge),
      "igloo_ro" : int(pass_ro_igloo),
      "igloo_rw" : int(pass_rw_igloo),
      "qie_rw" : int(pass_rw_qie),
      "Comments" : "Adding a comment to the register test",
      "Tester_Name" : "Chris Madrid"
   }

   testresults.update(per_reg_pass_ro_bridge)
   testresults.update(per_reg_pass_ro_iTop)
   testresults.update(per_reg_pass_ro_iBot)

   with open(outputPath+"results.json", 'w') as testresultsfile:
      json.dump(testresults, testresultsfile)
      #testresultsfile.write(str(testresults))
   logger.info('the test results have been saved as {0}results.log'.format(outputPath))

   logger.info('finished crate {0}, rm {1}, slot {2}'.format(crate, rm, slot))
   logger.info(time.ctime(time.time()))
   logger.info("##########")


