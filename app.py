from flask import Flask, render_template, redirect, url_for
import AttendanceProject  # Import your existing functionality
import csv
app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to start webcam-based attendance
@app.route('/start_attendance', methods=['GET'])
def start_attendance():
    AttendanceProject.start_attendance_system()  # Correct function name
    return redirect(url_for('index'))

# Route to view results and stop camera
@app.route('/view_results')
def view_results():
    results = []
    with open('Attendance_Result.csv', 'r') as f:
        reader = csv.reader(f)
        results = [line for line in reader]
    return render_template('results.html', results=results[1:]) 
    # Stop camera
    AttendanceProject.cap.release()  # Assuming 'cap' is the video capture object
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
