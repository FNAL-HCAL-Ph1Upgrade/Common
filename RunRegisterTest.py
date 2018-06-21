import os
import sys

def runCard(switch, rbx, rm, slot, runNum):
    if int(switch):
        os.system('python registerTest.py -c {0} -r {1} -s {2} -R {3}'.format(rbx, rm, slot, runNum))
        #print 'python registerTest.py -c {0} -r {1} -s {2} -R {3}:    switch {4}'.format(rbx, rm, slot, runNum, switch)

if __name__ == "__main__":
    rbx = 1
    runNum = sys.argv[1]

    ##For testing
    #for i in range(1,17):
    #    print "RunNum {0} Card {1} Run: {2} ".format(runNum, i, sys.argv[i+1])

    #RM1
    runCard(sys.argv[2], rbx, 1, 1, runNum)
    runCard(sys.argv[3], rbx, 1, 2, runNum) 
    runCard(sys.argv[4], rbx, 1, 3, runNum) 
    runCard(sys.argv[5], rbx, 1, 4, runNum) 
    #RM2
    runCard(sys.argv[6], rbx, 2, 1, runNum)
    runCard(sys.argv[7], rbx, 2, 2, runNum) 
    runCard(sys.argv[8], rbx, 2, 3, runNum) 
    runCard(sys.argv[9], rbx, 2, 4, runNum) 
    #RM3
    runCard(sys.argv[10], rbx, 3, 1, runNum)
    runCard(sys.argv[11], rbx, 3, 2, runNum) 
    runCard(sys.argv[12], rbx, 3, 3, runNum) 
    runCard(sys.argv[13], rbx, 3, 4, runNum) 
    #RM4
    runCard(sys.argv[14], rbx, 4, 1, runNum)
    runCard(sys.argv[15], rbx, 4, 2, runNum) 
    runCard(sys.argv[16], rbx, 4, 3, runNum) 
    runCard(sys.argv[17], rbx, 4, 4, runNum) 
