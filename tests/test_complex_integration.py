import pytest
from src.models import Parameters
from src.manager import Manager

def test_get_apartment_costs_basic():
    params = Parameters()
    manager = Manager(params)
    
    assert manager.get_apartment_costs('ZMYSLONE_MIESZKANIE', 2026, 4) is None
    assert manager.get_apartment_costs('apart-polanka', 1999, 1) == 0.0
    wynik = manager.get_apartment_costs('apart-polanka', 2026, 4)
    assert wynik is not None
    assert type(wynik) is float

    assert manager.get_apartment_costs('apart-polanka', 2026, 13) is None #test na 13 miesiąc

from src.manager import Manager
from src.models import Parameters
from src.models import Bill


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0

def test_apartment_settlement_tdd():
    from src.models import Parameters
    from src.manager import Manager
    
    params = Parameters()
    manager = Manager(params)
    
    settlement = manager.generate_apartment_settlement('apart-polanka', 2026, 4)
    
    if settlement:
        assert settlement.apartment == 'apart-polanka'
        assert settlement.year == 2026                  
        assert settlement.month == 4                    
        assert settlement.total_bills_pln >= 0.0        
        assert settlement.total_rent_pln >= 0.0         
        assert settlement.total_due_pln == settlement.total_rent_pln - settlement.total_bills_pln  

    assert manager.generate_apartment_settlement('WIDMO_MIESZKANIE', 2026, 4) is None

    settlement_empty = manager.generate_apartment_settlement('apart-polanka', 1999, 1)
    
    if settlement_empty:
        assert settlement_empty.year == 1999            
        assert settlement_empty.total_bills_pln == 0.0
        assert settlement_empty.total_due_pln == settlement_empty.total_rent_pln