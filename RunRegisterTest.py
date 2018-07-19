import os
import sys

def runCard(switch, rbx, rm, slot, n, tName, comments):
    if int(switch):
        op = os.system('python registerTest.py -c {0} -r {1} -s {2} -n {3} -t "{4}" -C "{5}"'.format(rbx, rm, slot, n, tName, comments))
        if op != 0:
            print "problem with rm {0}, slot {1}, seems to have aborted".format(rm,slot)
        outdict  = ["sysres":op,"rm":rm,"slot":slot]
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

    for d in runout:
        if d["sysres"] != 0:
            print "There was a problem running reg test on RM {0}, slot{1}".format(d["rm"],d["slot"])


