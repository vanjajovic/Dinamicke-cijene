import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistem Cijena", layout="wide")

st.title("💰 Sistem Dinamičkih Cijena")
st.markdown("Određivanje optimalnih cijena na osnovu starosti zaliha i finansijskih troškova")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Podešavanja")
    
    dso = st.slider(
        "Prosečan rok naplate (DSO) - dani",
        min_value=30,
        max_value=180,
        value=83,
        help="Koliko dana u proseku kupac plaća račun"
    )
    
    rokovi_dobavljac = st.slider(
        "Rok plaćanja dobavljačima - dani",
        min_value=30,
        max_value=120,
        value=60
    )
    
    st.markdown("---")
    st.info("""
    **Vodič:**
    - 0-30 dana: Drži punu cijenu
    - 31-90 dana: Ponudi mali popust
    - 91-180 dana: Ponudi veliki popust
    - 180+ dana: Prodaj odmah
    """)

# ---------- PODACI ----------
@st.cache_data
def ucitaj_podatke():
    podaci = [
        {"Proizvod": "Cement 25kg", "Nabavna": 10.50, "Trenutna": 15.75, "Dana": 45, "Količina": 100, "Kategorija": "Građevina"},
        {"Proizvod": "Šperploča 18mm", "Nabavna": 8.20, "Trenutna": 13.50, "Dana": 120, "Količina": 50, "Kategorija": "Građevina"},
        {"Proizvod": "Gvozdeni šip 6mm", "Nabavna": 15.00, "Trenutna": 22.50, "Dana": 210, "Količina": 20, "Kategorija": "Metal"},
        {"Proizvod": "Boja bijela 10L", "Nabavna": 18.00, "Trenutna": 27.00, "Dana": 15, "Količina": 30, "Kategorija": "Bojenje"},
        {"Proizvod": "PVC cijev 50mm", "Nabavna": 3.50, "Trenutna": 6.00, "Dana": 250, "Količina": 150, "Kategorija": "Hidraulika"},
    ]
    return pd.DataFrame(podaci)

df = ucitaj_podatke()

# ---------- LOGIKA ----------
def izracunaj_preporucenu_cijenu(nabavna, dani, dso, rokovi_dobavljac):
    # Osnovni množitelj prema starosti
    if dani > 180:
        osnovna = nabavna * 0.95  # Ispod nabavne - hitna prodaja
    elif dani > 90:
        osnovna = nabavna * 1.10  # Samo 10% marže
    elif dani > 30:
        osnovna = nabavna * 1.25  # 25% marže
    else:
        osnovna = nabavna * 1.50  # 50% marže (normalno)
    
    # Prilagodba za finansijske troškove
    cash_gap = max(dso - rokovi_dobavljac, 0)
    troskovi_finansiranja = osnovna * (0.08 / 365) * cash_gap
    
    # Konačna preporučena cijena
    konacna = osnovna - troskovi_finansiranja
    
    # Zaokruži
    return round(konacna, 2)

# Primeni funkciju na sve proizvode
df['Preporučeno'] = df.apply(
    lambda x: izracunaj_preporucenu_cijenu(x['Nabavna'], x['Dana'], dso, rokovi_dobavljac), 
    axis=1
)

# Izračunaj popust
df['Popust %'] = ((df['Trenutna'] - df['Preporučeno']) / df['Trenutna'] * 100).round(1)

# Odredi status
def odredi_status(dani):
    if dani > 180:
        return "🚨 HITNO"
    elif dani > 90:
        return "⚠️ POPUST"
    elif dani > 30:
        return "🟡 PAŽNJA"
    else:
        return "✅ NORMALNO"

df['Status'] = df['Dana'].apply(odredi_status)

# ---------- PRIKAZ ----------
st.subheader("📊 Analiza proizvoda")
st.dataframe(df)

# Brze statistike
col1, col2, col3 = st.columns(3)
with col1:
    ukupno_hitno = len(df[df['Dana'] > 180])
    st.metric("Hitna prodaja", ukupno_hitno)
with col2:
    prosek_popusta = df['Popust %'].mean()
    st.metric("Prosečan popust", f"{prosek_popusta:.1f}%")
with col3:
    ukupna_vrednost = (df['Preporučeno'] * df['Količina']).sum()
    st.metric("Ukupna vrednost", f"{ukupna_vrednost:.0f} KM")

# Preporuke za akciju
st.subheader("🎯 Preporuke za prodaju")

if ukupno_hitno > 0:
    st.error("🚨 **HITNA AKCIJA POTREBNA:**")
    hitni_proizvodi = df[df['Dana'] > 180]
    for _, proizvod in hitni_proizvodi.iterrows():
        st.write(f"• **{proizvod['Proizvod']}**: {proizvod['Dana']} dana → Prodaj po **{proizvod['Preporučeno']} KM**")

st.success("✅ **PROIZVODI U REDU:**")
normalni_proizvodi = df[df['Dana'] <= 30]
for _, proizvod in normalni_proizvodi.iterrows():
    st.write(f"• **{proizvod['Proizvod']}**: Drži cijenu od **{proizvod['Preporučeno']} KM**")

# Footer
st.markdown("---")
st.caption("Sistem za dinamičko određivanje cijena | MVP verzija")