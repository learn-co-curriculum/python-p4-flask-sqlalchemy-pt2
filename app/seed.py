#!/usr/bin/env python3
#seeding is an essential strategy for creating realistic sets of data to test against
#Seeding in Flask-SQLAlchemy, we are working with db.session objects instead of session objects

from random import choice as rc

from faker import Faker

from app import app
from models import db, Owner, Pet     #To retrieve all pets

db.init_app(app)

#we initialize the application with our SQLAlchemy instance
#This is necessary because db is generated with each new run of the application- it lives in models.py, 
#so we need to initialize the application to connect the two. 

fake = Faker()

with app.app_context():
    
#we create an application context with app.app_context() before we begin
# it ensures that applications fail quickly if they are not configured with this important context

    Pet.query.delete()
    Owner.query.delete()

#Deletion of all records is handled through models with Model.query.delete() rather than session.query(Model).delete()

    owners = []
    for n in range(50):
        owner = Owner(name=fake.name())
        owners.append(owner)

    db.session.add_all(owners)

    pets = []
    species = ['Dog', 'Cat', 'Chicken', 'Hamster', 'Turtle']
    for n in range(100):
        pet = Pet(name=fake.first_name(), species=rc(species), owner=rc(owners))
        pets.append(pet)

    db.session.add_all(pets)
    db.session.commit()
