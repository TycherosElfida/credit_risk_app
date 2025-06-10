# expert_system/engine.py
from typing import TypedDict, List, Tuple

# A TypedDict provides clarity and static analysis for your input structure.
class LoanApplicant(TypedDict):
    age: int
    marital: str
    emp_status: str
    emp_tenure: str
    income: float
    total_debt: float
    loan_amt: float
    collateral_val: float
    savings_bal: float
    credit_score: int
    late_hist: str

class CreditRiskExpertSystem:
    """
    A class-based expert system for assessing credit risk.
    Encapsulates all the rules and logic for a clean, reusable component.
    """
    _RISK_SCALE = ["Rendah", "Sedang", "Tinggi"]

    def _safe_ratio(self, num: float, denom: float) -> float:
        """Helper for safe division to avoid ZeroDivisionError."""
        return round(num / denom, 3) if denom else 1.0

    def _categorize_credit_score(self, score: int) -> str:
        return "Bagus" if score >= 725 else "Sedang" if score >= 650 else "Buruk"

    def _categorize_age(self, age: int) -> str:
        return "Muda" if age < 25 else "Prima" if age <= 55 else "Senior"

    def _categorize_tenure(self, tenure: str) -> str:
        return "Pendek" if tenure == "<1 tahun" else "Sedang" if tenure == "1-3 tahun" else "Lama"

    def _evaluate_base_risk(self, inp: LoanApplicant) -> Tuple[str, List[str]]:
        """The core decision tree for initial risk assessment."""
        path = []
        dti = self._safe_ratio(inp['total_debt'], inp['income'])
        lti = self._safe_ratio(inp['loan_amt'], inp['income'])
        cltv = self._safe_ratio(inp['loan_amt'], inp['collateral_val'])
        sav = self._safe_ratio(inp['savings_bal'], inp['loan_amt'])
        score_cat = self._categorize_credit_score(inp['credit_score'])
        late_hist = inp['late_hist']

        if late_hist == "Sering":
            path.append("Riwayat telat 'Sering' → Risiko Tinggi")
            return "Tinggi", path
        path.append(f"Riwayat Telat: {late_hist}")

        if late_hist == "Tidak Pernah":
            path.append(f"Skor Kredit: {score_cat} ({inp['credit_score']})")
            if score_cat == "Bagus":
                return ("Sedang", path + [f"LTI {lti:.2f} > 0.8 → Risiko Sedang"]) if lti > 0.8 \
                    else ("Rendah", path + [f"LTI {lti:.2f} ≤ 0.8 → Risiko Rendah"])
            elif score_cat == "Sedang":
                if dti > 0.5:
                    return "Tinggi", path + [f"DTI {dti:.2f} > 0.5 → Risiko Tinggi"]
                path.append(f"DTI {dti:.2f} ≤ 0.5")
                return ("Rendah", path + ["Status Pekerjaan 'Tetap' → Risiko Rendah"]) if inp['emp_status'] == "Tetap" \
                    else ("Sedang", path + ["Status Pekerjaan Bukan 'Tetap' → Risiko Sedang"])
            else:  # score_cat == "Buruk"
                if dti > 0.5:
                    return "Tinggi", path + [f"DTI {dti:.2f} > 0.5 → Risiko Tinggi"]
                return ("Sedang", path + ["Status Pekerjaan 'Tetap' → Risiko Sedang"]) if inp['emp_status'] == "Tetap" \
                    else ("Tinggi", path + ["Status Pekerjaan Bukan 'Tetap' → Risiko Tinggi"])
        
        # late_hist == "Pernah ≤2×"
        path.append(f"Skor Kredit: {score_cat} ({inp['credit_score']})")
        if dti > 0.5:
            path.append(f"DTI {dti:.2f} > 0.5")
            return ("Tinggi", path + [f"Rasio Tabungan {sav:.2f} < 0.2 → Risiko Tinggi"]) if sav < 0.2 \
                else ("Sedang", path + [f"Rasio Tabungan {sav:.2f} ≥ 0.2 → Risiko Sedang"])
        else:
            path.append(f"DTI {dti:.2f} ≤ 0.5")
            return ("Sedang", path + [f"CLTV {cltv:.2f} > 0.9 → Risiko Sedang"]) if cltv > 0.9 \
                else ("Rendah", path + [f"CLTV {cltv:.2f} ≤ 0.9 → Risiko Rendah"])

    def _apply_adjustments(self, base_risk: str, inp: LoanApplicant) -> Tuple[str, List[str]]:
        """Applies adjustments based on demographic and employment factors."""
        try:
            risk_index = self._RISK_SCALE.index(base_risk)
        except ValueError:
            return base_risk, ["Error: Base risk level unknown."]

        notes = []

        # Age adjustment
        age_cat = self._categorize_age(inp['age'])
        if age_cat in ("Muda", "Senior"):
            risk_index = min(risk_index + 1, len(self._RISK_SCALE) - 1)
            notes.append(f"[PENYESUAIAN] Umur '{age_cat}' menaikkan level risiko.")

        # Marital status adjustment
        if inp['marital'] == "Menikah":
            risk_index = max(risk_index - 1, 0)
            notes.append(f"[PENYESUAIAN] Status 'Menikah' menurunkan level risiko.")

        # Employment tenure adjustment
        tenure_cat = self._categorize_tenure(inp['emp_tenure'])
        if tenure_cat == "Pendek":
            risk_index = min(risk_index + 1, len(self._RISK_SCALE) - 1)
            notes.append(f"[PENYESUAIAN] Durasi kerja '{tenure_cat}' menaikkan level risiko.")
        elif tenure_cat == "Lama" and risk_index > 0:
            risk_index -= 1
            notes.append(f"[PENYESUAIAN] Durasi kerja 'Lama' menurunkan level risiko.")

        return self._RISK_SCALE[risk_index], notes

    def evaluate(self, applicant_data: LoanApplicant) -> Tuple[str, List[str]]:
        """
        The main public method to evaluate a loan applicant.
        It runs the base tree and applies adjustments.
        """
        base_risk, decision_path = self._evaluate_base_risk(applicant_data)
        final_risk, adjustment_notes = self._apply_adjustments(base_risk, applicant_data)
        
        if final_risk != base_risk:
            decision_path.append(f"Risiko awal '{base_risk}' disesuaikan menjadi '{final_risk}'.")
        
        decision_path.extend(adjustment_notes)
        return final_risk, decision_path