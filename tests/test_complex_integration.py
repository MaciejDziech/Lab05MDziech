import pytest
from src.models import Parameters
from src.manager import Manager

def test_get_apartment_costs_basic():
    params = Parameters()
    manager = Manager(params)
    
    assert manager.get_apartment_costs('ZMYSLONE_MIESZKANIE', 2026, 4) is None
    assert manager.get_apartment_costs('apart-polanka', 1999, 1) == 0.0