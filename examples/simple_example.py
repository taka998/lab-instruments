"""Simple device connection example"""
import lab_instruments

# Connect to IM3590 LCR meter - type is automatically inferred as IM3590SCPI
with lab_instruments.connect(dev="im3590") as lcr:
    print(lcr.idn())
    lcr.set_freq(1000)
    print(lcr.measure())
