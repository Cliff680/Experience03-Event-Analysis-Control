import numpy as np
from src.switch_models import IDLE,RESERVED,SLOTS
def t_switch(input_frame,control_memory):
    out=np.full(SLOTS,IDLE,dtype=np.uint8)
    out[list(RESERVED)]=input_frame[list(RESERVED)]
    for dst,src in control_memory.items():
        if dst not in range(SLOTS) or src not in range(SLOTS) or dst in RESERVED or src in RESERVED:raise ValueError('invalid slot')
        out[dst]=input_frame[src]
    return out
