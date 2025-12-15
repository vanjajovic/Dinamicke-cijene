# app.py - REORGANIZOVANA VERZIJA SA 3 GLAVNE KARTICE
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional

# ---------- KONFIGURACIJA ----------
st.set_page_config(
    page_title="Biznis Analitika - Skladište, Cash Flow & Prodaja",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- DATA KLASE ----------
@dataclass
class Product:
    """Klasa za proizvod"""
    id: int
    name: str
    category: str
    cost_price: float
    selling_price: float
    quantity: int
    min_stock: int
    days_in_stock: int
    last_purchase: datetime
    supplier: str
    
    def get_status(self):
        """Vraća status zaliha"""
        if self.days_in_stock > 180:
            return ("🚨 Kritično", "danger")
        elif self.days_in_stock > 90:
            return ("⚠️ Visoko", "warning")
        elif self.quantity <= self.min_stock:
            return ("📉 Nisko", "warning")
        else:
            return ("✅ Normalno", "success")
    
    def get_value(self):
        return self.cost_price * self.quantity
    
    def get_recommendation(self):
        if self.days_in_stock > 180:
            return f"HITNA PRODAJA - Popust 15-20%"
        elif self.days_in_stock > 90:
            return f"SNIŽENJE - Promocija 10-15%"
        elif self.quantity <= self.min_stock:
            return f"NARUČITI - {self.min_stock * 2 - self.quantity} kom"
        else:
            return f"ODRŽAVATI - Trenutno stanje OK"

@dataclass
class PaymentTerm:
    """Klasa za rokove plaćanja"""
    customer: str
    amount: float
    due_date: datetime
    days_overdue: int
    status: str

@dataclass
class SalesActivity:
    """Klasa za prodajne aktivnosti"""
    salesperson: str
    client: str
    activity_type: str
    date: datetime
    notes: str
    follow_up: datetime

@dataclass 
class CashFlowItem:
    """Klasa za cash flow stavke"""
    date: datetime
    type: str  # 'in' ili 'out'
    category: str
    amount: float
    description: str

# ---------- INICIJALIZACIJA SESIJE ----------
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "skladiste"
if 'current_subtab' not in st.session_state:
    st.session_state.current_subtab = "stanje"

# ---------- PODACI ZA DEMO ----------
def load_warehouse_data():
    """Učitava demo podatke za skladište"""
    return [
        Product(1, "Skeletni sistem PRO-200", "Skele", 850.00, 1275.00, 15, 5, 25, 
                datetime.now() - timedelta(days=25), "Čeličar d.o.o."),
        Product(2, "Podloga za skele 1x1m", "Skele", 45.00, 67.50, 120, 50, 180,
                datetime.now() - timedelta(days=180), "Čeličar d.o.o."),
        Product(3, "Šperploča oplatna 2.44x1.22m", "Oplata", 65.00, 97.50, 40, 20, 60,
                datetime.now() - timedelta(days=60), "Drvopromet"),
        Product(4, "Oplatni gredič 5x10cm", "Oplata", 4.80, 7.20, 200, 100, 90,
                datetime.now() - timedelta(days=90), "Drvopromet"),
        Product(5, "Ograda protivpadska 2m", "Sigurnost", 72.00, 108.00, 60, 30, 120,
                datetime.now() - timedelta(days=120), "Sigurnost Plus"),
        Product(6, "Mreža zaštitna zelena", "Sigurnost", 18.50, 27.75, 150, 75, 30,
                datetime.now() - timedelta(days=30), "Sigurnost Plus"),
        Product(7, "Torba alata čelična", "Pribor", 89.00, 133.50, 30, 10, 45,
                datetime.now() - timedelta(days=45), "Alat&Oprema"),
        Product(8, "Podizač za materijal 500kg", "Transport", 2200.00, 3300.00, 5, 2, 90,
                datetime.now() - timedelta(days=90), "Mašine d.o.o."),
        Product(9, "Podupirači čelični 3m", "Oplata", 28.50, 42.75, 80, 40, 45,
                datetime.now() - timedelta(days=45), "Čeličar d.o.o."),
        Product(10, "Kuke sigurnosne", "Skele", 8.20, 12.30, 300, 150, 15,
                datetime.now() - timedelta(days=15), "Sigurnost Plus"),
    ]

def load_cashflow_data():
    """Učitava demo podatke za cash flow"""
    today = datetime.now()
    return [
        PaymentTerm("Gradevinar d.o.o.", 12500.00, today - timedelta(days=15), 0, "na vrijeme"),
        PaymentTerm("Izgradnja Plus", 8700.00, today - timedelta(days=30), 0, "na vrijeme"),
        PaymentTerm("Kamen d.o.o.", 15600.00, today - timedelta(days=45), 15, "kasni"),
        PaymentTerm("Betonski sistemi", 9200.00, today + timedelta(days=15), -15, "uskoro"),
        PaymentTerm("Zidar-majstor", 4300.00, today - timedelta(days=60), 30, "kasni"),
        PaymentTerm("Građevinski materijal", 21000.00, today + timedelta(days=30), -30, "buduće"),
    ]

def load_sales_activities():
    """Učitava demo podatke za prodajne aktivnosti"""
    today = datetime.now()
    return [
        SalesActivity("Marko M.", "Gradevinar d.o.o.", "Ponuda", 
                     today - timedelta(days=2), "Ponuda za skelete PRO-200", 
                     today + timedelta(days=7)),
        SalesActivity("Ana A.", "Izgradnja Plus", "Sastanak", 
                     today - timedelta(days=1), "Dogovor o cijenama oplata", 
                     today + timedelta(days=14)),
        SalesActivity("Ivan I.", "Kamen d.o.o.", "Telefonski razgovor", 
                     today, "Podsjetnik za naplatu", 
                     today + timedelta(days=3)),
        SalesActivity("Marko M.", "Betonski sistemi", "Ponuda", 
                     today, "Ponuda za podizač", 
                     today + timedelta(days=10)),
        SalesActivity("Ana A.", "Zidar-majstor", "Email", 
                     today - timedelta(days=3), "Poslana faktura", 
                     today + timedelta(days=5)),
    ]

# ---------- GLAVNI MENI ----------
def show_main_menu():
    """Prikazuje glavni meni sa 3 kartice"""
    st.markdown("""
        <style>
        .main-menu {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            height: 50px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📦 **SKLADIŠTE**", 
                    type="primary" if st.session_state.current_tab == "skladiste" else "secondary",
                    help="Stanje zaliha, preporuke i kalkulator cijena"):
            st.session_state.current_tab = "skladiste"
            st.session_state.current_subtab = "stanje"
            st.rerun()
    
    with col2:
        if st.button("💰 **CASH FLOW**", 
                    type="primary" if st.session_state.current_tab == "cashflow" else "secondary",
                    help="Rokovi plaćanja, plan nabavki i preporuke"):
            st.session_state.current_tab = "cashflow"
            st.session_state.current_subtab = "rokovi"
            st.rerun()
    
    with col3:
        if st.button("📈 **PRODAJA**", 
                    type="primary" if st.session_state.current_tab == "prodaja" else "secondary",
                    help="Prodajne aktivnosti, ponude i analitika"):
            st.session_state.current_tab = "prodaja"
            st.session_state.current_subtab = "aktivnosti"
            st.rerun()

# ---------- PODMENI ----------
def show_submenu():
    """Prikazuje podmeni za trenutni tab"""
    
    if st.session_state.current_tab == "skladiste":
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Trenutno stanje", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "stanje" else "secondary"):
                st.session_state.current_subtab = "stanje"
                st.rerun()
        
        with col2:
            if st.button("🎯 Preporuke ulaz/izlaz", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "preporuke" else "secondary"):
                st.session_state.current_subtab = "preporuke"
                st.rerun()
        
        with col3:
            if st.button("🧮 Kalkulator cijena", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "kalkulator" else "secondary"):
                st.session_state.current_subtab = "kalkulator"
                st.rerun()
    
    elif st.session_state.current_tab == "cashflow":
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 Rokovi plaćanja", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "rokovi" else "secondary"):
                st.session_state.current_subtab = "rokovi"
                st.rerun()
        
        with col2:
            if st.button("📊 Plan nabavki", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "nabavke" else "secondary"):
                st.session_state.current_subtab = "nabavke"
                st.rerun()
        
        with col3:
            if st.button("🎯 Preporuke", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "cf_preporuke" else "secondary"):
                st.session_state.current_subtab = "cf_preporuke"
                st.rerun()
    
    elif st.session_state.current_tab == "prodaja":
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📋 Aktivnosti", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "aktivnosti" else "secondary"):
                st.session_state.current_subtab = "aktivnosti"
                st.rerun()
        
        with col2:
            if st.button("📝 Ponude", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "ponude" else "secondary"):
                st.session_state.current_subtab = "ponude"
                st.rerun()
        
        with col3:
            if st.button("👥 Analiza klijenata", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "klijenti" else "secondary"):
                st.session_state.current_subtab = "klijenti"
                st.rerun()
        
        with col4:
            if st.button("📊 Pregled prodaje", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_subtab == "pregled" else "secondary"):
                st.session_state.current_subtab = "pregled"
                st.rerun()

# ---------- SKLADIŠTE MODUL ----------
def show_warehouse():
    """Modul za skladište"""
    
    # Naslov
    st.title("📦 Skladište - Upravljanje zalihama")
    
    # Podmeni
    show_submenu()
    
    # Učitaj podatke
    products = load_warehouse_data()
    
    if st.session_state.current_subtab == "stanje":
        show_warehouse_status(products)
    elif st.session_state.current_subtab == "preporuke":
        show_warehouse_recommendations(products)
    elif st.session_state.current_subtab == "kalkulator":
        show_price_calculator()

def show_warehouse_status(products):
    """Prikazuje trenutno stanje skladišta"""
    
    st.subheader("📊 Trenutno stanje zaliha")
    
    # Sumarni pregled
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_value = sum(p.get_value() for p in products)
        st.metric("Ukupna vrijednost", f"{total_value:,.0f} KM")
    
    with col2:
        critical_items = len([p for p in products if p.days_in_stock > 180])
        st.metric("Kritična roba", critical_items, delta_color="inverse")
    
    with col3:
        low_stock = len([p for p in products if p.quantity <= p.min_stock])
        st.metric("Niske zalihe", low_stock, delta_color="inverse")
    
    with col4:
        total_items = sum(p.quantity for p in products)
        st.metric("Ukupno artikala", total_items)
    
    # Tabela sa stanjem
    st.markdown("---")
    st.subheader("📋 Detaljan pregled")
    
    data = []
    for p in products:
        status, color = p.get_status()
        data.append({
            "ID": p.id,
            "Proizvod": p.name,
            "Kategorija": p.category,
            "Nabavna": f"{p.cost_price:.2f} KM",
            "Prodajna": f"{p.selling_price:.2f} KM",
            "Količina": p.quantity,
            "Min. zaliha": p.min_stock,
            "Dana u lageru": p.days_in_stock,
            "Status": status,
            "Vrijednost": f"{p.get_value():,.0f} KM",
            "Dobavljač": p.supplier
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Grafikoni
    col1, col2 = st.columns(2)
    
    with col1:
        # Po kategoriji
        cat_data = {}
        for p in products:
            cat_data[p.category] = cat_data.get(p.category, 0) + p.get_value()
        
        fig1 = px.pie(values=list(cat_data.values()), names=list(cat_data.keys()),
                     title="Vrijednost po kategoriji")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Status zaliha
        status_counts = {"✅ Normalno": 0, "📉 Nisko": 0, "⚠️ Visoko": 0, "🚨 Kritično": 0}
        for p in products:
            status_counts[p.get_status()[0]] += 1
        
        fig2 = px.bar(x=list(status_counts.keys()), y=list(status_counts.values()),
                     title="Status zaliha (broj artikala)",
                     color=list(status_counts.keys()),
                     color_discrete_map={
                         "✅ Normalno": "green",
                         "📉 Nisko": "orange", 
                         "⚠️ Visoko": "yellow",
                         "🚨 Kritično": "red"
                     })
        st.plotly_chart(fig2, use_container_width=True)

def show_warehouse_recommendations(products):
    """Prikazuje preporuke za ulaz/izlaz iz skladišta"""
    
    st.subheader("🎯 Preporuke za upravljanje zalihama")
    
    # Filtri
    col1, col2 = st.columns(2)
    with col1:
        filter_status = st.selectbox("Filtriraj po statusu", 
                                   ["Sve", "🚨 Kritično", "⚠️ Visoko", "📉 Nisko", "✅ Normalno"])
    with col2:
        filter_category = st.selectbox("Filtriraj po kategoriji", 
                                     ["Sve"] + list(set(p.category for p in products)))
    
    # Filtriranje
    filtered = products
    if filter_status != "Sve":
        filtered = [p for p in filtered if p.get_status()[0] == filter_status]
    if filter_category != "Sve":
        filtered = [p for p in filtered if p.category == filter_category]
    
    # Preporuke
    st.markdown("### 📋 Lista preporuka")
    
    if not filtered:
        st.info("Nema preporuka za odabrane filtere.")
        return
    
    for p in filtered:
        status, color = p.get_status()
        rec = p.get_recommendation()
        
        with st.container():
            cols = st.columns([1, 3, 2, 2])
            with cols[0]:
                st.write(f"**{p.name}**")
            with cols[1]:
                st.write(f"Status: {status}")
            with cols[2]:
                st.write(f"Količina: {p.quantity} / Min: {p.min_stock}")
            with cols[3]:
                if "HITNA PRODAJA" in rec or "SNIŽENJE" in rec:
                    st.error(rec)
                elif "NARUČITI" in rec:
                    st.warning(rec)
                else:
                    st.success(rec)
            st.markdown("---")
    
    # Sumarne preporuke
    st.markdown("### 📈 Sumarni izvještaj")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        urgent_sales = [p for p in filtered if "HITNA PRODAJA" in p.get_recommendation()]
        urgent_value = sum(p.get_value() for p in urgent_sales)
        st.metric("Za hitnu prodaju", len(urgent_sales), f"{urgent_value:,.0f} KM")
    
    with col2:
        to_order = [p for p in filtered if "NARUČITI" in p.get_recommendation()]
        order_qty = sum(p.min_stock * 2 - p.quantity for p in to_order if p.quantity < p.min_stock)
        st.metric("Za naručiti", len(to_order), f"{order_qty} kom")
    
    with col3:
        promotions = [p for p in filtered if "SNIŽENJE" in p.get_recommendation()]
        promo_value = sum(p.get_value() for p in promotions)
        st.metric("Za promociju", len(promotions), f"{promo_value:,.0f} KM")
    
    # Akcije
    st.markdown("### 🚀 Preuzmi akcije")
    
    if st.button("📥 Generiši naloge za nabavku", type="primary"):
        # Generisanje naloga za naručivanje
        orders = []
        for p in to_order:
            order_qty = p.min_stock * 2 - p.quantity
            if order_qty > 0:
                orders.append({
                    'Proizvod': p.name,
                    'Dobavljač': p.supplier,
                    'Količina': order_qty,
                    'Ukupno': order_qty * p.cost_price
                })
        
        if orders:
            orders_df = pd.DataFrame(orders)
            csv = orders_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Preuzmi naloge za nabavku (CSV)",
                data=csv,
                file_name=f"nalozi_nabavka_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def show_price_calculator():
    """Kalkulator za određivanje cijena"""
    
    st.subheader("🧮 Kalkulator cijena")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Parametri proizvoda")
        cost_price = st.number_input("Nabavna cijena (KM)", 0.0, 100000.0, 100.0, 1.0)
        days_in_stock = st.number_input("Dana u lageru", 0, 730, 45, 1)
        category = st.selectbox("Kategorija", ["Skele", "Oplata", "Sigurnost", "Transport", "Pribor"])
        quantity = st.number_input("Količina u lageru", 1, 10000, 100, 1)
    
    with col2:
        st.markdown("### 👥 Tržišni parametri")
        dso = st.slider("Prosječan DSO kupaca (dani)", 30, 180, 90, 1)
        supplier_terms = st.slider("Rok plaćanja dobavljačima (dani)", 30, 120, 60, 1)
        demand_factor = st.slider("Potražnja na tržištu", 0.5, 2.0, 1.0, 0.1)
        competition_factor = st.slider("Konkurencija", 0.5, 2.0, 1.0, 0.1,
                                      help="Više = jača konkurencija = niže cijene")
    
    # Kalkulacija
    if st.button("🎯 Izračunaj optimalnu cijenu", type="primary"):
        # Osnovna kalkulacija
        if days_in_stock > 180:
            base_multiplier = 0.95  # Gubitak
        elif days_in_stock > 90:
            base_multiplier = 1.10  # Niska marža
        elif days_in_stock > 30:
            base_multiplier = 1.25  # Standardna marža
        else:
            base_multiplier = 1.50  # Visoka marža
        
        # Prilagodba za finansiranje
        cash_gap = max(dso - supplier_terms, 0)
        financing_cost = cost_price * (0.08 / 365) * cash_gap
        
        # Tržišne prilagodbe
        base_price = cost_price * base_multiplier
        market_adjusted = base_price * demand_factor / competition_factor
        
        # Konačna cijena
        final_price = max(market_adjusted - financing_cost, cost_price * 0.9)
        
        # Rezultati
        st.markdown("---")
        st.subheader("📊 Rezultati kalkulacije")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Optimalna cijena", f"{final_price:.2f} KM")
        
        with col2:
            margin = ((final_price - cost_price) / cost_price) * 100
            st.metric("Marža", f"{margin:.1f}%")
        
        with col3:
            total_value = final_price * quantity
            st.metric("Ukupna vrijednost", f"{total_value:,.0f} KM")
        
        with col4:
            if days_in_stock > 180:
                st.error("🚨 HITNA PRODAJA")
            elif days_in_stock > 90:
                st.warning("⚠️ PROMOVIŠI")
            else:
                st.success("✅ ODRŽAVAJ")
        
        # Detaljan izračun
        st.markdown("---")
        st.subheader("🔍 Detaljan izračun")
        
        calc_data = {
            'Komponenta': [
                'Nabavna cijena',
                'Osnovni multiplikator',
                'Finansiranje (kamatni trošak)',
                'Prilagodba potražnje',
                'Prilagodba konkurencije',
                '**Optimalna cijena**'
            ],
            'Vrijednost': [
                f"{cost_price:.2f} KM",
                f"×{base_multiplier:.2f}",
                f"-{financing_cost:.2f} KM",
                f"×{demand_factor:.1f}",
                f"÷{competition_factor:.1f}",
                f"**{final_price:.2f} KM**"
            ],
            'Obrazloženje': [
                'Stvarni trošak',
                f'{days_in_stock} dana u lageru',
                f'{cash_gap} dana razlike (DSO {dso} - Rok {supplier_terms})',
                'Visoka/niska potražnja',
                'Jača/slabija konkurencija',
                'Preporučena prodajna cijena'
            ]
        }
        
        calc_df = pd.DataFrame(calc_data)
        st.table(calc_df)
        
        # Preporuka
        st.markdown("---")
        st.subheader("💡 Preporuka")
        
        if days_in_stock > 180:
            st.error(f"**HITNO PRODAJ!** Predloži popust od {100-margin:.0f}% za brzu prodaju.")
        elif days_in_stock > 90:
            st.warning(f"**Vrijeme za promociju.** Razmotri popust 5-10% za ubrzanje prodaje.")
        else:
            st.success(f"**Možeš držati ovu cijenu.** Marža od {margin:.1f}% je dobra.")

# ---------- CASH FLOW MODUL ----------
def show_cash_flow():
    """Modul za cash flow"""
    
    st.title("💰 Cash Flow Management")
    
    # Podmeni
    show_submenu()
    
    # Učitaj podatke
    payments = load_cashflow_data()
    products = load_warehouse_data()
    
    if st.session_state.current_subtab == "rokovi":
        show_payment_terms(payments)
    elif st.session_state.current_subtab == "nabavke":
        show_purchase_planning(products, payments)
    elif st.session_state.current_subtab == "cf_preporuke":
        show_cashflow_recommendations(payments, products)

def show_payment_terms(payments):
    """Prikazuje rokove plaćanja"""
    
    st.subheader("📅 Rokovi plaćanja - Trenutno stanje")
    
    # Sumarni pregled
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_receivable = sum(p.amount for p in payments if p.days_overdue >= 0)
        st.metric("Naplate u tijeku", f"{total_receivable:,.0f} KM")
    
    with col2:
        overdue = sum(p.amount for p in payments if p.days_overdue > 0)
        st.metric("Kasne naplate", f"{overdue:,.0f} KM", delta_color="inverse")
    
    with col3:
        overdue_count = len([p for p in payments if p.days_overdue > 0])
        st.metric("Kasne fakture", overdue_count, delta_color="inverse")
    
    with col4:
        future_payments = sum(p.amount for p in payments if p.days_overdue < 0)
        st.metric("Buduće naplate", f"{future_payments:,.0f} KM")
    
    # Tabela plaćanja
    st.markdown("---")
    st.subheader("📋 Detaljan pregled plaćanja")
    
    data = []
    for p in payments:
        status_color = "🟢" if p.status == "na vrijeme" else "🟡" if p.status == "uskoro" else "🔴"
        data.append({
            "Klijent": p.customer,
            "Iznos": f"{p.amount:,.0f} KM",
            "Rok plaćanja": p.due_date.strftime("%d.%m.%Y."),
            "Dana do/poslije roka": f"{abs(p.days_overdue)}" + (" dana do" if p.days_overdue < 0 else " dana kasni"),
            "Status": f"{status_color} {p.status}",
            "Prioritet": "VISOK" if p.days_overdue > 30 else "SREDNJI" if p.days_overdue > 0 else "NIZAK"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Grafikoni
    col1, col2 = st.columns(2)
    
    with col1:
        # Status plaćanja
        status_summary = {}
        for p in payments:
            status_summary[p.status] = status_summary.get(p.status, 0) + p.amount
        
        fig1 = px.pie(values=list(status_summary.values()), names=list(status_summary.keys()),
                     title="Plaćanja po statusu (vrijednost)")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Vremenska linija
        timeline_data = []
        for p in payments:
            timeline_data.append({
                'Klijent': p.customer,
                'Datum': p.due_date,
                'Iznos': p.amount,
                'Status': p.status
            })
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            fig2 = px.scatter(timeline_df, x='Datum', y='Iznos', size='Iznos',
                            color='Status', hover_name='Klijent',
                            title="Vremenska linija plaćanja",
                            color_discrete_map={
                                'na vrijeme': 'green',
                                'uskoro': 'yellow',
                                'kasni': 'red'
                            })
            st.plotly_chart(fig2, use_container_width=True)

def show_purchase_planning(products, payments):
    """Planiranje nabavki prema dinamici prodaje"""
    
    st.subheader("📊 Planiranje nabavki")
    
    # Analiza prodaje
    st.markdown("### 📈 Analiza dinamike prodaje")
    
    # Simulacija prodajne historije
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Avg', 'Sep', 'Okt', 'Nov', 'Dec']
    categories = list(set(p.category for p in products))
    
    # Generisanje podataka
    np.random.seed(42)
    sales_data = {}
    
    for category in categories:
        base_sales = np.random.randint(50000, 200000)
        seasonal = [1.0, 0.8, 0.9, 1.1, 1.3, 1.5, 1.4, 1.2, 1.1, 1.0, 0.9, 0.8]  # Sezonalnost
        trend = [base_sales * seasonal[i] * (1 + 0.02 * i) for i in range(12)]
        sales_data[category] = trend
    
    # Prikaz trendova
    fig = go.Figure()
    for category in categories:
        fig.add_trace(go.Scatter(x=months, y=sales_data[category],
                                mode='lines+markers',
                                name=category))
    
    fig.update_layout(title="Mjesečna prodaja po kategorijama (historija)",
                     xaxis_title="Mjesec",
                     yaxis_title="Prodaja (KM)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Predikcija i plan nabavki
    st.markdown("---")
    st.subheader("🛒 Preporuke za nabavke")
    
    # Kalkulacija potreba
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Analiza zaliha vs prodaja")
        lead_time = st.slider("Vrijeme isporuke (dani)", 7, 60, 14, 1)
        safety_stock = st.slider("Sigurnosna zaliha (dani prodaje)", 7, 60, 30, 1)
    
    # Preporuke za nabavku
    recommendations = []
    
    for p in products:
        # Procijeni mjesečnu prodaju za kategoriju
        category_sales = sales_data.get(p.category, [10000] * 12)
        avg_monthly_sales = np.mean(category_sales)
        
        # Procijeni prodaju za ovaj proizvod (proporcionalno vrijednosti)
        category_products = [prod for prod in products if prod.category == p.category]
        total_category_value = sum(prod.get_value() for prod in category_products)
        if total_category_value > 0:
            product_share = p.get_value() / total_category_value
            estimated_monthly_sales_units = (avg_monthly_sales * product_share) / p.cost_price
        else:
            estimated_monthly_sales_units = 10
        
        # Izračunaj potrebe
        daily_sales = estimated_monthly_sales_units / 30
        days_of_stock = p.quantity / daily_sales if daily_sales > 0 else 999
        
        # Generiši preporuku
        if days_of_stock < lead_time + safety_stock:
            order_qty = max((lead_time + safety_stock) * daily_sales - p.quantity, 0)
            if order_qty > 0:
                recommendations.append({
                    'Proizvod': p.name,
                    'Trenutno': p.quantity,
                    'Potrebno': int(np.ceil(order_qty)),
                    'Rok nabavke': (datetime.now() + timedelta(days=lead_time)).strftime("%d.%m.%Y."),
                    'Iznos': order_qty * p.cost_price,
                    'Prioritet': 'VISOK' if days_of_stock < lead_time else 'SREDNJI'
                })
    
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)
        
        # Sumarno
        total_order_value = rec_df['Iznos'].sum()
        st.metric("Ukupna vrijednost predloženih nabavki", f"{total_order_value:,.0f} KM")
        
        # Export
        csv = rec_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Preuzmi plan nabavki (CSV)",
            data=csv,
            file_name=f"plan_nabavki_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("✅ Trenutno nema potrebe za nabavkama prema analizi.")

def show_cashflow_recommendations(payments, products):
    """Preporuke za poboljšanje cash flow-a"""
    
    st.subheader("🎯 Preporuke za optimizaciju cash flow-a")
    
    # Analiza stanja
    overdue = [p for p in payments if p.days_overdue > 0]
    slow_moving = [p for p in products if p.days_in_stock > 90]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Problematična područja")
        
        if overdue:
            st.error(f"**Kasne naplate: {len(overdue)} fakture**")
            for p in overdue[:3]:  # Prikaži samo 3
                st.write(f"• {p.customer}: {p.amount:,.0f} KM kasni {p.days_overdue} dana")
        else:
            st.success("✅ Nema kasnih naplata")
        
        if slow_moving:
            slow_value = sum(p.get_value() for p in slow_moving)
            st.warning(f"**Spora roba: {len(slow_moving)} artikala**")
            st.write(f"Ukupna vrijednost: {slow_value:,.0f} KM")
        else:
            st.success("✅ Nema spore robe")
    
    with col2:
        st.markdown("### 💰 Potencijal za poboljšanje")
        
        # Potencijal za brže naplate
        future_payments = [p for p in payments if p.days_overdue < -7]  # Više od 7 dana do roka
        if future_payments:
            potential = sum(p.amount for p in future_payments)
            st.info(f"**Rani popusti:** {len(future_payments)} faktura")
            st.write(f"Potencijal: {potential * 0.03:,.0f} KM (3% popusta)")
        
        # Potencijal za prodaju spore robe
        if slow_moving:
            st.info(f"**Prodaja spore robe:** {len(slow_moving)} artikala")
            st.write(f"Potencijal: {sum(p.get_value() for p in slow_moving) * 0.15:,.0f} KM (15% popusta)")
    
    # SPECIFIČNE PREPORUKE
    st.markdown("---")
    st.subheader("🚀 Specifične preporuke")
    
    tab1, tab2, tab3 = st.tabs(["📈 Povećanje priljeva", "📉 Smanjenje odljeva", "⚖️ Balans"])
    
    with tab1:
        st.markdown("### Strategije za povećanje priljeva")
        
        if overdue:
            st.write("**1. Intenziviraj naplatu:**")
            for p in overdue:
                if p.days_overdue > 30:
                    st.write(f"- {p.customer}: {p.amount:,.0f} KM → **PRAVNI ODSJEK**")
                elif p.days_overdue > 15:
                    st.write(f"- {p.customer}: {p.amount:,.0f} KM → **Telefonski poziv svaki dan**")
        
        if future_payments:
            st.write("**2. Ponudi popuste za brže plaćanje:**")
            for p in future_payments[:3]:
                discount = p.amount * 0.03
                st.write(f"- {p.customer}: 3% popusta ({discount:,.0f} KM) za plaćanje unutar 48h")
    
    with tab2:
        st.markdown("### Strategije za smanjenje odljeva")
        
        # Analiza nabavki
        suppliers = {}
        for p in products:
            suppliers[p.supplier] = suppliers.get(p.supplier, 0) + p.get_value()
        
        if suppliers:
            main_supplier = max(suppliers.items(), key=lambda x: x[1])
            st.write(f"**1. Pregovori sa glavnim dobavljačem:**")
            st.write(f"- {main_supplier[0]}: {main_supplier[1]:,.0f} KM vrijednosti")
            st.write(f"- Traži produženje roka sa 60 na 90 dana")
            
            st.write("**2. Optimizuj zalihe:**")
            excess_inventory = sum(p.get_value() for p in products if p.quantity > p.min_stock * 3)
            if excess_inventory > 0:
                st.write(f"- Smanji zalihe za {excess_inventory:,.0f} KM")
    
    with tab3:
        st.markdown("### Strategije za balans")
        
        # Cash flow projekcija
        st.write("**1. 30-dnevna cash flow projekcija:**")
        
        # Generisanje projekcije
        projection = []
        today = datetime.now()
        cash_position = 100000  # Početni cash
        
        for day in range(30):
            date = today + timedelta(days=day)
            
            # Inflows
            day_inflows = sum(p.amount for p in payments 
                            if p.due_date.date() == date.date())
            
            # Outflows (simulacija)
            day_outflows = 5000 if day % 7 == 0 else 2000  # Plaće svake subote, ostalo operativno
            
            cash_position += day_inflows - day_outflows
            projection.append({
                'Datum': date.strftime("%d.%m."),
                'Priljevi': day_inflows,
                'Odljevi': day_outflows,
                'Stanje': cash_position
            })
        
        proj_df = pd.DataFrame(projection)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=proj_df['Datum'], y=proj_df['Stanje'],
                                mode='lines+markers',
                                name='Cash stanje',
                                line=dict(color='green')))
        fig.update_layout(title="30-dnevna cash flow projekcija",
                         xaxis_title="Datum",
                         yaxis_title="Stanje (KM)")
        st.plotly_chart(fig, use_container_width=True)

# ---------- PRODAJA MODUL ----------
def show_sales():
    """Modul za prodaju"""
    
    st.title("📈 Prodaja - Analitika i Aktivnosti")
    
    # Podmeni
    show_submenu()
    
    # Učitaj podatke
    activities = load_sales_activities()
    products = load_warehouse_data()
    
    if st.session_state.current_subtab == "aktivnosti":
        show_sales_activities(activities)
    elif st.session_state.current_subtab == "ponude":
        show_quotes()
    elif st.session_state.current_subtab == "klijenti":
        show_client_analysis()
    elif st.session_state.current_subtab == "pregled":
        show_sales_overview()

def show_sales_activities(activities):
    """Prikazuje prodajne aktivnosti"""
    
    st.subheader("📋 Prodajne aktivnosti")
    
    # Forma za novu aktivnost
    with st.expander("➕ Dodaj novu aktivnost", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            salesperson = st.selectbox("Prodavač", ["Marko M.", "Ana A.", "Ivan I.", "Petar P."])
            client = st.text_input("Klijent")
            activity_type = st.selectbox("Tip aktivnosti", 
                                       ["Sastanak", "Telefonski razgovor", "Email", "Ponuda", "Pratnja"])
        
        with col2:
            activity_date = st.date_input("Datum", datetime.now())
            follow_up = st.date_input("Pratnja do", datetime.now() + timedelta(days=7))
            notes = st.text_area("Bilješke")
        
        if st.button("💾 Sačuvaj aktivnost", type="primary"):
            st.success("Aktivnost sačuvana!")
            # Ovdje bi se dodalo u bazu
    
    # Tabela aktivnosti
    st.markdown("---")
    st.subheader("📅 Lista aktivnosti")
    
    # Filteri
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_salesperson = st.selectbox("Filter po prodavaču", 
                                        ["Svi"] + list(set(a.salesperson for a in activities)))
    with col2:
        filter_type = st.selectbox("Filter po tipu", 
                                 ["Sve"] + list(set(a.activity_type for a in activities)))
    with col3:
        filter_status = st.selectbox("Filter po statusu", 
                                   ["Sve", "Aktivne", "Završene"])
    
    # Prikaz aktivnosti
    for activity in activities:
        if filter_salesperson != "Svi" and activity.salesperson != filter_salesperson:
            continue
        if filter_type != "Sve" and activity.type != filter_type:
            continue
        
        with st.container():
            cols = st.columns([1, 2, 2, 2])
            with cols[0]:
                st.write(f"**{activity.salesperson}**")
            with cols[1]:
                st.write(f"👤 {activity.client}")
            with cols[2]:
                st.write(f"📝 {activity.activity_type}")
                st.write(f"📅 {activity.date.strftime('%d.%m.%Y.')}")
            with cols[3]:
                days_to_follow = (activity.follow_up - datetime.now()).days
                if days_to_follow < 0:
                    st.error(f"⚠️ Kasni {abs(days_to_follow)} dana")
                elif days_to_follow <= 3:
                    st.warning(f"⏰ Pratnja za {days_to_follow} dana")
                else:
                    st.info(f"✅ Pratnja za {days_to_follow} dana")
                
                with st.expander("Detalji"):
                    st.write(activity.notes)
            st.markdown("---")
    
    # Nedeljni plan
    st.markdown("---")
    st.subheader("📅 Nedeljni plan aktivnosti")
    
    # Grupisanje po prodavaču
    salespeople = set(a.salesperson for a in activities)
    
    for sp in salespeople:
        sp_activities = [a for a in activities if a.salesperson == sp]
        sp_upcoming = [a for a in sp_activities if a.follow_up >= datetime.now()]
        
        with st.expander(f"📋 {sp} - {len(sp_upcoming)} aktivnosti", expanded=True):
            for activity in sp_upcoming:
                days = (activity.follow_up - datetime.now()).days
                st.write(f"- **{activity.client}**: {activity.activity_type} ({days} dana)")

def show_quotes():
    """Upravljanje ponudama"""
    
    st.subheader("📝 Upravljanje ponudama")
    
    # Demo ponude
    quotes = [
        {
            'id': 1,
            'client': 'Gradevinar d.o.o.',
            'value': 28500.00,
            'status': 'Odobrena',
            'date': datetime.now() - timedelta(days=5),
            'valid_until': datetime.now() + timedelta(days=25),
            'items': [
                {'product': 'Skeletni sistem PRO-200', 'qty': 10, 'price': 1200.00},
                {'product': 'Podloga za skele 1x1m', 'qty': 50, 'price': 60.00}
            ]
        },
        {
            'id': 2,
            'client': 'Izgradnja Plus',
            'value': 15600.00,
            'status': 'Na čekanju',
            'date': datetime.now() - timedelta(days=2),
            'valid_until': datetime.now() + timedelta(days=28),
            'items': [
                {'product': 'Šperploča oplatna', 'qty': 100, 'price': 85.00},
                {'product': 'Oplatni gredič', 'qty': 200, 'price': 6.50}
            ]
        },
        {
            'id': 3,
            'client': 'Betonski sistemi',
            'value': 42000.00,
            'status': 'Odbijena',
            'date': datetime.now() - timedelta(days=10),
            'valid_until': datetime.now() + timedelta(days=20),
            'items': [
                {'product': 'Podizač za materijal', 'qty': 2, 'price': 3200.00},
                {'product': 'Transportna oprema', 'qty': 5, 'price': 1500.00}
            ]
        }
    ]
    
    # Statistik
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_quotes = len(quotes)
        st.metric("Ukupno ponuda", total_quotes)
    
    with col2:
        approved = len([q for q in quotes if q['status'] == 'Odobrena'])
        st.metric("Odobrene", approved)
    
    with col3:
        pending = len([q for q in quotes if q['status'] == 'Na čekanju'])
        st.metric("Na čekanju", pending)
    
    with col4:
        total_value = sum(q['value'] for q in quotes if q['status'] in ['Odobrena', 'Na čekanju'])
        st.metric("Ukupna vrijednost", f"{total_value:,.0f} KM")
    
    # Tabela ponuda
    st.markdown("---")
    st.subheader("📋 Lista ponuda")
    
    for quote in quotes:
        with st.container():
            cols = st.columns([1, 2, 1, 1, 1])
            
            with cols[0]:
                st.write(f"**#{quote['id']}**")
            
            with cols[1]:
                st.write(f"**{quote['client']}**")
                st.write(f"Datum: {quote['date'].strftime('%d.%m.%Y.')}")
            
            with cols[2]:
                st.write(f"**{quote['value']:,.0f} KM**")
            
            with cols[3]:
                status_color = {
                    'Odobrena': '✅',
                    'Na čekanju': '🟡',
                    'Odbijena': '❌'
                }
                st.write(f"{status_color[quote['status']]} {quote['status']}")
            
            with cols[4]:
                days_valid = (quote['valid_until'] - datetime.now()).days
                st.write(f"Važi: {days_valid} dana")
            
            with st.expander("📦 Stavke ponude"):
                for item in quote['items']:
                    st.write(f"- {item['product']}: {item['qty']} × {item['price']} KM = {item['qty'] * item['price']:,.0f} KM")
            
            st.markdown("---")
    
    # Nova ponuda forma
    st.markdown("---")
    st.subheader("➕ Kreiraj novu ponudu")
    
    with st.form("new_quote"):
        col1, col2 = st.columns(2)
        
        with col1:
            client = st.text_input("Klijent")
            valid_days = st.number_input("Vrijedi (dana)", 7, 90, 30)
            discount = st.slider("Popust (%)", 0, 50, 5)
        
        with col2:
            contact_person = st.text_input("Kontakt osoba")
            email = st.text_input("Email")
            phone = st.text_input("Telefon")
        
        # Dodavanje stavki
        st.markdown("### 🛒 Stavke ponude")
        
        items = []
        for i in range(3):  # 3 stavke za početak
            col1, col2, col3 = st.columns(3)
            with col1:
                product = st.selectbox(f"Proizvod {i+1}", 
                                     [p.name for p in load_warehouse_data()],
                                     key=f"product_{i}")
            with col2:
                qty = st.number_input(f"Količina {i+1}", 1, 1000, 1, key=f"qty_{i}")
            with col3:
                price = st.number_input(f"Cijena {i+1}", 0.0, 100000.0, 100.0, key=f"price_{i}")
            
            if product and qty > 0:
                items.append({'product': product, 'qty': qty, 'price': price})
        
        submitted = st.form_submit_button("📄 Generiši ponudu")
        
        if submitted and client:
            total = sum(item['qty'] * item['price'] for item in items)
            total_with_discount = total * (1 - discount/100)
            
            st.success(f"✅ Ponuda generisana! Ukupno: {total_with_discount:,.0f} KM (popust {discount}%)")
            
            # Download ponude kao CSV
            quote_data = pd.DataFrame({
                'Klijent': [client],
                'Ukupno': [total],
                'Popust': [f"{discount}%"],
                'Za platiti': [total_with_discount],
                'Vrijedi do': [(datetime.now() + timedelta(days=valid_days)).strftime("%d.%m.%Y.")]
            })
            
            csv = quote_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Preuzmi ponudu (CSV)",
                data=csv,
                file_name=f"ponuda_{client}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def show_client_analysis():
    """Analiza klijenata i profitabilnosti"""
    
    st.subheader("👥 Analiza profitabilnosti po klijentu")
    
    # Demo podaci o klijentima
    clients = [
        {
            'name': 'Gradevinar d.o.o.',
            'total_sales': 285000,
            'profit_margin': 32.5,
            'avg_dso': 45,
            'payment_history': 95,
            'category': 'A',
            'last_order': datetime.now() - timedelta(days=15)
        },
        {
            'name': 'Izgradnja Plus',
            'total_sales': 156000,
            'profit_margin': 28.7,
            'avg_dso': 60,
            'payment_history': 85,
            'category': 'B',
            'last_order': datetime.now() - timedelta(days=30)
        },
        {
            'name': 'Kamen d.o.o.',
            'total_sales': 89000,
            'profit_margin': 25.2,
            'avg_dso': 90,
            'payment_history': 70,
            'category': 'C',
            'last_order': datetime.now() - timedelta(days=60)
        },
        {
            'name': 'Betonski sistemi',
            'total_sales': 420000,
            'profit_margin': 35.1,
            'avg_dso': 30,
            'payment_history': 98,
            'category': 'A',
            'last_order': datetime.now() - timedelta(days=5)
        }
    ]
    
    # KPI-ovi
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = sum(c['total_sales'] for c in clients)
        st.metric("Ukupna prodaja", f"{total_sales:,.0f} KM")
    
    with col2:
        avg_margin = np.mean([c['profit_margin'] for c in clients])
        st.metric("Prosječna marža", f"{avg_margin:.1f}%")
    
    with col3:
        avg_dso = np.mean([c['avg_dso'] for c in clients])
        st.metric("Prosječan DSO", f"{avg_dso:.0f} dana")
    
    with col4:
        category_a = len([c for c in clients if c['category'] == 'A'])
        st.metric("A kategorija", category_a)
    
    # Matrica klijenata
    st.markdown("---")
    st.subheader("📊 Matrica klijenata (Profitabilnost vs Rizik)")
    
    # Kreiranje scatter plot-a
    client_df = pd.DataFrame(clients)
    
    fig = px.scatter(client_df, x='avg_dso', y='profit_margin',
                    size='total_sales', color='category',
                    hover_name='name',
                    title="Klijenti po profitabilnosti i riziku",
                    labels={
                        'avg_dso': 'Prosječan DSO (dani)',
                        'profit_margin': 'Profit marža (%)',
                        'category': 'Kategorija'
                    })
    
    # Dodaj kvadrante
    fig.add_hline(y=30, line_dash="dash", line_color="gray")
    fig.add_vline(x=60, line_dash="dash", line_color="gray")
    
    # Anotacije kvadranata
    fig.add_annotation(x=30, y=35, text="ZVIJEZDE", showarrow=False, font=dict(size=12, color="green"))
    fig.add_annotation(x=30, y=25, text="PRIPITOMLJIVE", showarrow=False, font=dict(size=12, color="orange"))
    fig.add_annotation(x=90, y=35, text="RIZIČNE", showarrow=False, font=dict(size=12, color="red"))
    fig.add_annotation(x=90, y=25, text="PROBLEMATIČNE", showarrow=False, font=dict(size=12, color="red"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detaljna analiza po klijentu
    st.markdown("---")
    st.subheader("📋 Detaljna analiza klijenata")
    
    for client in clients:
        with st.expander(f"🔍 {client['name']} - Kategorija {client['category']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Ukupna prodaja", f"{client['total_sales']:,.0f} KM")
                st.metric("Profit marža", f"{client['profit_margin']:.1f}%")
            
            with col2:
                st.metric("Prosječan DSO", f"{client['avg_dso']} dana")
                st.metric("Historija plaćanja", f"{client['payment_history']}%")
            
            # Preporuke
            st.markdown("### 🎯 Preporuke")
            
            if client['category'] == 'A':
                st.success("**VIP Klijent** - Nastavi odličan rad!")
                st.write("- Ponudi ekskluzivne uslove")
                st.write("- Redovni sastanci")
            elif client['category'] == 'B':
                st.warning("**Potencijal za poboljšanje**")
                st.write("- Rad na skraćenju DSO")
                st.write("- Pregled cjenovne politike")
            else:
                st.error("**Zahtijeva pažnju**")
                st.write("- Stroži uvjeti plaćanja")
                st.write("- Povećane cijene za pokriće rizika")
            
            # Akcije
            if st.button(f"📅 Zakazivanje sastanka - {client['name']}", key=f"meeting_{client['name']}"):
                st.info(f"Sastanak sa {client['name']} zakazan!")

def show_sales_overview():
    """Pregled prodaje po regiji, prodavaču, proizvodu i kanalu"""
    
    st.subheader("📊 Pregled prodaje")
    
    # Demo podaci
    regions = ['Sarajevo', 'Mostar', 'Banja Luka', 'Tuzla']
    salespeople = ['Marko M.', 'Ana A.', 'Ivan I.', 'Petar P.']
    products = ['Skele', 'Oplata', 'Sigurnost', 'Transport', 'Pribor']
    channels = ['Direktno', 'Distributer', 'Online', 'Preporuka']
    
    # Generisanje podataka
    np.random.seed(42)
    
    # Prodaja po regiji
    region_sales = {region: np.random.randint(50000, 200000) for region in regions}
    
    # Prodaja po prodavaču
    salesperson_sales = {sp: np.random.randint(30000, 150000) for sp in salespeople}
    
    # Prodaja po proizvodu
    product_sales = {product: np.random.randint(20000, 120000) for product in products}
    
    # Prodaja po kanalu
    channel_sales = {channel: np.random.randint(10000, 80000) for channel in channels}
    
    # Tabs za različite preglede
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Po regiji", "👥 Po prodavaču", "📦 Po proizvodu", "🛒 Po kanalu"])
    
    with tab1:
        st.markdown("### Prodaja po regiji")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(x=list(region_sales.keys()), y=list(region_sales.values()),
                        title="Prodaja po regiji",
                        labels={'x': 'Regija', 'y': 'Prodaja (KM)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            region_df = pd.DataFrame({
                'Regija': list(region_sales.keys()),
                'Prodaja': list(region_sales.values()),
                'Udio (%)': [f"{(v/sum(region_sales.values())*100):.1f}" 
                           for v in region_sales.values()]
            })
            st.dataframe(region_df, hide_index=True)
        
        # Regionalni insights
        best_region = max(region_sales.items(), key=lambda x: x[1])
        st.info(f"**Najbolja regija:** {best_region[0]} ({best_region[1]:,.0f} KM)")
    
    with tab2:
        st.markdown("### Prodaja po prodavaču")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.pie(values=list(salesperson_sales.values()), 
                        names=list(salesperson_sales.keys()),
                        title="Udio prodaje po prodavaču")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Performanse prodavača
            performance_data = []
            for sp in salespeople:
                sales = salesperson_sales[sp]
                margin = np.random.uniform(25, 40)
                dso = np.random.randint(30, 90)
                performance_data.append({
                    'Prodavač': sp,
                    'Prodaja': f"{sales:,.0f} KM",
                    'Marža': f"{margin:.1f}%",
                    'DSO': f"{dso} dana"
                })
            
            perf_df = pd.DataFrame(performance_data)
            st.dataframe(perf_df, hide_index=True)
        
        # Najbolji prodavač
        best_salesperson = max(salesperson_sales.items(), key=lambda x: x[1])
        st.success(f"**Najbolji prodavač:** {best_salesperson[0]} ({best_salesperson[1]:,.0f} KM)")
    
    with tab3:
        st.markdown("### Prodaja po proizvodu")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig = px.bar(x=list(product_sales.keys()), y=list(product_sales.values()),
                        title="Prodaja po proizvodu",
                        color=list(product_sales.keys()))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Profitabilnost proizvoda
            product_data = []
            for product in products:
                sales = product_sales[product]
                cost_ratio = np.random.uniform(0.6, 0.8)
                profit = sales * (1 - cost_ratio)
                product_data.append({
                    'Proizvod': product,
                    'Prodaja': f"{sales:,.0f} KM",
                    'Trošak': f"{(sales*cost_ratio):,.0f} KM",
                    'Profit': f"{profit:,.0f} KM",
                    'Marža': f"{(1-cost_ratio)*100:.1f}%"
                })
            
            product_df = pd.DataFrame(product_data)
            st.dataframe(product_df, hide_index=True)
        
        # Najprofitabilniji proizvod
        if product_data:
            best_product = max(product_data, key=lambda x: float(x['Marža'].replace('%', '')))
            st.info(f"**Najprofitabilniji:** {best_product['Proizvod']} (marža {best_product['Marža']})")
    
    with tab4:
        st.markdown("### Prodaja po kanalu")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.line(x=list(channel_sales.keys()), y=list(channel_sales.values()),
                         markers=True, title="Prodaja po kanalu",
                         labels={'x': 'Kanal', 'y': 'Prodaja (KM)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ROI po kanalu
            channel_roi = {}
            for channel in channels:
                sales = channel_sales[channel]
                cost = sales * np.random.uniform(0.1, 0.3)
                roi = (sales - cost) / cost * 100
                channel_roi[channel] = roi
            
            roi_df = pd.DataFrame({
                'Kanal': list(channel_roi.keys()),
                'ROI (%)': [f"{v:.1f}" for v in channel_roi.values()]
            })
            st.dataframe(roi_df, hide_index=True)
        
        # Najefikasniji kanal
        best_channel = max(channel_roi.items(), key=lambda x: x[1])
        st.success(f"**Najefikasniji kanal:** {best_channel[0]} (ROI {best_channel[1]:.1f}%)")
    
    # Export opcije
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export regije (CSV)"):
            df = pd.DataFrame({
                'Regija': list(region_sales.keys()),
                'Prodaja': list(region_sales.values())
            })
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Preuzmi",
                data=csv,
                file_name="prodaja_regije.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Export prodavači (CSV)"):
            df = pd.DataFrame({
                'Prodavač': list(salesperson_sales.keys()),
                'Prodaja': list(salesperson_sales.values())
            })
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Preuzmi",
                data=csv,
                file_name="prodaja_prodavaci.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📥 Export proizvodi (CSV)"):
            df = pd.DataFrame({
                'Proizvod': list(product_sales.keys()),
                'Prodaja': list(product_sales.values())
            })
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Preuzmi",
                data=csv,
                file_name="prodaja_proizvodi.csv",
                mime="text/csv"
            )

# ---------- GLAVNI PROGRAM ----------
def main():
    """Glavni program"""
    
    # Sakrij sidebar
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Naslov
    st.markdown("<h1 style='text-align: center;'>📊 Biznis Analitika</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Skladište • Cash Flow • Prodaja</p>", 
                unsafe_allow_html=True)
    
    # Glavni meni
    show_main_menu()
    
    # Prikaz odabranog modula
    if st.session_state.current_tab == "skladiste":
        show_warehouse()
    elif st.session_state.current_tab == "cashflow":
        show_cash_flow()
    elif st.session_state.current_tab == "prodaja":
        show_sales()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("<p style='text-align: center; color: gray;'>Biznis Analitika</p>", 
                    unsafe_allow_html=True)

# ---------- POKRETANJE ----------
if __name__ == "__main__":
    main()