from DahuaCam.camera import Camera


c0 = Camera('VTop')
c1 = Camera('VBottom')
c2 = Camera('STop')
c3 = Camera('SBottom')

VToploc = '/home/egcs/BatteryIMG/VTop.bmp'
VBottomloc = '/home/egcs/BatteryIMG/VBottom.bmp'
SToploc = '/home/egcs/BatteryIMG/STop.bmp'
SBottomloc = '/home/egcs/BatteryIMG/SBottom.bmp'


c0.takephoto(VToploc)
c0.saveImgFile(VToploc, 'null')

c1.takephoto(VBottomloc)
print c1.stat
c1.saveImgFile(VBottomloc, 'null')

c2.takephoto(SToploc)
c2.saveImgFile(SToploc, 'null')

c3.takephoto(SBottomloc)
c3.saveImgFile(SBottomloc, 'null')

