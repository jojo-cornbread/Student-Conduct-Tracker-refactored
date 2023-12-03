from App.database import db
from .student import Student
from datetime import datetime
from .karma import Karma

# from abc import ABC, abstractmethod
from .vote_strategies import VoteStrategy, UpvoteStrategy, DownvoteStrategy

# Define the association table for staff upvotes on reviews
review_staff_upvoters = db.Table(
    'review_staff_upvoters',
    db.Column('reviewID', db.Integer, db.ForeignKey('review.ID')),
    db.Column('staffID', db.String(10), db.ForeignKey('staff.ID')),
)

review_staff_downvoters = db.Table(
    'review_staff_downvoters',
    db.Column('reviewID', db.Integer, db.ForeignKey('review.ID')),
    db.Column('staffID', db.String(10), db.ForeignKey('staff.ID')),
)


class Review(db.Model):
  __tablename__ = 'review'
  ID = db.Column(db.Integer, primary_key=True)
  reviewerID = db.Column(
      db.String(10),
      db.ForeignKey('staff.ID'))  #each review has 1 creator

  #create reverse relationship from Staff back to Review to access reviews created by a specific staff member
  reviewer = db.relationship('Staff',
                             backref=db.backref('reviews_created',
                                                lazy='joined'),
                             foreign_keys=[reviewerID])

  studentID = db.Column(db.String(10), db.ForeignKey('student.ID'))

  staffUpvoters = db.relationship(
      'Staff',
      secondary=review_staff_upvoters,
      backref=db.backref(
          'reviews_upvoted',
          lazy='joined'))  #for staff who have voted on the review

  staffDownvoters = db.relationship(
      'Staff',
      secondary=review_staff_downvoters,
      backref=db.backref(
          'reviews_downvoted',
          lazy='joined'))  #for staff who have voted on the review

  upvotes = db.Column(db.Integer, nullable=False)
  downvotes = db.Column(db.Integer, nullable=False)
  isPositive = db.Column(db.Boolean, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  comment = db.Column(db.String(400), nullable=False)

  # Strategy instance for voting (initially set to UpvoteStrategy)
  vote_strategy = UpvoteStrategy()

  # initialize the review. when it is created the date is automatically gotten and votes are at 0
  def __init__(self, reviewer, student, isPositive, comment):
    self.reviewerID = reviewer.ID
    self.reviewer = reviewer
    self.studentID = student.ID
    self.isPositive = isPositive
    self.comment = comment
    self.upvotes = 0
    self.downvotes = 0
    self.created = datetime.now()

  def get_id(self):
    return self.ID

# Method to set the voting strategy (can be called to switch between upvoting and downvoting)
  def set_vote_strategy(self, strategy:VoteStrategy):
    self.vote_strategy = strategy


# Method to perform the vote using the current strategy
  def vote(self, staff):
    return self.vote_strategy.vote(self, staff)


#allows the comment and whether the review is positive to be edited if the staff member is the creator of the review, returns none if not

  def editReview(self, staff, isPositive, comment):
    if self.reviewer == staff:
      self.isPositive = isPositive
      self.comment = comment
      db.session.add(self)
      db.session.commit()
      return True
    return None

  #deletes the review when called if the staff memeber is the creator of the review, return none if not

  def deleteReview(self, staff):
    if self.reviewer == staff:
      db.session.delete(self)
      db.session.commit()
      return True
    return None

  #adds 1 to the upvotes for the review when called
  # def upvoteReview(self, staff): 
  #   if staff in self.staffUpvoters:  # If they upvoted the review already, return current votes
  #     return self.upvotes

  #   else:
  #     if staff not in self.staffUpvoters:  #if staff has not upvoted allow the vote
  #       self.upvotes += 1
  #       self.staffUpvoters.append(staff)

  #       if staff in self.staffDownvoters:  #if they had downvoted previously then remove their downvote to account for switching between votes
  #         self.downvotes -= 1
  #         self.staffDownvoters.remove(staff)

  #     db.session.add(self)
  #     db.session.commit()

  #     # Retrieve the associated Student object using studentID
  #     student = Student.query.get(self.studentID)

  #     # Check if the student has a Karma record (karmaID) and create a new Karma record for them if not
  #     if student.karmaID is None:
  #       karma = Karma(score=0.0, rank=-99)
  #       db.session.add(karma)  # Add the Karma record to the session
  #       db.session.flush()  # Ensure the Karma record gets an ID
  #       student.karmaID = karma.karmaID  # Set the student's karmaID to the new Karma record's ID

  #     # Update Karma for the student
  #     student_karma = Karma.query.get(student.karmaID)
  #     student_karma.calculateScore(student)
  #     student_karma.updateRank()
  #     db.session.commit()

  #   return self.upvotes

  # #adds 1 to the downvotes for the review when called

  # def downvoteReview(self, staff): 
  #   if staff in self.staffDownvoters:  # If they downvoted the review already, return current votes
  #     return self.downvotes

  #   else:
  #     if staff not in self.staffDownvoters:  #if staff has not downvoted allow the vote
  #       self.downvotes += 1
  #       self.staffDownvoters.append(staff)

  #       if staff in self.staffUpvoters:  #if they had upvoted previously then remove their upvote to account for switching between votes
  #         self.upvotes -= 1
  #         self.staffUpvoters.remove(staff)

  #     db.session.add(self)
  #     db.session.commit()
  #     # Retrieve the associated Student object using studentID
  #     student = Student.query.get(self.studentID)

  #     # Check if the student has a Karma record (karmaID) and create a new Karma record for them if not
  #     if student.karmaID is None:
  #       karma = Karma(score=0.0, rank=-99)
  #       db.session.add(karma)  # Add the Karma record to the session
  #       db.session.flush()  # Ensure the Karma record gets an ID
  #       db.session.commit()
  #       student.karmaID = karma.karmaID  # Set the student's karmaID to the new Karma record's ID

  # # Update Karma for the student
  #     student_karma = Karma.query.get(student.karmaID)
  #     student_karma.calculateScore(student)
  #     student_karma.updateRank()

  #   return self.downvotes

  #return json representation of the review

  def to_json(self):
    return {
        "reviewID": self.ID,
        "reviewer": self.reviewer.firstname + " " + self.reviewer.lastname,
        "studentID": self.student.ID,
        "studentName": self.student.firstname + " " + self.student.lastname,
        "created":
        self.created.strftime("%d-%m-%Y %H:%M"),  #format the date/time
        "isPositive": self.isPositive,
        "upvotes": self.upvotes,
        "downvotes": self.downvotes,
        "comment": self.comment
    }

# TEMP CODE FOR IMPLEMENTING THE STRATEGY DESIGN PATTERN
# MOVE TO SEPERATE MODEL FILES AFTER

# # Define the strategy interface
# class VoteStrategy(ABC):
#     @abstractmethod
#     def vote(self, review, staff):
#         pass

# # Concrete strategy for upvoting
# class UpvoteStrategy(VoteStrategy):
#     def vote(self, review, staff):
#         if staff in review.staffUpvoters:
#             return review.upvotes
#         else:
#             if staff not in review.staffUpvoters:
#                 review.upvotes += 1
#                 review.staffUpvoters.append(staff)

#                 if staff in review.staffDownvoters:
#                     review.downvotes -= 1
#                     review.staffDownvoters.remove(staff)

#             db.session.add(review)
#             db.session.commit()

#             # ... (rest of your code for updating Karma)
#             # Retrieve the associated Student object using studentID
#             student = Student.query.get(self.studentID)

#             #  check if the student has a karma record (KarmaID) and create a new Karma record for them if not
#             if student.karmaID is None:
#               karma = Karma(score=0.0, rank=-99)
#               db.session.add(karma) # Add the Karma record to the session
#               db.session.flush() # Ensure the KArma record gets an ID
#               student.karmaID = karma.karmaID # Set the student's KArmaID to the new KArma record's ID

#               # Update Karma for the student
#               student_karma = Karma.query.get(student.karmaID)
#               student_karma.calculateScore(student)
#               student_karma.updateRank()
#               db.session.commit()

#         return review.upvotes

# # Concrete strategy for downvoting
# class DownvoteStrategy(VoteStrategy):
#     def vote(self, review, staff):
#         if staff in review.staffDownvoters:
#             return review.downvotes
#         else:
#             if staff not in review.staffDownvoters:
#                 review.downvotes += 1
#                 review.staffDownvoters.append(staff)

#                 if staff in review.staffUpvoters:
#                     review.upvotes -= 1
#                     review.staffUpvoters.remove(staff)

#             db.session.add(review)
#             db.session.commit()

#             # ... (rest of your code for updating Karma)
#             # Retrieve the associated Student object using studentID
#             student = Student.query.get(self.studentID)

#             #  check if the student has a karma record (KarmaID) and create a new Karma record for them if not
#             if student.karmaID is None:
#               karma = Karma(score=0.0, rank=-99)
#               db.session.add(karma) # Add the Karma record to the session
#               db.session.flush() # Ensure the KArma record gets an ID
#               student.karmaID = karma.karmaID # Set the student's KArmaID to the new KArma record's ID

#               # Update Karma for the student
#               student_karma = Karma.query.get(student.karmaID)
#               student_karma.calculateScore(student)
#               student_karma.updateRank()
#               db.session.commit()

#         return review.downvotes
