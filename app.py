# app.py
from flask import Flask, render_template, request, flash
from expert_system.engine import CreditRiskExpertSystem, LoanApplicant

app = Flask(__name__)
# A secret key is required for flashing messages
app.secret_key = 'your_super_secret_key' # Change this to a random string

@app.route('/', methods=['GET'])
def index():
    """Renders the main input form page."""
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    Handles the form submission, processes the data,
    and displays the evaluation result.
    """
    try:
        # 1. Collect and sanitize form data
        form_data = LoanApplicant(
            age=int(request.form['age']),
            marital=str(request.form['marital']),
            emp_status=str(request.form['emp_status']),
            emp_tenure=str(request.form['emp_tenure']),
            income=float(request.form['income']),
            total_debt=float(request.form['total_debt']),
            loan_amt=float(request.form['loan_amt']),
            collateral_val=float(request.form['collateral_val']),
            savings_bal=float(request.form['savings_bal']),
            credit_score=int(request.form['credit_score']),
            late_hist=str(request.form['late_hist']),
        )

        # 2. Instantiate the expert system and run the evaluation
        expert_system = CreditRiskExpertSystem()
        risk, path = expert_system.evaluate(form_data)

        # 3. Render the result page with the output
        return render_template('result.html', risk=risk, path=path, applicant_data=form_data)

    except (ValueError, KeyError) as e:
        # Handle cases where form data is missing or has the wrong type
        flash(f'Error: Input tidak valid atau tidak lengkap. Pastikan semua field terisi dengan benar. Detail: {e}', 'error')
        return render_template('index.html')

if __name__ == '__main__':
    # debug=True is great for development, but should be False in production
    app.run(debug=True)