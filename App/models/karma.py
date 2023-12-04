from App.database import db
from .student import Student


class Karma(db.Model):
  __tablename__ = "karma"
  karmaID = db.Column(db.Integer, primary_key=True)
  score = db.Column(db.Float, nullable=False, default=0.0)
  rank = db.Column(db.Integer, nullable=False, default=-99)

  

  def __init__(self, score=0.0, rank=-99):
    self.score = score
    self.rank = rank

  def to_json(self):
    return {"karmaID": self.karmaID, "score": self.score, "rank": self.rank}

# Calculate the karma score for the provided student based on reviews

  def calculateScore(self, student):
    goodKarma = 0
    badKarma = 0

    # Iterate through reviews associated with the student
    for review in student.reviews:
      if review.isPositive == True:  #if review is positive then upvotes on the review contributes to good karma
        goodKarma += review.upvotes
        badKarma += review.downvotes
      else:  #if review is not positive then upvotes on the review contributes to bad karma
        badKarma += review.upvotes
        goodKarma += review.downvotes

# Calculate the karma score
    self.score = goodKarma - badKarma

    # connect the karma record to the student
    student.karmaID = self.karmaID

    # Commit the changes to the database
    db.session.add(self)
    db.session.commit()

    return self.score

  @classmethod
  def updateRank(cls):
    # Calculate the rank of students based on their karma score

    # Query all students with karma scores in descending order
    studentsOrdered = db.session.query(Student, Karma)\
               .join(Karma, Student.karmaID == Karma.karmaID)\
               .order_by(db.desc(Karma.score))\
               .all()

    rank = 1
    prev_score = None

    #assign ranks to student with the highest karma at the top
    for student, karma in studentsOrdered:
      if prev_score is None:
        prev_score = karma.score
        karma.rank = rank
      elif prev_score == karma.score:
        karma.rank = rank
      else:
        rank += 1
        karma.rank = rank
        prev_score = karma.score

      student.karmaID = karma.karmaID

  # Commit the changes to the database
    db.session.commit()

  @classmethod
  def getScore(cls, karmaID):
    # Retrieve the karma score by karma id
    karma = cls.query.filter_by(karmaID=karmaID).first()
    if karma:
      return karma.score
    return None
