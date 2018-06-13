import os
import sys
import json
import time
from optparse import OptionParser
import uuid
import ngFECSendCommand as sendCommands
import logging

port = 64000
host = 'localhost'

from registerTest_setDefaults import registerTest_setDefaults_bridge
from registerTest_setDefaults import registerTest_setDefaults_igloo
from registerTest_setDefaults import registerTest_setDefaults_qie
from registerTest_ro import registerTest_ro_bridge
from registerTest_ro import registerTest_ro_igloo
from registerTest_ro import registerTest_ro_qie
from registerTest_rw import registerTest_rw_bridge
from registerTest_rw import registerTest_rw_igloo
from registerTest_rw import registerTest_rw_qie

def backplanereset(crate, half):
   logger = logging.getLogger(__name__)
   logger.info('resetting backplane {0}'.format(half))   
  
   cmds = [
      'put HB{0}{1}-bkp_pwr_enable 1'.format(crate, half),
      'put HB{0}{1}-bkp_reset 1'.format(crate, half),
      'put HB{0}{1}-bkp_reset 0'.format(crate, half)
   ]
   
   output = []
   for cmd in cmds:
      output += sendCommands.send_commands(cmds=cmd, script=True, port=port, control_hub=host)
   for entry in output:
      result = entry['result']
      if not 'OK' in result:
         logger.critical('trouble with put command: {0}'.format(entry))
         sys.exit()

   return output


def checkid(crate, rm, slot):
   logger = logging.getLogger(__name__)
   logger.info('checking UniqueID')

   cmd = [
      'get HB{0}-{1}-{2}-UniqueID'.format(crate, rm, slot)
   ]
   output = sendCommands.send_commands(cmds=cmd, script=True, port=port, control_hub=host)

   result = output[0]['result']
   if "ERROR" in result:
      logger.critical('trouble with get command: {0}'.format(output[0]))
      sys.exit()
   
   uID = output[0]['result']
   logger.info('UniqueID is: {0}'.format(uID))
   uID = uID.split(" ")
   uID = uID[1]+"_"+uID[2]
   return output, uID


def checktemp(crate, rm, slot):
   logger = logging.getLogger(__name__)
   logger.info('checking the bridge temperature')
   
   cmd = [
      'get HB{0}-{1}-{2}-B_SHT_temp_f'.format(crate, rm, slot)
   ]

   output = sendCommands.send_commands(cmds=cmd, script=True, port=port, control_hub=host)

   result = output[0]['result']
   if "ERROR" in result:
      logger.critical('trouble with get command: {0}'.format(output[0]))
      sys.exit()

   temp = result.split()
   logger.info('bridge has temperature: {0}'.format(temp[0]))
   
   return output


if __name__ == "__main__":

   tf = "{0}.tmp".format(str(uuid.uuid4()))
   logging.basicConfig(filename=tf, level=logging.DEBUG)
   
   console = logging.StreamHandler()
   console.setLevel(logging.INFO)
   logging.getLogger('').addHandler(console)
   logger = logging.getLogger(__name__)
   
   logger.info("##########")
   logger.info('your temporary logfile: ./{0}'.format(tf))
   logger.info(time.ctime(time.time()))

   parser = OptionParser()
   parser.add_option("-c", "--crate", dest="c",
      default=-1,
      type = "int",
      help="crate number",
   )
   parser.add_option("-r", "--readoutmodule", dest="r",
      default=-1,
      type = "int",
      help="readout module number",
   )
   parser.add_option("-s", "--slot", dest="s",
      default=-1,
      type = "int",
      help="slot number within the readout module",
   )
   (options, args) = parser.parse_args()

   crate = options.c
   if not (crate==0 or crate==1):
      logger.critical('specify a proper crate number!')
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

   logger.info('begin crate {0}, rm {1}, slot {2}'.format(crate, rm, slot))

   outlog = []

   # reset the backplane
   if (rm==1 or rm==2):
      outlog += backplanereset(crate, "")
   elif (rm==3 or rm==4): 
      outlog += backplanereset(crate, "")

   # check the temperature sensor
   outlog += checktemp(crate, rm, slot)

   # check for the unique id
   out, uID = checkid(crate, rm, slot)
   outlog += out

   # rename log file to have uID in name
   runlog_fname = "./testresults.{0}.log".format(uID)
   os.rename(tf, runlog_fname)
   logger.info('the temporary log file has been renamed: {0}'.format(runlog_fname))

   # set defaults
   outlog += registerTest_setDefaults_bridge(crate, rm, slot)
   outlog += registerTest_setDefaults_igloo(crate, rm, slot)
   outlog += registerTest_setDefaults_qie(crate, rm, slot)
   
   # run bridge tests
   outlog += registerTest_ro_bridge(crate, rm, slot)
   outlog += registerTest_rw_bridge(crate, rm, slot)
   outlog += registerTest_setDefaults_bridge(crate, rm, slot)
   
   # run igloo tests
   outlog += registerTest_ro_igloo(crate, rm, slot)
   outlog += registerTest_rw_igloo(crate, rm, slot)
   outlog += registerTest_setDefaults_igloo(crate, rm, slot)

   # run qie tests
   outlog += registerTest_ro_qie(crate, rm, slot)
   outlog += registerTest_rw_qie(crate, rm, slot)
   outlog += registerTest_setDefaults_qie(crate, rm, slot)

   # dump all communication
   outlog_fname = "./commands.{0}.json".format(uID)
   with open(outlog_fname, "w") as file:
      file.write(json.dumps(outlog))
 
   logger.info('finished crate {0}, rm {1}, slot {2}'.format(crate, rm, slot))
   logger.info(time.ctime(time.time()))
   logger.info("##########")

