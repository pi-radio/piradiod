from .register import Register, BFRegister
class bf_tx:
    bf_tx_awv_idx_table = Register(name="bf_tx_awv_idx_table",addr=0x100,size=0x40,default=0x0)
    bf_tx_awv_idx = Register(name="bf_tx_awv_idx",addr=0x140,size=0x1,default=0x0)
    bf_tx_awv_ce = Register(name="bf_tx_awv_ce",addr=0x141,size=0x1,default=0x0)
    bf_tx_cfg = Register(name="bf_tx_cfg",addr=0x143,size=0x1,default=0x1)
    bf_tx_mbist_0_pat = Register(name="bf_tx_mbist_0_pat",addr=0x144,size=0x2,default=0x5555)
    bf_tx_mbist_1_pat = Register(name="bf_tx_mbist_1_pat",addr=0x146,size=0x2,default=0xaaaa)
    bf_tx_mbist_2p_sel = Register(name="bf_tx_mbist_2p_sel",addr=0x149,size=0x1,default=0x0)
    bf_tx_mbist_en = Register(name="bf_tx_mbist_en",addr=0x14a,size=0x2,default=0x0)
    bf_tx_mbist_result = Register(name="bf_tx_mbist_result",addr=0x14c,size=0x2,default=0x0)
    bf_tx_mbist_done = Register(name="bf_tx_mbist_done",addr=0x14e,size=0x2,default=0x0)
    bf_tx_awv_ptr = Register(name="bf_tx_awv_ptr",addr=0x142,size=0x1,default=0x0)
    bf_tx_awv = BFRegister(name="bf_tx_awv",addr=0x800)

