from App.database import db
from App.models.student import Student  # Make sure to adjust the import path accordingly
from App.models.karma import Karma

from abc import ABC, abstractmethod

# Define the strategy interface
class VoteStrategy(ABC):
    @abstractmethod
    def vote(self, review, staff):
        pass

# Concrete strategy for upvoting
class UpvoteStrategy(VoteStrategy):
    def vote(self, review, staff):
        if staff in review.staffUpvoters:
            return review.upvotes
        else:
            if staff not in review.staffUpvoters:
                review.upvotes += 1
                review.staffUpvoters.append(staff)

                if staff in review.staffDownvoters:
                    review.downvotes -= 1
                    review.staffDownvoters.remove(staff)

            db.session.add(review)
            db.session.commit()

            # ... (rest of your code for updating Karma)
            # Retrieve the associated Student object using studentID
            student = Student.query.get(self.studentID)

            #  check if the student has a karma record (KarmaID) and create a new Karma record for them if not
            if student.karmaID is None:
              karma = Karma(score=0.0, rank=-99)
              db.session.add(karma) # Add the Karma record to the session
              db.session.flush() # Ensure the KArma record gets an ID
              student.karmaID = karma.karmaID # Set the student's KArmaID to the new KArma record's ID

              # Update Karma for the student
              student_karma = Karma.query.get(student.karmaID)
              student_karma.calculateScore(student)
              student_karma.updateRank()
              db.session.commit()

        return review.upvotes

# Concrete strategy for downvoting
class DownvoteStrategy(VoteStrategy):
    def vote(self, review, staff):
        if staff in review.staffDownvoters:
            return review.downvotes
        else:
            if staff not in review.staffDownvoters:
                review.downvotes += 1
                review.staffDownvoters.append(staff)

                if staff in review.staffUpvoters:
                    review.upvotes -= 1
                    review.staffUpvoters.remove(staff)

            db.session.add(review)
            db.session.commit()

            # ... (rest of your code for updating Karma)
            # Retrieve the associated Student object using studentID
            student = Student.query.get(self.studentID)

            #  check if the student has a karma record (KarmaID) and create a new Karma record for them if not
            if student.karmaID is None:
              karma = Karma(score=0.0, rank=-99)
              db.session.add(karma) # Add the Karma record to the session
              db.session.flush() # Ensure the KArma record gets an ID
              student.karmaID = karma.karmaID # Set the student's KArmaID to the new KArma record's ID

              # Update Karma for the student
              student_karma = Karma.query.get(student.karmaID)
              student_karma.calculateScore(student)
              student_karma.updateRank()
              db.session.commit()

        return review.downvotes