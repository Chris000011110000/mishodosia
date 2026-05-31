import streamlit as st
import pandas as pd
from datetime import datetime

# Ρύθμιση της σελίδας για κινητά
st.set_page_config(page_title="Μισθοδοσία", page_icon="📱", layout="centered")

# Προσομοίωση βάσης δεδομένων στη μνήμη
if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Ημερομηνία", "Κατάσταση", "Είσοδος", "Έξοδος", "Διάλειμμα Από", "Διάλειμμα Έως", "Έξτρα Μικτά"])

# Λίστες για τους τροχούς (00-23 για ώρες, 00-59 για λεπτά)
hours_options = [f"{h:02d}" for h in range(24)]
minutes_options = [f"{m:02d}" for m in range(60)]

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

# --- ΤΡΟΧΟΙ ΩΡΑΣ ΕΙΣΟΔΟΥ (Όπως η φωτογραφία σου) ---
st.write("🕒 **Ώρα Εισόδου:**")
col_in_h, col_in_m = st.columns(2)
with col_in_h:
    in_h = st.selectbox("Ω", hours_options, index=7, key="in_h") # Προεπιλογή 07
with col_in_m:
    in_m = st.selectbox("Λ", minutes_options, index=30, key="in_m") # Προεπιλογή 30

# --- TΡΟΧΟΙ ΩΡΑΣ ΕΞΟΔΟΥ (Όπως η φωτογραφία σου) ---
st.write("🕒 **Ώρα Εξόδου:**")
col_out_h, col_out_m = st.columns(2)
with col_out_h:
    out_h = st.selectbox("Ω ", hours_options, index=18, key="out_h") # Προεπιλογή 18
with col_out_m:
    out_m = st.selectbox("Λ ", minutes_options, index=20, key="out_m") # Προεπιλογή 20

# ΕΠΙΛΟΓΗ ΚΑΤΑΣΤΑΣΗΣ
status = st.selectbox("Περισσότερα", ["Κανονικό Ωράριο", "Αργία (Εργασία)", "Ρεπό", "Άδεια", "Ασθένεια"])

# --- 3. ΠΛΑΙΣΙΟ ΔΙΑΛΕΙΜΜΑΤΟΣ ---
st.markdown('<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 15px;">', unsafe_allow_html=True)
has_break = st.toggle("ΔΙΑΛΕΙΜΜΑ", value=True)

if has_break:
    col_b_in_h, col_b_in_m = st.columns(2)
    with col_b_in_h:
        bin_h = st.selectbox("Από (Ω)", hours_options, index=13, key="bin_h") # Προεπιλογή 13
    with col_b_in_m:
        bin_m = st.selectbox("Από (Λ)", minutes_options, index=0, key="bin_m") # Προεπιλογή 00
        
    col_b_out_h, col_b_out_m = st.columns(2)
    with col_b_out_h:
        bout_h = st.selectbox("Μέχρι (Ω)", hours_options, index=13, key="bout_h") # Προεπιλογή 13
    with col_b_out_m:
        bout_m = st.selectbox("Μέχρι (Λ)", minutes_options, index=30, key="bout_m") # Προεπιλογή 30
else:
    bin_h, bin_m, bout_h, bout_m = "00", "00", "00", "00"
st.markdown('</div>', unsafe_allow_html=True)

# Σταθεροί υπολογισμοί
gross_salary = 1196.0
hourly_rate = gross_salary * 0.006  
day_rate = gross_salary / 25        

# --- 4. ΚΟΥΜΠΙ ΠΡΟΣΘΗΚΗΣ & ΥΠΟΛΟΓΙΣΜΟΙ ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("ΠΡΟΣΘΗΚΗ", use_container_width=True):
    try:
        extra_pay = 0.0
        time_in_str = f"{in_h}:{in_m}"
        time_out_str = f"{out_h}:{out_m}"
        break_in_str = f"{bin_h}:{bin_m}"
        break_out_str = f"{bout_h}:{bout_m}"
        
        if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]:
            total_hours = ((int(out_h) * 60 + int(out_m)) - (int(in_h) * 60 + int(in_m))) / 60.0
            
            if has_break:
                break_hours = ((int(bout_h) * 60 + int(bout_m)) - (int(bin_h) * 60 + int(bin_m))) / 60.0
                total_hours -= break_hours
                
            if total_hours <= 0:
                st.error("⚠️ Η ώρα εξόδου πρέπει να είναι μετά την ώρα εισόδου!")
            else:
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
            "Είσοδος": time_in_str if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"] else "-",
            "Έξοδος": time_out_str if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"] else "-",
            "Διάλειμμα Από": break_in_str if (has_break and status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]) else "-",
            "Διάλειμμα Έως": break_out_str if (has_break and status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]) else "-",
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
    
