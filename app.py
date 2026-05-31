import streamlit as st
import pandas as pd
from datetime import datetime

# Ρύθμιση της σελίδας για κινητά
st.set_page_config(page_title="Μισθοδοσία", page_icon="📱", layout="centered")

# Προσομοίωση βάσης δεδομένων στη μνήμη
if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Ημερομηνία", "Κατάσταση", "Είσοδος", "Έξοδος", "Διάλειμμα Από", "Διάλειμμα Έως", "Έξτρα Μικτά"])

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

col1, col2 = st.columns(2)
with col1:
    time_in = st.text_input("Από", value="07:30")
with col2:
    time_out = st.text_input("Μέχρι", value="18:20")

# ΕΠΙΛΟΓΗ ΚΑΤΑΣΤΑΣΗΣ (Εδώ μπήκαν τα Ρεπό και οι Αργίες)
status = st.selectbox("Περισσότερα", ["Κανονικό Ωράριο", "Αργία (Εργασία)", "Ρεπό", "Άδεια", "Ασθένεια"])

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
hourly_rate = gross_salary * 0.006  # Βασικό Ωρομίσθιο
day_rate = gross_salary / 25        # Βασικό Μεροκάματο

# --- 4. ΚΟΥΜΠΙ ΠΡΟΣΘΗΚΗΣ & ΥΠΟΛΟΓΙΣΜΟΙ ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("ΠΡΟΣΘΗΚΗ", use_container_width=True):
    try:
        extra_pay = 0.0
        
        # Υπολογισμός μόνο αν δούλεψες (Κανονικά ή Αργία)
        if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]:
            fmt = '%H:%M'
            t1 = datetime.strptime(time_in, fmt)
            t2 = datetime.strptime(time_out, fmt)
            total_hours = (t2 - t1).seconds / 3600.0
            
            if has_break:
                b1 = datetime.strptime(break_in, fmt)
                b2 = datetime.strptime(break_out, fmt)
                break_hours = (b2 - b1).seconds / 3600.0
                total_hours -= break_hours
                
            # Υπεργασίες & Υπερωρίες
            hypergasia = 0.0
            hyperoria = 0.0
            if total_hours > 8.0:
                hypergasia = min(1.0, total_hours - 8.0)
            if total_hours > 9.0:
                hyperoria = total_hours - 9.0
                
            # Βασική έξτρα αμοιβή ωρών
            extra_pay = (hypergasia * hourly_rate * 1.20) + (hyperoria * hourly_rate * 1.40)
            
            # ΑΝ ΕΙΝΑΙ ΑΡΓΙΑ: Προσθέτει έξτρα προσαύξηση +75% στο μεροκάματο!
            if status == "Αργία (Εργασία)":
                extra_pay += (day_rate * 0.75)
                
        # Αποθήκευση
        new_row = pd.DataFrame([{
            "Ημερομηνία": date_val.strftime('%d/%m/%Y'),
            "Κατάσταση": status,
            "Είσοδος": time_in if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"] else "-",
            "Έξοδος": time_out if status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"] else "-",
            "Διάλειμμα Από": break_in if (has_break and status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]) else "-",
            "Διάλειμμα Έως": break_out if (has_break and status in ["Κανονικό Ωράριο", "Αργία (Εργασία)"]) else "-",
            "Έξτρα Μικτά": round(extra_pay, 2)
        }])
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
        st.success(f"ΕΠΙΤΥΧΙΑ: Καταχωρήθηκε η ημέρα {date_val.strftime('%d/%m/%Y')} ως {status}!")
    except Exception:
        st.error("⚠️ Παρακαλώ ελέγξτε τη μορφή των ωρών (ΩΩ:ΛΛ)")

# --- 5. ΣΤΑΤΙΣΤΙΚΑ ΜΗΝΑ ---
if not st.session_state.db.empty:
    st.markdown("---")
    st.subheader("Στατιστικά Μήνα")
    
    input_bonus = st.number_input("Μπόνους Μήνα (€):", value=120.0, step=10.0)
    
    # Μετρητές για τις ημέρες
    total_entries = len(st.session_state.db)
    working_days = len(st.session_state.db[st.session_state.db["Κατάσταση"].isin(["Κανονικό Ωράριο", "Αργία (Εργασία)"])])
    repot_days = len(st.session_state.db[st.session_state.db["Κατάσταση"] == "Ρεπό"])
    adeia_days = len(st.session_state.db[st.session_state.db["Κατάσταση"] == "Άδεια"])

    
