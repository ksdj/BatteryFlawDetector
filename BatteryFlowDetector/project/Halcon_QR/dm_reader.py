import os, time

def getBarString(rev):
    try:
        rr = rev.split(':')
        if len(rr)==2 and rr[0]=='DataString':
            return True, rr[1]
        
        return False, rev
    except:
        return False, "Error happend"

# change to your dm_reader path
dm_reader_path = '/opt/BatteryFlawDetector/project/Halcon_QR/dm_reader'
if __name__=='__main__':
    for x in range(1,2):
        file_path = '/home/egcs/{}.bmp'.format(x)
        output = os.popen('{} {}'.format(dm_reader_path, file_path) )
	cs = time.time()
        ok, msg = getBarString(output.read())
	ce = time.time()
        if ok:
            print 'imge {}, result: {}'.format(file_path, msg)
        else:
            print 'error: {}'.format(msg)

	print ce - cs
