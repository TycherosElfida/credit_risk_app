# expert_system/engine.py
from typing import TypedDict, List, Tuple, Dict
from dataclasses import dataclass, field

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

@dataclass
class ScorecardResult:
    """A structured container for a single factor's score and explanation."""
    points: int
    reason: str

@dataclass
class CreditScorecard:
    """A comprehensive data object to hold the entire evaluation result."""
    final_risk_grade: str = "N/A"
    final_score: float = 0.0
    knockout_rule_fired: bool = False
    decision_path: List[str] = field(default_factory=list)
    score_breakdown: Dict = field(default_factory=dict)

class CreditRiskExpertSystem:
    """
    A professional, scorecard-based expert system for assessing credit risk
    in the Indonesian context. It is built upon the 5 Cs of Credit framework.
    """
    # --- Weights for the 5 Cs of Credit ---
    WEIGHTS = {
        "character": 0.40,
        "capacity": 0.30,
        "capital": 0.10,
        "collateral": 0.10,
        "conditions": 0.10,
    }

    def _safe_ratio(self, num: float, denom: float) -> float:
        """Helper for safe division to avoid ZeroDivisionError."""
        if denom == 0:
            return float('inf') # Return a large number to be handled by scoring logic
        return round(num / denom, 4)

    # --- CHARACTER SCORING (Weight: 40%) ---
    def _score_credit_history(self, late_hist: str) -> ScorecardResult:
        """Scores based on payment history (SLIK Kol proxy). This is a knockout rule."""
        if late_hist == "Sering":
            return ScorecardResult(0, "Riwayat pembayaran 'Sering' (proksi Kol 3+) adalah aturan penolakan otomatis.")
        elif late_hist == "Pernah ≤2×":
            return ScorecardResult(70, "Riwayat pembayaran 'Pernah ≤2×' (proksi Kol 2) menunjukkan risiko sedang.")
        # 'Tidak Pernah' (Kol 1)
        return ScorecardResult(100, "Riwayat pembayaran 'Tidak Pernah' (proksi Kol 1) adalah ideal.")

    def _score_credit_score(self, score: int) -> ScorecardResult:
        """Scores the numerical credit score (e.g., from a private bureau)."""
        if score >= 780:
            return ScorecardResult(100, f"Skor kredit {score} (>=780) tergolong Sangat Baik.")
        if score >= 720:
            return ScorecardResult(80, f"Skor kredit {score} (720-779) tergolong Baik.")
        if score >= 660:
            return ScorecardResult(60, f"Skor kredit {score} (660-719) tergolong Cukup.")
        return ScorecardResult(40, f"Skor kredit {score} (<660) tergolong Kurang.")

    # --- CAPACITY SCORING (Weight: 30%) ---
    def _score_dti(self, dti: float) -> ScorecardResult:
        """Scores the Debt-to-Income ratio based on Indonesian benchmarks."""
        dti_pct = dti * 100
        if dti <= 0.35:
            return ScorecardResult(100, f"Rasio Utang terhadap Pendapatan (DTI) {dti_pct:.1f}% (<=35%) adalah Ideal.")
        if dti <= 0.49:
            return ScorecardResult(50, f"Rasio Utang terhadap Pendapatan (DTI) {dti_pct:.1f}% (36%-49%) menunjukkan tekanan finansial.")
        return ScorecardResult(0, f"Rasio Utang terhadap Pendapatan (DTI) {dti_pct:.1f}% (>=50%) adalah berisiko tinggi.")

    def _score_employment(self, status: str, tenure: str) -> ScorecardResult:
        """Scores employment stability based on status and tenure."""
        if status == "Tetap":
            if tenure == ">3 tahun":
                return ScorecardResult(100, "Status kerja 'Tetap' dengan durasi '>3 tahun' menunjukkan stabilitas tertinggi.")
            if tenure == "1-3 tahun":
                return ScorecardResult(80, "Status kerja 'Tetap' dengan durasi '1-3 tahun' menunjukkan stabilitas baik.")
        elif status in ["Wiraswasta", "Kontrak"]:
            return ScorecardResult(50, f"Status kerja '{status}' memiliki stabilitas pendapatan yang lebih rendah.")
        
        # Covers Tetap <1 tahun and Tidak Tetap
        return ScorecardResult(20, f"Status kerja '{status}' dengan durasi '{tenure}' menunjukkan stabilitas terendah.")

    # --- CAPITAL SCORING (Weight: 10%) ---
    def _score_stl(self, stl: float) -> ScorecardResult:
        """Scores the Savings-to-Loan ratio."""
        stl_pct = stl * 100
        if stl >= 0.50:
            return ScorecardResult(100, f"Rasio Tabungan terhadap Pinjaman (STL) {stl_pct:.1f}% (>=50%) menunjukkan cadangan modal sangat baik.")
        if stl >= 0.20:
            return ScorecardResult(70, f"Rasio Tabungan terhadap Pinjaman (STL) {stl_pct:.1f}% (20%-49%) menunjukkan cadangan modal baik.")
        if stl >= 0.10:
            return ScorecardResult(40, f"Rasio Tabungan terhadap Pinjaman (STL) {stl_pct:.1f}% (10%-19%) menunjukkan cadangan modal sedang.")
        return ScorecardResult(0, f"Rasio Tabungan terhadap Pinjaman (STL) {stl_pct:.1f}% (<10%) menunjukkan cadangan modal minimal.")

    # --- COLLATERAL SCORING (Weight: 10%) ---
    def _score_ltv(self, ltv: float) -> ScorecardResult:
        """Scores the Loan-to-Value ratio."""
        ltv_pct = ltv * 100
        if ltv_pct == float('inf'):
            return ScorecardResult(0, "Nilai agunan nol membuat LTV tidak terdefinisi (risiko sangat tinggi).")
        if ltv <= 0.70:
            return ScorecardResult(100, f"Rasio Pinjaman terhadap Nilai Agunan (LTV) {ltv_pct:.1f}% (<=70%) berisiko sangat rendah.")
        if ltv <= 0.85:
            return ScorecardResult(70, f"Rasio Pinjaman terhadap Nilai Agunan (LTV) {ltv_pct:.1f}% (71%-85%) berisiko rendah.")
        if ltv <= 0.95:
            return ScorecardResult(40, f"Rasio Pinjaman terhadap Nilai Agunan (LTV) {ltv_pct:.1f}% (86%-95%) berisiko sedang.")
        return ScorecardResult(0, f"Rasio Pinjaman terhadap Nilai Agunan (LTV) {ltv_pct:.1f}% (>95%) berisiko tinggi.")

    # --- CONDITIONS SCORING (Weight: 10%) ---
    def _score_age(self, age: int) -> ScorecardResult:
        """Scores applicant's age."""
        if 25 <= age <= 55:
            return ScorecardResult(100, f"Umur {age} (25-55) berada dalam rentang usia produktif utama.")
        return ScorecardResult(50, f"Umur {age} berada di luar rentang usia produktif utama.")

    def _score_marital_status(self, marital: str) -> ScorecardResult:
        """Scores marital status."""
        if marital == "Menikah":
            return ScorecardResult(100, "Status 'Menikah' seringkali berkorelasi dengan stabilitas finansial rumah tangga.")
        return ScorecardResult(60, f"Status '{marital}' dapat mengindikasikan ketergantungan pada satu sumber pendapatan.")

    def _get_risk_grade(self, score: float) -> str:
        """Assigns final risk grade based on the total score."""
        if score >= 80:
            return "Rendah"
        if score >= 60:
            return "Sedang"
        return "Tinggi"

    def evaluate(self, applicant: LoanApplicant) -> CreditScorecard:
        """
        The main public method to evaluate a loan applicant using the scorecard model.
        """
        card = CreditScorecard()
        
        # --- 1. KNOCKOUT RULE CHECK (from Character) ---
        history_score = self._score_credit_history(applicant['late_hist'])
        card.score_breakdown = history_score
        
        if applicant['late_hist'] == "Sering":
            card.knockout_rule_fired = True
            card.final_risk_grade = "Tinggi"
            card.decision_path.append(history_score.reason)
            return card

        # --- 2. CALCULATE DERIVED METRICS ---
        dti = self._safe_ratio(applicant['total_debt'], applicant['income'])
        ltv = self._safe_ratio(applicant['loan_amt'], applicant['collateral_val'])
        stl = self._safe_ratio(applicant['savings_bal'], applicant['loan_amt'])

        # --- 3. SCORE ALL FACTORS ---
        # Character
        card.score_breakdown = self._score_credit_score(applicant['credit_score'])
        
        # Capacity
        card.score_breakdown = self._score_dti(dti)
        card.score_breakdown = self._score_employment(applicant['emp_status'], applicant['emp_tenure'])
        
        # Capital
        card.score_breakdown = self._score_stl(stl)
        
        # Collateral
        card.score_breakdown = self._score_ltv(ltv)
        
        # Conditions
        card.score_breakdown['Usia'] = self._score_age(applicant['age'])
        card.score_breakdown = self._score_marital_status(applicant['marital'])

        # --- 4. CALCULATE COMPOSITE SCORES FOR EACH 'C' ---
        char_score = (history_score.points + card.score_breakdown.points) / 2
        cap_score = (card.score_breakdown.points + card.score_breakdown.points) / 2
        capl_score = card.score_breakdown.points
        coll_score = card.score_breakdown.points
        cond_score = (card.score_breakdown['Usia'].points + card.score_breakdown.points) / 2

        # --- 5. CALCULATE FINAL WEIGHTED SCORE ---
        final_score = (
            char_score * self.WEIGHTS["character"] +
            cap_score * self.WEIGHTS["capacity"] +
            capl_score * self.WEIGHTS["capital"] +
            coll_score * self.WEIGHTS["collateral"] +
            cond_score * self.WEIGHTS["conditions"]
        )
        card.final_score = round(final_score, 2)
        
        # --- 6. DETERMINE FINAL RISK GRADE ---
        card.final_risk_grade = self._get_risk_grade(card.final_score)
        
        # --- 7. POPULATE DECISION PATH FOR EXPLAINABILITY ---
        for factor, result in card.score_breakdown.items():
            card.decision_path.append(f"{factor}: {result.reason} [Poin: {result.points}]")
            
        return card