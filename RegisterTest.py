##############################################
# Taken from similar HF script
# https://github.com/dnoonan08/hcalScripts/blob/master/RegisterTest.py
##############################################

import sys
import os
import sqlite3
from random import randint

#from ROOT import *
#gROOT.SetBatch(True)

from optparse import OptionParser
import subprocess
import pexpect
from time import time, sleep
from datetime import date, datetime
from re import search, escape

#from ngccmServerInfo import *


import sendCommands
#UID_SN_DB = sqlite3.connect("/nfshome0/dnoonan/serialNumberToUIDmap.db")
#cursor = UID_SN_DB.cursor()

v = False
names = []			# List of names ordered as in registers list.
# fe_crate = 13
# fe_slot = 2
n = 1#5 #at.n
errdic = {}
port = 64000
host = 'localhost'


def setQIEDefaults(crate, rm_slot, RBXtype):

    rm = rm_slot.split("-")[0]
    slot = rm_slot.split("-")[1]

    #port = serverLocations[int(crate)]['port']
    #host = serverLocations[int(crate)]['host']
    
    cmds  = ['put {0}{1}-{2}-{3}-B_Igloo_VDD_Enable 1'.format(RBXtype,crate,rm,slot),
             'put {0}{1}-{2}-{3}-B_Top_RESET_N 1'.format(RBXtype,crate,rm,slot),
             'put {0}{1}-{2}-{3}-B_Top_TRST_N 1'.format(RBXtype,crate,rm,slot),
             'put {0}{1}-{2}-{3}-B_Bottom_RESET_N 1'.format(RBXtype,crate,rm,slot),
             'put {0}{1}-{2}-{3}-B_Bottom_TRST_N 1'.format(RBXtype,crate,rm,slot),
             ]
    if RBXtype == "HE":
        cmds += ["put HE{0}-{1}-{2}-i_AddrToSERDES 0".format(crate,rm,slot),
                 "put HE{0}-{1}-{2}-i_CntrReg_CImode 0".format(crate,rm,slot),
                 "put HE{0}-{1}-{2}-i_CntrReg_WrEn_InputSpy 0".format(crate,rm,slot),
                 "put HE{0}-{1}-{2}-i_CtrlToSERDES_i2c_go 0".format(crate,rm,slot),
                 "put HE{0}-{1}-{2}-i_CtrlToSERDES_i2c_write 0".format(crate,rm,slot),
                 "put HE{0}-{1}-{2}-i_DataToSERDES 0".format(crate,rm,slot),
                 "put HE{0}-{1}-{2}-i_LinkTestMode 0".format(crate,rm,slot),
                 ]
    # TODO: add HB igloo (not sure yet what the format is)

    nQIE = 12 #48
    if RBXtype == "HB":
        nQIE = 64
    cmds += ["put {0}{1}-{2}-QIE[1-{3}]_Lvds {3}*1".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_Trim {3}*2".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_DiscOn {3}*1".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_TGain {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_TimingThresholdDAC {3}*0xff".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_TimingIref {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_PedestalDAC {3}*0x26".format(RBXtype, crate, rm, nQIE),    
             "put {0}{1}-{2}-QIE[1-{3}]_CapID0pedestal {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_CapID1pedestal {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_CapID2pedestal {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_CapID3pedestal {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_FixRange {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_RangeSet {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_ChargeInjectDAC {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_Gsel {3}*7".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_Hsel {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_Idcset {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_CkOutEn {3}*1".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_TDCmode {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-QIE[1-{3}]_PhaseDelay {3}*0".format(RBXtype, crate, rm, nQIE),
             "put {0}{1}-{2}-Qie[1-{3}]_ck_ph {3}*0".format(RBXtype, crate, rm, nQIE),
             ]
    # TODO: check default values
    output = sendCommands.send_commands(cmds, script = False, progbar = False,port=port, control_hub=host)

    goodReset = True
    for entry in output:
        if not 'OK' in entry['result']:
            print entry
            goodReset = False

    return goodReset

def rand(size = 1):
	output = ''

	if size % 32:
		output += hex(randint(0, 2**(size % 32-1))) + ' '
	for i in range(int(size/32)):
		output += hex(randint(0, 2**32-1)) + ' '

	return output[:-1]

def register(name = None, size = 1, n = 5, multQIEs = False, nQIE=48):
	cmds = []
	for i in range(n):
		r = ''
		if multQIEs:
			for i in range(nQIE):
				r += '{0} '.format(rand(size))
		else:
			r = rand(size)
		#cmds += ['put {0} {1}'.format(name, r),'get {0}_rr'.format(name)]
		cmds += ['put {0} {1}'.format(name, r), 'wait','get {0}'.format(name), 'wait']
	return cmds

def create_plots(info = [-1,-1,'0x00000000 0x00000000'],names = None, dic = None, k = 1):

    
        uID = info[-1]
        sernumber = cursor.execute("select serial from UIDtoSerialNumber where uid=?",(uID,)).fetchone()
                
        if type(sernumber)==type(tuple()):
            serialnumber = '500'+str(sernumber[0])
        else:
            serialnumber = '500999'

	outputDir = 'registerTestResults/%s__%s'%(serialnumber,info[2].replace(' ','_'))
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)
	outputDir = 'registerTestResults/%s__%s/%s'%(serialnumber,info[2].replace(' ','_'),str(date.today()))
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)

	outFile = TFile("{0}/HF{1}-{2}_{3}_{4}.root".format(outputDir,str(info[0]),info[1],info[2].replace(' ','_'),serialnumber),'recreate')
	gROOT.SetStyle("Plain")
	gStyle.SetOptStat(0)
        canvas = TCanvas()#"regTest","regTest",1200,600)
	canvas.Divide(1, k)
        canvas.SetBottomMargin(0.3)
	tothist = []
	rwhist = []
	xhist = []
	stacks = []
	for i in range(k):
		namespart = names[i*len(names)/k: (i+1)*len(names)/k]	# On (i+1)*len(names)/n, first i*len(names) is done, then the division by n. By that way, i = k - 1 => (i+1)*len(names)/k = len(names). So we don't lose any bins because of integer division.
		tothist.append(TH1F("Total_{0}".format(i+1), "", len(namespart), -0.5, len(namespart)-0.5))
		rwhist.append(TH1F("R/W_{0}".format(i+1), "", len(namespart), -0.5, len(namespart)-0.5))
		xhist.append(TH1F("Exec_{0}".format(i+1), "", len(namespart), -0.5, len(namespart)-0.5))
		stacks.append(THStack("Error_{0}".format(i+1), ""))
		tothist[i].SetFillColor(kGreen)
		rwhist[i].SetFillColor(kRed)
		xhist[i].SetFillColor(kOrange)
		for j, name in enumerate(namespart):
			tothist[i].GetXaxis().SetBinLabel(j+1, name)
			rwhist[i].GetXaxis().SetBinLabel(j+1, name)
			xhist[i].GetXaxis().SetBinLabel(j+1, name)
			tothist[i].Fill(j, dic[name][1][0])
			rwhist[i].Fill(j, dic[name][1][1])
			xhist[i].Fill(j, dic[name][1][2])
                tothist[i].GetXaxis().LabelsOption("vd")
		rwhist[i].GetXaxis().LabelsOption("vd")
		xhist[i].GetXaxis().LabelsOption("vd")
		canvas.cd(i + 1)
		tothist[i].GetXaxis().SetLabelOffset(0.02)
		tothist[i].Write()
		rwhist[i].Write()
		xhist[i].Write()
		stacks[i].Add(rwhist[i])
		stacks[i].Add(xhist[i])
		stacks[i].Write()
		tothist[i].SetMaximum(1.15*n)
		tothist[i].SetMinimum(0)
		stacks[i].SetMaximum(1.15*n)
		stacks[i].SetMinimum(0)
		tothist[i].Draw()
		stacks[i].Draw("SAME")
                        



	canvas.SaveAs("{0}/HF{1}-{2}_{3}.pdf".format(outputDir,info[0],info[1],info[2].replace(' ','_')))
	canvas.SaveAs("{0}/HF{1}-{2}_{3}.png".format(outputDir,info[0],info[1],info[2].replace(' ','_')))


        
        # canvas.SetBottomMargin(0)
        canvas = TCanvas()
        for j, name in enumerate(namespart):
            if dic[name][2]==24*[0]:
                continue
            
            canvas.Clear()
            QI = []
            text = TLatex()
            text.SetTextAlign(12)
            text.SetTextSize(0.07)
            text.DrawText(0.3,0.9,name)

            text.SetTextSize(0.04)
            for i_qie in range(12):
                QI.append(TBox( .02+(i_qie*.08) , .6 , .09+(i_qie*.08), .7))
                QI[-1].SetLineColor(kBlack)
                if dic[name][2][i_qie]>0:
                    QI[-1].SetFillColor(kRed)
                else:
                    QI[-1].SetFillColor(kGreen)
                QI[-1].Draw('l')
            for i_qie in range(12,24):
                QI.append(TBox( .02+((i_qie-12)*.08) , .4 , .09+((i_qie-12)*.08), .5))
                QI[-1].SetLineColor(kBlack)
                if dic[name][2][i_qie]>0:
                    QI[-1].SetFillColor(kRed)
                else:
                    QI[-1].SetFillColor(kGreen)
                QI[-1].Draw('l')

            for i_qie in range(9):
                text.DrawText( .05+(i_qie*.08) , .65, "%i"%(i_qie+1))
            for i_qie in range(9,12):
                text.DrawText( .04+(i_qie*.08) , .65, "%i"%(i_qie+1))
            for i_qie in range(12,24):
                text.DrawText( .04+((i_qie-12)*.08) , .45, "%i"%(i_qie+1))

            canvas.SaveAs("{0}/HF{1}-{2}_{3}_{4}.pdf".format(outputDir,info[0],info[1],info[2].replace(' ','_'),name.replace('[1-24]','')))
            canvas.SaveAs("{0}/HF{1}-{2}_{3}_{4}.png".format(outputDir,info[0],info[1],info[2].replace(' ','_'),name.replace('[1-24]','')))
                
	outFile.Write()
	outFile.Close()
	return 0

def registerTest(fe_crate, rm_slot, RBXtype):
    rm = rm_slot.split("-")[0]
    slot = rm_slot.split("-")[1]

    #port = serverLocations[int(fe_crate)]['port']
    #host = serverLocations[int(fe_crate)]['host']

    output = sendCommands.send_commands(cmds = 'get {0}{1}-{2}-{3}-UniqueID'.format(RBXtype, fe_crate, rm, slot), 
                                        script = False, progbar = False, port=port, control_hub=host)
    uID = "%s %s"%(output[0]['result'].split()[1],output[0]['result'].split()[2])


    print '{0} {1}, RM {2}, Slot {3}, UniqueId {4}'.format(RBXtype, fe_crate, rm, slot, uID)
    
    if "NACK" in uID:
        print "Could not communicate with UniqueId, will skip rest of the test"
        return

    names = []
    registers = []			# List of commands to be sent to ngFEC tool
    errdic = {}

    nQIE = 12 #48
    if RBXtype == "HB":
        nQIE = 64

    registers.extend(
        register("{0}{1}-{2}-QIE[1-{3}]_Lvds".format(RBXtype, fe_crate, rm, nQIE), 1, n, True, nQIE) +			# 1 bit
        register("{0}{1}-{2}-QIE[1-{3}]_Trim".format(RBXtype, fe_crate, rm, nQIE), 2, n, True, nQIE) +			# 2 bits
        register("{0}{1}-{2}-QIE[1-{3}]_DiscOn".format(RBXtype, fe_crate, rm, nQIE), 1, n, True, nQIE) +			# 1 bit
        register("{0}{1}-{2}-QIE[1-{3}]_TGain".format(RBXtype, fe_crate, rm, nQIE), 1, n, True, nQIE) +			# 1 bit
        register("{0}{1}-{2}-QIE[1-{3}]_TimingThresholdDAC".format(RBXtype, fe_crate, rm, nQIE), 8, n, True, nQIE) +	# 8 bits
        register("{0}{1}-{2}-QIE[1-{3}]_TimingIref".format(RBXtype, fe_crate, rm, nQIE), 3, n, True, nQIE) +		# 3 bits
        register("{0}{1}-{2}-QIE[1-{3}]_PedestalDAC".format(RBXtype, fe_crate, rm, nQIE), 6, n, True, nQIE) +		# 6 bits
        register("{0}{1}-{2}-QIE[1-{3}]_CapID0pedestal".format(RBXtype, fe_crate, rm, nQIE), 4, n, True, nQIE) +		# 4 bits
        register("{0}{1}-{2}-QIE[1-{3}]_CapID1pedestal".format(RBXtype, fe_crate, rm, nQIE), 4, n, True, nQIE) +		# 4 bits
        register("{0}{1}-{2}-QIE[1-{3}]_CapID2pedestal".format(RBXtype, fe_crate, rm, nQIE), 4, n, True, nQIE) +		# 4 bits
        register("{0}{1}-{2}-QIE[1-{3}]_CapID3pedestal".format(RBXtype, fe_crate, rm, nQIE), 4, n, True, nQIE) +		# 4 bits
        register("{0}{1}-{2}-QIE[1-{3}]_FixRange".format(RBXtype, fe_crate, rm, nQIE), 1, n, True, nQIE) +			# 1 bit
        register("{0}{1}-{2}-QIE[1-{3}]_RangeSet".format(RBXtype, fe_crate, rm, nQIE), 2, n, True, nQIE) +			# 2 bits
        register("{0}{1}-{2}-QIE[1-{3}]_ChargeInjectDAC".format(RBXtype, fe_crate, rm, nQIE), 3, n, True, nQIE) +		# 3 bits
        register("{0}{1}-{2}-QIE[1-{3}]_Gsel".format(RBXtype, fe_crate, rm, nQIE), 5, n, True, nQIE) +			# 5 bits
        register("{0}{1}-{2}-QIE[1-{3}]_Hsel".format(RBXtype, fe_crate, rm, nQIE), 1, n, True, nQIE) +			# 1 bit
        register("{0}{1}-{2}-QIE[1-{3}]_Idcset".format(RBXtype, fe_crate, rm, nQIE), 5, n, True, nQIE) +			# 5 bits
        register("{0}{1}-{2}-QIE[1-{3}]_CkOutEn".format(RBXtype, fe_crate, rm, nQIE), 1, n, True, nQIE) +			# 1 bit
        register("{0}{1}-{2}-QIE[1-{3}]_TDCmode".format(RBXtype, fe_crate, rm, nQIE), 1, n, True, nQIE) +			# 1 bit
        register("{0}{1}-{2}-Qie[1-{3}]_ck_ph".format(RBXtype, fe_crate, rm, nQIE), 4, n, True, nQIE)			# 4 bits
        )
    
    if RBXtype == "HE":
        registers.extend(
        register("HE{0}-{1}-{2}-i_CntrReg_CImode".format(fe_crate, rm, slot), 1, n) +			# 1 bit
        register("HE{0}-{1}-{2}-i_CntrReg_WrEn_InputSpy".format(fe_crate, rm, slot), 1, n) +		# 1 bit
        register("HE{0}-{1}-{2}-i_AddrToSERDES".format(fe_crate, rm, slot), 16, n) +			# 16 bits
        register("HE{0}-{1}-{2}-i_CtrlToSERDES_i2c_go".format(fe_crate, rm, slot), 1, n) +		# 1 bit
        register("HE{0}-{1}-{2}-i_CtrlToSERDES_i2c_write".format(fe_crate, rm, slot), 1, n) +		# 1 bit
        register("HE{0}-{1}-{2}-i_DataToSERDES".format(fe_crate, rm, slot), 32, n) +			# 32 bits
        register("HE{0}-{1}-{2}-i_LinkTestMode".format(fe_crate, rm, slot), 8, n) 			# 8 bits
        )
    
    for reg in registers[2::4*n]:
        names.extend([reg[4:]])

    #print registers

    output = sendCommands.send_commands(cmds = registers, script = True, progbar = True,control_hub=host,port=port)

    errlist = []
    totaltests = 0
    rwerr = 0
    xerr = 0
    #print output
    lastCmd = ''
    for i, (put, get) in enumerate(zip(output[::4], output[2::4])):
        #print i, put, get
        if not get['cmd'][4:]== lastCmd:
            badChannels = nQIE*[0]
        lastCmd = get['cmd'][4:]
        totaltests += 1
                
        if 'ERROR' in put['result'] or 'ERROR' in get['result']:
            xerr += 1
        elif ' '.join(put['cmd'].split()[2:]).replace('0x', '') != get['result'].replace('0x', ''):
            rwerr += 1
            errlist.append([' '.join(put['cmd'].split()[2:]).replace('0x', ''), get['result'].replace('0x', '')])
            putList = ' '.join(put['cmd'].split()[2:]).replace('0x', '').split()
            getList = get['result'].replace('0x', '').split()

            for j in range(len(putList)):
                if not putList[j]==getList[j]:
                    badChannels[j] = 1

        if 'ERROR' in put['result']:
            errlist.append([put['cmd'], put['result']])
        if 'ERROR' in get['result']:
            errlist.append([get['cmd'], get['result']])
        if not (i+1) % n:
            errdic.update({get['cmd'][4:]: [errlist, [totaltests, rwerr, xerr],badChannels]})
            errlist = []
            totaltests = 0
            rwerr = 0
            xerr = 0

#---------------Last report of errors------------------
    print "\n====== SUMMARY ============================"
    passedTests = True


    if errdic.values().count([[], [n, 0, 0],nQIE*[0]]) == len(names):
        print '[OK] There were no errors.'
    else:
        print 'R/W errors (put != get):'
        passedTests = False
        for name in names:
            for error in errdic[name][0]:
                if (error[0] != error[1] and not 'ERROR' in error[1]):
                    print '\t*Register: ' + name + ' -> Data: 0x' + error[0].replace(' ', ' 0x') + ' != 0x' + error[1].replace(' ', ' 0x')

        print '\nExecution errors:'
        for name in names:
            for error in errdic[name][0]:
                if 'ERROR' in error[1]:
                    print '\t*Command: ' + error[0] + ' -> Result: ' + error[1]
    print "===========================================\n"


#---------------Create histogram-----------------------
    #create_plots([fe_crate, fe_slot, uID],names, errdic, 2)


if __name__ == "__main__":
        
        parser = OptionParser()
        parser.add_option("-c", "--fecrate", dest="c",
                          default=1,
                          help="RBX number (default is %default).",
                          metavar="nr"
                          )
        parser.add_option("-s", "--feslot", dest="s",
                          default="-1",
                          help="RM number(s) within the RBX, can be integer or list of integers comma separated without spaces (default is -1)",
                          metavar="nr"
                          )
        parser.add_option("-q", "--qiecard", dest="q",
                          default="-1",
                          help="QIE card number(s) within the RBX, can be integer or list of integers comma separated without spaces (default is -1)",
                          metavar="nr"
                          )
        parser.add_option("-t", "--type", dest="type",
                          default="HE",
                          help="Front end type, either HE or HB. Defaults to %default.",
                          metavar="HE"
                          )
        (options, args) = parser.parse_args()

        fe_crate = options.c
        if fe_crate == -1:
            print 'specify a crate number'
            sys.exit()

        if ',' in options.s and not(options.s[0]=='[' and options.s[-1]==']'):
            options.s = '['+options.s+']'
        fe_slot = eval(options.s)

        if ',' in options.q and not(options.q[0]=='[' and options.q[-1]==']'):
            options.q = '['+options.q+']'
        qie_cards = eval(options.q)
        if qie_cards == -1:
            qie_cards = [1,2,3,4]
        
        #port = serverLocations[int(fe_crate)]['port']
        #host = serverLocations[int(fe_crate)]['host']

        if fe_slot == -1:
            # We'll check whether we can find the filled slots ourselves
            slotList = ["1-1","1-2","1-3","1-4","2-1","2-2","2-3","2-4","3-1","3-2","3-3","3-4","4-1","4-2","4-3","4-4"]
            cmd = []
            for slot in slotList:
                cmd.append('get {0}{1}-{2}-B_SHT_temp_f'.format(options.type, fe_crate, slot))
            output = sendCommands.send_commands(cmds = cmd,script=True,port=port,control_hub=host)
            filledSlots = []
            for islot, slot in enumerate(slotList):
                temps = output[islot]['result'].split()
                try:
                    if float(temps[0])>0:
                        filledSlots.append(slot)
                    elif float(temps[0])>-270:
                        print 'Problem with card in slot %s', slot
                except ValueError as err:
                    #print 'Problem with card in slot', slot
                    #print "Error was: ", err
                    print "No card detected in slot", slot
        else:
            if type(qie_cards) == type(int()):
                qie_cards = [qie_cards]
            # Now qie_cards is always a list
            filledSlots = []
            if type(fe_slot)==type(list()): 
                for fe in fe_slot:
                    filledSlots.extend(['%i-%i' % (int(fe), int(qie_card)) for qie_card in qie_cards])
            else:
                filledSlots = ['%i-%i' % (int(fe_slot), int(qie_card)) for qie_card in qie_cards]
            
	outputDir = 'registerTestResults'
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)

        print 'Running over slots', filledSlots
        for i_slot in filledSlots:
            print 'Slot %s'%i_slot
            registerTest(fe_crate, i_slot, options.type)
            setQIEDefaults(fe_crate, i_slot, options.type)

