import streamlit as st
import pandas as pd
from datetime import datetime

# Ρύθμιση της σελίδας για κινητά
st.set_page_config(page_title="Μισθοδοσία", page_icon="📱", layout="centered")

# Προσομοίωση βάσης δεδομένων στη μνήμη
if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Ημερομηνία", "Κατάσταση", "Είσοδος", "Έξοδος", "Διάλειμμα Από", "Διάλειμμα Έως", "Έξτρα Μικτά"])

# Συναρτήση που μετατρέπει τα λεπτά σε μορφή Ώρα:Λεπτά (π.χ. 450 -> 07:30)
def minutes_to_string(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

# --- 1. ΠΑΝΩ ΜΠΛΕ ΜΠΑΡΑ ---
st.markdown(
    f"""
    <div style="background-color: #1e73be; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">Δευτέρα 1 Ιουν 2026</h2>
        <p style="color: #d1e8ff; margin: 5px 0 0 0; font-weight: bold; word-spacing: 20px;">ΜΙΑ ΜΕΡΑ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ΠΟΛΛΕΣ ΜΕΡΕΣ</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 2. ΠΕΡΙΟΧΗ ΚΑΤΑΧΩΡΗΣΗΣ ---
st.subheader("Επεξεργασία Ημέρας")

date_val = st.date_input("Επιλογή Ημέρας", datetime.now(), format="DD/MM/YYYY")

# Ώρες Από / Μέχρι με Μπάρα Κύλισης (Slider) - Σέρνεις το δάχτυλο για να αλλάξει η ώρα!
st.write("🕒 **Ωράριο Εργασίας (Σύρετε για να αλλάξετε την ώρα):**")

# Από 05:00 (300 λεπτά) έως 23:00 (1380 λεπτά), με βήμα 15 λεπτά
min_in = st.slider("Από (Είσοδος)", min_value=300, max_value=1380, value=450, step=15, format="")
st.info(f"Ώρα Εισόδου: **{minutes_to_string(min_in)}**")

min_out = st.slider("Μέχρι (Έξοδος)", min_value=300, max_value=1380, value=1100, step=15, format="")
st.info(f"Ώρα Εξόδου: **{minutes_to_string(min_out)}**")

# ΕΠΙΛΟΓΗ ΚΑΤΑΣΤΑΣΗΣ
status = st.selectbox("Περισσότερα", ["Κανονικό Ωράριο", "Αργία (Εργασία)", "Ρεπό", "Άδεια", "Ασθένεια"])

# --- 3. ΠΛΑΙΣΙΟ ΔΙΑΛΕΙΜΜΑΤΟΣ ---
st.markdown('<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 15px;">', unsafe_allow_html=True)
has_break = st.toggle("ΔΙΑΛΕΙΜΜΑ", value=True)

if has_break:
    min_b_in = st.slider("Διάλειμμα Από", min_value=300, max_value=1380, value=780, step=15, format="")
    st.caption(f"Από: **{minutes_to_string(min_b_in)}**")
    
    min_b_out = st.slider("Διάλειμμα Μέχρι", min_value=300, max_value=1380, value=810, step=15, format="")
    st.caption(f"Έως: **{minutes_to_string(min_b_out)}**")
else:
    min_b_in, min_b_out = 0, 0
st.markdown('</div>', unsafe_allow_html=True)

# Σταθερός βασικός μικτός μισθός
gross_salary = 1196.0
hourly_rate = gross_salary * 0.006  
day_rate = gross_salary / 25        

# --- 4. ΚΟΥΜΠΙ ΠΡΟΣΘΗΚΗΣ & ΥΠΟΛΟΓΙΣΜΟΙ ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("ΠΡΟΣΘΗΚΗ", use_container_width=True):
    try:
        extra_pay = 0.0
        
        if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]:
            total_hours = (min_out - min_in) / 60.0
            
            if has_break:
                break_hours = (min_b_out - min_b_in) / 60.0
                total_hours -= break_hours
                
            if total_hours <= 0:
                st.error("⚠️ Η ώρα εξόδου πρέπει να είναι μετά την ώρα εισόδου!")
            else:
                # Υπεργασίες & Υπερωρίες
                hypergasia = 0.0
                hyperoria = 0.0
                if total_hours > 8.0:
                    hypergasia = min(1.0, total_hours - 8.0)
                if total_hours > 9.0:
                    hyperoria = total_hours - 9.0
                    
                extra_pay = (hypergasia * hourly_rate * 1.20) + (hyperoria * hourly_rate * 1.40)
                
                if status == "Αργία (Εργασία)":
                    extra_pay += (day_rate * 0.75)
                    
        # Αποθήκευση
        new_row = pd.DataFrame([{
            "Ημερομηνία": date_val.strftime('%d/%m/%Y'),
            "Κατάσταση": status,
            "Είσοδος": minutes_to_string(min_in) if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"] else "-",
            "Έξοδος": minutes_to_string(min_out) if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"] else "-",
            "Διάλειμμα Από": minutes_to_string(min_b_in) if (has_break and status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]) else "-",
            "Διάλειμμα Έως": minutes_to_string(min_b_out) if (has_break and status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]) else "-",
            "Έξτρα Μικτά": round(extra_pay, 2)
        }])
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
        st.success(f"ΕΠΙΤΥΧΙΑ: Καταχωρήθηκε η ημέρα {date_val.strftime('%d/%m/%Y')}!")
    except Exception as e:
        st.error(f"⚠️ Παρουσιάστηκε σφάλμα: {str(e)}")

# --- 5. ΣΤΑΤΙΣΤΙΚΑ ΜΗΝΑ ---
if not st.session_state.db.empty:
    st.markdown("---")
    st.subheader("Στατιστικά Μήνα")
    
    input_bonus = st.number_input("Μπόνους Μήνα (€):", value=120.0, step=10.0)
    
    total_entries = len(st.session_state.db)
    working_days = len(st.session_state.db[st.session_state.db["Κατάσταση"].isin(["Κανονικό Ωράριο", "Αργία (Εργασία)"])])
    repot_days = len(st.session_state.db[st.session_state.db["Κατάσταση"] == "Ρεπό"])
    adeia_days = len(st.session_state.db[st.session_state.db["Κατάσταση"] == "Άδεια"])
    
    total_extra_gross = st.session_state.db["Έξτρα Μικτά"].sum()
    total_gross_all = gross_salary + input_bonus + total_extra_gross
    
    raw_ika = total_gross_all * 0.1337
    subsidy = 58.70
    actual_ika = max(0.0, raw_ika - subsidy)
    
    taxable_income = total_gross_all - actual_ika
    if taxable_income > 833:
        total_fmy = (taxable_income - 833) * 0.22
    else:
        total_fmy = 0.0
        
    final_net_salary = total_gross_all - actual_ika - total_fmy
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric(label="Εργάσιμες Ημέρες", value=f"{working_days} μέρες")
        st.metric(label="Άδειες", value=f"{adeia_days} μέρες")
    with col_stat2:
        st.metric(label="Ρεπό", value=f"{repot_days} μέρες")
        st.metric(label="Σύνολο Καταχωρήσεων", value=f"{total_entries} γραμμές")

    st.metric(label="💰 ΤΕΛΙΚΟΣ ΚΑΘΑΡΟΣ ΜΙΣΘΟΣ (Στην τσέπη)", value=f"{round(final_net_salary, 2)} €")
    
    st.write("📝 **Ανάλυση Αποδοχών:**")
    st.text(f"• Σύνολο Μικτών Αποδοχών: {round(total_gross_all, 2)} €")
    st.text(f"• Πραγματικές Κρατήσεις ΙΚΑ: -{round(actual_ika, 2)} €")
    st.text(f"• Κρατήσεις ΦΜΥ (Φόρος): -{round(total_fmy, 2)} €")
    
    st.write("<br>📂 **Καταχωρημένες Ημέρες (Πατήστε το X για διαγραφή):**", unsafe_allow_html=True)
    for index, row in st.session_state.db.iterrows():
        col_text, col_btn = st.columns([0.85, 0.15])
        with col_text:
            st.info(f"📅 {row['Ημερομηνία']} | 🛠️ {row['Κατάσταση']} | 🕒 {row['Είσοδος']}-{row['Έξοδος']} | ➕ Έξτρα: {row['Έξτρα Μικτά']} € μικτά")
        with col_btn:
            if st.button("❌", key=f"del_{index}"):
                st.session_state.db = st.session_state.db.drop(index).reset_index(drop=True)
                st.rerun()
    
