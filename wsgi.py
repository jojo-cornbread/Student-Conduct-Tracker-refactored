from App.views.index import generate_random_contact_number
import click, pytest, sys
from flask import Flask, jsonify
from flask.cli import with_appcontext, AppGroup
import random
import randomname
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( 
    create_user, 
    create_staff, 
    create_student, 
    get_all_users_json, 
    get_all_users,
    get_all_students,
    get_all_students_json,
    get_all_staff,
    get_all_staff_json,
    get_reviews,
    get_all_reviews_json,
    create_review,
    get_staff,
    upvoteReview,
    set_vote_strategy,
    vote )
from App.views import (generate_random_contact_number)

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


# todo
#   Make student NOT a User - fix all the code that utilizes this - DONE? Test more
#   add in more command line tests - for reviews and upvoting

# notification system ideas: 
# 1 - when a review is upvoted or downvoted, send msg in VIEWs to user
#   - this would work by getting the review (reviewid) and the creator (userid/staffid) of it, then checking if the
#   - current user is that same creator and making a flash notification if yes? or some kind of notification
#   - 


# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  db.drop_all()
  db.create_all()
  admin= create_user('bob', 'boblast' , 'bobpass')
  for ID in  range(2, 50): 
    staff= create_staff(admin, 
          randomname.get_name(), 
          randomname.get_name(), 
          randomname.get_name(), 
          str(ID), 
          randomname.get_name() + '@schooling.com', 
          str(random.randint(1, 15))
      )
    db.session.add(staff)
    db.session.commit()

  for ID in range(50, 150): 
      contact= generate_random_contact_number()
      student= create_student(admin, str(ID),
          randomname.get_name(), 
          randomname.get_name(), 
        #   randomname.get_name(),
          contact,
          random.choice(['Full-Time','Part-Time', 'Evening']),
          str(random.randint(1, 8))
      )
      db.session.add(student)
      db.session.commit()

  return jsonify({'message': 'Database initialized'}),201

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("firstname", default="rob")
@click.argument("lastname", default="roblast")
@click.argument("password", default="robpass")
def create_user_command(firstname,lastname, password):
    create_user(firstname, lastname, password)
    print(f'{firstname} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

# staff commands
staff_cli = AppGroup('staff', help='staff object commands')

@staff_cli.command("list", help='lists staff object in database')
@click.argument("format", default="string")
def list_staff_command(format):
    if format == 'string':
        print(get_all_staff())
    else:
        print(get_all_staff_json())

app.cli.add_command(staff_cli)

# student commands
student_cli = AppGroup('student', help="student object commands")

# @student_cli("create", help="creates a student")

@student_cli.command("list", help="Lists students in the database")
@click.argument("format", default="string")
def list_students_command(format):
    if format == 'string':
        print(get_all_students())
    else:
        print(get_all_students_json())

# @student_cli.command("get", help="Get all information about a specific student")

app.cli.add_command(student_cli)

# add in cli commands for reviews and karma

# review commands
review_cli = AppGroup('review', help="review object commands")

@review_cli.command("list", help='Lists review objects in the database')
@click.argument("format", default="String")
def list_reviews_command(format):
    if format == 'string':
        print(get_reviews())
    else:
        print(get_all_reviews_json())

# cli command to create reviews
@review_cli.command("create", help="Creates a new review object in the database")
@click.argument("staffid", default="2")
@click.argument("studentid", default="50")
@click.argument("is_positive", default=True)
@click.argument("comment", default="Good boy")
def create_review_command(staffid, studentid, is_positive, comment):
    create_review(staffid, studentid, is_positive, comment)
    print('Review created!')

# cli command to test upvoting
@review_cli.command("upvote", help="upvotes a review object in the database")
@click.argument("reviewid", default="1")
@click.argument("staffid", default = "2")
@click.argument("strategy", default="upvote")
def upvote_review_command(reviewid, staffid, strategy):
    # print(get_staff(staffid).to_json())

    # staff = get_staff(staffid)
    # upvoteReview(reviewid, staff)

    staff = get_staff(staffid)
    set_vote_strategy(reviewid, strategy)
    vote(reviewid, staff)
    

    print("Review upvoted!")

app.cli.add_command(review_cli)
'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)