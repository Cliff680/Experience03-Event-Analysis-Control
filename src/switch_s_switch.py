import numpy as np
from src.switch_models import IDLE,RESERVED,SLOTS,LINKS
def s_switch(input_frames,spatial_map):
    out=np.full((LINKS,SLOTS),IDLE,dtype=np.uint8)
    out[:,list(RESERVED)]=input_frames[:,list(RESERVED)]
    for (dst,slot),src in spatial_map.items():
        if dst not in range(LINKS) or src not in range(LINKS) or slot not in range(SLOTS) or slot in RESERVED:raise ValueError('invalid endpoint')
        out[dst,slot]=input_frames[src,slot]
    return out
