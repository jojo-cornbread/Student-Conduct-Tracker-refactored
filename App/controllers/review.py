from App.models import Review, Karma, Student, VoteStrategy, UpvoteStrategy, DownvoteStrategy
from App.database import db

# from .vote_strategies import UpvoteStrategy, DownvoteStrategy

def get_reviews(): 
    return db.session.query(Review).all()

def get_all_reviews_json():
    reviews = get_reviews()
    if not reviews:
        return []
    reviews = [review.to_json() for review in reviews]
    return reviews

def get_reviews_for_student(studentID):
    return db.session.query(Review).filter_by(studentID=studentID).all()

def get_review(reviewID):
    return Review.query.filter_by(ID=reviewID).first()

def get_reviews_by_staff(staffID):
    return db.session.query(Review).filter_by(reviewerID=staffID).all()


def edit_review(review, staff, is_positive, comment):
    if review.reviewer == staff:
        review.isPositive = is_positive
        review.comment = comment
        db.session.add(review)
        db.session.commit()
        return review
    return None


def delete_review(review, staff):
    if review.reviewer == staff:
        db.session.delete(review)
        db.session.commit()
        return True
    return None

# design pattern implementation
def set_vote_strategy(reviewID, strategy):
    review = get_review(reviewID)

    if strategy.lower() == "upvote":
        strategy = UpvoteStrategy()
    elif strategy.lower() == "downvote":
        strategy = DownvoteStrategy()

    review.set_vote_strategy(strategy)

    if strategy:
        return strategy
    return None
    
def vote(reviewID, staff):
    review = get_review(reviewID)
    return review.vote(staff)

# def downvoteReview(reviewID, staff):
#     review = db.session.query(Review).get(reviewID)
#     if staff in review.staffDownvoters:  # If they downvoted the review already, return current votes
#         return review.downvotes

#     else:
#         if staff not in review.staffDownvoters:  # if staff has not downvoted allow the vote
#             review.downvotes += 1
#             review.staffDownvoters.append(staff)

#             if staff in review.staffUpvoters:  # if they had upvoted previously then remove their upvote to account for switching between votes
#                 review.upvotes -= 1
#                 review.staffUpvoters.remove(staff)

#         db.session.add(review)
#         db.session.commit()
#         # Retrieve the associated Student object using studentID
#         student = db.session.query(Student).get(review.studentID)

#         # Check if the student has a Karma record (karmaID) and create a new Karma record for them if not
#         if student.karmaID is None:
#             karma = Karma(score=0.0, rank=-99)
#             db.session.add(karma)  # Add the Karma record to the session
#             db.session.flush()  # Ensure the Karma record gets an ID
#             db.session.commit()
#             # Set the student's karmaID to the new Karma record's ID
#             student.karmaID = karma.karmaID

#       # Update Karma for the student
#         student_karma = db.session.query(Karma).get(student.karmaID)
#         student_karma.calculateScore(student)
#         student_karma.updateRank()

#     return review.downvotes


# def upvoteReview(reviewID, staff):
#     review = db.session.query(Review).get(reviewID)

#     if staff in review.staffUpvoters:  # If they upvoted the review already, return current votes
#         return review.upvotes

#     else:
#         if staff not in review.staffUpvoters:  # if staff has not upvoted allow the vote
#             review.upvotes += 1
#             review.staffUpvoters.append(staff)

#             if staff in review.staffDownvoters:  # if they had downvoted previously then remove their downvote to account for switching between votes
#                 review.downvotes -= 1
#                 review.staffDownvoters.remove(staff)

#         db.session.add(review)
#         db.session.commit()

#         # work out and update the karma ranking
#         # Retrieve the associated Student object using studentID
#         student = db.session.query(Student).get(review.studentID)

#         # Check if the student has a Karma record (karmaID) and create a new Karma record for them if not
#         if student.karmaID is None:
#             karma = Karma(score=0.0, rank=-99)
#             db.session.add(karma)  # Add the Karma record to the session
#             db.session.flush()  # Ensure the Karma record gets an ID
#             db.session.commit()
#             # Set the student's karmaID to the new Karma record's ID
#             student.karmaID = karma.karmaID

#       # Update Karma for the student
#         student_karma = db.session.query(Karma).get(student.karmaID)
#         student_karma.calculateScore(student)
#         student_karma.updateRank()

#     return review.upvotes
