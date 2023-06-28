#!/usr/bin/env python3
#Serving Database Records in Flask Applications

from flask import Flask, make_response
from flask_migrate import Migrate

from models import db, Owner, Pet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' #Our app.config is set up to point to our existing database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   #SQLALCHEMY_TRACK_MODIFICATIONS' is set to False to avoid building up too much unhelpful data in memory when our application is running.

migrate = Migrate(app, db) #Our migrate instance configures the application and models for Flask-Migrate

db.init_app(app)  #connects our database to our application before it runs

@app.route('/') #determines which resources are available at which URLs and saves them to the application's URL map
def index():
    response = make_response( #Responses are what we return to the client after a request
        '<h1>Welcome to the pet/owner directory!</h1>',
        200 #The included response has a status code of 200, which means that the resource exists and is accessible at the provided URL.
    )
    return response
#Enter the app/ directory if you're not there already and run python app.py
#Navigate to 127.0.0.1:5555, and you should see this message in your browser
#Welcome to the pet/owner directory

#Creating our views
#Let's start working on displaying data in our Flask application.
#We'll start by adding another view for pets, searched by ID

@app.route('/pets/<int:id>')
def pet_by_id(id):
    pet = Pet.query.filter(Pet.id == id).first()

    if not pet:
        response_body = '<h1>404 pet not found</h1>'
        response = make_response(response_body, 404)
        return response

    response_body = f'''
        <h1>Information for {pet.name}</h1>
        <h2>Pet Species is {pet.species}</h2>
        <h2>Pet Owner is {pet.owner.name}</h2>
    '''

    response = make_response(response_body, 200)

    return response

#Run the application again and navigate to 127.0.0.1:5555/pets/1
#Because we generated data with Faker, you will probably not see the same names, but :
#e.g Information for Ben.

#Navigate now to 127.0.0.1:5555/pets/1000.
#You will see an error message, "404 pet not found," that suggests something went wrong on your server. 
#We're not tracking 1000 pets right now, but we still don't want our users to see error pages like this
#Let's make another small change to the pet_by_id view to fix this

#404 is the status code for "Not Found".
# used for the case we see here: an ID or username that went into the URL but does not exist

#Let's finish out with a view for owners:

# pet_by_id()
@app.route('/owner/<int:id>')
def owner_by_id(id):
    owner = Owner.query.filter(Owner.id == id).first()

    if not owner:
        response_body = '<h1>404 owner not found</h1>'
        response = make_response(response_body, 404)
        return response

    response_body = f'<h1>Information for {owner.name}</h1>'

    pets = [pet for pet in owner.pets]

    if not pets:
        response_body += f'<h2>Has no pets at this time.</h2>'

    else:
        for pet in pets:
            response_body += f'<h2>Has pet {pet.species} named {pet.name}.</h2>'

    response = make_response(response_body, 200)

    return response
#Not all people have pets, but they still might be in our database if they had a pet before or are inquiring about pets now
#If an owner has no pets, we return a message informing the user of this fact
#***note : back to our browser (localhost:5555/owner/1)
#***Information for Ben
#***Has pet Dog named Ben

#If an owner does have pets, we use an interpretation to collect the pets
#and a for loop to add a new line item for each pet with its species and name



if __name__ == '__main__':
    app.run(port=5555)

#we should now be able to use Flask-SQLAlchemy and Flask-Migrate to send and receive information between databases, web servers, and clients far away

