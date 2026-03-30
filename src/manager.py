from src.models import Apartment, Bill, Parameters, Tenant, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key: str, year: int=None, month: int=None):
        if apartment_key not in self.apartments:
            return None
        
        if month is not None and (month < 1 or month > 12):
            return None
        suma = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if year is None:
                    suma += bill.amount_pln
                elif month is None:
                    if bill.settlement_year == year:
                        suma += bill.amount_pln
                else:
                    if bill.settlement_year == year and bill.settlement_month == month:
                        suma += bill.amount_pln
                        
        return suma

    def generate_apartment_settlement(self, apartment_key: str, year: int, month: int):
        from src.models import ApartmentSettlement 
        
        if apartment_key not in self.apartments:
            return None
            
        rachunki = self.get_apartment_costs(apartment_key, year, month)
        if rachunki is None:
            rachunki = 0.0
        
        czynsze = 0.0
        for tenant in self.tenants.values():
            if tenant.apartment == apartment_key:
                czynsze += tenant.rent_pln
                
        bilans = czynsze - rachunki
        
        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=czynsze,
            total_bills_pln=rachunki,
            total_due_pln=bilans
        )
    
    def generate_tenant_settlements(self, apartment_key: str, year: int, month: int):
        from src.models import TenantSettlement
        
        if apartment_key not in self.apartments:
            return []
            
        rachunki = self.get_apartment_costs(apartment_key, year, month)
        if rachunki is None:
            rachunki = 0.0
            
        apt_tenants = []
        for key, tenant in self.tenants.items():
            if tenant.apartment == apartment_key:
                apt_tenants.append((key, tenant))
                
        if len(apt_tenants) == 0:
            return []
            
        rachunki_na_osobe = rachunki / len(apt_tenants)
        
        rozliczenia = []
        for key, tenant in apt_tenants:
            rent = tenant.rent_pln
            total_due = rent + rachunki_na_osobe
            balance = 0.0 - total_due 
            
            s = TenantSettlement(
                tenant=key,
                apartment_settlement=apartment_key,
                month=month,
                year=year,
                rent_pln=rent,
                bills_pln=rachunki_na_osobe,
                total_due_pln=total_due,
                balance_pln=balance
            )
            rozliczenia.append(s)
            
        return rozliczenia