from App.database import db
from .student import Student
from .staff import Staff
from .user import User

class Admin(User):
	ID= db.Column(db.String, primary_key= True)

	def __init__(self, firstname, lastname, password):
		super().__init__(firstname, lastname, password)
		self.ID = "A" + str(Admin.query.count() + 1)

	def get_id(self):
		return self.ID

	#add student to the database
	def addStudent(self, id, firstname, lastname, contact, studentType, yearofStudy):
		newStudent= Student(id, firstname, lastname, contact, studentType, yearofStudy)
		try: # catch any errors when trying to add a student that already exists
			db.session.add(newStudent)
			db.session.commit()  # Commit to save the new student to the database
			return newStudent 
		except:
			db.session.rollback()
			return None

	# add staff to the database
	def addStaff(self, id, firstname, lastname, password, email, teachingExperience):
		newStaff= Staff(id, firstname, lastname, password, email, teachingExperience)
		try: # safetey measure for trying to add duplicate staff
			db.session.add(newStaff)
			db.session.commit()  # Commit to save the new staff to the database
			return newStaff
		except:
			db.session.rollback()
			return None

	#takes a studentID, string for field_to_update and new_value . Updates the  relative field for the student
	def updateStudent(self, studentID, field_to_update, new_value):
		# List of fields that can be updated for a student record
		allowed_fields = ["ID", "contact", "firstname", "lastname", "studenttype", "yearofstudy"]

		# Normalize the input field name by converting it to lowercase and replacing '-', '_', ' ' with ''
		input_field = field_to_update.lower().replace('-', '').replace('_', '').replace(' ', '')

	# Retrieve the student record based on student id
		student = Student.query.filter_by(ID=studentID).first()

		if student is None:
			return "Student not found"

		# Check if the specified field exists in the Student model, change column names on model to lowercase so that it could be compared to the normalized input
		found_field = None
		for field in Student.__table__.columns.keys():
			if field.lower() == input_field:
				found_field = field
				break

		if found_field is None:
			return f"Field '{field_to_update}' does not exist for Student"

		# Check if the specified field is in the list of editable fields
		if input_field not in allowed_fields:
			return f"Field '{field_to_update}' cannot be updated for Student"

		# Update the specified field with the new value
		setattr(student, found_field, new_value)

		# Commit to save the changes
		db.session.add(student)
		db.session.commit()
		return True
	
	def to_json(self):
		return {
	        "adminID": self.ID,
    	    "firstname": self.firstname,
        	"lastname": self.lastname,
    	}
