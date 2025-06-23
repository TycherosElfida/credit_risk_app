from flask import Flask, render_template, request
from expert_system.engine import CreditRiskExpertSystem

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main input form page."""
    # We render the new index.html which is styled with Tailwind CSS
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Process the form data and display the evaluation result."""
    
    # --- DATA GATHERING AND TYPE CONVERSION ---
    # We now gather all the new fields from our redesigned form.
    # It's crucial to convert strings from the form into the correct numeric types (int/float).
    
    try:
        applicant_data = {
            # Character & Personal Info
            'kolektibilitas': int(request.form['kolektibilitas']),
            'age': int(request.form['age']),
            'marital_status': request.form['marital_status'],
            'number_of_dependents': int(request.form['number_of_dependents']),
            
            # Capacity & Employment
            'monthly_income': float(request.form['monthly_income']),
            'monthly_debt': float(request.form['monthly_debt']),
            'employment_status': request.form['employment_status'],
            'employment_tenure': request.form['employment_tenure'],
            
            # Capital, Collateral & Conditions
            'loan_amount': float(request.form['loan_amount']),
            'loan_purpose': request.form['loan_purpose'],
            'collateral_value': float(request.form['collateral_value']),
            'savings_balance': float(request.form['savings_balance']),
            
            # Handling the checkbox (boolean value)
            # If the checkbox is checked, 'is_first_home_purchase' will be in the form data.
            # If it's not checked, it won't be present. This is a clean way to get a True/False value.
            'is_first_home_purchase': 'is_first_home_purchase' in request.form
        }

        # --- EXPERT SYSTEM EVALUATION ---
        expert_system = CreditRiskExpertSystem(applicant_data)
        result = expert_system.evaluate()
        
        # We will create 'result.html' in the next step.
        return render_template('result.html', result=result, applicant=applicant_data)

    except (KeyError, ValueError) as e:
        # Basic error handling if a field is missing or has a wrong data type
        # In a real-world app, you might want a more user-friendly error page.
        return f"Terjadi kesalahan: Data tidak lengkap atau format salah. Pastikan semua field terisi. Error: {e}", 400


if __name__ == '__main__':
    app.run(debug=True)