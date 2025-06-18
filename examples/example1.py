# If you want to use static analysis, uncomment the import and type annotation lines below.

from core.factory import connect
#from plugins.im3590.im3590_scpi import IM3590SCPI

with connect(dev="im3590") as ins:
    #ins: IM3590SCPI
    print(ins.idn())
    ins.set_freq()
    ins.measure()
    
