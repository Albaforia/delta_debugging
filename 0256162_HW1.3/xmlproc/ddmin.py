#!/usr/bin/env python
# $Id: ddmin.py,v 2.2 2005/05/12 22:01:18 zeller Exp $

from split import split
from listsets import listminus
from xml.parsers.xmlproc import xmlproc
import re
import sys
import outputters

PASS       = "PASS"
FAIL       = "FAIL"
UNRESOLVED = "UNRESOLVED"
RECORDFILE = "record.xml"

def ddmin(circumstances, test):
    """Return a sublist of CIRCUMSTANCES that is a relevant configuration
       with respect to TEST."""
    
    #assert test([]) == PASS
    #assert test(circumstances) == FAIL

    n = 2
    while len(circumstances) >= 2:
        subsets = split(circumstances, n)
        assert len(subsets) == n
	
        some_complement_is_failing = 0
        for subset in subsets:

            complement = listminus(circumstances, subset)

            if test(complement) == FAIL:
                circumstances = complement
                n = max(n - 1, 2)
                some_complement_is_failing = 1
                break

        if not some_complement_is_failing:
            if n == len(circumstances):
                break
            n = min(n * 2, len(circumstances))

    return circumstances

if __name__ == "__main__":
    circumstances = []
    testnum = 0

    warnings=1
    entstack=0
    rawxml=0

    app = xmlproc.Application()
    p = xmlproc.XMLProcessor()  
    p.set_application(app)
    err=outputters.MyErrorHandler(p, p, warnings, entstack, rawxml)
    p.set_error_handler(err)
    p.set_data_after_wf_error(0) #Make program error output clear...

    def string_to_list(s):
        c = []
        for i in range(len(s)):
            c.append((i, s[i]))
        return c
    
    def mytest(c):
        global circumstances
        global testnum

        s = ""
        for (index, char) in c:
            s += char

        f = open(RECORDFILE,'w')
        f.write(s)
        f.close()
        testnum += 1
        print "Test Num %d" % testnum

        try:
            p.parse_resource(RECORDFILE)
            if err.errors == 0:   #Parser parse xml successfully.
                print PASS
                return PASS
            else:
                print UNRESOLVED  #Parser parse xml unsuccssfully,
                return UNRESOLVED #but do not make program crash.
        except UnboundLocalError: #Xml input make program crash
            print FAIL
            return FAIL

    def showResult(xmlfile):
        file = open(xmlfile)
        result = str(file.read())
        file.close
        print "************RESULT**OF**DELTA**DUBUGGING*************"
        print "%s" % (result)
        print "*****************************************************"

    file = open(sys.argv[1], 'r')
    content = file.read()
    file.close()
    circumstances = string_to_list(content)
    mytest(ddmin(circumstances, mytest))
    showResult(RECORDFILE)
