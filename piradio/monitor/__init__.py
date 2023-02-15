
_monitor=None

def get_monitor():
    from .monitor import Monitor
    global _monitor
    
    if _monitor is None:
        _monitor = Monitor()

    return _monitor

