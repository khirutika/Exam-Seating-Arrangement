from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

departments = []
students = []
halls = {}
hall_teachers = {}

current_hall_id = 1


# Step 1: Get number of departments
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['num_departments'] = int(request.form['num_departments'])
        return redirect(url_for('department_form', dept_id=1))
    return render_template('index.html')


# Step 2: Department Details Form
@app.route('/department_form/<int:dept_id>', methods=['GET', 'POST'])
def department_form(dept_id):
    if request.method == 'POST':
        department_name = request.form['department_name']
        start_reg = int(request.form['start_register_number'])
        end_reg = int(request.form['end_register_number'])
        lateral_entry = request.form['lateral_entry']
        lateral_numbers = request.form['lateral_numbers'].split(",") if lateral_entry == 'yes' else []

        student_list = [{'register_number': str(i), 'department': department_name} for i in range(start_reg, end_reg + 1)]
        for lateral in lateral_numbers:
            student_list.append({'register_number': lateral.strip(), 'department': department_name})

        departments.append({'name': department_name, 'students': student_list})
        students.extend(student_list)

        if dept_id < session['num_departments']:
            return redirect(url_for('department_form', dept_id=dept_id + 1))
        else:
            return redirect(url_for('generate_seating'))

    return render_template('department_form.html', dept_id=dept_id)


# Step 3: Generate Seating Arrangement with Alternating Students
@app.route('/generate_seating')
def generate_seating():
    global halls, current_hall_id
    halls.clear()
    current_hall_id = 1

    department_students = {dept['name']: sorted(dept['students'], key=lambda x: int(x['register_number'])) for dept in departments}
    department_names = list(department_students.keys())

    if len(department_names) < 2:
        return "At least two departments are required for seating arrangement."

    unallocated_students = []

    # Pair departments and alternate students
    while len(department_names) >= 2:
        dept1, dept2 = department_names.pop(0), department_names.pop(0)
        students1 = department_students[dept1]
        students2 = department_students[dept2]

        # Alternate seating: CSE 1, EEE 1, CSE 2, EEE 2
        combined_students = []
        max_len = max(len(students1), len(students2))

        for i in range(max_len):
            if i < len(students1):
                combined_students.append(students1[i])
            if i < len(students2):
                combined_students.append(students2[i])

        unallocated_students.extend(combined_students)

    # Add remaining students from any unmatched department
    for dept in department_names:
        unallocated_students.extend(department_students[dept])

    # Allocate students to halls (25 per hall)
    while unallocated_students:
        halls[current_hall_id] = {'students': unallocated_students[:25]}
        unallocated_students = unallocated_students[25:]
        current_hall_id += 1

    session['halls'] = halls
    return redirect(url_for('assign_teachers'))


# Step 4: Assign Teachers
@app.route('/assign_teachers', methods=['GET', 'POST'])
def assign_teachers():
    if request.method == 'POST':
        teacher_names = request.form.getlist('teacher_name[]')
        teacher_departments = request.form.getlist('teacher_department[]')

        for hall_id, teacher_name in enumerate(teacher_names, start=1):
            if hall_id in halls:
                hall_teachers[hall_id] = {
                    'teacher_name': teacher_name,
                    'teacher_department': teacher_departments[hall_id - 1]
                }

        return redirect(url_for('view_seating'))

    return render_template('assign_teachers.html', halls=halls)


# Step 5: View Seating Arrangement
@app.route('/view_seating')
def view_seating():
    return render_template('seating_arrangement.html', halls=halls, hall_teachers=hall_teachers)


# Reset Data
@app.route('/clear')
def clear_data():
    global departments, students, halls, hall_teachers, current_hall_id
    departments.clear()
    students.clear()
    halls.clear()
    hall_teachers.clear()
    current_hall_id = 1
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)






















