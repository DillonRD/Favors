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
reservation_args = reqparse.RequestParser()
reservation_args.add_argument("user_id", type = int, help = "Enter the users ID. (int)", required = True)
reservation_args.add_argument("hotel_id", type = int, help = "Enter the hotel ID. (int)", required = True)
reservation_args.add_argument("check_in", type = str, help = "Enter the check_in of the reservation. (string)", required = True)
reservation_args.add_argument("check_out", type = str, help = "Enter the check_out of the reservation. (string)", required = True)
reservation_args.add_argument("total_price", type = int, help = "Enter the total price of the reservation (decimal number)", required = True)
reservation_args.add_argument("reserved_standard_count", type = int, help = "Enter the number of standard rooms (int)", required = True)
reservation_args.add_argument("reserved_queen_count", type = int, help = "Enter the number of queen rooms (int)", required = True)
reservation_args.add_argument("reserved_king_count", type = int, help = "Enter the number of king rooms (int)", required = True)

put_reservation_args = reqparse.RequestParser()
put_reservation_args.add_argument("check_in", type = str, help = "Enter the check_in of the reservation. (string)", required = True)
put_reservation_args.add_argument("check_out", type = str, help = "Enter the check_out of the reservation. (string)", required = True)
put_reservation_args.add_argument("total_price", type = int, help = "Enter the total price of the reservation (decimal number)", required = True)
put_reservation_args.add_argument("reserved_standard_count", type = int, help = "Enter the number of standard rooms (int)", required = True)
put_reservation_args.add_argument("reserved_queen_count", type = int, help = "Enter the number of queen rooms (int)", required = True)
put_reservation_args.add_argument("reserved_king_count", type = int, help = "Enter the number of king rooms (int)", required = True)


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
        # set up output file for database classes
        #outfile = io.open(outfile, "w",
        #                encoding="utf-8") if outfile else sys.stdout
        # generate code and output to outfile
        #generator = CodeGenerator(metadata)
        #generator.render(outfile)

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
    
    for cur_user, cur_res, cur_hotel in user_results:
        
        # skips the users that are already done but adds the reservation
        if cur_user.user_id == prev_user:
            reservation_info = generate_reservation_entry(cur_res, cur_hotel)
            result_list[postion]["reservations"].append(reservation_info)
            continue
        
        #other wise updates the user it is writing to and the postion
        prev_user = cur_user.user_id
        postion+=1

        # set up dictionary to be added to result list
        new_entry = {}
        
        # enter each respective variable into the dictionary
        new_entry["user_id"] = cur_user.user_id
        new_entry["first_name"] = cur_user.first_name
        new_entry["last_name"] = cur_user.last_name
        new_entry["email"] = cur_user.email
        new_entry["password"] = cur_user.password
        new_entry["isAdmin"] = cur_user.isAdmin
        new_entry["phone_number"] = cur_user.phone_number
        new_entry["date_of_birth"] = str(cur_user.date_of_birth)

        # set up reservations
        reservation_info = []
        result = generate_reservation_entry(cur_res, cur_hotel)
        reservation_info.append(result)
        
        new_entry["reservations"] = reservation_info
        
        # append the new_entry into results if it is not already added
        if new_entry not in result_list:
            result_list.append(new_entry)

    # return results
    return result_list


# returns a dictionary of the information of the reservation sent
# used when the admin gets all the users information and a single reservation
def generate_reservation_entry(res, hotel):
    # set up dictionary to be added to result list
    new_entry = {}
    
    # enter each respective variable into the dictionary
    new_entry["reservation_id"] = res.reservation_id
    new_entry["check_in"] = str(res.check_in)
    new_entry["check_out"] = str(res.check_out)
    new_entry["total_price"] = float(res.total_price)
    new_entry["reserved_standard_count"] = res.reserved_standard_count
    new_entry["reserved_queen_count"] = res.reserved_queen_count
    new_entry["reserved_king_count"] = res.reserved_king_count

    hotel_info = generate_hotel_entry(hotel)

    new_entry["hotel_information"] = hotel_info

    # return results
    return new_entry



def generate_hotel_entry(hotel):

    # enter the info for the hotel
    hotel_info = {}
    hotel_info["hotel_id"] = hotel.hotel_id
    hotel_info["hotel_name"] = hotel.hotel_name
    hotel_info["street_address"] = hotel.street_address
    hotel_info["city"] = hotel.city
    hotel_info["state"] = hotel.state
    hotel_info["zipcode"] = hotel.zipcode
    hotel_info["phone_number"] = hotel.phone_number
    hotel_info["weekend_diff_percentage"] = float(hotel.weekend_diff_percentage)
    # calculate total number of rooms
    num_standard = hotel.standard_count
    num_queen = hotel.queen_count
    num_king = hotel.king_count
    total_rooms = num_standard + num_queen + num_king
    hotel_info["number_of_rooms"] = total_rooms
    # set up amenities list
    amenities_list = generate_amenities(hotel)
    hotel_info["amenities"] = amenities_list
    # set up room_types list
    hotel_info["standard_count"] = hotel.standard_count
    hotel_info["standard_price"] = float(hotel.standard_price)
    hotel_info["queen_count"] = hotel.queen_count
    hotel_info["queen_price"] = float(hotel.queen_price)
    hotel_info["king_count"] = hotel.king_count
    hotel_info["king_price"] = float(hotel.king_price)

    return hotel_info


# generates the list of attributes a hotel has
def generate_amenities(hotel):
    amenities = []
    # check if hotel has pool
    if hotel.Pool:
        amenities.append("Pool")
    # check if hotel has gym
    if hotel.Gym:
        amenities.append("Gym")
    # check if hotel has spa
    if hotel.Spa:
        amenities.append("Spa")
    # check if hotel has business office
    if hotel.Bussiness_Office:
        amenities.append("Business Office")
    # check if hotel as wifi
    if hotel.Wifi:
        amenities.append("Wifi")
    return amenities


# returns a dictionary of the information of the reservation sent
# used when the admin gets all the users information and a single reservation
def generate_user_reservations_entry(result):
    
    result_list = []
    for hotel, res in result:
        
        # set up dictionary to be added to result list
        new_entry = {}
        
        # enter each respective variable into the dictionary
        new_entry["reservation_id"] = res.reservation_id
        new_entry["user_id"] = res.user_id
        new_entry["check_in"] = str(res.check_in)
        new_entry["check_out"] = str(res.check_out)
        new_entry["total_price"] = float(res.total_price)
        new_entry["reserved_standard_count"] = res.reserved_standard_count
        new_entry["reserved_queen_count"] = res.reserved_queen_count
        new_entry["reserved_king_count"] = res.reserved_king_count

        hotel_info = generate_hotel_entry(hotel)
        
        new_entry["hotel_information"] = hotel_info
        result_list.append(new_entry)
    # return results
    return result_list

# function to set a valid json for user object
# returns a user dictionary including the user info reservation info and hotel info
def generate_single_reservation_entry(user, res, hotel):

    # set up dictionary to be added to result list
    format = {}
    entry = {}
    
    # enter each respective variable into the dictionary
    entry["user_id"] = user.user_id
    entry["first_name"] = user.first_name
    entry["last_name"] = user.last_name
    entry["email"] = user.email
    entry["password"] = user.password
    entry["isAdmin"] = user.isAdmin
    entry["phone_number"] = user.phone_number
    entry["date_of_birth"] = str(user.date_of_birth)

    format["user_information"] = entry
    
    # set up reservations
    format["reservation_id"] = res.reservation_id
    format["check_in"] = str(res.check_in)
    format["check_out"] = str(res.check_out)
    format["total_price"] = float(res.total_price)
    format["reserved_standard_count"] = res.reserved_standard_count
    format["reserved_queen_count"] = res.reserved_queen_count
    format["reserved_king_count"] = res.reserved_king_count

    format["hotel_information"] = generate_hotel_entry(hotel)

    # return results
    return format

## ---------- Admin ---------- ##
# class for interacting with all Reservations in the database
class AllReservations(Resource):

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
            all_users = session.query(User, Reservation, Hotel).filter(User.user_id == Reservation.user_id).filter(Reservation.hotel_id == Hotel.hotel_id).order_by(User.user_id).order_by(Reservation.check_in).all()
        
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
            args = reservation_args.parse_args()
            # gets the reservation information
            user_id = request.json["user_id"]
            hotel_id = request.json["hotel_id"]
            check_in = request.json["check_in"]
            check_out = request.json["check_out"]
            total_price = request.json["total_price"]
            standard = request.json["reserved_standard_count"]
            queen = request.json["reserved_queen_count"]
            king = request.json["reserved_king_count"]
            # make insert statement for the database
            new_reservation = Reservation( user_id = user_id, hotel_id = hotel_id, check_in = check_in, check_out = check_out,
                                                        total_price = total_price, reserved_standard_count = standard,
                                                        reserved_queen_count = queen, reserved_king_count = king)
            # que the insert and commit the changes
            session.add(new_reservation)
            session.commit()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e
        else:
            return {
                "message":
                f"Reservation ID {new_reservation.reservation_id} was successfully created."
            }

        finally:
            session.close()
            engine.dispose()


## ---------- User ---------- ##
# class for interacting with user Reservations in the database

class UserReservation(Resource):
    
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
            query_result = session.query(Hotel, Reservation).filter(Hotel.hotel_id == Reservation.hotel_id).filter(Reservation.user_id == user_id).order_by(Reservation.check_in).all()

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:

            # generate a list from hotels
            result = generate_user_reservations_entry(query_result)
            
            # if there are no reservations, show error
            if not result:
                abort(404,
                    description=
                    f"USER ID {user_id} does not have any reservations in the database.")
        # return the result
            return result

        finally:
            session.close()
            engine.dispose()

    
    


class SingleBooking(Resource):
    # function to delete a single reservation from the database by ID number
    def delete(self, reservation_id):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()

        
        try:
            result = session.query(Reservation).get(reservation_id)
        

        except sq.exc.DBAPIError as e:
            session.rollback()
            return e    
        else:
                        
            if not result:
                abort(
                    404,
                    description=
                    f"Reservation ID {reservation_id} does not exist in the database."
                )

        
            session.delete(result)
            session.commit()
            # return message on success
            return {
                "message":
                f"Reservation ID {reservation_id} was successfully deleted."
            }
        finally:
            session.close()
            engine.dispose()

    def put(self, reservation_id):
        
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
            result = session.query(Reservation).get(reservation_id)
            # if it doesn't exsist error
            if not result:
                abort(
                    404,
                    description=
                    f"Reservation ID {reservation_id} does not exist in the database."
                )
            # checks to see if the necessary argument have been passed 
            args = put_reservation_args.parse_args()

            result.check_in = request.json["check_in"]
            result.check_out = request.json["check_out"]
            result.total_price = request.json["total_price"]
            result.reserved_standard_count = request.json["reserved_standard_count"]
            result.reserved_queen_count = request.json["reserved_queen_count"]
            result.reserved_king_count = request.json["reserved_king_count"]
            
            # update the information in the entry
            session.commit()
        
        except sq.exc.DBAPIError as e:
            session.rollback()
            return e
        else:
            # return message on success
            return {
                "message":
                f"Reservation ID {reservation_id} was successfully updated."
            }
        finally:
            session.close()
            engine.dispose()

    # function to get a specific reservation based on reservation_id from the database
    def get(self, reservation_id):

        # get username, password, host, and database
        host = os.environ.get("host")
        username = os.environ.get("user")
        password = os.environ.get("password")
        database = os.environ.get("database")

        engine = generate_model(host, username, password, database)

        Session = sessionmaker(bind = engine)
        session = Session()

        
        try:     

            query_result = session.query(User, Reservation, Hotel).filter(User.user_id == Reservation.user_id).filter(Reservation.hotel_id == Hotel.hotel_id).filter(Reservation.reservation_id == reservation_id).first()
                
        except sq.exc.DBAPIError as e:
            session.rollback()
            return e

        else:
            if query_result is None:
                abort(
                    404,
                    description=
                    f"Reservation ID {reservation_id} does not exist in the database."
                )

            # generate a dict from res
            result = generate_single_reservation_entry(query_result[0], query_result[1], query_result[2] )
            
        # return the result
            return result

        finally:
            session.close()
            engine.dispose()

    

# add to each class to API
api.add_resource(UserReservation, "/api/user/<int:user_id>")
api.add_resource(AllReservations, "/api/user")
api.add_resource(SingleBooking, "/api/reservation/<int:reservation_id>")

if __name__ == "__main__":  
    app.run(debug=True)
