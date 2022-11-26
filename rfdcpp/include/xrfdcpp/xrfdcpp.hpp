
struct rfdc_csr;
struct rftile_csr;

class XRFDCTile
{
  volatile rftile_csr *csr;
public:
  XRFDCTile(volatile rftile_csr *);
  
  uint32_t state();

  bool cdetect_status();
  
  bool clock_detected();
  bool supplies_up();
  bool power_up();
  bool pll_locked();  
};

class XilinxRFDC
{
  volatile struct rfdc_csr *csr;
  uint64_t csr_len;
  int uio_fd;
  
public:
  XilinxRFDC();
  ~XilinxRFDC();

  std::tuple<int, int, int, int> version();

  void reset();
  
  uint32_t POSM();
  
  XRFDCTile adc(int);
  XRFDCTile dac(int);
};
