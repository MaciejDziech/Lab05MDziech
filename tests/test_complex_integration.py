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

def test_tenant_settlements_tdd():
    from src.models import Parameters, Apartment, Tenant, Bill
    from src.manager import Manager
    
    manager = Manager(Parameters())

    manager.apartments['APT_0'] = Apartment(key='APT_0', name='Test', location='Test', area_m2=50.0, rooms={})
    manager.apartments['APT_1'] = Apartment(key='APT_1', name='Test', location='Test', area_m2=50.0, rooms={})
    manager.apartments['APT_2'] = Apartment(key='APT_2', name='Test', location='Test', area_m2=50.0, rooms={})

    manager.tenants['T_1'] = Tenant(name='Jan', apartment='APT_1', room='R1', rent_pln=1000.0, deposit_pln=0.0, date_agreement_from='', date_agreement_to='')
    manager.tenants['T_2A'] = Tenant(name='Anna', apartment='APT_2', room='R1', rent_pln=800.0, deposit_pln=0.0, date_agreement_from='', date_agreement_to='')
    manager.tenants['T_2B'] = Tenant(name='Piotr', apartment='APT_2', room='R2', rent_pln=900.0, deposit_pln=0.0, date_agreement_from='', date_agreement_to='')

    manager.bills.append(Bill(amount_pln=200.0, date_due='2026-04-10', apartment='APT_1', settlement_year=2026, settlement_month=4, type='prad'))
    manager.bills.append(Bill(amount_pln=300.0, date_due='2026-04-10', apartment='APT_2', settlement_year=2026, settlement_month=4, type='prad'))


    wynik_0 = manager.generate_tenant_settlements('APT_0', 2026, 4)
    assert isinstance(wynik_0, list)
    assert len(wynik_0) == 0        

    wynik_1 = manager.generate_tenant_settlements('APT_1', 2026, 4)
    assert len(wynik_1) == 1         
    assert wynik_1[0].tenant == 'T_1'
    assert wynik_1[0].bills_pln == 200.0 
    assert wynik_1[0].total_due_pln == 1200.0


    wynik_2 = manager.generate_tenant_settlements('APT_2', 2026, 4)
    assert len(wynik_2) == 2         
    assert wynik_2[0].bills_pln == 150.0 
    assert wynik_2[1].bills_pln == 150.0 
    assert wynik_2[0].month == 4        