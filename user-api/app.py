from audioop import add
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
def generate_users_entry(user_results):
    result = []

    for user in user_results:
        entry = {}

        entry["user_id"] = user.user_id
        entry["email"] = user.email
        entry["password"] = user.password
        entry["first"] = user.first
        entry["last"] = user.last
        entry["address"] = user.address
        entry["state"] = user.state
        entry["zipcode"] = user.zipcode
        entry["is_admin"] = user.is_admin

        result.append(entry)

    # return results
    return result
        
   





# returns a dictionary of the information of the reservation sent
# used when the admin gets all the users information and a single reservation
def generate_user_entry(user):
    entry = {}

    entry["user_id"] = user.user_id
    entry["email"] = user.email
    entry["password"] = user.password
    entry["first"] = user.first
    entry["last"] = user.last
    entry["address"] = user.address
    entry["state"] = user.state
    entry["zipcode"] = user.zipcode
    entry["is_admin"] = user.is_admin

    # return results
    return entry


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

            all_users = session.query(User).all()
        
        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:
            # generate a list from hotels
            result = generate_users_entry(all_users)
        
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
            email = request.json["email"]
            password = request.json["password"]
            first = request.json["first"]
            last = request.json["last"]
            address = request.json["address"]
            state = request.json["state"]
            zipcode = request.json["zipcode"]
            # make insert statement for the database
            new_user = User( user_id = user_id, email = email, password = password, first = first,
                                                        last = last, address = address,
                                                        state = state, zipcode = zipcode)
            # que the insert and commit the changes
            session.add(new_user)
            session.commit()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e
        else:
            return {
                "message":
                f"User ID {new_user.user_id} was successfully created."
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
            query_result = session.query(User).get(user_id)

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:
            if not query_result:
                abort(
                    404,
                    description=
                    f"User ID {user_id} does not exist in the database."
                )

            # generate a list from hotels
            result = generate_user_entry(query_result)
            
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

