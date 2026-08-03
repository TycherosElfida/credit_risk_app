# Credit Risk Classification

A decision-tree expert system that sorts loan applicants into three risk tiers, served through a Flask web interface.

**~96% test accuracy** on a 2,000-record financial dataset.

---

## The problem

Credit risk scoring is a domain where the *reason* for a decision matters as much as the decision itself — an applicant refused credit is entitled to know why, and a loan officer needs to be able to defend the call. That constraint rules out most black-box classifiers.

## Approach

A **C4.5-style decision tree**, chosen deliberately over higher-accuracy alternatives:

- Every classification traces to a readable rule path, so a decision can be explained in plain language rather than as a probability with no provenance.
- Information-gain-ratio splitting handles the mixed categorical/continuous attributes typical of financial application data without heavy preprocessing.
- The learned tree is inspectable — you can read the model itself and sanity-check whether it has picked up sensible financial logic or a spurious correlation.

Applicants are sorted into three tiers rather than a binary approve/reject, which leaves room for a manual-review band instead of forcing marginal cases to one extreme.

## Results

| Metric | Value |
|---|---|
| Test accuracy | ~96% |
| Dataset | 2,000 records |
| Output classes | 3 risk tiers |

<!-- Optional, if you have the numbers: add per-class precision/recall here.
     Accuracy alone can hide poor performance on a minority tier. -->

## Running it

```bash
git clone https://github.com/sanderskeaned/credit_risk_app.git
cd credit_risk_app

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 and submit an applicant profile through the form to get a risk tier back.

## Structure

```
credit_risk_app/
├── app.py             # Flask entry point and routes
├── expert_system/     # Decision tree model and classification logic
├── templates/         # HTML views
├── Static/css/        # Styling
└── requirements.txt
```

## What I would do differently

- **Validation is thin.** A single train/test split reports one number; k-fold cross-validation with per-class precision and recall would say considerably more, particularly about the middle tier.
- **No class-imbalance handling.** If the risk tiers are unevenly distributed — and in credit data they usually are — headline accuracy flatters the model. Stratified splits and a confusion matrix would expose that.
- **No baseline comparison.** Benchmarking against logistic regression and a random forest would establish whether the interpretability of the tree costs any real accuracy, which is the trade-off actually worth measuring.

---

Built as part of an expert-systems course. Not intended for production lending decisions.
