from flask import Blueprint, jsonify, redirect, render_template, request, abort, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import current_user
from App.controllers import Review, Staff
from App.controllers.user import get_staff
from App.controllers.student import search_student

from App.controllers.review import (
    get_reviews_by_staff,
    edit_review,
    delete_review,
    # upvoteReview,
    # downvoteReview,
    get_reviews,
    get_reviews_for_student, 
    get_review,
    set_vote_strategy,
    vote
)

# Create a Blueprint for Review views
review_views = Blueprint("review_views", __name__, template_folder='../templates')

# Route to list all reviews (you can customize this route as needed)
@review_views.route('/reviews', methods=['GET'])
def list_reviews():
    reviews = get_reviews()
    return jsonify([review.to_json() for review in reviews]), 200

# Route to view a specific review and vote on it
@review_views.route('/review/<int:review_id>', methods=['GET',])
def view_review(review_id):
    review = get_review(review_id)
    if review:
        return jsonify(review.to_json())
    else: 
        return 'Review does not exist', 404

#Route to upvote review 
# might be able to merge both upvote and downvote routes by making the /upvote intoa variable
# and then using that variable (either upvote or downvote) as the strategy in set strategy method
@review_views.route('/review/<int:review_id>/upvote', methods=['POST'])
@jwt_required()
def upvote (review_id):
    if not jwt_current_user or not isinstance(jwt_current_user, Staff):
      return "You are not authorized to upvote this review", 401
      
    review= get_review(review_id) 
    if review:
        staff = get_staff(jwt_current_user.ID)
        if staff:
            current = review.upvotes

            set_vote_strategy(review_id, "upvote")
            new_votes= vote(review_id, staff)

            if new_votes == current: 
               return jsonify(review.to_json(), 'Review Already Upvoted'), 201 
            else:
                return jsonify(review.to_json(), 'Review Upvoted'), 200
        else: 
            return jsonify('Staff does not exist'), 404     
    else: 
        return'Review does not exist', 404

#Route to downvote review 
@review_views.route('/review/<int:review_id>/downvote', methods=['POST'])
@jwt_required()
def downvote (review_id):
    if not jwt_current_user or not isinstance(jwt_current_user, Staff):
      return "You are not authorized to downvote this review", 401
  
    review= get_review(review_id) 
    if review:
        staff = get_staff(jwt_current_user.ID)
        if staff:
            current = review.downvotes

            set_vote_strategy(review_id, "downvote")
            new_votes= vote(review_id, staff)
            if new_votes == current: 
               return jsonify(review.to_json(), 'Review Already Downvoted'), 201 
            else:
                return jsonify(review.to_json(), 'Review Downvoted Successfully'), 200 
        else: 
            return jsonify(get_review(review_id).to_json(), 'Staff does not exist'), 404
    else: 
        return'Review does not exist', 404

# Route to get reviews by student ID
@review_views.route("/student/<string:student_id>/reviews", methods=["GET"])
def get_reviews_of_student(student_id):
    if search_student(student_id):
        reviews = get_reviews_for_student(student_id)
        if reviews:
            return jsonify([review.to_json() for review in reviews]), 200
        else:
            return "No reviews found for the student", 404
    return "Student does not exist", 404

# Route to get reviews by staff ID
@review_views.route("/staff/<string:staff_id>/reviews", methods=["GET"])
def get_reviews_from_staff(staff_id):
    if get_staff(str(staff_id)):
        reviews = get_reviews_by_staff(staff_id)
        if reviews:
            return jsonify([review.to_json() for review in reviews]), 200
        else:
            return "No reviews found by the staff member", 404
    return "Staff does not exist", 404

# Route to edit a review
@review_views.route("/review/edit/<int:review_id>", methods=["PUT"])
@jwt_required()
def review_edit(review_id):
    review = get_review(review_id)
    if not review:
      return "Review not found", 404
      
    if not jwt_current_user or not isinstance(jwt_current_user, Staff) or review.reviewerID != jwt_current_user.ID :
      return "You are not authorized to edit this review", 401

    staff = get_staff(jwt_current_user.ID)

    data = request.json

    if not data['comment']:
        return "Invalid request data", 400
    
    if data['isPositive'] not in (True, False):
        return jsonify({"message": f"invalid Positivity value  ({data['isPositive']}). Positive: true or false"}), 400

    updated= edit_review(review, staff, data['isPositive'], data['comment'])
    if updated: 
      return jsonify(review.to_json(), 'Review Edited'), 200
    else:
      return "Error updating review", 400



# Route to delete a review
@review_views.route("/review/delete/<int:review_id>", methods=["DELETE"])
@jwt_required()
def review_delete(review_id):
    review = get_review(review_id)
    if not review:
      return "Review not found", 404

    if not jwt_current_user or not isinstance(jwt_current_user, Staff) or review.reviewerID != jwt_current_user.ID :
      return "You are not authorized to delete this review", 401

    staff = get_staff(jwt_current_user.ID)
   
    if delete_review(review, staff):
        return "Review deleted successfully", 200
    else:
        return "Issue deleting review", 400

