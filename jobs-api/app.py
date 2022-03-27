from sqlalchemy.sql.functions import user #allowing vs to use sql commands
from database import *
from flask import Flask, request, abort, jsonify
from flask_restful import Api, Resource, reqparse 
from sqlalchemy.orm import sessionmaker
from sqlacodegen.codegen import CodeGenerator
from flask_cors import CORS#database frame work, interact with database.
import dotenv
import io
import os
import sqlalchemy as sq
import sys



"""
post
 - creating a job based on the info given from the front end
 - check for invailed entries data check is good for the given field
 - check to see if the job already exsists
put
 - checks the info 1 for invailid data 2 for if there is a change in the data
 - make sure to only allow them to change the proper fields
get
 - get a single job based on a job_id
 - get all jobs
delete
 - make sure job is being deleted by user who owns job
 - match job then delete there is example line ~407
"""


# set up request parser for POST 
jobs_args = reqparse.RequestParser()
jobs_args.add_argument("user_id", type = int, help = "Enter the users ID. (int)", required = True)
jobs_args.add_argument("title", type = str, help = "Enter the title (string)", required = True)
jobs_args.add_argument("description", type = str, help = "Enter the description of the job (string)", required = True)
jobs_args.add_argument("pay", type = float, help = "Enter the pay of the job (float)", required = True)
jobs_args.add_argument("address", type = str, help = "Enter the address of the job (string)", required = True)
jobs_args.add_argument("state", type = str, help = "Enter the state of the job (string)", required = True)
jobs_args.add_argument("zipcode", type = str, help = "Enter the zipcode of job (string)", required = True)


put_jobs_args = reqparse.RequestParser()
put_jobs_args.add_argument("title", type = str, help = "Enter the title (string)", required = True)
put_jobs_args.add_argument("description", type = str, help = "Enter the description of the job (string)", required = True)
put_jobs_args.add_argument("pay", type = float, help = "Enter the pay of the job (float)", required = True)
put_jobs_args.add_argument("address", type = str, help = "Enter the address of the job (string)", required = True)
put_jobs_args.add_argument("state", type = str, help = "Enter the state of the job (string)", required = True)
put_jobs_args.add_argument("zipcode", type = str, help = "Enter the zipcode of job (string)", required = True)

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



# returns a dictionary of the information of the reservation sent
# used when the admin gets all the users information and a single reservation
def generate_job_entry(job):
    # set up dictionary to be added to result list
    new_entry = {}

    # enter each respective variable into the dictionary
    new_entry["job_id"] = job.job_id
    new_entry["user_id"] = job.user_id
    new_entry["title"] = job.title
    new_entry["description"] = job.description
    new_entry["pay"] = float(job.pay)
    new_entry["address"] = job.address
    new_entry["state"] = job.state
    new_entry["zipcode"] = job.zipcode

    # return results
    return new_entry




# returns a dictionary of the information of the reservation sent
# used when the admin gets all the users information and a single reservation
def generate_all_job_entry(result):

    result_list = []
    for job in result:

        # set up dictionary to be added to result list
        new_entry = {}

        # enter each respective variable into the dictionary
        new_entry["job_id"] = job.job_id
        new_entry["user_id"] = job.user_id
        new_entry["title"] = job.title
        new_entry["description"] = job.description
        new_entry["pay"] = float(job.pay)
        new_entry["address"] = job.address
        new_entry["state"] = job.state
        new_entry["zipcode"] = job.zipcode

        result_list.append(new_entry)
    # return results
    return result_list

## ---------- Admin ---------- ##
# class for interacting with all Reservations in the database
class AllJobs(Resource):

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
            all_users = session.query(Job).order_by(Job.user_id).all()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:
            # generate a list from hotels
            result = generate_all_job_entry(all_users)

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
            args = jobs_args.parse_args()
            
            # gets the reservation information
            user_id = request.json["user_id"]
            
            title = request.json["title"]
            description = request.json["description"]
            pay = request.json["pay"]
            address = request.json["address"]
            
            state = request.json["state"]
            zipcode = request.json["zipcode"]
            
            
            # make insert statement for the database
            new_job = Job( user_id = user_id, title = title, description = description,
                                                        pay = pay, address = address,
                                                        state = state, zipcode = zipcode)
            
            # que the insert and commit the changes
            session.add(new_job)
            session.commit()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e
        else:
            return {
                "message":
                f"Job ID {new_job.job_id} was successfully created."
            }

        finally:
            session.close()
            engine.dispose()


## ---------- User ---------- ##
# class for interacting with user Reservations in the database

class UserJobs(Resource):

    # function to get a user reservations based on user_id from the database
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
            query_result = session.query(Job).filter(Job.user_id == user_id).all()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:

            # generate a list from hotels
            result = generate_all_job_entry(query_result)

            # if there are no reservations, show error
            if not result:
                abort(404,
                    description=
                    f"USER ID {user_id} does not have any jobs in the database.")
        # return the result
            return result

        finally:
            session.close()
            engine.dispose()





class SingleJob(Resource):
    # function to delete a single reservation from the database by ID number
    def delete(self, job_id):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()


        try:
            result = session.query(Job).get(job_id)


        except sq.exc.DBAPIError as e:
            session.rollback()
            return e    
        else:

            if not result:
                abort(
                    404,
                    description=
                    f"Job ID {job_id} does not exist in the database."
                )


            session.delete(result)
            session.commit()
            # return message on success
            return {
                "message":
                f"Job ID {job_id} was successfully deleted."
            }
        finally:
            session.close()
            engine.dispose()

    def put(self, job_id):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()

        try:
            # finds the reservation based on reservation ID
            result = session.query(Job).get(job_id)
            # if it doesn't exsist error
            if not result:
                abort(
                    404,
                    description=
                    f"Job ID {job_id} does not exist in the database."
                )
            # checks to see if the necessary argument have been passed 
            args = put_jobs_args.parse_args()

            result.title = request.json["title"]
            result.description = request.json["description"]
            result.pay = request.json["pay"]
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
                f"Job ID {job_id} was successfully updated."
            }
        finally:
            session.close()
            engine.dispose()

    # function to get a specific reservation based on reservation_id from the database
    def get(self, job_id):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()


        try:     

            query_result = session.query(Job).get(job_id)

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:
            if query_result is None:
                abort(
                    404,
                    description=
                    f"Job ID {job_id} does not exist in the database."
                )

            # generate a dict from res
            result = generate_job_entry(query_result)

        # return the result
            return result

        finally:
            session.close()
            engine.dispose()



# add to each class to API
api.add_resource(UserJobs, "/api/user/<int:user_id>")
api.add_resource(AllJobs, "/api/job")
api.add_resource(SingleJob, "/api/job/<int:job_id>")

if __name__ == "__main__":  
    app.run(debug=True)