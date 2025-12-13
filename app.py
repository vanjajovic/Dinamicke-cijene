# app.py - KOMPLETNA VERZIJA SA 5 MODULA
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ---------- KONFIGURACIJA ----------
st.set_page_config(
    page_title="Dinamičke Cijene",
    page_icon="💰",
    layout="wide"
)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

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
            return "🚨 HITNO PRODAJ"
        elif self.days_in_stock > 90:
            return "⚠️ SNIŽI CIJENU"
        elif self.days_in_stock > 30:
            return "🟡 ODRŽI CIJENU"
        else:
            return "✅ POVEĆAJ CIJENU"
    
    def get_recommended_action(self):
        """Vraća preporuku za akciju"""
        if self.days_in_stock > 180:
            return f"Prodaj po {self.cost_price * 0.95:.2f} KM (5% gubitak)"
        elif self.days_in_stock > 90:
            return f"Popust 10-15% - prodaj po {self.selling_price * 0.85:.2f} KM"
        elif self.days_in_stock > 30:
            return f"Drži cijenu {self.selling_price:.2f} KM"
        else:
            return f"Povečaj za 5-10% - na {self.selling_price * 1.08:.2f} KM"

# ---------- POMOĆNE FUNKCIJE ----------
def load_sample_products():
    """Učitava primjer proizvoda za skele"""
    return [
        Product("Skeletni sistem PRO-200", 850.00, 1275.00, 25, 15, "Skele"),
        Product("Podloga za skele 1x1m", 45.00, 67.50, 180, 120, "Skele"),
        Product("Šperploča oplatna 2.44x1.22m", 65.00, 97.50, 60, 40, "Oplata"),
        Product("Oplatni gredič 5x10cm", 4.80, 7.20, 90, 200, "Oplata"),
        Product("Ograda protivpadska 2m", 72.00, 108.00, 120, 60, "Ograda"),
        Product("Mreža zaštitna zelena", 18.50, 27.75, 30, 150, "Sigurnost"),
        Product("Torba alata čelična", 89.00, 133.50, 45, 30, "Pribor"),
        Product("Podizač za materijal 500kg", 2200.00, 3300.00, 90, 5, "Transport"),
        Product("Podupirači čelični 3m", 28.50, 42.75, 45, 80, "Podupirači"),
        Product("Kuke sigurnosne", 8.20, 12.30, 15, 300, "Skele"),
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

# ---------- TOP NAVIGACIJA ----------
def show_top_navigation():
    """Prikazuje top navigaciju sa 5 kartica"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📊 DASHBOARD", use_container_width=True, 
                    type="primary" if st.session_state.current_page == 'dashboard' else "secondary"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    
    with col2:
        if st.button("👥 ANALIZA KUPCA", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'customer_analytics' else "secondary"):
            st.session_state.current_page = 'customer_analytics'
            st.rerun()
    
    with col3:
        if st.button("🧮 KALKULATOR", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'price_calculator' else "secondary"):
            st.session_state.current_page = 'price_calculator'
            st.rerun()
    
    with col4:
        if st.button("💰 CASH FLOW", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'cash_flow' else "secondary"):
            st.session_state.current_page = 'cash_flow'
            st.rerun()
    
    with col5:
        if st.button("📈 PRODAJNA ANALIZA", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'sales_analytics' else "secondary"):
            st.session_state.current_page = 'sales_analytics'
            st.rerun()
    
    st.markdown("---")

# ---------- DASHBOARD MODUL ----------
def show_dashboard():
    """Glavni dashboard sa TOP NAVIGACIJOM"""
    
    show_top_navigation()
    
    st.title("💰 Dinamičke cijene")
    st.markdown("**Sistem za analizu profitabilnosti i upravljanje gotovinskim tokom**")
    
    # DSO UNOS - sada na glavnoj strani
    col1, col2, col3 = st.columns(3)
    with col1:
        dso = st.slider("Prosječan DSO (dani)", 30, 180, 83, 
                       help="DSO = Days Sales Outstanding - Prosječan broj dana za naplatu")
    
    with col2:
        supplier_terms = st.slider("Rok plaćanja dobavljačima", 30, 120, 60)
    
    with col3:
        interest_rate = st.slider("Kamatna stopa (%)", 1.0, 20.0, 8.0, 0.1) / 100
    
    # Učitaj proizvode
    products = load_sample_products()
    
    # Prikaz proizvoda SA PREPORUKAMA
    st.subheader("📦 Analiza zaliha sa preporukama")
    
    data = []
    for p in products:
        rec_price = calculate_dynamic_price(p.cost_price, p.days_in_stock, dso, supplier_terms)
        current_margin = ((p.selling_price - p.cost_price) / p.cost_price * 100)
        recommended_margin = ((rec_price - p.cost_price) / p.cost_price * 100)
        
        data.append({
            "Proizvod": p.name,
            "Nabavna": p.cost_price,
            "Trenutna": p.selling_price,
            "Trenutna marža": f"{current_margin:.1f}%",
            "Preporučeno": round(rec_price, 2),
            "Preporučena marža": f"{recommended_margin:.1f}%",
            "Starost": p.days_in_stock,
            "Status": p.get_inventory_status(),
            "Preporuka": p.get_recommended_action(),
            "Količina": p.quantity,
            "Vrijednost": round(p.quantity * rec_price, 2)
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Sumarni pregled
    st.subheader("📈 Sumarni pregled")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        dead_stock = len([p for p in products if p.days_in_stock > 180])
        dead_value = sum([p.cost_price * p.quantity for p in products if p.days_in_stock > 180])
        st.metric("Mrtva roba", dead_stock, f"{dead_value:,.0f} KM")
    
    with col2:
        total_value = df["Vrijednost"].sum()
        st.metric("Ukupna vrijednost", f"{total_value:,.0f} KM")
    
    with col3:
        avg_discount = ((df["Trenutna"] - df["Preporučeno"]).mean() / df["Trenutna"].mean() * 100)
        st.metric("Prosječna promjena", f"{avg_discount:+.1f}%")
    
    with col4:
        avg_margin = ((df["Preporučeno"] - df["Nabavna"]).mean() / df["Nabavna"].mean() * 100)
        st.metric("Prosječna marža", f"{avg_margin:.1f}%")
    
    # DETALJNA PREPORUKA ZA SVAKI STATUS
    st.markdown("---")
    st.subheader("🎯 Detaljne preporuke")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 🚨 HITNO PRODAJ (>180 dana)")
        hitno_prodaj = [p for p in products if p.days_in_stock > 180]
        if hitno_prodaj:
            for p in hitno_prodaj:
                st.write(f"• **{p.name}**: {p.get_recommended_action()}")
        else:
            st.write("✓ Nema artikala u ovoj kategoriji")
    
    with col2:
        st.markdown("### ⚠️ SNIŽI CIJENU (91-180 dana)")
        snizi_cijenu = [p for p in products if 90 < p.days_in_stock <= 180]
        if snizi_cijenu:
            for p in snizi_cijenu:
                st.write(f"• **{p.name}**: {p.get_recommended_action()}")
        else:
            st.write("✓ Nema artikala u ovoj kategoriji")
    
    with col3:
        st.markdown("### 🟡 ODRŽI CIJENU (31-90 dana)")
        odrzi_cijenu = [p for p in products if 30 < p.days_in_stock <= 90]
        if odrzi_cijenu:
            for p in odrzi_cijenu:
                st.write(f"• **{p.name}**: {p.get_recommended_action()}")
        else:
            st.write("✓ Nema artikala u ovoj kategoriji")
    
    with col4:
        st.markdown("### ✅ POVEĆAJ CIJENU (<30 dana)")
        povecaj_cijenu = [p for p in products if p.days_in_stock <= 30]
        if povecaj_cijenu:
            for p in povecaj_cijenu:
                st.write(f"• **{p.name}**: {p.get_recommended_action()}")
        else:
            st.write("✓ Nema artikala u ovoj kategoriji")

# ---------- ANALIZA KUPCA MODUL ----------
def show_customer_analytics():
    """NOVA KORIGOVANA ANALIZA PROFITABILNOSTI PO KUPKU"""
    
    show_top_navigation()
    
    st.title("👥 Analiza profitabilnosti po kupcu")
    st.markdown("**Izračun stvarne marže i dobiti uz sve troškove**")
    
    # FORMA ZA UNOS PODATAKA
    with st.form("customer_analysis_form"):
        st.subheader("📋 Osnovni podaci o kupcu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Naziv kupca", "Gradevinar DOO")
            period = st.selectbox("Period analize", ["Mjesečno", "Kvartalno", "Godišnje"])
            total_sales = st.number_input("Ukupna prodaja (KM)", 0.0, 10000000.0, 50000.0, 100.0)
            total_cost = st.number_input("Trošak nabavke (KM)", 0.0, 10000000.0, 35000.0, 100.0)
        
        with col2:
            supplier_terms = st.number_input("Rok plaćanja dobavljačima (dani)", 0, 365, 60)
            customer_dso = st.number_input("Prosječno trajanje naplate (dani)", 0, 365, 90)
            commission_rate = st.number_input("Provizija prodavača (%)", 0.0, 100.0, 3.0, 0.1) / 100
            interest_rate = st.number_input("Kamatna stopa finansiranja (%)", 0.0, 50.0, 8.0, 0.1) / 100
        
        st.subheader("📊 Dodatni troškovi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            logistics_cost = st.number_input("Logistika (KM)", 0.0, 100000.0, 500.0, 50.0)
            storage_cost = st.number_input("Skladištenje (KM)", 0.0, 100000.0, 300.0, 50.0)
        
        with col2:
            admin_cost = st.number_input("Administracija (KM)", 0.0, 100000.0, 200.0, 50.0)
            risk_cost = st.number_input("Trošak rizika (KM)", 0.0, 100000.0, 100.0, 50.0)
        
        with col3:
            other_costs = st.number_input("Ostali troškovi (KM)", 0.0, 100000.0, 150.0, 50.0)
            payment_history = st.slider("Historija plaćanja (%)", 50, 100, 85) / 100
        
        submitted = st.form_submit_button("🎯 IZRAČUNAJ STVARNU PROFITABILNOST")
    
    if submitted:
        # IZRAČUN SVIH TROŠKOVA
        st.markdown("---")
        st.subheader(f"📊 Analiza za: **{customer_name}**")
        
        # 1. Osnovna dobit
        paper_profit = total_sales - total_cost
        
        # 2. Trošak finansiranja
        cash_gap_days = max(customer_dso - supplier_terms, 0)
        financing_cost = total_sales * (interest_rate / 365) * cash_gap_days
        
        # 3. Provizija prodavača
        commission_cost = total_sales * commission_rate
        
        # 4. Ukupni dodatni troškovi
        additional_costs = {
            'financing': financing_cost,
            'commission': commission_cost,
            'logistics': logistics_cost,
            'storage': storage_cost,
            'administration': admin_cost,
            'risk': risk_cost,
            'other': other_costs
        }
        
        total_additional_costs = sum(additional_costs.values())
        
        # 5. Stvarna dobit i marža
        real_profit = paper_profit - total_additional_costs
        profit_margin = (real_profit / total_sales) * 100 if total_sales > 0 else 0
        
        # 6. Status profitabilnosti
        if profit_margin > 15:
            status = "🟢 IZVRSNO"
        elif profit_margin > 8:
            status = "🟡 DOBRO"
        elif profit_margin > 0:
            status = "🟠 SLABO"
        else:
            status = "🔴 GUBITAK"
        
        # PRIKAZ REZULTATA
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ukupna prodaja", f"{total_sales:,.0f} KM")
        
        with col2:
            st.metric("'Papirna' dobit", f"{paper_profit:,.0f} KM", 
                     f"{(paper_profit/total_sales*100):.1f}%")
        
        with col3:
            st.metric("Stvarna dobit", f"{real_profit:,.0f} KM", 
                     delta=f"{profit_margin:.1f}%", delta_color="normal" if profit_margin > 0 else "inverse")
        
        with col4:
            st.metric("Status", status)
        
        # DETALJNI TROŠKOVI
        st.markdown("---")
        st.subheader("🔍 Detaljna analiza troškova")
        
        costs_df = pd.DataFrame({
            'Trošak': list(additional_costs.keys()),
            'Iznos (KM)': list(additional_costs.values()),
            'Procenat od prodaje': [(cost/total_sales*100) if total_sales > 0 else 0 for cost in additional_costs.values()]
        })
        
        # Formatiranje
        costs_df['Iznos (KM)'] = costs_df['Iznos (KM)'].round(2)
        costs_df['Procenat od prodaje'] = costs_df['Procenat od prodaje'].round(1)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(costs_df, use_container_width=True)
        
        with col2:
            # Pie chart
            fig = px.pie(costs_df, values='Iznos (KM)', names='Trošak', 
                        title="Struktura dodatnih troškova")
            st.plotly_chart(fig, use_container_width=True)
        
        # PREPORUKE
        st.markdown("---")
        st.subheader("🎯 Preporuke za poboljšanje")
        
        recommendations = []
        
        if cash_gap_days > 30:
            savings = total_sales * (interest_rate / 365) * 30
            recommendations.append(f"• **Skrati rok naplate sa {customer_dso} na {supplier_terms + 15} dana**")
            recommendations.append(f"  Ušteda: {savings:.0f} KM ({savings/total_sales*100:.1f}% prodaje)")
        
        if profit_margin < 5:
            needed_increase = (0.05 - profit_margin/100) * total_sales
            recommendations.append(f"• **Povećaj cijene za ovog kupca za {needed_increase/total_sales*100:.1f}%**")
            recommendations.append(f"  Dodatna dobit: {needed_increase:.0f} KM")
        
        if additional_costs['financing'] > real_profit * 0.3:
            recommendations.append("• **Razmotri prelazak na predračune ili avanse**")
            recommendations.append("  Smanji potrebu za finansiranjem")
        
        if not recommendations:
            recommendations.append("• Ovaj kupac je profitabilan - nastavi ovako!")
            recommendations.append("• Razmotri dodatni popust za veće količine")
        
        for rec in recommendations:
            st.write(rec)
        
        # ŠTA AKO ANALIZA
        st.markdown("---")
        st.subheader("📈 Šta ako analiza")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_dso = st.number_input("Novi rok naplate (dani)", 30, 180, 75, key="new_dso")
            if new_dso != customer_dso:
                new_financing = total_sales * (interest_rate / 365) * max(new_dso - supplier_terms, 0)
                savings = financing_cost - new_financing
                st.metric("Ušteda na finansiranju", f"{savings:.0f} KM")
        
        with col2:
            discount = st.slider("Popust za brže plaćanje (%)", 0, 20, 3, key="discount")
            if discount > 0:
                faster_payment_dso = customer_dso * 0.7  # 30% brže plaćanje
                new_financing = total_sales * (1 - discount/100) * (interest_rate / 365) * max(faster_payment_dso - supplier_terms, 0)
                discount_cost = total_sales * (discount/100)
                net_effect = (financing_cost - new_financing) - discount_cost
                st.metric(f"Neto efekat {discount}% popusta", f"{net_effect:.0f} KM")
        
        with col3:
            better_terms = st.checkbox("Bolji uvjeti sa dobavljačem (+15 dana)")
            if better_terms:
                new_financing = total_sales * (interest_rate / 365) * max(customer_dso - (supplier_terms + 15), 0)
                savings = financing_cost - new_financing
                st.metric("Ušteda sa boljim uvjetima", f"{savings:.0f} KM")
        
        # EXPORT
        st.markdown("---")
        if st.button("📥 Export analize u CSV"):
            export_df = pd.DataFrame([{
                'Kupac': customer_name,
                'Period': period,
                'Prodaja_KM': total_sales,
                'Nabavka_KM': total_cost,
                'Papirna_Dobit_KM': paper_profit,
                'Stvarna_Dobit_KM': real_profit,
                'Profit_Margin_%': profit_margin,
                'Status': status,
                'DSO_Kupca': customer_dso,
                'Rok_Dobavljaca': supplier_terms,
                'Finansiranje_KM': additional_costs['financing'],
                'Provizija_KM': additional_costs['commission']
            }])
            
            csv = export_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Preuzmi CSV",
                data=csv,
                file_name=f"analiza_{customer_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("🔽 Popunite formu iznad i kliknite 'IZRAČUNAJ' da biste vidjeli analizu")

# ---------- KALKULATOR MODUL ----------
def show_price_calculator():
    """Interaktivni kalkulator za određivanje cijena"""
    
    show_top_navigation()
    
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
        interest_rate = st.slider("Kamatna stopa (%)", 1.0, 20.0, 8.0, 0.1) / 100
    
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
            profit_margin = (profit_per_unit / cost) * 100
            st.metric("Marža", f"{profit_margin:.1f}%")
        
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
        
        # Detaljan breakdown
        st.markdown("---")
        st.subheader("🔍 Detaljan izračun")
        
        # Break down the calculation
        if days > 180:
            base = cost * 0.95
            multiplier_text = "×0.95 (>180 dana)"
        elif days > 90:
            base = cost * 1.10
            multiplier_text = "×1.10 (91-180 dana)"
        elif days > 30:
            base = cost * 1.25
            multiplier_text = "×1.25 (31-90 dana)"
        else:
            base = cost * 1.50
            multiplier_text = "×1.50 (≤30 dana)"
        
        cash_gap = max(dso - supplier_terms, 0)
        financing = base * (interest_rate / 365) * cash_gap
        
        calculation_data = {
            'Komponenta': ['Nabavna cijena', 'Osnovni multiplikator', 'Finansiranje', 'Preporučena cijena'],
            'Vrijednost (KM)': [cost, base - cost, -financing, rec_price],
            'Obrazloženje': [
                f"{cost} KM",
                multiplier_text,
                f"{cash_gap} dana × {interest_rate*100:.1f}% godišnje",
                f"Konačna preporuka"
            ]
        }
        
        calc_df = pd.DataFrame(calculation_data)
        st.dataframe(calc_df, use_container_width=True)
    
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
           - Dnevna kamata = Kamatna stopa / 365 dana
           - Finansiranje = Osnovna cijena × Dnevna kamata × Razlika
        
        **Konačna cijena = Osnovna - Finansiranje**
        
        *Cijena neće biti niža od 90% nabavne.*
        """)

# ---------- CASH FLOW MODUL ----------
def show_cash_flow():
    """Cash Flow Management Module"""
    
    show_top_navigation()
    
    st.title("💰 Cash Flow Management")
    st.markdown("**Predikcija gotovinskog toka i upravljanje likvidnošću**")
    
    with st.expander("⚙️ Osnovni parametri", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            monthly_sales = st.number_input("Mjesečna prodaja (KM)", 0, 10000000, 100000, 1000)
            growth_rate = st.slider("Očekivani rast prodaje (%)", -20, 100, 10, 1) / 100
        
        with col2:
            dso = st.number_input("Prosječni DSO (dani)", 0, 365, 90, 5)
            dpo = st.number_input("Rok dobavljača (dani)", 0, 365, 60, 5)
            dio = st.number_input("Obrt zaliha (dani)", 30, 365, 120, 10)
        
        with col3:
            cogs_percentage = st.slider("Trošak robe prodaje (%)", 50, 90, 70, 1) / 100
            fixed_costs = st.number_input("Fiksni troškovi mjesečno (KM)", 0, 500000, 20000, 1000)
            starting_cash = st.number_input("Početni gotovina (KM)", 0, 1000000, 50000, 5000)
    
    # Sezonalni faktori
    st.subheader("📅 Sezonalnost prodaje")
    
    seasonal_factors = {}
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 
              'Jul', 'Avg', 'Sep', 'Okt', 'Nov', 'Dec']
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        for i, month in enumerate(months):
            if month in ['Jan', 'Feb', 'Dec']:
                default_val = 0.7  # Zima
            elif month in ['Jun', 'Jul', 'Avg']:
                default_val = 1.3  # Ljeto
            else:
                default_val = 1.0  # Proljeće/jesen
            
            seasonal_factors[month] = st.slider(
                f"{month}", 0.3, 2.0, default_val, 0.1,
                key=f"seasonal_{month}"
            )
    
    
    if st.button("📈 Generiši cash flow projekciju", type="primary"):
        # Generisanje cash flow projekcije
        cash_flow_data = []
        current_cash = starting_cash
        
        for i, month in enumerate(months):
            # Izračun prodaje sa sezonalnošću i rastom
            month_index = i + 1
            growth_factor = (1 + growth_rate) ** (month_index / 12)
            seasonal_factor = seasonal_factors[month]
            
            monthly_sales_adj = monthly_sales * growth_factor * seasonal_factor
            
            # Priljevi (kada stižu novci)
            cash_in_month = month_index + int(dso / 30)
            if cash_in_month <= 12:
                cash_in = monthly_sales_adj
            else:
                cash_in = 0
            
            # Odljevi (kada se plaća)
            cogs = monthly_sales_adj * cogs_percentage
            cash_out_month = month_index + int(dpo / 30)
            if cash_out_month <= 12:
                cash_out = cogs + fixed_costs
            else:
                cash_out = fixed_costs  # Plaćaš samo fiksne troškove
            
            # Mjesečni cash flow
            monthly_cash_flow = cash_in - cash_out
            current_cash += monthly_cash_flow
            
            cash_flow_data.append({
                'Mjesec': month,
                'Prodaja': round(monthly_sales_adj, 0),
                'Priljevi': round(cash_in, 0),
                'Odljevi': round(cash_out, 0),
                'Neto Cash Flow': round(monthly_cash_flow, 0),
                'Ukupni Cash': round(current_cash, 0)
            })
        
        df = pd.DataFrame(cash_flow_data)
        
        # Metrike
        st.subheader("📊 Cash Flow Metrike")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            min_cash = df['Ukupni Cash'].min()
            min_month = df.loc[df['Ukupni Cash'].idxmin(), 'Mjesec']
            st.metric("Najniži cash", f"{min_cash:,.0f} KM", 
                     f"{min_month}", delta_color="inverse" if min_cash < 0 else "normal")
        
        with col2:
            avg_cash_flow = df['Neto Cash Flow'].mean()
            st.metric("Prosječni mjesečni CF", f"{avg_cash_flow:,.0f} KM")
        
        with col3:
            ccc = dio + dso - dpo
            st.metric("Cash Conversion Cycle", f"{ccc:.0f} dana")
        
        with col4:
            if min_cash < 0:
                financing_needed = abs(min_cash)
                st.metric("Potrebno finansiranje", f"{financing_needed:,.0f} KM")
            else:
                st.metric("Minimum Buffer", f"{min_cash:,.0f} KM")
        
        # Grafikoni
        st.subheader("📈 Vizuelizacija")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.line(df, x='Mjesec', y='Ukupni Cash',
                          title="Predikcija gotovine (12 mjeseci)",
                          markers=True)
            fig1.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(df, x='Mjesec', y=['Priljevi', 'Odljevi'],
                         title="Priljevi vs Odljevi",
                         barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Detaljna tabela
        st.subheader("📋 Detaljna projekcija")
        st.dataframe(df.style.format({
            'Prodaja': '{:,.0f}',
            'Priljevi': '{:,.0f}',
            'Odljevi': '{:,.0f}',
            'Neto Cash Flow': '{:,.0f}',
            'Ukupni Cash': '{:,.0f}'
        }), use_container_width=True)
        
        # Preporuke
        st.subheader("🎯 Preporuke za poboljšanje cash flow-a")
        
        recommendations = []
        
        if ccc > 120:
            recommendations.append(f"• **CCC predug: {ccc} dana**")
            recommendations.append(f"  - Smanji zalihe: {dio} → {dio*0.8:.0f} dana")
            recommendations.append(f"  - Skrati naplate: {dso} → {dso*0.8:.0f} dana")
        
        if min_cash < 0:
            recommendations.append(f"• **Negativan cash u {min_month}**")
            recommendations.append(f"  - Osiguraj kreditnu liniju: {abs(min_cash):,.0f} KM")
            recommendations.append(f"  - Ponudi popust za brže plaćanje u {min_month}")
        
        if dso - dpo > 60:
            recommendations.append(f"• **Veliki cash gap: {dso - dpo} dana**")
            recommendations.append(f"  - Pregovaraj sa dobavljačima: {dpo} → {dpo + 15} dana")
            recommendations.append(f"  - Uvedi avanse od kupaca")
        
        if not recommendations:
            recommendations.append("• Cash flow je dobar - nastavi ovako!")
        
        for rec in recommendations:
            st.write(rec)
        
        # Šta ako scenariji
        st.subheader("📊 Šta ako analiza")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("DSO -15 dana", key="dso_button"):
                new_dso = max(dso - 15, 30)
                savings = monthly_sales * (ANNUAL_INTEREST / 365) * 15 * 12
                st.info(f"**Ušteda na finansiranju:**\n{savings:,.0f} KM godišnje")
        
        with col2:
            if st.button("+20% prodaja", key="sales_button"):
                additional_cash_needed = monthly_sales * 0.2 * cogs_percentage * (dio / 30)
                st.info(f"**Dodatni kapital potreban:**\n{additional_cash_needed:,.0f} KM")
        
        with col3:
            if st.button("Inventory -20%", key="inventory_button"):
                freed_capital = monthly_sales * cogs_percentage * 0.2 * (dio / 30)
                st.info(f"**Oslobođeni kapital:**\n{freed_capital:,.0f} KM")
    
    else:
        st.info("🔽 Podesi parametre i klikni 'Generiši cash flow projekciju'")

# ---------- PRODAJNA ANALIZA MODUL ----------
def show_sales_analytics():
    """Sales Analytics Module"""
    
    show_top_navigation()
    
    st.title("📈 Prodajna analiza")
    st.markdown("**Analiza po prodavaču, regiji i kanalu**")
    
    # Sample data - u praksi bi se ovo učitavalo iz baze
    sales_data = {
        'Prodavači': [
            {'Ime': 'Marko Marković', 'Prodaja': 580_000, 'Marža': 35.2, 
             'Broj narudžbi': 42, 'Prosječna narudžba': 13_810, 'DSO': 68,
             'Regija': 'Sarajevo', 'Kanali': ['Direktno', 'Distributer']},
            {'Ime': 'Ana Anić', 'Prodaja': 420_000, 'Marža': 38.1,
             'Broj narudžbi': 65, 'Prosječna narudžba': 6_462, 'DSO': 52,
             'Regija': 'Mostar', 'Kanali': ['Direktno']},
            {'Ime': 'Ivan Ivanić', 'Prodaja': 250_000, 'Marža': 28.7,
             'Broj narudžbi': 31, 'Prosječna narudžba': 8_065, 'DSO': 95,
             'Regija': 'Banja Luka', 'Kanali': ['Distributer', 'Online']},
        ],
        'Regije': [
            {'Regija': 'Sarajevo', 'Prodaja': 850_000, 'Rast': 22.5,
             'Prosječna marža': 34.2, 'Broj kupaca': 28, 'Top proizvod': 'Skele'},
            {'Regija': 'Mostar', 'Prodaja': 620_000, 'Rast': 15.3,
             'Prosječna marža': 36.1, 'Broj kupaca': 19, 'Top proizvod': 'Oplata'},
            {'Regija': 'Banja Luka', 'Prodaja': 580_000, 'Rast': 31.2,
             'Prosječna marža': 32.7, 'Broj kupaca': 22, 'Top proizvod': 'Sigurnost'},
            {'Regija': 'Tuzla', 'Prodaja': 400_000, 'Rast': 8.7,
             'Prosječna marža': 29.5, 'Broj kupaca': 18, 'Top proizvod': 'Pribor'},
        ],
        'Kanali': [
            {'Kanal': 'Direktna prodaja', 'Prodaja': 850_000, 'Marža': 34.5,
             'Trošak prodaje %': 12.3, 'Broj kupaca': 45},
            {'Kanal': 'Distributeri', 'Prodaja': 600_000, 'Marža': 28.7,
             'Trošak prodaje %': 8.5, 'Broj kupaca': 32},
            {'Kanal': 'Iznajmljivanje', 'Prodaja': 300_000, 'Marža': 52.1,
             'Trošak prodaje %': 15.8, 'Broj kupaca': 28},
            {'Kanal': 'Online', 'Prodaja': 150_000, 'Marža': 41.3,
             'Trošak prodaje %': 10.2, 'Broj kupaca': 65},
        ]
    }
    
    # TOP METRIKE
    st.subheader("📊 Ukupni pregled")
    
    total_sales = sum([p['Prodaja'] for p in sales_data['Prodavači']])
    avg_margin = np.mean([p['Marža'] for p in sales_data['Prodavači']])
    total_customers = sum([r['Broj kupaca'] for r in sales_data['Regije']])
    avg_dso = np.mean([p['DSO'] for p in sales_data['Prodavači']])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ukupna prodaja", f"{total_sales:,.0f} KM")
    
    with col2:
        st.metric("Prosječna marža", f"{avg_margin:.1f}%")
    
    with col3:
        st.metric("Ukupno kupaca", total_customers)
    
    with col4:
        st.metric("Prosječni DSO", f"{avg_dso:.0f} dana")
    
    # TABS ZA RAZLIČITE ANALIZE
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Po prodavaču", 
        "🗺️ Po regiji", 
        "🛒 Po kanalu", 
        "📈 Trendovi"
    ])
    
    with tab1:
        st.subheader("Analiza po prodavaču")
        
        # Sortiranje opcije
        sort_option = st.selectbox(
            "Sortiraj po:",
            ["Prodaja (visoka → niska)", "Marža (visoka → niska)", "DSO (niska → visoka)"],
            key="sort_sales_reps"
        )
        
        # Sortiranje podataka
        if sort_option == "Prodaja (visoka → niska)":
            sorted_reps = sorted(sales_data['Prodavači'], key=lambda x: x['Prodaja'], reverse=True)
        elif sort_option == "Marža (visoka → niska)":
            sorted_reps = sorted(sales_data['Prodavači'], key=lambda x: x['Marža'], reverse=True)
        else:
            sorted_reps = sorted(sales_data['Prodavači'], key=lambda x: x['DSO'])
        
        # Prikaz tabela
        rep_df = pd.DataFrame(sorted_reps)
        st.dataframe(rep_df.style.format({
            'Prodaja': '{:,.0f}',
            'Marža': '{:.1f}%',
            'Prosječna narudžba': '{:,.0f}',
            'DSO': '{:.0f}'
        }), use_container_width=True)
        
        # Grafikoni
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(rep_df, x='Ime', y='Prodaja',
                         title="Prodaja po prodavaču",
                         color='Marža',
                         color_continuous_scale='viridis')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.scatter(rep_df, x='DSO', y='Marža', size='Prodaja',
                             hover_name='Ime', title="DSO vs Marža",
                             labels={'DSO': 'Dana za naplatu', 'Marža': 'Marža (%)'})
            st.plotly_chart(fig2, use_container_width=True)
        
        # Preporuke za prodavače
        st.subheader("🎯 Preporuke za prodavače")
        
        best_margin = max(sales_data['Prodavači'], key=lambda x: x['Marža'])
        worst_dso = max(sales_data['Prodavači'], key=lambda x: x['DSO'])
        
        st.write(f"• **Najbolja marža**: {best_margin['Ime']} ({best_margin['Marža']}%)")
        st.write(f"• **Najduže naplate**: {worst_dso['Ime']} ({worst_dso['DSO']} dana)")
        
        if worst_dso['DSO'] > 90:
            st.warning(f"**{worst_dso['Ime']} treba trening o naplati!**")
    
    with tab2:
        st.subheader("Analiza po regiji")
        
        region_df = pd.DataFrame(sales_data['Regije'])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(region_df.style.format({
                'Prodaja': '{:,.0f}',
                'Rast': '{:.1f}%',
                'Prosječna marža': '{:.1f}%',
                'Broj kupaca': '{:.0f}'
            }), use_container_width=True)
        
        with col2:
            fig = px.pie(region_df, values='Prodaja', names='Regija',
                        title="Udio regija u prodaji")
            st.plotly_chart(fig, use_container_width=True)
        
        # Regionalni insights
        st.subheader("🎯 Regionalne strategije")
        
        fastest_growth = max(sales_data['Regije'], key=lambda x: x['Rast'])
        lowest_margin = min(sales_data['Regije'], key=lambda x: x['Prosječna marža'])
        
        st.write(f"• **Najbrži rast**: {fastest_growth['Regija']} (+{fastest_growth['Rast']}%)")
        st.write(f"• **Najniža marža**: {lowest_margin['Regija']} ({lowest_margin['Prosječna marža']}%)")
        
        # Preporuke po regiji
        for region in sales_data['Regije']:
            if region['Rast'] > 20:
                st.success(f"**{region['Regija']}**: Razmotri dodavanje novog prodavača")
            elif region['Prosječna marža'] < 30:
                st.warning(f"**{region['Regija']}**: Pregledaj cjenovnu politiku")
    
    with tab3:
        st.subheader("Analiza po kanalu")
        
        channel_df = pd.DataFrame(sales_data['Kanali'])
        channel_df['Efikasnost'] = (channel_df['Marža'] / channel_df['Trošak prodaje %']).round(2)
        
        st.dataframe(channel_df.style.format({
            'Prodaja': '{:,.0f}',
            'Marža': '{:.1f}%',
            'Trošak prodaje %': '{:.1f}%',
            'Efikasnost': '{:.2f}',
            'Broj kupaca': '{:.0f}'
        }), use_container_width=True)
        
        # Grafikoni kanala
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(channel_df, x='Kanal', y=['Prodaja', 'Marža'],
                         title="Prodaja i marža po kanalu",
                         barmode='group')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(channel_df, x='Kanal', y='Efikasnost',
                         title="Efikasnost kanala (Marža/Trošak)")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Preporuke za kanale
        st.subheader("🎯 Strategija kanala")
        
        most_efficient = channel_df.loc[channel_df['Efikasnost'].idxmax()]
        highest_margin = channel_df.loc[channel_df['Marža'].idxmax()]
        
        st.write(f"• **Najefikasniji kanal**: {most_efficient['Kanal']}")
        st.write(f"• **Najbolja marža**: {highest_margin['Kanal']} ({highest_margin['Marža']}%)")
        
        if highest_margin['Kanal'] == "Iznajmljivanje":
            st.success("**✅ Iznajmljivanje je zlatni rudnik!** Razmotri ekspanziju ovog kanala")
    
    with tab4:
        st.subheader("Trend analiza")
        
        # Simulacija trendova
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 
                 'Jul', 'Avg', 'Sep', 'Okt', 'Nov', 'Dec']
        
        # Generisanje trend podataka
        np.random.seed(42)
        base_sales = 80_000
        trend_sales = [base_sales * (1 + 0.1 * i + np.random.normal(0, 0.05)) for i in range(12)]
        trend_margin = [32 + 0.3 * i + np.random.normal(0, 1) for i in range(12)]
        
        trend_df = pd.DataFrame({
            'Mjesec': months,
            'Prodaja (000 KM)': [x/1000 for x in trend_sales],
            'Marža (%)': trend_margin
        })
        
        # Trend chart
        fig = px.line(trend_df, x='Mjesec', y=['Prodaja (000 KM)', 'Marža (%)'],
                     title="Mjesečni trendovi", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend insights
        peak_month = trend_df.loc[trend_df['Prodaja (000 KM)'].idxmax()]
        lowest_margin_month = trend_df.loc[trend_df['Marža (%)'].idxmin()]
        
        st.subheader("📈 Trend insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Najbolji mjesec", peak_month['Mjesec'], 
                     f"{peak_month['Prodaja (000 KM)']*1000:,.0f} KM")
        
        with col2:
            st.metric("Najniža marža", lowest_margin_month['Mjesec'],
                     f"{lowest_margin_month['Marža (%)']:.1f}%")
        
        # Sezonske preporuke
        st.subheader("🎯 Sezonske preporuke")
        
        winter_months = ['Dec', 'Jan', 'Feb']
        summer_months = ['Jun', 'Jul', 'Avg']
        
        winter_avg = trend_df[trend_df['Mjesec'].isin(winter_months)]['Prodaja (000 KM)'].mean()
        summer_avg = trend_df[trend_df['Mjesec'].isin(summer_months)]['Prodaja (000 KM)'].mean()
        
        if summer_avg > winter_avg * 1.5:
            st.info("**Sezonalnost skela:** Jaka sezonalnost - planiraj zalhe za ljeto unaprijed")
        
        # # Akcije po sezonama (KOMENTARISANO - aktiviraj kasnije)
# st.write("• **Zima (Dec-Feb)**: Fokus na održavanje i popravke")
# st.write("• **Proljeće (Mar-May)**: Priprema za sezonu, promotivne akcije")
# st.write("• **Ljeto (Jun-Aug)**: Maksimiziraj prodaju, minimalni popusti")
# st.write("• **Jesen (Sep-Nov)**: Naplata, priprema za narednu godinu")

# ---------- GLAVNI MENI ----------
def main():
    # Hide sidebar completely
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Prikaz odabrane stranice
    if st.session_state.current_page == 'dashboard':
        show_dashboard()
    elif st.session_state.current_page == 'customer_analytics':
        show_customer_analytics()
    elif st.session_state.current_page == 'price_calculator':
        show_price_calculator()
    elif st.session_state.current_page == 'cash_flow':
        show_cash_flow()
    elif st.session_state.current_page == 'sales_analytics':
        show_sales_analytics()
    else:
        show_dashboard()

# ---------- POKRETANJE ----------
if __name__ == "__main__":
    main()