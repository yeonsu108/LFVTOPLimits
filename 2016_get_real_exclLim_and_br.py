import sys
# From 2016 paper, Hut limit on Xsec is ~ 1.23pb (utilisant le plot et une latte) on BR 0.34%
# From 2016 paper, Hct limit on Xsec is ~ 1.15pb (utilisant le plot et une latte) on BR 0.44%

limit_from_combine = float(sys.argv[1])

Xsec = 50.82 #Hut kirill
#Xsec = 38.88/10 #Hct kirill

#Xsec = 60.34 #Hut 2017ANv3
#Xsec = 48.4 #Hct 2017ANv3

realLimit = (limit_from_combine*Xsec)/float(10)
print "Real limit: %f"%realLimit

BR = realLimit*0.19/(Xsec*1.32158)
print "BR: %f %%"%(BR*100)

print "To be compared with 2016 paper, Hut limit on Xsec is ~ 1.23pb on BR 0.34%% \n\t Hct limit on Xsec is ~ 1.15pb on BR 0.44%%"
