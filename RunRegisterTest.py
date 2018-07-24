import os
import sys
import ngFECSendCommand as sendCmds

def runCard(switch, rbx, rm, slot, n, tName, comments):
    if int(switch):
        op = os.system('python registerTest.py -c {0} -r {1} -s {2} -n {3} -t "{4}" -C "{5}"'.format(rbx, rm, slot, n, tName, comments))
        if op != 0:
            print '\x1b[91mREG TEST STOPPED for rm {0}, slot {1}, run it again ninja\x1b[0m'.format(rm,slot)#weird characters make it red
        outdict  = {"sysres":op,"rm":rm,"slot":slot}
        return outdict
        

if __name__ == "__main__":
    rbx = 1
    n = sys.argv[1]
    tName = sys.argv[18]
    comments = sys.argv[19]
    runout   = []

    #RM1
    runout.append(runCard(sys.argv[2], rbx, 1, 1, n, tName, comments))
    runout.append(runCard(sys.argv[3], rbx, 1, 2, n, tName, comments))
    runout.append(runCard(sys.argv[4], rbx, 1, 3, n, tName, comments)) 
    runout.append(runCard(sys.argv[5], rbx, 1, 4, n, tName, comments)) 
    #RM2
    runout.append(runCard(sys.argv[6], rbx, 2, 1, n, tName, comments))
    runout.append(runCard(sys.argv[7], rbx, 2, 2, n, tName, comments)) 
    runout.append(runCard(sys.argv[8], rbx, 2, 3, n, tName, comments)) 
    runout.append(runCard(sys.argv[9], rbx, 2, 4, n, tName, comments)) 
    #RM3
    runout.append(runCard(sys.argv[10], rbx, 3, 1, n, tName, comments))
    runout.append(runCard(sys.argv[11], rbx, 3, 2, n, tName, comments)) 
    runout.append(runCard(sys.argv[12], rbx, 3, 3, n, tName, comments)) 
    runout.append(runCard(sys.argv[13], rbx, 3, 4, n, tName, comments)) 
    #RM4
    runout.append(runCard(sys.argv[14], rbx, 4, 1, n, tName, comments))
    runout.append(runCard(sys.argv[15], rbx, 4, 2, n, tName, comments)) 
    runout.append(runCard(sys.argv[16], rbx, 4, 3, n, tName, comments)) 
    runout.append(runCard(sys.argv[17], rbx, 4, 4, n, tName, comments)) 

    servcmds = []
    badpos   = []
    for d in runout:
        if d is not None and d["sysres"] != 0:
            servcmds.append('get HB{0}-{1}-{2}-UniqueID'.format(rbx,d["rm"],d["slot"]))
            badpos.append(d)

    output = sendCmds.send_commands(cmds=servcmds,script = False, port = 64000,control_hub = 'localhost')#Hack for port and host!!!!! 
        
    message = "play -q ~/Downloads/Help_-The_Beatles.mp3 trim 0:00 0:03.4; sleep 0.5; python3 -m google_speech -v warning 'Re do register test for a card' -e vol 2.0 &> /dev/null"
    if output != []:
        os.system(message)

    for i,entry in enumerate(output):
        uid = entry['result']
        uid = uid.split(" ")
        uid = uid[1]+"_"+uid[2]
        outline = 'FAILED RUNNING REG TEST on RM {0}, slot {1}, UniqueID {2} sys error {3}'.format(badpos[i]["rm"],badpos[i]["slot"],uid,badpos[i]["sysres"])
        print '\x1b[91m'+outline+', RUN AGAIN\x1b[0m'

        #Get directory of crashed run 
        extension = 1
        #dirpath = "BAD DIRECTORY"
        while os.path.exists( "/home/hcalpro/DATA/RegTestResults/{0}_v{1}/".format(uid, extension) ):
            extension += 1
        #dirpath = "./registerTestResults/{0}_v{1}/".format(uid, extension)
        while os.path.exists( "./registerTestResults/{0}_v{1}/".format(uid, extension) ):
            extension += 1
        if extension == 1:
            continue
        else:
            extension -= 1
        dirpath = "./registerTestResults/{0}_v{1}/".format(uid, extension)

        print dirpath

        #Appending what happened to log
        fname = open(dirpath+"run.log","a")
        fname.write('\n'+outline)
        
        mvline = 'mv {0} ~/DATA/RegTestResults/'.format(dirpath)
        print mvline
        #Moving the directory lacking json
        moveit = os.system(mvline)
        if moveit == 0:
            print "moved bad directory to ~/DATA/RegTestResults/"
    
