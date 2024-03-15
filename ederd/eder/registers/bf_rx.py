from .register import Register, BFRegister

class bf_rx:
    bf_rx_awv_idx_table = Register(name="bf_rx_awv_idx_table",addr=0x160,size=0x40,default=0x0)
    bf_rx_awv_idx = Register(name="bf_rx_awv_idx",addr=0x1a0,size=0x1,default=0x0)
    bf_rx_awv_ce = Register(name="bf_rx_awv_ce",addr=0x1a1,size=0x1,default=0x0)
    bf_rx_cfg = Register(name="bf_rx_cfg",addr=0x1a3,size=0x1,default=0x1)
    bf_rx_mbist_0_pat = Register(name="bf_rx_mbist_0_pat",addr=0x1a4,size=0x2,default=0x5555)
    bf_rx_mbist_1_pat = Register(name="bf_rx_mbist_1_pat",addr=0x1a6,size=0x2,default=0xaaaa)
    bf_rx_mbist_2p_sel = Register(name="bf_rx_mbist_2p_sel",addr=0x1a9,size=0x1,default=0x0)
    bf_rx_mbist_en = Register(name="bf_rx_mbist_en",addr=0x1aa,size=0x2,default=0x0)
    bf_rx_mbist_result = Register(name="bf_rx_mbist_result",addr=0x1ac,size=0x2,default=0x0)
    bf_rx_mbist_done = Register(name="bf_rx_mbist_done",addr=0x1ae,size=0x2,default=0x0)
    bf_rx_awv_ptr = Register(name="bf_rx_awv_ptr",addr=0x1a2,size=0x1,default=0x0)
    bf_rx_awv = BFRegister(name="bf_rx_awv",addr=0x1000)

