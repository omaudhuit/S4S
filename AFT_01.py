import math
import streamlit as st


# Helper functions
def IF(condition, true_val, false_val):
    return true_val if condition else false_val

def PMT(rate, nper, pv):
    # If rate is zero, simple division is used.
    if rate == 0:
        return pv / nper
    return (rate * pv) / (1 - (1 + rate) ** (-nper))

# Residential Consumers (Οικιακοί καταναλωτές)
def compute_residential():
    # --- Input Values (from CSV "Οικιακοί καταναλωτές.csv") ---
    annual_consumption = 11536         # kWh (cell_B7)
    consumption_time = "Απόγευμα-Βράδυ"  # (cell_B12) user choice: "Πρωί-Μεσημέρι" or "Απόγευμα-Βράδυ"
    supply_power = 35                  # kVA (cell_B8)
    tariff_category = "Γ1"             # (cell_B9), e.g. "Γ1" or "Γ1Ν"
    normal_tariff = 0.3                # €/kWh (cell_B10)
    night_tariff = 0.08                # €/kWh (cell_B11)
    region = "Δυτική Ελλάδα"           # (cell_B13)
    roof_type = "Στέγη"                # (cell_B14)
    orientation = "ΝΔ"                 # (cell_B15)
    available_area = 75                # (cell_B16)
    battery_choice = "Όχι"             # (cell_E14) – whether the battery-saving effect is taken into account
    battery_capacity_choice = 12       # (cell_E15)
    storage_decision = "Ναι"           # (cell_E16) – if storage is used

    # --- Intermediate Calculations ---
    # I7: Percentage consumption in the “normal” tariff period.
    I7 = IF(consumption_time == "Πρωί-Μεσημέρι", 0.7, 0.5)
    I8 = 1 - I7

    # I11: Annual PV production factor (depends on region)
    if region in ["Νότιο Αιγαίο", "Κρήτη"]:
        I11 = 1600
    elif region in ["Αττική", "Δυτική Ελλάδα", "Ιόνιοι Νήσοι"]:
        I11 = 1550
    elif region == "Πελοπόννησος":
        I11 = 1500
    elif region in ["Ήπειρος", "Θεσσαλία", "Στερεά Ελλάδα"]:
        I11 = 1450
    else:
        I11 = 1400

    # I10: Production coefficient based on roof type and orientation
    if roof_type == "Στέγη":
        if orientation in ["Α", "Δ"]:
            I10 = 0.85
        elif orientation in ["ΝΑ", "ΝΔ"]:
            I10 = 0.93
        else:
            I10 = 0.95
    else:
        I10 = 1.0

    I12 = I11 * I10

    # L7: Required inverter power for full self-consumption
    L7 = annual_consumption / I12

    # L8: Upper limit of installed power (based on supply power)
    L8 = 5 if supply_power <= 12 else 10.8

    # L9: Selected inverter power: the minimum of calculated value and L8
    L9 = min(annual_consumption / I12, L8)

    # I9: Percentage for PV production matching demand (varies with consumption time)
    I9 = 0.7 if consumption_time == "Πρωί-Μεσημέρι" else 0.3

    # I13: Area coefficient based on roof type (Ταράτσα gives 7, otherwise 5)
    I13 = 7 if roof_type == "Ταράτσα" else 5

    # L10: Maximum inverter capacity based on available area
    L10 = available_area / I13

    # L11: Final selected inverter capacity
    L11 = min(L9, L10)

    # L12: Annual PV production (kWh)
    L12 = L11 * I12

    # L14: Daily PV production available for battery sizing
    L14 = L12 * (1 - I9) / 365

    # L15: Battery capacity selected (from user)
    L15 = battery_capacity_choice

    # L16: Final battery capacity decision (depends on whether battery effect is considered)
    L16 = L15 if battery_choice == "Όχι" else L14

    # L17: Baseline electricity cost without the system
    if tariff_category == "Γ1":
        L17 = (normal_tariff + 0.046) * 1.06 * annual_consumption
    elif tariff_category == "Γ1Ν":
        L17 = ((normal_tariff + 0.046) * I7 + (night_tariff + 0.01707) * I8) * 1.06 * annual_consumption
    else:
        L17 = None

    # O7: Effective tariff rate (depends on tariff category)
    if tariff_category == "Γ1Ν":
        O7 = (normal_tariff * I7 + night_tariff * I8)
    else:
        O7 = normal_tariff

    O8 = 0.046

    # O9: Estimated savings on the main part of the electricity bill (with PV)
    O9 = (L12 * O7 + O8 * L12 * I9) * 1.06

    # O10: Additional saving from battery usage
    O10 = L16 * 365 * O8 * 1.06

    # O11: Total estimated savings with the system
    O11 = (O9 + O10) if storage_decision == "Ναι" else O9

    # O15: Baseline cost is taken as L17
    O15 = L17

    # O16: Difference between baseline cost and PV-based savings
    O16 = O15 - O9

    # O17: Final expected saving (here set equal to O11)
    O17 = O11

    # --- Pack and return results ---
    results = {
        "Annual Consumption (kWh)": annual_consumption,
        "I7 (Normal consumption fraction)": I7,
        "I8 (Reduced consumption fraction)": I8,
        "I11 (PV production factor by region)": I11,
        "I10 (Production coefficient)": I10,
        "I12 (Combined production factor)": I12,
        "L7 (Required inverter power)": L7,
        "L8 (Upper power limit)": L8,
        "L9 (Selected inverter power)": L9,
        "I9 (PV production factor based on time)": I9,
        "I13 (Area coefficient)": I13,
        "L10 (Area-based capacity)": L10,
        "L11 (Final inverter capacity)": L11,
        "L12 (Annual PV production, kWh)": L12,
        "L14 (Daily production for battery sizing)": L14,
        "L15 (Battery capacity selection)": L15,
        "L16 (Final battery capacity)": L16,
        "L17 (Baseline electricity cost)": L17,
        "O7 (Effective tariff)": O7,
        "O8 (Cost factor)": O8,
        "O9 (Estimated PV saving)": O9,
        "O10 (Additional saving with battery)": O10,
        "O11 (Total saving with system)": O11,
        "O15 (Baseline cost)": O15,
        "O16 (Cost saving difference)": O16,
        "O17 (Final expected saving)": O17
    }
    return results

def compute_loan():
    # --- Input Values (from CSV "Υπολογισμός δανείου.csv") ---
    power = 8                # kW (cell_B3)
    interest_rate = 0.06     # Annual interest rate (cell_E3)
    repayment_years = 5      # Loan term in years (cell_E4)
    battery_kWh = 12         # kWh (cell_B4)
    annual_saving = 656      # €/year saving (cell_B5)
    prepayment_fraction = 0.5  # Fraction of loan paid upfront (cell_E5)

    # Cost per kW for the PV system depends on the installed power:
    if power <= 5:
        cost_per_kw = 2000
    elif power <= 10:
        cost_per_kw = 1500
    elif power <= 20:
        cost_per_kw = 1200
    elif power <= 50:
        cost_per_kw = 1000
    elif power <= 100:
        cost_per_kw = 850
    else:
        cost_per_kw = 750

    # Cost per kWh for the battery:
    cost_per_kWh = 800  # (cell_H4)

    # --- Intermediate Calculations ---
    pv_cost = power * cost_per_kw          # (cell_H5)
    monthly_saving = annual_saving / 12     # (cell_B6)
    battery_cost = cost_per_kWh * battery_kWh  # (cell_H6)
    # Estimate loan amount (here we assume no override from user input)
    estimated_loan = pv_cost + battery_cost  # (cell_H7)
    # Calculate monthly payment using PMT: note that the principal is reduced by any prepayment
    principal_for_loan = estimated_loan - prepayment_fraction * estimated_loan
    monthly_payment = PMT(interest_rate / 12, repayment_years * 12, principal_for_loan)  # (cell_H8)
    half_loan = estimated_loan / 2  # (cell_C11)

    # --- Pack and return results ---
    results = {
        "Power (kW)": power,
        "Interest Rate": interest_rate,
        "Repayment Years": repayment_years,
        "Battery Capacity (kWh)": battery_kWh,
        "Annual Saving (€)": annual_saving,
        "Prepayment Fraction": prepayment_fraction,
        "Cost per kW (€)": cost_per_kw,
        "PV Cost (€)": pv_cost,
        "Cost per kWh (Battery, €)": cost_per_kWh,
        "Battery Cost (€)": battery_cost,
        "Estimated Loan (€)": estimated_loan,
        "Monthly Payment (€)": monthly_payment,
        "Half of Loan (€)": half_loan
    }
    return results

def compute_kwh_estimation():
    # --- Input Values (from CSV "Εύρεση kWh βάσει €.csv") ---
    annual_electricity_cost_known = 900  # €/year for known tariff (cell_B8)
    tariff = 0.07                        # €/kWh (cell_B9)
    annual_electricity_cost_unknown = 900 # €/year for unknown tariff (cell_F8)
    consumer_category_known = "Κατοικία"  # (cell_B10)
    consumer_category_unknown = "Κατοικία"  # (cell_F9)

    # --- Estimated Prices based on consumer category ---
    if consumer_category_known == "Κατοικία":
        estimated_price_known = tariff + 0.05
    elif consumer_category_known == "Επιχείρηση χαμηλής τάσης":
        estimated_price_known = tariff + 0.04
    else:
        estimated_price_known = tariff + 0.035

    if consumer_category_unknown == "Κατοικία":
        estimated_price_unknown = 0.17
    elif consumer_category_unknown == "Επιχείρηση χαμηλής τάσης":
        estimated_price_unknown = 0.15
    else:
        estimated_price_unknown = 0.12

    # --- Estimated Annual Consumption ---
    consumption_known = annual_electricity_cost_known / estimated_price_known
    consumption_unknown = annual_electricity_cost_unknown / estimated_price_unknown

    results = {
        "Annual Electricity Cost (known, €)": annual_electricity_cost_known,
        "Tariff (€/kWh)": tariff,
        "Estimated Price (known, €/kWh)": estimated_price_known,
        "Estimated Annual Consumption (known, kWh)": consumption_known,
        "Annual Electricity Cost (unknown, €)": annual_electricity_cost_unknown,
        "Estimated Price (unknown, €/kWh)": estimated_price_unknown,
        "Estimated Annual Consumption (unknown, kWh)": consumption_unknown
    }
    return results

def compute_corporate():
    # --- Input Values (from CSV "Εταιρικοί Καταναλωτές Χ.Τ.csv") ---
    annual_consumption = 240000          # kWh (cell_B7)
    consumption_time = "Απόγευμα-Βράδυ"   # (assumed from cell_B12)
    tariff_category = "Γ1"               # (cell_B9)
    normal_tariff = 0.3                  # €/kWh (cell_B10)
    night_tariff = 0.08                  # €/kWh (cell_B11)
    region = "Δυτική Ελλάδα"             # (cell_B13)
    roof_type = "Στέγη"                  # (cell_B14)
    orientation = "ΝΔ"                   # (cell_B15)

    # --- Intermediate Calculations ---
    if consumption_time == "Πρωί-Μεσημέρι":
        I7 = 0.7
    elif consumption_time == "Απόγευμα-Βράδυ":
        I7 = 0.3
    else:
        I7 = 0.6
    I8 = 1 - I7

    if region in ["Νότιο Αιγαίο", "Κρήτη"]:
        I11 = 1600
    elif region in ["Αττική", "Δυτική Ελλάδα", "Ιόνιοι Νήσοι"]:
        I11 = 1550
    elif region == "Πελοπόννησος":
        I11 = 1500
    elif region in ["Ήπειρος", "Θεσσαλία", "Στερεά Ελλάδα"]:
        I11 = 1450
    else:
        I11 = 1400

    if roof_type == "Στέγη":
        if orientation in ["Α", "Δ"]:
            I10 = 0.85
        elif orientation in ["ΝΑ", "ΝΔ"]:
            I10 = 0.93
        else:
            I10 = 0.95
    else:
        I10 = 1.0

    I12 = I11 * I10
    L7 = annual_consumption / I12

    if tariff_category == "Γ1Ν":
        O7 = normal_tariff * I7 + night_tariff * I8
    else:
        O7 = normal_tariff

    O8 = 0.046

    if tariff_category == "Γ1":
        L17 = (normal_tariff + 0.046) * 1.06 * annual_consumption
    else:
        L17 = None

    results = {
        "Annual Consumption (kWh)": annual_consumption,
        "I7": I7,
        "I8": I8,
        "I11": I11,
        "I10": I10,
        "I12": I12,
        "L7": L7,
        "O7 (Effective Tariff)": O7,
        "O8": O8,
        "Estimated Baseline Cost (L17)": L17
    }
    return results

# Streamlit app main routine
def main():
    st.title("Excel Calculator Results")
    calc_type = st.sidebar.radio("Select Calculation", 
                                  ("Residential", "Loan", "kWh Estimation", "Corporate"))
    
    if calc_type == "Residential":
        st.header("Residential Consumers Data")
        results = compute_residential()
        st.write(results)
    elif calc_type == "Loan":
        st.header("Loan Calculation Data")
        results = compute_loan()
        st.write(results)
    elif calc_type == "kWh Estimation":
        st.header("kWh Estimation Data")
        results = compute_kwh_estimation()
        st.write(results)
    elif calc_type == "Corporate":
        st.header("Corporate Consumers Data")
        results = compute_corporate()
        st.write(results)

if __name__ == "__main__":
    main()