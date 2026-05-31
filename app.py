import streamlit as st
import pandas as pd
from datetime import datetime

# Ρύθμιση της σελίδας για κινητά
st.set_page_config(page_title="Μισθοδοσία", page_icon="📱", layout="centered")

# Προσομοίωση βάσης δεδομένων στη μνήμη
if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Ημερομηνία", "Μικτός", "Είσοδος", "Έξοδος", "Διάλειμμα Από", "Διάλειμμα Έως", "Καθαρά"])

# --- 1. ΠΑΝΩ ΜΠΛΕ ΜΠΑΡΑ ---
st.markdown(
    f"""
    <div style="background-color: #1e73be; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">Κυριακή 31 Μαΐ 2026</h2>
        <p style="color: #d1e8ff; margin: 5px 0 0 0; font-weight: bold; word-spacing: 20px;">ΜΙΑ ΜΕΡΑ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ΠΟΛΛΕΣ ΜΕΡΕΣ</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 2. ΠΕΡΙΟΧΗ ΚΑΤΑΧΩΡΗΣΗΣ ---
st.subheader("Επεξεργασία Ημέρας")

date_val = st.date_input("Επιλογή Ημέρας", datetime.now(), format="DD/MM/YYYY")

col1, col2 = st.columns(2)
with col1:
    time_in = st.text_input("Από", value="07:30")
with col2:
    time_out = st.text_input("Μέχρι", value="18:20")

st.selectbox("Περισσότερα", ["Κανονικό Ωράριο", "Ρεπό", "Άδεια", "Ασθένεια"])

# --- 3. ΠΛΑΙΣΙΟ ΔΙΑΛΕΙΜΜΑΤΟΣ ---
st.markdown('<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 15px;">', unsafe_allow_html=True)
has_break = st.toggle("ΔΙΑΛΕΙΜΜΑ", value=True)

col3, col4 = st.columns(2)
with col3:
    break_in = st.text_input("Από ", value="13:00", disabled=not has_break)
with col4:
    break_out = st.text_input("Μέχρι ", value="13:30", disabled=not has_break)
st.markdown('</div>', unsafe_allow_html=True)

# Σταθερός βασικός μικτός μισθός
gross_salary = 1196.0

# --- 4. ΚΟΥΜΠΙ ΠΡΟΣΘΗΚΗΣ & ΥΠΟΛΟΓΙΣΜΟΙ ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("ΠΡΟΣΘΗΚΗ", use_container_width=True):
    try:
        fmt = '%H:%M'
        t1 = datetime.strptime(time_in, fmt)
        t2 = datetime.strptime(time_out, fmt)
        total_hours = (t2 - t1).seconds / 3600.0
        
        if has_break:
            b1 = datetime.strptime(break_in, fmt)
            b2 = datetime.strptime(break_out, fmt)
            break_hours = (b2 - b1).seconds / 3600.0
            total_hours -= break_hours
            
        hypergasia = 0.0
        hyperoria = 0.0
        if total_hours > 8.0:
            hypergasia = min(1.0, total_hours - 8.0)
        if total_hours > 9.0:
            hyperoria = total_hours - 9.0
            
        hourly_rate = gross_salary * 0.006
        extra_pay = (hypergasia * hourly_rate * 1.20) + (hyperoria * hourly_rate * 1.40)
        
        new_row = pd.DataFrame([{
            "Ημερομηνία": date_val.strftime('%d/%m/%Y'),
            "Μικτός": gross_salary,
            "Είσοδος": time_in,
            "Έξοδος": time_out,
            "Διάλειμμα Από": break_in if has_break else "-",
            "Διάλειμμα Έως": break_out if has_break else "-",
            "Έξτρα Μικτά": round(extra_pay, 2)
        }])
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
        st.success(f"ΕΠΙΤΥΧΙΑ: Καταχωρήθηκε η ημέρα {date_val.strftime('%d/%m/%Y')}!")
    except Exception:
        st.error("⚠️ Παρακαλώ ελέγξτε τη μορφή των ωρών (ΩΩ:ΛΛ)")

# --- 5. ΣΤΑΤΙΣΤΙΚΑ ΜΗΝΑ ---
if not st.session_state.db.empty:
    st.markdown("---")
    st.subheader("Στατιστικά Μήνα")
    
    input_bonus = st.number_input("Μπόνους Μήνα (€):", value=120.0, step=10.0)
    
    total_entries = len(st.session_state.db)
    total_extra_gross = st.session_state.db["Έξτρα Μικτά"].sum()
    
    # Σύνολο Αποδοχών (Μικτά)
    total_gross_all = gross_salary + input_bonus + total_extra_gross
    
    # Αρχικές κρατήσεις βάσει ΙΚΑ 13.37%
    raw_ika = total_gross_all * 0.1337
    subsidy = 58.70
    
    # Πραγματικές Κρατήσεις ΙΚΑ (Η επιδότηση μειώνει τις κρατήσεις)
    actual_ika = max(0.0, raw_ika - subsidy)
    
    # Υπολογισμός Φόρου ΦΜΥ
    taxable_income = total_gross_all - actual_ika
    if taxable_income > 833:
        total_fmy = (taxable_income - 833) * 0.22
    else:
        total_fmy = 0.0
        
    # Τελικός Καθαρός Μισθός
    final_net_salary = total_gross_all - actual_ika - total_fmy
    
    st.metric(label="Εργάσιμες Ημέρες", value=f"{total_entries} μέρες")
    st.metric(label="💰 ΤΕΛΙΚΟΣ ΚΑΘΑΡΟΣ ΜΙΣΘΟΣ (Στην τσέπη)", value=f"{round(final_net_salary, 2)} €")
    
    st.write("📝 **Ανάλυση Αποδοχών (Όπως το εκκαθαριστικό σου):**")
    st.text(f"• Σύνολο Μικτών Αποδοχών: {round(total_gross_all, 2)} €")
    st.text(f"• Πραγματικές Κρατήσεις ΙΚΑ (Μειωμένες λόγω επιδότησης): -{round(actual_ika, 2)} €")
    st.text(f"• Κρατήσεις ΦΜΥ (Φόρος): -{round(total_fmy, 2)} €")
    
    st.write("<br>📂 **Καταχωρημένες Ημέρες (Πατήστε το X για διαγραφή):**", unsafe_allow_html=True)
    for index, row in st.session_state.db.iterrows():
        col_text, col_btn = st.columns([0.85, 0.15])
        with col_text:
            st.info(f"📅 {row['Ημερομηνία']} | 🕒 {row['Είσοδος']}-{row['Έξοδος']} | ➕ Έξτρα: {row['Έξτρα Μικτά']} € μικτά")
        with col_btn:
            if st.button("❌", key=f"del_{index}"):
                st.session_state.db = st.session_state.db.drop(index).reset_index(drop=True)
                st.rerun()
                
                
    
                                                               
  
