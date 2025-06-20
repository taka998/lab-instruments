# If you want to use static analysis, uncomment the import and type annotation lines below.
# When running this script directly (e.g., `python examples/example1.py` or `uv run -m examples.example1.py`),

from core.factory import connect
#from plugins.im3590.im3590_scpi import IM3590SCPI

with connect(dev="im3590") as ins:
    #ins: IM3590SCPI
    print(ins.idn())
    ins.set_freq(1000)
    ins.get_freq()
    print(ins.measure())
    
