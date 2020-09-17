""" RentOn

An application to look for places to rent anywhere
in India (images are not required)

Functionality:

Three modes of Login (user, owner, admin)
admin has all the priveledges
the owner can only add/update/delete property they own
user can rent a property
user can also request to get in touch with the owner
the property should have details like
area in sq-ft
number of bedrooms
amenities
furnishing
locality

Note

use jwt to find if the person logging in is an owner,user or admin

use test-driven development, where you write the tests of a function
first then make the functionality of the function and pass all the tests

every file in the project should pass PEP 8 guidelines
all the potential exceptions should be handled
use csv for storing all the information """

from flask import Flask
from flask import request
import jwt
import csv
import json
import time


app = Flask(__name__)


def decode_auth(token):
    key = "RentOn"
    try:
        data = jwt.decode(token, key)
        if data['expire'] > time.time():
            return True,data
        else:
            return False,data
    except jwt.InvalidSignatureError:
        return json.dumps({"message": "Invalid token"})



@app.route('/renton/register', methods=['POST'])
def register():
    try:
        user = {}
        user_name = request.json['user_name']
        password = request.json['password']
        mobile = request.json['mobile']
        email = request.json['email']
        user_type = request.json['type']
        with open('data/users.csv', 'r') as user_file:
            csv_reader = csv.reader(user_file)
            data = list(csv_reader)
        # id automatically generating
        u_id = int(data[-1][0]) + 1
        user['id'] = u_id
        user['uname'] = user_name
        user['password'] = password
        user['mobile'] = mobile
        user['email'] = email
        user['type'] = user_type
        with open('data/users.csv', 'a') as user_file:
            headers = ['id', 'uname', 'password', 'mobile', 'email', 'type']
            csv_writer = csv.DictWriter(user_file, fieldnames=headers)
            csv_writer.writerow(user)
        return json.dumps({"message": "User added successfully"})
    except FileNotFoundError:
        return json.dumps({"message": "File not Found"})
    except KeyError as error:
        return json.dumps({
            "message": "Key Error. %s not Found" % (error.args[0])})


@app.route('/renton/login', methods=['POST'])
def login():
    try:
        user_name = request.json['user_name']
        password = request.json['password']
        with open('data/users.csv', 'r') as user_file:
            csv_reader = csv.DictReader(user_file)
            valid_user = False
            for row in csv_reader:
                if row['uname'].lower() == user_name.lower() and row['password'] == password.lower():
                    valid_user = True
                    user_id = row['id']
                    user_type = row['type']
                    output_msg = "Login Successfully"
                    break
                else:
                    output_msg = "Login Failed"
        if valid_user:
            payload = {"user_name": user_name, "user_id": user_id, "user_type": user_type, 'expire': time.time()+600}
            key = "RentOn"
            encode_jwt = jwt.encode(payload, key)
            return json.dumps({"auth_token": encode_jwt.decode(), "message": output_msg})
        else:
            return json.dumps({"message": output_msg})
    except KeyError:
        return json.dumps({"message": "Key not found error"})


@app.route('/renton/view_users', methods=['GET'])
def view_users():
    try:
        user_list = []
        with open('data/users.csv', 'r') as users_file:
            csv_reader = csv.DictReader(users_file)
            for row in csv_reader:
                user_list.append(row)
            return json.dumps({"users": user_list})
    except FileNotFoundError:
        return json.dumps({"message": "File not found"})

@app.route('/renton/properties/add', methods=['POST'])
def add_property():
    try:
        auth_token = request.headers.get('auth_token')
        name = request.json['name']
        area = request.json['area']
        bedroom = request.json['bedroom']
        amenities = request.json['amenities']
        furnishing = request.json['furnishing']
        locality = request.json['locality']
        price = request.json['price']
        # key = "RentOn"
        # data = jwt.decode(auth_token, key)
        valid_flag = decode_auth(auth_token)
        if valid_flag:
            if data['user_type'] == 'admin' or data['user_type'] == 'owner':
                if data['expire'] >= time.time():
                    with open('data/properties.csv', 'r') as csv_file:
                        csv_reader = csv.reader(csv_file)
                        data_csv = list(csv_reader)
                    prop = {}
                    # print(data_csv)
                    prop_id = int(data_csv[-1][0]) + 1
                    prop['id'] = prop_id
                    prop['name'] = name
                    prop['area'] = area
                    prop['bedroom'] = bedroom
                    prop['amenities'] = amenities
                    prop['furnishing'] = furnishing
                    prop['locality'] = locality
                    prop['price'] = price
                    prop['owner_id'] = data['user_id']
                    # print(prop)
                    with open('data/properties.csv', 'a') as csv_file:
                        headers = ['id', 'name', 'area', 'bedroom', 'amenities', 'furnishing', 'locality', 'price', 'owner_id']
                        csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
                        csv_writer.writerow(prop)
                    return json.dumps({"message": "Property added successfully", "status": True})
                else:
                    return json.dumps({"message": "Session time expired", "status": False})
            else:
                return json.dumps({"message": "Only admin and owner has the previlage", "status": False})
        else:
            return json.dumps({"message":"Session expired", "status": False})
    except KeyError as e:
        return json.dumps({"message": "Key not found, %s" % (e.args[0]), "status": False})
    except FileNotFoundError:
        return json.dumps({"message": "File not found", "status": False})

@app.route('/renton/properties/update', methods=['PATCH'])
def update_property():
    try:
        auth_token = request.headers.get('auth_token')
        prop_id = request.json['id']
        name = request.json['name']
        area = request.json['area']
        bedroom = request.json['bedroom']
        amenities = request.json['amenities']
        furnishing = request.json['furnishing']
        locality = request.json['locality']
        price = request.json['price']
        # key = "RentOn"
        valid_flag, decode_data = decode_auth(auth_token)
        # decode_data = jwt.decode(auth_token, key)
        if valid_flag:
            if decode_data['user_type'] == 'admin' or decode_data['user_type'] == 'owner':
                # if decode_data['expire'] >= time.time():
                with open('data/properties.csv','r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    data = list(csv_reader)
                # print(data)
                for i in range(len(data)):
                    if data[i][0] == prop_id:
                        if decode_data['user_id'] == data[i][8]:
                            data[i][0] = prop_id
                            data[i][1] = name
                            data[i][2] = area
                            data[i][3] = bedroom
                            data[i][4] = amenities
                            data[i][5] = furnishing
                            data[i][6] = locality
                            data[i][7] = price
                            data[i][8] = decode_data['user_id']
                        else:
                            return json.dumps({"message": "Wrong property", "status": False})

                with open('data/properties.csv', 'w') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerows(data)
                return json.dumps({"message": "Property updated successfully", "status": True})
                # else:
                #     return json.dumps({"message": "Session time expired", "status": False})
            else:
                return json.dumps({"message": "Only owner or admin has the previlage", "status": False})
        else:
            return json.dumps({"message":"Session expired", "status": False})
    except KeyError as e:
        return json.dumps({"message": "Key not found, %s" % (e.args[0]), "status": False})
    except FileNotFoundError:
        return json.dumps({"message": "File not found", "status": False})
    except jwt.exceptions.DecodeError:
        return json.dumps({"message": "Decode error in jwt", "status": False})

@app.route('/renton/properties/delete', methods=['DELETE'])
def delete_property():
    try:
        auth_token = request.json['auth_token']
        prop_id = request.json['id']
        key = "RentOn"
        decode_data = jwt.decode(auth_token, key)
        if decode_data['user_type'] == 'admin' or decode_data['user_type'] == 'owner':
            if decode_data['expire'] >= time.time():
                new_list = []
                with open('data/properties.csv', 'r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    lines  = list(csv_reader)
                    for i in range(len(lines)):
                        if lines[i][0] != prop_id:
                            new_list.append(lines[i])
                with open('data/properties.csv', 'w') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerows(new_list)
                return json.dumps({"message": "Property deleted successfully"})
            else:
                return json.dumps({"message": "Session expired"})
        else:
            return json.dumps({"message": "Only owner and admin has the previlage"})
    except KeyError as e:
        return json.dumps({"message": "Key not found, %s" % (e.args[0])})
    except FileNotFoundError:
        return json.dumps({"message": "File not found"})
    except jwt.exceptions.DecodeError:
        return json.dumps({"message": "Decode error in jwt"})

@app.route('/renton/properties/view', methods=['GET'])
def view_properties():
    try:
        property_list = []
        with open('data/properties.csv', 'r') as prop_file:
            csv_reader = csv.DictReader(prop_file)
            # print(csv_reader['owner_id'])
            for row in csv_reader:
                owner_id = row['owner_id']
                property_list.append(row)
                with open('data/users.csv', 'r') as user_file:
                    user_reader = csv.DictReader(user_file)
                    for line in user_reader:
                        if line['id'] == owner_id:
                            property_list.append({"owner details": line})
        return json.dumps({"properties": property_list})
    except FileNotFoundError:
        return json.dumps({"message": "File not found"})
                     



