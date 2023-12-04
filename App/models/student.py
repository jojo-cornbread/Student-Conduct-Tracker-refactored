from App.database import db
from .user import User


class Student(db.Model):
	__tablename__ = 'student'

	firstname = db.Column(db.String(120), nullable=False)
	lastname = db.Column(db.String(120), nullable=False)
  	# password = db.Column(db.String(120), nullable=False)

	ID = db.Column(db.String(10), primary_key=True)
	contact = db.Column(db.String(30), nullable=False)
	studentType = db.Column(db.String(30))  #full-time, part-time or evening
	yearOfStudy = db.Column(db.Integer, nullable=False)
	
	reviews = db.relationship('Review', backref='student', lazy='joined')

	karmaID = db.Column(db.Integer, db.ForeignKey('karma.karmaID', name='fk_karmaID', use_alter=True))

	# karma = db.relationship('Karma', backref='student', lazy='joined', foreign_keys=[karmaID])

	# karma = db.relationship('Karma', backref='student', lazy='joined')
	# karma = db.relationship('Karma', back_populates='student', foreign_keys=[karmaID])


  #When student is newly created there would be no reviews or karma yet
	def __init__(self, studentID, firstname, lastname, contact, studentType, yearofStudy):

		# super().__init__(firstname, lastname, password)
		self.firstname = firstname
		self.lastname = lastname

		self.ID = studentID
		self.contact = contact
		self.studentType = studentType
		self.yearOfStudy = yearofStudy
		self.reviews = []
	
	def get_id(self):
		return self.ID

#Gets the student details and returns in JSON format
	def to_json(self):
		karma = self.getKarma()
		return {
        "studentID": self.ID,
        "firstname": self.firstname,
        "lastname": self.lastname,
        "contact": self.contact,
        "studentType": self.studentType,
        "yearOfStudy": self.yearOfStudy,
        "reviews": [review.to_json() for review in self.reviews],
				"karmaScore": karma.score if karma else None,
        "karmaRank": karma.rank if karma else None,
    }

#get karma record from the karma table using the karmaID attached to the student
	def getKarma(self):
		from .karma import Karma
		return Karma.query.get(self.karmaID)
