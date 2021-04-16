import pytest

def test_health():
    """ Test the core library is "there". 
    Also check whether the module-system's version """ 
    from .. import health as health1
    from hdl21 import health as health2

    a = health1()
    assert a == "alive"

    if health1 is not health2:
        import warnings
        import hdl21

        warnings.warn(f"Module under test is not installed version {hdl21}")


