# app.py - KOMPLETAN SA CUSTOMER ANALYTICS
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ---------- KONFIGURACIJA ----------
st.set_page_config(
    page_title="Dinamičke Cijene",
    page_icon="💰",
    layout="wide"
)

# ---------- KONSTANTE ----------
SUPPLIER_TERMS = 60  # Plaćanje dobavljačima za 60 dana
ANNUAL_INTEREST = 0.08  # 8% godišnje
MONTHLY_STORAGE = 0.005  # 0.5% mjesečno
COMMISSION_RATE = 0.03  # 3% provizija prodavača
LOGISTICS_RATE = 0.015  # 1.5% logistika

# ---------- KLASE ----------
class Product:
    """Klasa za proizvod"""
    def __init__(self, name, cost_price, selling_price, days_in_stock, quantity=1, category="General"):
        self.name = name
        self.cost_price = cost_price
        self.selling_price = selling_price
        self.days_in_stock = days_in_stock
        self.quantity = quantity
        self.category = category
    
    def calculate_storage_cost(self):
        """Računa trošak skladištenja"""
        months = self.days_in_stock / 30
        return self.cost_price * MONTHLY_STORAGE * months * self.quantity
    
    def get_inventory_status(self):
        """Vraća status zaliha"""
        if self.days_in_stock > 180:
            return "🚨 DEAD STOCK"
        elif self.days_in_stock > 90:
            return "⚠️ SLOW MOVING"
        elif self.days_in_stock > 30:
            return "🟡 NORMAL"
        else:
            return "✅ FRESH"

class Customer:
    """NOVA KLASA: Analiza profitabilnosti po kupcu"""
    def __init__(self, name, dso, customer_type="Regular", payment_history=0.95):
        self.name = name
        self.dso = dso  # Days Sales Outstanding
        self.customer_type = customer_type  # 'A', 'B', 'C' ili 'Veliki', 'Srednji', 'Mali'
        self.payment_history = payment_history  # 0-1 (95% = plaća na vrijeme)
        self.transactions = []  # Lista kupovina
        
    def add_transaction(self, product_name, quantity, cost_price, selling_price, days_in_stock):
        """Dodaje transakciju kupca"""
        self.transactions.append({
            'product': product_name,
            'quantity': quantity,
            'cost_price': cost_price,
            'selling_price': selling_price,
            'days_in_stock': days_in_stock,
            'total_cost': cost_price * quantity,
            'total_sale': selling_price * quantity
        })
    
    def calculate_financing_cost(self, transaction_amount):
        """Računa trošak finansiranja za transakciju"""
        cash_gap = max(self.dso - SUPPLIER_TERMS, 0)
        daily_interest = ANNUAL_INTEREST / 365
        return transaction_amount * daily_interest * cash_gap
    
    def calculate_total_profitability(self):
        """Računa kompletnu profitabilnost kupca"""
        if not self.transactions:
            return {'error': 'Nema transakcija'}
        
        total_sales = sum(t['total_sale'] for t in self.transactions)
        total_cost = sum(t['total_cost'] for t in self.transactions)
        
        # Početna "papirna" dobit
        paper_profit = total_sales - total_cost
        
        # Svi dodatni troškovi
        additional_costs = {
            'financing': 0,
            'storage': 0,
            'commission': 0,
            'logistics': 0,
            'risk': 0
        }
        
        for transaction in self.transactions:
            # Trošak finansiranja
            additional_costs['financing'] += self.calculate_financing_cost(transaction['total_sale'])
            
            # Trošak skladištenja
            months = transaction['days_in_stock'] / 30
            additional_costs['storage'] += transaction['total_cost'] * MONTHLY_STORAGE * months
            
            # Provizija prodavača
            additional_costs['commission'] += transaction['total_sale'] * COMMISSION_RATE
            
            # Logistika (dostava)
            additional_costs['logistics'] += transaction['total_sale'] * LOGISTICS_RATE
        
        # Trošak rizika (ako kasni s plaćanjem)
        risk_factor = 1 - self.payment_history
        additional_costs['risk'] = total_sales * risk_factor * 0.05  # 5% od iznosa za rizične
        
        total_additional_costs = sum(additional_costs.values())
        
        # Stvarna dobit
        real_profit = paper_profit - total_additional_costs
        
        return {
            'total_sales': total_sales,
            'total_cost': total_cost,
            'paper_profit': paper_profit,
            'additional_costs': additional_costs,
            'total_additional_costs': total_additional_costs,
            'real_profit': real_profit,
            'profit_margin': (real_profit / total_sales) if total_sales > 0 else 0,
            'status': self.get_profitability_status(real_profit / total_sales if total_sales > 0 else 0)
        }
    
    def get_profitability_status(self, margin):
        """Određuje status profitabilnosti"""
        if margin > 0.15:
            return "🟢 IZVRSNO"
        elif margin > 0.08:
            return "🟡 DOBRO"
        elif margin > 0:
            return "🟠 SLABO"
        else:
            return "🔴 GUBITAK"
    
    def get_recommendations(self, analysis):
        """Generiše preporuke za poboljšanje"""
        recs = []
        
        if self.dso > SUPPLIER_TERMS + 30:
            recs.append(f"• **Pregovaraj o skraćenju roka sa {self.dso} na {SUPPLIER_TERMS + 15} dana**")
            recs.append(f"• Ponudi 2-3% popusta za brže plaćanje")
        
        if analysis['additional_costs']['storage'] > analysis['real_profit'] * 0.3:
            recs.append("• **Usmjeri kupca na brže pokretnu robu**")
            recs.append("• Smanji prosječno vrijeme zaliha")
        
        if analysis['profit_margin'] < 0.05:
            recs.append("• **Razmotri povećanje cijena za ovog kupca**")
            recs.append("• Ograniči vrstu ili količinu robe")
        
        if not recs:
            recs.append("• Ovaj kupac je dobar - nastavi ovako!")
        
        return recs

# ---------- POMOĆNE FUNKCIJE ----------
def load_sample_products():
    """Učitava primjer proizvoda"""
    return [
        Product("Cement 25kg", 10.50, 15.75, 45, 100, "Građevina"),
        Product("Šperploča 18mm", 8.20, 13.50, 120, 50, "Građevina"),
        Product("Gvozdeni šip 6mm", 15.00, 22.50, 210, 20, "Metal"),
        Product("Boja bijela 10L", 18.00, 27.00, 15, 30, "Bojenje"),
        Product("PVC cijev 50mm", 3.50, 6.00, 250, 150, "Hidraulika"),
    ]

def calculate_dynamic_price(cost, days_old, dso, supplier_terms=60):
    """Računa dinamičku cijenu"""
    if days_old > 180:
        base = cost * 0.95
    elif days_old > 90:
        base = cost * 1.10
    elif days_old > 30:
        base = cost * 1.25
    else:
        base = cost * 1.50
    
    # Finansijska prilagodba
    cash_gap = max(dso - supplier_terms, 0)
    financing = base * (ANNUAL_INTEREST / 365) * cash_gap
    
    return max(base - financing, cost * 0.90)  # Ne ispod 90% nabavne

# ---------- STRANICE APLIKACIJE ----------
def show_dashboard():
    """Glavni dashboard"""
    st.title("💰 Dinamičke Cijene PRO")
    st.markdown("**Sistem za analizu profitabilnosti i upravljanje gotovinskim tokom**")
    
    # Sidebar konfiguracija
    with st.sidebar:
        st.header("⚙️ Konfiguracija")
        dso = st.slider("Prosječan DSO (dani)", 30, 180, 83)
        st.markdown("---")
        st.info("**DSO = Days Sales Outstanding**\nProsječan broj dana za naplatu.")
    
    # Učitaj proizvode
    products = load_sample_products()
    
    # Prikaz proizvoda
    st.subheader("📦 Analiza zaliha")
    
    data = []
    for p in products:
        rec_price = calculate_dynamic_price(p.cost_price, p.days_in_stock, dso)
        data.append({
            "Proizvod": p.name,
            "Nabavna": p.cost_price,
            "Trenutna": p.selling_price,
            "Preporučeno": round(rec_price, 2),
            "Starost": p.days_in_stock,
            "Status": p.get_inventory_status(),
            "Količina": p.quantity,
            "Vrijednost": round(p.quantity * rec_price, 2)
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Sumarni pregled
    col1, col2, col3 = st.columns(3)
    with col1:
        dead_stock = len([p for p in products if p.days_in_stock > 180])
        st.metric("Mrtva roba", dead_stock)
    with col2:
        total_value = df["Vrijednost"].sum()
        st.metric("Ukupna vrijednost", f"{total_value:,.0f} KM")
    with col3:
        avg_discount = ((df["Trenutna"] - df["Preporučeno"]).mean() / df["Trenutna"].mean() * 100)
        st.metric("Prosječan popust", f"{avg_discount:.1f}%")

def show_customer_analytics():
    """NOVA STRANICA: Analiza profitabilnosti po kupcu"""
    st.title("👥 Analiza profitabilnosti po kupcu")
    st.markdown("**Otkrij koji kupci stvarno donose profit, a koji jedu maržu**")
    
    # Sidebar za unos kupca
    with st.sidebar:
        st.header("➕ Dodaj novog kupca")
        
        customer_name = st.text_input("Naziv kupca", "Gradevinar DOO")
        customer_dso = st.number_input("DSO kupca (dani)", 30, 180, 110)
        customer_type = st.selectbox("Tip kupca", ["Veliki", "Srednji", "Mali", "VIP"])
        payment_history = st.slider("Historija plaćanja (%)", 50, 100, 85) / 100
        
        st.markdown("---")
        st.header("🛒 Dodaj transakcije")
        
        # Dinamički unos transakcija
        if 'transactions' not in st.session_state:
            st.session_state.transactions = []
        
        col1, col2 = st.columns(2)
        with col1:
            product = st.selectbox("Proizvod", ["Cement 25kg", "Šperploča", "Gvozdeni šip", "Boja", "PVC cijev"])
            quantity = st.number_input("Količina", 1, 1000, 10)
        
        with col2:
            cost = st.number_input("Nabavna (KM)", 0.0, 1000.0, 10.5)
            selling = st.number_input("Prodajna (KM)", 0.0, 1000.0, 15.75)
            days = st.number_input("Dana u lageru", 0, 365, 45)
        
        if st.button("Dodaj transakciju"):
            st.session_state.transactions.append({
                'product': product,
                'quantity': quantity,
                'cost': cost,
                'selling': selling,
                'days': days
            })
            st.success(f"Dodano: {quantity} × {product}")
        
        if st.session_state.transactions:
            st.markdown("### 📝 Trenutne transakcije")
            for i, t in enumerate(st.session_state.transactions):
                st.write(f"{i+1}. {t['quantity']}× {t['product']} ({t['selling']} KM)")
            
            if st.button("Obriši sve transakcije"):
                st.session_state.transactions = []
                st.rerun()
    
    # Glavni panel - analiza
    if not st.session_state.transactions:
        st.warning("⚠️ Dodajte transakcije u sidebar-u da biste vidjeli analizu.")
        return
    
    # Kreiraj kupca i dodaj transakcije
    customer = Customer(customer_name, customer_dso, customer_type, payment_history)
    
    for t in st.session_state.transactions:
        customer.add_transaction(
            t['product'], t['quantity'], t['cost'], t['selling'], t['days']
        )
    
    # Izračunaj profitabilnost
    analysis = customer.calculate_total_profitability()
    
    if 'error' in analysis:
        st.error(analysis['error'])
        return
    
    # Prikaz rezultata
    st.subheader(f"📊 Analiza za: **{customer_name}**")
    
    # Glavne metrike
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ukupna prodaja", f"{analysis['total_sales']:,.0f} KM")
    with col2:
        st.metric("'Papirna' dobit", f"{analysis['paper_profit']:,.0f} KM")
    with col3:
        st.metric("Stvarna dobit", f"{analysis['real_profit']:,.0f} KM", 
                 delta=f"{analysis['real_profit'] - analysis['paper_profit']:,.0f} KM")
    with col4:
        st.metric("Profit margin", f"{analysis['profit_margin']:.1%}", 
                 delta=analysis['status'])
    
    # Detaljni troškovi
    st.subheader("🔍 Detaljna analiza troškova")
    
    costs_df = pd.DataFrame({
        'Trošak': ['Finansiranje', 'Skladištenje', 'Provizija', 'Logistika', 'Rizik'],
        'Iznos (KM)': [
            analysis['additional_costs']['financing'],
            analysis['additional_costs']['storage'],
            analysis['additional_costs']['commission'],
            analysis['additional_costs']['logistics'],
            analysis['additional_costs']['risk']
        ]
    })
    
    # Dodaj procenat
    costs_df['Procenat'] = (costs_df['Iznos (KM)'] / analysis['total_sales'] * 100).round(1)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(costs_df, use_container_width=True)
    
    with col2:
        # Pie chart troškova
        fig = px.pie(costs_df, values='Iznos (KM)', names='Trošak', 
                     title="Struktura dodatnih troškova")
        st.plotly_chart(fig, use_container_width=True)
    
    # Preporuke
    st.subheader("🎯 Preporuke za poboljšanje")
    
    recommendations = customer.get_recommendations(analysis)
    for rec in recommendations:
        st.write(rec)
    
    # Scenario analiza
    st.subheader("📈 Šta ako analiza")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_dso = st.number_input("Novi DSO (dani)", 30, 180, 75)
        if new_dso != customer_dso:
            # Ponovna kalkulacija sa novim DSO
            temp_customer = Customer(customer_name, new_dso, customer_type, payment_history)
            for t in st.session_state.transactions:
                temp_customer.add_transaction(t['product'], t['quantity'], 
                                            t['cost'], t['selling'], t['days'])
            new_analysis = temp_customer.calculate_total_profitability()
            
            savings = analysis['additional_costs']['financing'] - new_analysis['additional_costs']['financing']
            st.metric("Ušteda na finansiranju", f"{savings:.0f} KM")
    
    with col2:
        discount = st.slider("Popust za brže plaćanje (%)", 0, 10, 3)
        if discount > 0:
            new_sales = analysis['total_sales'] * (1 - discount/100)
            new_profit = analysis['real_profit'] - (analysis['total_sales'] * discount/100)
            st.metric(f"Sa {discount}% popusta", f"{new_profit:,.0f} KM")
    
    with col3:
        better_payment = st.checkbox("Bolja historija plaćanja (+10%)")
        if better_payment:
            risk_savings = analysis['additional_costs']['risk'] * 0.3
            st.metric("Ušteda na riziku", f"{risk_savings:.0f} KM")
    
    # Export opcija
    st.markdown("---")
    if st.button("📥 Export analize u CSV"):
        export_df = pd.DataFrame([{
            'Kupac': customer_name,
            'DSO': customer_dso,
            'Tip': customer_type,
            'Ukupna_Prodaja': analysis['total_sales'],
            'Papirna_Dobit': analysis['paper_profit'],
            'Stvarna_Dobit': analysis['real_profit'],
            'Margin': analysis['profit_margin'],
            'Status': analysis['status'],
            'Finansiranje_KM': analysis['additional_costs']['financing'],
            'Skladištenje_KM': analysis['additional_costs']['storage'],
            'Provizija_KM': analysis['additional_costs']['commission']
        }])
        
        csv = export_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="Preuzmi CSV",
            data=csv,
            file_name=f"analiza_{customer_name}.csv",
            mime="text/csv"
        )

# ---------- KALKULATOR CIJENA ----------
def show_price_calculator():
    """Interaktivni kalkulator za određivanje cijena"""
    st.title("🧮 Kalkulator dinamičkih cijena")
    st.markdown("**Izračunaj optimalnu cijenu za bilo koji proizvod**")
    
    # Dva stupca za unos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Podaci o proizvodu")
        cost = st.number_input("Nabavna cijena (KM)", 0.0, 100000.0, 100.0, 1.0)
        days = st.number_input("Dana u lageru", 0, 730, 45, 1)
        current_price = st.number_input("Trenutna cijena (KM)", 0.0, 100000.0, 150.0, 1.0)
        quantity = st.number_input("Količina", 1, 10000, 100, 1)
    
    with col2:
        st.subheader("👥 Podaci o kupcu")
        dso = st.slider("DSO kupca (dani)", 30, 180, 90, 1)
        supplier_terms = st.selectbox("Rok plaćanja dobavljačima", [30, 45, 60, 90], index=2)
        customer_type = st.selectbox("Tip kupca", ["Novi", "Redovan", "VIP", "Problematiční"])
    
    # GUMB ZA IZRAČUN
    if st.button("🎯 Izračunaj optimalnu cijenu", type="primary"):
        # Izračun
        rec_price = calculate_dynamic_price(cost, days, dso, supplier_terms)
        
        # Rezultati
        st.markdown("---")
        st.subheader("📊 Rezultati")
        
        # Metrike u gridu
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Preporučena cijena", f"{rec_price:.2f} KM")
        
        with col2:
            if current_price > 0:
                discount = ((current_price - rec_price) / current_price * 100)
                st.metric("Potreban popust", f"{discount:.1f}%")
        
        with col3:
            total_value = rec_price * quantity
            st.metric("Ukupna vrijednost", f"{total_value:,.0f} KM")
        
        with col4:
            profit_per_unit = rec_price - cost
            st.metric("Dobit/kom", f"{profit_per_unit:.2f} KM")
        
        # Preporuka
        st.markdown("---")
        st.subheader("💡 Preporuka")
        
        if rec_price < current_price:
            st.warning(f"**Smanji cijenu sa {current_price} na {rec_price} KM**")
            st.write(f"- Potrebno je {discount:.1f}% popusta")
            st.write(f"- Ukupna ušteda za kupca: {(current_price - rec_price) * quantity:.2f} KM")
        elif rec_price > current_price:
            st.success(f"**Povečaj cijenu sa {current_price} na {rec_price} KM**")
            st.write(f"- Možeš dodati {(rec_price - current_price):.2f} KM po komadu")
            st.write(f"- Dodatni prihod: {(rec_price - current_price) * quantity:.2f} KM")
        else:
            st.info("**Drži trenutnu cijenu - optimalna je!**")
    
    # Pomoć
    with st.expander("❓ Kako se računa?", expanded=False):
        st.markdown("""
        **Formula dinamičke cijene:**
        
        1. **Osnovni multiplikator** (po starosti):
           - ≤30 dana: ×1.50 (50% marža)
           - 31-90 dana: ×1.25 (25% marža)
           - 91-180 dana: ×1.10 (10% marža)
           - >180 dana: ×0.95 (5% gubitak)
        
        2. **Trošak finansiranja**:
           - Razlika = DSO kupca - Rok dobavljača
           - Dnevna kamata = 8% / 365 dana
           - Finansiranje = Osnovna cijena × Dnevna kamata × Razlika
        
        3. **Trošak skladištenja**:
           - Mjeseci = Dana / 30
           - Skladištenje = Nabavna × 0.5% × Mjeseci
        
        **Konačna cijena = Osnovna - Finansiranje - Skladištenje**
        """)

def show_settings():
    """Stranica sa podešavanjima"""
    st.title("⚙️ Podešavanja sistema")
    
    st.subheader("Finansijski parametri")
    col1, col2 = st.columns(2)
    
    with col1:
        global SUPPLIER_TERMS, ANNUAL_INTEREST
        SUPPLIER_TERMS = st.number_input("Rok plaćanja dobavljačima (dani)", 
                                        30, 120, 60)
        ANNUAL_INTEREST = st.number_input("Godišnja kamatna stopa (%)", 
                                        1.0, 20.0, 8.0) / 100
    
    with col2:
        global MONTHLY_STORAGE, COMMISSION_RATE, LOGISTICS_RATE
        MONTHLY_STORAGE = st.number_input("Mjesečni trošak skladištenja (%)", 
                                         0.1, 5.0, 0.5) / 100
        COMMISSION_RATE = st.number_input("Provizija prodavača (%)", 
                                         0.0, 10.0, 3.0) / 100
        LOGISTICS_RATE = st.number_input("Trošak logistike (%)", 
                                         0.0, 5.0, 1.5) / 100
    
    st.success("✅ Podešavanja su sačuvana za ovu sesiju")
    
    st.subheader("O sistemu")
    st.info("""
    **Dinamičke Cijene PRO** v1.1
    
    Funkcionalnosti:
    1. 📦 Analiza zaliha i dinamičko određivanje cijena
    2. 👥 Analiza profitabilnosti po kupcu (NOVO!)
    3. 💰 Uračunavanje svih skrivenih troškova
    4. 📊 Izvještaji i preporuke
    
    Kontakt: tvoj@email.com
    """)

# ---------- GLAVNI MENI ----------
def main():
    # Sidebar navigacija
    st.sidebar.title("🧭 Navigacija")
    
    page = st.sidebar.radio(
        "Odaberi stranicu:",
        ["📊 Dashboard", "🧮 Kalkulator cijena", "👥 Analiza kupaca", "⚙️ Podešavanja"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Podrška:**
    • F1: Dashboard - analiza zaliha
    • F2: Analiza kupaca - profitabilnost
    • F3: Podešavanja - parametri sistema
    """)
    
    # Prikaz odabrane stranice
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🧮 Kalkulator cijena":
        show_price_calculator() 
    elif page == "👥 Analiza kupaca":
        show_customer_analytics()
    elif page == "⚙️ Podešavanja":
        show_settings()

# ---------- POKRETANJE ----------
if __name__ == "__main__":
    main()