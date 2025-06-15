from core.factory import connect
from plugins.im3590.im3590_scpi import IM3590SCPI

with connect(dev="im3590", method="serial") as ins:
    ins: IM3590SCPI
    ins.idn()
    
    
