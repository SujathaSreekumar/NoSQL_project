from flask import Flask, render_template, request
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['student_marks']
collection = db['marks']




# Home Page
@app.route("/")
def home():
    return render_template("home.html")




# Display the list of Students and Roll No
@app.route("/display_students")
def display_students():
    records = collection.find()
    return render_template("display_students.html",records=records)




# Add marks of Students
@app.route("/add_marks", methods=['GET','POST'])
def add_marks():
    if(request.method == "GET"):
        return render_template("add_marks.html")
    elif(request.method == "POST"):
        # getting fields data from the form
        name = request.form['name']
        roll = request.form['roll']
        gender = request.form['gender']
        maths = int(request.form['maths'])
        english = int(request.form['english'])
        physics = int(request.form['physics'])
        chemistry = int(request.form['chemistry'])
        biology = int(request.form['biology'])

        record = {
            'name': name,
            'roll': roll,
            'gender': gender,
            'maths': maths,
            'english': english,
            'physics': physics,
            'chemistry': chemistry,
            'biology': biology
        }
        try:
            collection.insert_one(record)
        except:
            print("Something went wrong!")
            return render_template("home.html")

        return render_template("home.html")




# Edit the marks of Students
@app.route("/edit_marks", methods=['GET','POST'])
def edit_marks():
    if(request.method == 'GET'):
        return render_template("edit_marks.html")
    elif(request.method == 'POST'):
        # getting fields data from the form
        name = request.form['name']
        roll = request.form['roll']
        maths = int(request.form['maths'])
        english = int(request.form['english'])
        physics = int(request.form['physics'])
        chemistry = int(request.form['chemistry'])
        biology = int(request.form['biology'])

        try:
            collection.update_one(
                {'roll' : roll, 'name': name},
                {
                    '$set' :{
                        'maths': maths,
                        'english': english,
                        'physics': physics,
                        'chemistry': chemistry,
                        'biology': biology

                    }
                }
            )
        except:
            print("Something went wrong!")
            return render_template("home.html")


        return render_template("home.html")




# Returns the percentage marks of the Student
@app.route("/percentage_marks", methods = ['GET','POST'])
def percentage_marks():
      if (request.method == 'GET'):
          return render_template("percentage_marks.html")
      elif(request.method == 'POST'):
        # getting fields data from the form
        name = request.form['name']
        roll = request.form['roll']

        try:
            stud = list(collection.aggregate([
                {
                    '$match':{'roll':roll, 'name':name}
                },
                {
                    '$addFields':{
                        'total_marks': {
                            '$sum':['$maths','$english','$physics','$chemistry','$biology']
                        }
                    }
                },
                {
                    '$addFields':{
                        'total_percentage':{
                            '$divide':['$total_marks',5]
                        }

                    }
                }
            ]))
            stud_detail = {}
            stud_detail = stud[0]
            total_marks = stud_detail['total_marks']
            total_percentage = stud_detail['total_percentage']
            

            return render_template("display_percentage.html",name=name,roll=roll,total_marks=total_marks,total_percentage=total_percentage)

        except:
            print("No Record Found!")
            return render_template("home.html")
          



# Returns the percentile the Student is in
@app.route("/percentile_marks", methods = ['GET','POST'])
def percentile_marks():
    if (request.method == 'GET'):
        return render_template("percentile_marks.html")
    elif(request.method == 'POST'):
        # getting fields data from the form
        name = request.form['name']
        roll = request.form['roll']

        try:
            # Get the target student
            target_student = collection.find_one({'name': name, 'roll': roll})
            
            # Get the total number of students
            total_students = collection.count_documents({})

            # Sort the student records by total marks in descending order
            pipeline = [
                {
        
                    '$project': {
                        'name': 1,
                        'roll': 1,
                        'total_marks': {
                            '$sum': ['$maths', '$english', '$physics', '$chemistry', '$biology']
                        }
                    }
                },
                {
                    '$sort': {'total_marks': -1}
                }
            ]
            sorted_students = list(collection.aggregate(pipeline))
            total_marks_list = [doc['total_marks'] for doc in sorted_students]

            # Find the percentile of the target student
            for student in sorted_students:
                if student['_id'] == target_student['_id']:
                    target_total_marks = student['total_marks']
                    students_less_than_target = len([marks for marks in total_marks_list if marks <= target_total_marks])
                    break
            
            # Calculate the percentile
            percentile = np.round(( students_less_than_target / total_students) * 100,0)

            return render_template("display_percentile.html", percentile=percentile, name=name, roll=roll, target_total_marks=target_total_marks)
               
            
        except:
            print("Something went wrong!")
            return render_template("home.html")
           
 


# Returns the class topper from the entire list of Students
@app.route("/class_topper")
def class_topper():
    # Sort the student records by total marks in descending order
    pipeline = [
        {
            
            '$project': {
                'name': 1,
                'roll': 1,
                'total_marks': {
                    '$sum': ['$maths', '$english', '$physics', '$chemistry', '$biology']
                }
            }
        },
        {
            '$sort': {'total_marks': -1}
        }
    ]
    sorted_students = list(collection.aggregate(pipeline))
    total_marks_list = [doc['total_marks'] for doc in sorted_students]

    list_of_toppers = []

    # Calculate class topper
    for student in sorted_students:
        if student['total_marks'] == total_marks_list[0]:
            list_of_toppers.append(student)

    return render_template("class_topper.html",list_of_toppers=list_of_toppers)




# Deletes the entire record of the particular Student
@app.route("/delete_student", methods=['GET','POST'])
def delete_student():
    if (request.method == 'GET'):
        return render_template("delete_student.html")
    elif(request.method == 'POST'):
        # getting fields data from the form
        name = request.form['name']
        roll = request.form['roll']
        
        try:
            collection.delete_one({'name': name, 'roll' : roll})
        except:
            print("Something went wrong!")
            return render_template("home.html")
        

        return render_template("home.html")




if __name__ == "__main__":
    app.run(debug=True)