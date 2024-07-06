from flask import *
from datetime import datetime, timedelta
from flask_socketio import SocketIO, emit
from fpdf import FPDF
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import scipy.stats as zscore
import io
import base64


app = Flask(__name__)
socketio = SocketIO(app)



status = {
    "Drive_Pedal Sensor": "Normal",
    "Drive_Transmission Pressure": "Normal",
    "Engine_Oil Pressure": "Normal",
    "Engine_Speed": "Normal",
    "Engine_Temparature": "Normal",
    "Fuel_Level": "Normal",
    "Fuel_Pressure": "Normal",
    "Fuel_Water in Fuel": "Normal",
    "Misc_Air Filter Pressure": "Normal",
    "Misc_Exhaust Gas Temparature": "Normal",
    "Misc_Hydraulic Pump Rate": "Normal",
    "Misc_System Voltage": "Normal",
    "Drive_Brake Control": "Normal",
    "Fuel_Temparature": "Normal"
}


app.config["TEMPLATES_AUTO_RELOAD"] = True
app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/", methods=["GET"])
def home():
    if (request.method == "GET"):
        return render_template("home.html")
    
@app.route("/analysis", methods=["GET"])
def analysis():
    if (request.method == "GET"):
        return render_template("analysis.html")
    

@app.route("/analysis/articulated_truck", methods=["GET"])
def articulated_truck():
    if (request.method == "GET"):

        stat = status
        stat['Misc_Exhaust Gas Temperature'] = "Warning"
        stat['Fuel_Temperature'] = "Warning"

        possible_breakdowns = ['Potential breakdown on day 5 due to Misc_Exhaust Gas Temparature: 222.3', 
                               'Potential breakdown on day 8 due to Fuel_Temperature: 20']
        return render_template("articulated_truck.html",status=stat,possible_breakdowns=possible_breakdowns)
    
@app.route("/analysis/asphalt_paver", methods=["GET"])
def asphalt_paver():
    if (request.method == "GET"):
        possible_breakdowns = ['Potential breakdown on day 5 due to Engine_temperature: 107', 
                               'Potential breakdown on day 8 due to Engine_Oil Pressure: 23']
        return render_template("asphalt_paver.html",status=status,possible_breakdowns=possible_breakdowns)

@app.route("/analysis/backhoe_loader", methods=["GET"])
def backhoe_loader():
    if (request.method == "GET"):
        possible_breakdowns = ['Potential breakdown on day 8 due to System_Voltage: 15.4']
        return render_template("backhoe_loader.html",status=status,possible_breakdowns=possible_breakdowns)
    
@app.route("/analysis/dozer", methods=["GET"])
def dozer():
    if (request.method == "GET"):
        return render_template("dozer.html")
    
@app.route("/analysis/excavator", methods=["GET"])
def excavator():
    if (request.method == "GET"):
        return render_template("excavator.html")


feedback_data = {
    'machine_id': '',
    'performance': '',
    'comments': '',
    'power_usage': '',
    'satisfaction': '',
    'safety_incidents': '',
    'emissions': '',
    'downtime': '',
    'user_friendly': '',
    'training_ease': ''
}

@app.route('/customer_feedback')
def customer_feedback():
    return render_template('customer_feedback.html')

@socketio.on('submit')
def handle_submit(data):
    feedback_data.update(data)
    emit('response', {'message': 'Feedback received. You can now export it as a PDF.', 'status': 'complete'})

@app.route('/export')
def export_feedback():
    class PDF(FPDF):
        def header(self):
            # Logo
            
            # Address
            self.set_xy(150, 10)
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Caterpillar Hackathon\'24', 0, 1, 'R')
            self.cell(0, 13, 'PSG CT, Coimbatore, 641-045', 0, 1, 'R')
            self.cell(0, 16, 'Phone: +xxxxxxxxxx', 0, 1, 'R')
            self.ln(20)
        
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, 0, 1, 'C')
            self.ln(10)
        
        def feedback_table(self, data):
            self.set_font('Arial', '', 12)
            self.cell(0, 10, 'Feedback Summary', 0, 1, 'C')
            self.ln(10)
            self.set_font('Arial', '', 10)
            col_width = self.w / 2.5
            row_height = self.font_size + 2
            for key, value in data.items():
                self.cell(col_width, row_height, key.replace('_', ' ').capitalize(), border=1)
                self.cell(col_width, row_height, value, border=1)
                self.ln(row_height)
    
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title('Machine Performance Feedback')
    pdf.feedback_table(feedback_data)
    
    pdf_file = "feedback.pdf"
    pdf.output(pdf_file)
    
    return send_file(pdf_file, as_attachment=True, download_name='feedback.pdf')

if __name__ == '__main__':
    socketio.run(app, debug=True)



# Function to detect anomalies (example using z-score)
def detect_anomalies(data, threshold=5):
    mean = np.mean(data)
    std_dev = np.std(data)
    lower_bound = mean - threshold * std_dev
    upper_bound = mean + threshold * std_dev
    anomalies = data[(data < lower_bound) | (data > upper_bound)]
    return anomalies.index.tolist()

# Function to suggest fixes based on detected anomalies
def suggest_fixes(anomalies):
    fixes = {
        "Drive_Pedal Sensor": "Check sensor calibration or potential sensor malfunction.",
        "Drive_Transmission Pressure": "Inspect for leaks or mechanical issues in the transmission system.",
        "Engine_Oil Pressure": "Verify oil levels and pressure sensor functionality.",
        "Engine_Speed": "Check engine control unit (ECU) readings and sensor accuracy.",
        "Engine_Temparature": "Monitor cooling system performance and sensor readings.",
        "Fuel_Level": "Verify fuel gauge readings and fuel level sensor integrity.",
        "Fuel_Pressure": "Inspect fuel system components and pressure sensor calibration.",
        "Fuel_Water in Fuel": "Ensure proper fuel filtration and drainage system functionality.",
        "Misc_Air Filter Pressure": "Check air filter condition and pressure sensor calibration.",
        "Misc_Exhaust Gas Temparature": "Monitor exhaust system performance and sensor readings.",
        "Misc_Hydraulic Pump Rate": "Inspect hydraulic system for leaks or pump performance issues.",
        "Misc_System Voltage": "Verify battery condition and charging system operation.",
        "Drive_Brake Control": "Check brake system components and sensor readings.",
        "Fuel_Temparature": "Monitor fuel temperature sensor readings and fuel heating system."
    }
    return {col: fixes[col] for col in anomalies}



@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    path = r'static/normal.xlsx'

    df = pd.read_excel(path)

    feature_columns = []
    
    timestamp_column = 'Time'
    feature_columns = df.columns.difference([timestamp_column]).tolist()  # Exclude Timestamp column
    
    plot_url = ""
    abnormal_sentence = ""
    fix_sentence = ""
            
    selection = request.form.get('feature')
    
    # Detect abnormal values
    abnormal_values = {}
    for feature in feature_columns:
        if df[feature].dtype in [np.float64, np.float32]:  # Check if column is numeric
            anomalies = detect_anomalies(df[feature])
            abnormal_values[feature] = anomalies
    
    # Generate sentences for abnormal values and suggest fixes
    if selection and selection in abnormal_values and len(abnormal_values[selection]) > 0:
        abnormal_times = df.loc[abnormal_values[selection], timestamp_column].tolist()
        abnormal_sentence = f"{selection} is abnormal at " + ", ".join([str(time) for time in abnormal_times])
        
        fixes = suggest_fixes([selection])
        fix_sentence = fixes[selection]
        
        # Plotting
        plt.figure(figsize=(8, 6))
        plt.plot(df[timestamp_column], df[selection], marker='o', linestyle='-', color='b')
        plt.title(f"Anomalies in {selection}")
        plt.xlabel("Timestamp")
        plt.ylabel(selection)
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

    return render_template('visualize.html', plot_url=plot_url, abnormal_sentence=abnormal_sentence, fix_sentence=fix_sentence, feature_columns=feature_columns)
