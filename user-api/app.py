from sqlalchemy.sql.functions import user
from database import *
from flask import Flask, request, abort, jsonify
from flask_restful import Api, Resource, reqparse
from sqlalchemy.orm import sessionmaker
from sqlacodegen.codegen import CodeGenerator
from flask_cors import CORS
import dotenv
import io
import os
import sqlalchemy as sq
import sys


# set up request parser for POST
user_args = reqparse.RequestParser()
user_args.add_argument("user_id", type = int, help = "Enter the users ID. (int)", required = True)
user_args.add_argument("email", type = str, help = "Enter the Email of the USER. (string)", required = True)
user_args.add_argument("password", type = str, help = "Enter the Password of the USER. (string)", required = True)
user_args.add_argument("first", type = str, help = "Enter the First Name of the USER (string)", required = True)
user_args.add_argument("last", type = str, help = "Enter the Last Name of the USER (string)", required = True)
user_args.add_argument("address", type = str, help = "Enter the Address of the USER (string)", required = True)
user_args.add_argument("state", type = str, help = "Enter the State of the USER (string)", required = True)
user_args.add_argument("zipcode", type = str, help = "Enter the zip code of the USER (string)", required = True)

put_user_args = reqparse.RequestParser()
put_user_args.add_argument("email", type = str, help = "Enter the Email of the USER. (string)", required = True)
put_user_args.add_argument("password", type = str, help = "Enter the Password of the USER. (string)", required = True)
put_user_args.add_argument("first", type = str, help = "Enter the First Name of the USER (string)", required = True)
put_user_args.add_argument("last", type = str, help = "Enter the Last Name of the USER (string)", required = True)
put_user_args.add_argument("address", type = str, help = "Enter the Address of the USER (string)", required = True)
put_user_args.add_argument("state", type = str, help = "Enter the State of the USER (string)", required = True)
put_user_args.add_argument("zipcode", type = str, help = "Enter the zip code of the USER (string)", required = True)


# load Flask and API
app = Flask(__name__)
api = Api(app)
CORS(app)


def generate_model(host, user, password, database, outfile=None):
    try:
        # set up mysql engine
        engine = sq.create_engine(
            f"mysql+pymysql://{user}:{password}@{host}/{database}")
        metadata = sq.MetaData(bind=engine)
        metadata.reflect()
        # # set up output file for database classes
        # outfile = io.open(outfile, "w",
        #                 encoding="utf-8") if outfile else sys.stdout
        # # generate code and output to outfile
        # generator = CodeGenerator(metadata)
        # generator.render(outfile)

    except sq.exc.DBAPIError as e:
        return e

    return engine



# function to set a valid json for user object
# returns a list of dictionaries depending on the user query
def generate_user_entry(user_results):

    # set up list to return
    result_list = []
    prev_user = None
    postion = -1
    
    for cur_user, cur_job in user_results:
        
        # skips the users that are already done but adds the reservation
        if cur_user.user_id == prev_user:
            job = generate_job_entry(cur_job)
            result_list[postion]["reservations"].append(reservation_info)
            continue
        
        #other wise updates the user it is writing to and the postion
        prev_user = cur_user.user_id
        postion+=1

        # set up dictionary to be added to result list
        new_entry = {}
        
        # enter each respective variable into the dictionary
        new_entry["user_id"] = cur_user.user_id
        new_entry["email"] = cur_user.email
        new_entry["password"] = cur_user.password
        new_entry["first_name"] = cur_user.first
        new_entry["last_name"] = cur_user.last
        new_entry["address"] = cur_user.address
        new_entry["state"] = cur_user.state
        new_entry["zipcode"] = cur_user.zipcode
        new_entry["is_admin"] = cur_user.is_admin

        # set up reservations
        reservation_info = []
        result = generate_job_entry(cur_job)
        reservation_info.append(result)
        
        new_entry["reservations"] = reservation_info
        
        # append the new_entry into results if it is not already added
        if new_entry not in result_list:
            result_list.append(new_entry)

    # return results
    return result_list


# returns a dictionary of the information of the reservation sent
# used when the admin gets all the users information and a single reservation
def generate_job_entry(jobs):
    # set up dictionary to be added to result list
    new_entry = {}
    
    # enter each respective variable into the dictionary
    new_entry["job_id"] = jobs.job_id
    new_entry["title"] = jobs.title
    new_entry["description"] = jobs.description
    new_entry["pay"] = float(jobs.pay)
    new_entry["address"] = jobs.address
    new_entry["state"] = jobs.state
    new_entry["zipcode"] = jobs.zipcode
    # return results
    return new_entry


# returns a dictionary of the information of the reservation sent
# used when the admin gets all the users information and a single reservation
def generate_user_jobs_entry(result):
    
    result_list = []
    for user, jobs in result:
        # set up dictionary to be added to result list
        new_entry = {}
        
        # enter each respective variable into the dictionary
        new_entry["job_id"] = jobs.job_id
        new_entry["title"] = jobs.title
        new_entry["description"] = jobs.description
        new_entry["pay"] = float(jobs.pay)
        new_entry["address"] = jobs.address
        new_entry["state"] = jobs.state
        new_entry["zipcode"] = jobs.zipcode

        hotel_info = generate_single_user_entry(user)
        
        new_entry["user"] = hotel_info
        result_list.append(new_entry)
    # return results
    return result_list

# function to set a valid json for user object
# returns a user dictionary including the user info
def generate_single_user_entry(user):

    # set up dictionary to be added to result list
    entry = {}
    
    # enter each respective variable into the dictionary
    entry["user_id"] = user.user_id
    entry["email"] = user.email
    entry["password"] = user.password
    entry["first_name"] = user.first
    entry["last_name"] = user.last
    entry["address"] = user.address
    entry["state"] = user.state
    entry["zipcode"] = user.zipcode
    entry["is_admin"] = user.isAdmin



    # return results
    return format

## ---------- Admin ---------- ##
# class for interacting with all Reservations in the database
class AllUsers(Resource):

    # function to get all hotels from the database
    def get(self):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()

        # query to get all hotels
        try:

            all_users = session.query(User, Job).filter(User.user_id == Job.user_id).order_by(User.user_id).all()
        
        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:
            # generate a list from hotels
            result = generate_user_entry(all_users)
        
            # if there are no hotels, show error
            if not result:
                abort(404, description="There are no users in the database.")
            # return the results
            return result

        finally:
            session.close()
            engine.dispose()

        

    def post(self):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()


        try:
            #checks to see if there are the proper arguments


            args = user_args.parse_args()
            # gets the reservation information
            user_id = request.json["user_id"]
            hotel_id = request.json["email"]
            check_in = request.json["password"]
            check_out = request.json["first"]
            total_price = request.json["last"]
            standard = request.json["address"]
            queen = request.json["state"]
            king = request.json["zipcode"]
            # make insert statement for the database
            new_job = User( user_id = user_id, email = hotel_id, password = check_in, first = check_out,
                                                        last = total_price, address = standard,
                                                        state = queen, zipcode = king)
            # que the insert and commit the changes
            session.add(new_job)
            session.commit()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e
        else:
            return {
                "message":
                f"User ID {new_job.user_id} was successfully created."
            }

        finally:
            session.close()
            engine.dispose()
    

class SingleUser(Resource):

    def put(self, user_id):
        
        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()

        try:
            # finds the User based on User ID
            result = session.query(User).get(user_id)
            # if it doesn't exsist error
            if not result:
                abort(
                    404,
                    description=
                    f"Reservation ID {user_id} does not exist in the database."
                )
            # checks to see if the necessary argument have been passed 
            args = put_user_args.parse_args()

            result.email = request.json["email"]
            result.password = request.json["password"]
            result.first = request.json["first"]
            result.last = request.json["last"]
            result.address = request.json["address"]
            result.state = request.json["state"]
            result.zipcode = request.json["zipcode"]
            result.is_admin = request.json["is_admin"]
            
            # update the information in the entry
            session.commit()
        
        except sq.exc.DBAPIError as e:
            session.rollback()
            return e
        else:
            # return message on success
            return {
                "message":
                f"User ID {user_id} was successfully updated."
            }
        finally:
            session.close()
            engine.dispose()

    # function to get a specific User based on user_id from the database
    def get(self, user_id):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()

        
        try:
            query_result = session.query(User, Job).filter(User.user_id == user_id).filter(Job.user_id== User.user_id).all()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:

            # generate a list from hotels
            result = generate_user_jobs_entry(query_result[0], query_result[1])
            
        # return the result
            return result

        finally:
            session.close()
            engine.dispose()

    

# add to each class to API
api.add_resource(SingleUser, "/api/user/<int:user_id>")
api.add_resource(AllUsers, "/api/user")


if __name__ == "__main__":  
    app.run(debug=True)

