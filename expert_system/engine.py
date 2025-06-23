# expert_system/engine.py

# STEP 1: Import 'Tuple' from the typing module
from typing import TypedDict, List, Dict, Any, Literal, Tuple

# This is the new, expanded data structure for our applicant
class LoanApplicant(TypedDict):
    kolektibilitas: int
    age: int
    marital_status: str
    number_of_dependents: int
    employment_status: str
    employment_tenure: str
    monthly_income: float
    monthly_debt: float
    loan_amount: float
    loan_purpose: str
    collateral_value: float
    savings_balance: float
    is_first_home_purchase: bool

class CreditRiskExpertSystem:
    """
    An expert system for assessing credit risk using a weighted scoring model
    based on the 5 Cs of Credit.
    """

    def __init__(self, applicant_data: Dict[str, Any]):
        """
        Initializes the system with applicant data and sets up the evaluation parameters.
        """
        self.applicant: LoanApplicant = self._validate_and_prepare_data(applicant_data)
        self.decision_path: List[str] = []
        self.total_score = 100  # Start with a base score of 100
        self.ratios = {}

    def _validate_and_prepare_data(self, data: Dict[str, Any]) -> LoanApplicant:
        return data

    def evaluate(self) -> Dict[str, Any]:
        """
        Main evaluation orchestrator.
        """
        self._calculate_financial_ratios()

        hard_rule_verdict = self._check_hard_rules()
        if hard_rule_verdict:
            return hard_rule_verdict

        self._calculate_score()
        return self._classify_risk()

    def _calculate_financial_ratios(self):
        """Calculates key financial ratios like DTI, LTV, and STL."""
        income = self.applicant['monthly_income']
        collateral = self.applicant['collateral_value']
        loan = self.applicant['loan_amount']
        self.ratios['dti'] = (self.applicant['monthly_debt'] / income * 100) if income > 0 else 1000
        self.ratios['ltv'] = (loan / collateral * 100) if collateral > 0 else 1000
        self.ratios['stl'] = (self.applicant['savings_balance'] / loan * 100) if loan > 0 else 0
        self.decision_path.append(f"RASIO TERHITUNG: DTI={self.ratios['dti']:.1f}%, LTV={self.ratios['ltv']:.1f}%, STL={self.ratios['stl']:.1f}%")

    def _check_hard_rules(self) -> Dict[str, Any] | None:
        """Checks for absolute rejection criteria."""
        if self.applicant['kolektibilitas'] >= 3:
            self.decision_path.append(f"[ATURAN KERAS] Skor Kolektibilitas (Kol) {self.applicant['kolektibilitas']} tidak memenuhi syarat minimum.")
            return {'risk_level': 'Risiko Tinggi', 'score': 0, 'decision_path': self.decision_path}
        if self.ratios['dti'] >= 60:
            self.decision_path.append(f"[ATURAN KERAS] DTI {self.ratios['dti']:.1f}% melebihi batas aman 60%.")
            return {'risk_level': 'Risiko Tinggi', 'score': 0, 'decision_path': self.decision_path}
        if self.applicant['monthly_income'] <= 0:
            self.decision_path.append("[ATURAN KERAS] Tidak ada pendapatan yang terdeteksi.")
            return {'risk_level': 'Risiko Tinggi', 'score': 0, 'decision_path': self.decision_path}
        self.decision_path.append("[INFO] Lolos dari semua Aturan Keras. Melanjutkan ke proses skoring.")
        return None

    def _calculate_score(self):
        """Calculates the total score by summing points from various factors."""
        self.decision_path.append(f"SKOR AWAL: {self.total_score} poin.")
        scorers = [
            self._score_character, self._score_capacity_dti, self._score_capacity_stability,
            self._score_capacity_dependents, self._score_capital_savings, self._score_collateral_ltv,
            self._score_conditions_loan_purpose, self._score_conditions_stability
        ]
        for scorer in scorers:
            points, reason = scorer()
            self.total_score += points
            self.decision_path.append(reason)

    def _classify_risk(self) -> Dict[str, Any]:
        """Classifies the final risk level based on the total score."""
        score = self.total_score
        if score > 130:
            risk_level = "Risiko Rendah"
        elif 80 <= score <= 130:
            risk_level = "Risiko Sedang"
        else:
            risk_level = "Risiko Tinggi"
        self.decision_path.append(f"SKOR AKHIR {score} → Klasifikasi: {risk_level}")
        return {'risk_level': risk_level, 'score': score, 'decision_path': self.decision_path}

    # --- SCORING HELPER METHODS ---
    # STEP 2: Update the return type hint for all scorer methods

    def _score_character(self) -> Tuple[int, str]:
        kol = self.applicant['kolektibilitas']
        if kol == 1:
            return 25, f"[Karakter] Skor Kolektibilitas 1 (Lancar) menunjukkan riwayat kredit yang sangat baik. Poin: +25"
        elif kol == 2:
            return -30, f"[Karakter] Skor Kolektibilitas 2 (DPK) adalah peringatan signifikan. Poin: -30"
        return 0, ""

    def _score_capacity_dti(self) -> Tuple[int, str]:
        dti = self.ratios['dti']
        if dti <= 35:
            return 20, f"[Kapasitas] DTI sebesar {dti:.1f}% dinilai IDEAL. Poin: +20"
        elif 36 <= dti <= 49:
            return -10, f"[Kapasitas] DTI sebesar {dti:.1f}% dinilai KURANG IDEAL. Poin: -10"
        else:
            return -35, f"[Kapasitas] DTI sebesar {dti:.1f}% dinilai TIDAK IDEAL. Poin: -35"

    def _score_capacity_stability(self) -> Tuple[int, str]:
        status = self.applicant['employment_status']
        if status == 'Pegawai Tetap':
            return 10, f"[Kapasitas] Status 'Pegawai Tetap' menunjukkan stabilitas pendapatan yang tinggi. Poin: +10"
        if status == 'Wiraswasta':
            return 5, f"[Kapasitas] Status 'Wiraswasta' menunjukkan potensi pendapatan, namun dengan volatilitas. Poin: +5"
        if status == 'Pegawai Kontrak':
            return -5, f"[Kapasitas] Status 'Pegawai Kontrak' memiliki risiko pendapatan berhenti. Poin: -5"
        if status == 'Pekerja Lepas/Tidak Tetap':
            return -15, f"[Kapasitas] Status 'Pekerja Lepas' memiliki volatilitas pendapatan tertinggi. Poin: -15"
        return 0, ""

    def _score_capacity_dependents(self) -> Tuple[int, str]:
        dependents = self.applicant['number_of_dependents']
        if dependents == 0:
            return 10, f"[Kapasitas] 0 tanggungan menunjukkan beban pengeluaran yang lebih rendah. Poin: +10"
        if dependents >= 3:
            return -10, f"[Kapasitas] {dependents} tanggungan menunjukkan beban pengeluaran yang signifikan. Poin: -10"
        return 0, f"[Kapasitas] {dependents} tanggungan dinilai sebagai baseline. Poin: +0"

    def _score_capital_savings(self) -> Tuple[int, str]:
        stl = self.ratios['stl']
        if stl >= 50:
            return 15, f"[Modal] Rasio Tabungan/Pinjaman {stl:.1f}% menunjukkan cadangan modal yang kuat. Poin: +15"
        if stl >= 20:
            return 5, f"[Modal] Rasio Tabungan/Pinjaman {stl:.1f}% menunjukkan cadangan modal yang cukup. Poin: +5"
        return -10, f"[Modal] Rasio Tabungan/Pinjaman {stl:.1f}% menunjukkan cadangan modal yang rendah. Poin: -10"

    def _score_collateral_ltv(self) -> Tuple[int, str]:
        ltv = self.ratios['ltv']
        points = 0
        reason = []
        if ltv <= 70:
            points += 20
            reason.append(f"[Jaminan] LTV {ltv:.1f}% sangat rendah, ekuitas pemohon tinggi. Poin: +20")
        elif ltv <= 85:
            points += 5
            reason.append(f"[Jaminan] LTV {ltv:.1f}% berada di level standar. Poin: +5")
        elif ltv <= 100:
            points -= 15
            reason.append(f"[Jaminan] LTV {ltv:.1f}% tinggi, ekuitas pemohon rendah. Poin: -15")
        else:
            points -= 25
            reason.append(f"[Jaminan] LTV {ltv:.1f}% (di atas nilai jaminan) merupakan risiko tinggi. Poin: -25")
        
        if self.applicant['is_first_home_purchase'] and self.applicant['loan_purpose'] == 'KPR (Kredit Pemilikan Rumah)' and ltv > 85:
            points += 10
            reason.append(f"[Jaminan] BONUS: Pembelian rumah pertama mendapat kelonggaran LTV sesuai kebijakan BI. Poin: +10")
        return points, " ".join(reason)
        
    def _score_conditions_loan_purpose(self) -> Tuple[int, str]:
        purpose = self.applicant['loan_purpose']
        if purpose in ['KPR (Kredit Pemilikan Rumah)', 'Modal Usaha']:
            return 10, f"[Kondisi] Tujuan pinjaman '{purpose}' (Produktif/Aset) dinilai positif. Poin: +10"
        if purpose == 'Pendidikan':
            return 5, f"[Kondisi] Tujuan pinjaman '{purpose}' (Investasi Diri) dinilai cukup positif. Poin: +5"
        return -10, f"[Kondisi] Tujuan pinjaman '{purpose}' (Konsumtif) dinilai berisiko lebih tinggi. Poin: -10"
        
    def _score_conditions_stability(self) -> Tuple[int, str]:
        tenure = self.applicant['employment_tenure']
        if tenure == '> 5 tahun':
            return 10, f"[Kondisi] Lama bekerja '{tenure}' menunjukkan stabilitas karir yang sangat tinggi. Poin: +10"
        if tenure == '3-5 tahun':
            return 5, f"[Kondisi] Lama bekerja '{tenure}' menunjukkan stabilitas karir yang baik. Poin: +5"
        if tenure == '< 1 tahun':
            return -10, f"[Kondisi] Lama bekerja '{tenure}' menunjukkan risiko stabilitas. Poin: -10"
        return 0, f"[Kondisi] Lama bekerja '{tenure}' dinilai sebagai baseline. Poin: +0"