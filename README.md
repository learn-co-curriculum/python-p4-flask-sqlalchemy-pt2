# Flask-SQLAlchemy Part 2

## Learning Goals

- Build and run a Flask application on your computer.
- Extend a Flask application to meet the unique requirements of different projects.

***

## Key Vocab

- **Web Framework**: software that is designed to support the development of
  web applications. Web frameworks provide built-in tools for generating web
  servers, turning Python objects into HTML, and more.
- **Extension**: a package or module that adds functionality to a Flask
  application that it does not have by default.
- **Request**: an attempt by one machine to contact another over the internet.
- **Client**: an application or machine that accesses services being provided
  by a server through the internet.
- **Web Server**: a combination of software and hardware that uses Hypertext
  Transfer Protocol (HTTP) and other protocols to respond to requests made
  over the internet.
- **Web Server Gateway Interface (WSGI)**: an interface between web servers
  and applications.
- **Template Engine**: software that takes in strings with tokenized
  values, replacing the tokens with their values as output in a web browser.

***

## Introduction

Now that we've created a database that is intrinsically linked to a Flask
application, we should probably try to use it! The completed code from the
prior lesson is already configured here just enter your virtual environment
with `pipenv install && pipenv shell` and run `flask db upgrade head` from the
`server/` directory to generate your database.

Make sure to run the following commands in the `server/` directory as well to
configure your Flask environment:

```console
$ export FLASK_APP=app.py
$ export FLASK_RUN_PORT=5555
```

Port 5555 is already configured in `server/app.py` as well, if you prefer to run
your application as a script.

***

## The Flask Shell

We can absolutely interact with our code in the Python shell or `ipdb`, but
working with a web framework presents a bit of a conundrum: the application
isn't running!

Flask comes equipped with an interactive shell that runs a development version
of your application upon launch. Inside of this shell, you can interact with
models, views, contexts, and the database as if the application were really
running online.

If you're not there already, navigate to the `server/` directory. Enter `flask
shell` to enter the Flask shell.

```console
$ flask shell
# => Python 3.8.13 (main, May 12 2022, 12:46:07) [Clang 13.1.6 (clang-1316.0.21.2)] on darwin
# => App: app
# => Instance: /python-p4-flask-sqlalchemy-pt2/server/instance
>>> # enter code here!
```

Now that we're in, let's start adding some records:

```console
>>> from app import app
>>> from models import db, Owner, Pet

>>> pet = Pet(name="Ben", species="Dog")
>>> db.session.add(pet)
>>> db.session.commit()
>>> pet.id
# => 1

>>> owner = Owner(name="Ben")
>>> db.session.add(owner)
>>> db.session.commit()
>>> owner
# => <Pet Owner Ben>

>>> pet.owner = owner
>>> db.session.add(pet)
>>> db.session.commit()
>>> pet.owner
# => <Pet Owner Ben>
```

As with any shell, this is a great tool for debugging and adding one or two
records. We want our app to handle many records though, and we might want to
test what to do if there are too many pets to fit on a single page or multiple
owners and pets with the same names. That would take too long to do by hand in
the Flask shell.

***

## Seeding Flask-SQLAlchemy

As we saw in Phase 3, seeding is an essential strategy for creating realistic
sets of data to test against. Seeding in Flask-SQLAlchemy works just as it does
in vanilla SQLAlchemy, with the generally unimportant exception that we are
working with `db.session` objects instead of `session` objects. There are also
cases where methods will be run from models instead of the session itself- we'll
see an example in our seed script.

Open `server/seed.py` and enter the following:

```py
#!/usr/bin/env python3

from random import choice as rc

from faker import Faker

from app import app
from models import db, Owner, Pet

fake = Faker()

with app.app_context():

    Pet.query.delete()
    Owner.query.delete()

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

```

You'll notice that this looks virtually identical to our seed scripts from
Phase 3: we delete all records from the database, make lists of owner and pet
instances, generate attributes with `random` and `faker`, then commit the
transaction.

Let's go over the differences:

1. . We need to create an application context with `app.app_context()` before we
   begin. This will not necessarily be used, but it ensures that applications
   fail quickly if they are not configured with this important context.
2. Deletion of all records is handled through models with `Model.query.delete()`
   rather than `session.query(Model).delete()`. This syntax is carried through
   other SQLAlchemy statements and queries as well. Because the session is
   managed through the Flask application, there is no need to call it explicitly
   when we run these statements and queries.

These are the only differences you will typically see between Flask-SQLAlchemy
scripts and vanilla SQLAlchemy scripts. Keep an eye out for minor errors that
arise and refer back to the [Flask-SQLAlchemy documentation][flask_sqla] as
needed.

Run `python seed.py` from the `server/` directory to seed the database.

***

## Querying Flask-SQLAlchemy

Like deletions, queries in Flask-SQLAlchemy are best handled through the models
themselves. To retrieve all pets from the Flask shell, you would run:

```console
>>> from models import db, Pet, Owner
>>> from app import app
>>> with app.app_context():
...     Pet.query.all()
...
# => [<Pet Richard, Turtle>, <Pet Jonathan, Cat>, <Pet Victoria, Chicken>, ...]
```

We can also narrow our search using filters or chains of filters:

```console
// imports
>>> with app.app_context():
...     Owner.query.filter(Owner.name >= 'Ben').all()
# => [<Pet Owner Brenda Hernandez>, <Pet Owner Brian Stone>, ...]

>>> with app.app_context():
...     Owner.query.filter(Owner.name <= 'Ben').limit(2).all()
...
# => [<Pet Owner Alan Bryant>, <Pet Owner Allison Phillips DDS>]
```

Queries in Flask-SQLAlchemy have access to all of the same methods as those in
vanilla SQLAlchemy- just remember to start your statements with models!

***

## Serving Database Records in Flask Applications

The moment we've all been waiting for has arrived! We've already learned about
databases and SQLAlchemy, but Phase 4 is about _web_ development. Let's use
our newly-seeded database to put pet and owner information onto the internet.

Open `server/app.py` and modify it to reflect the code below:

```py
# server/app.py

#!/usr/bin/env python3

from flask import Flask, make_response
from flask_migrate import Migrate

from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    response = make_response(
        '<h1>Welcome to the pet/owner directory!</h1>',
        200
    )
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)

```

We've seen all of this code before in one way or another, but let's take a
moment to review before we keep moving:

- Our `app.config` is set up to point to our existing database, and
  `'SQLALCHEMY_TRACK_MODIFICATIONS'` is set to `False` to avoid building up
  too much unhelpful data in memory when our application is running.
- Our `migrate` instance configures the application and models for
  Flask-Migrate.
- `db.init_app` connects our database to our application before it runs.
- `@app.route` determines which resources are available at which URLs and
  saves them to the application's URL map.
- Responses are what we return to the client after a request. The included
  response has a status code of 200, which means that the resource exists
  and is accessible at the provided URL.

Enter the `server/` directory if you're not there already and run `python app.py`.
Navigate to 127.0.0.1:5555, and you should see this message in your browser:

![h1 text "Welcome to the pet/owner directory!" in Google Chrome](
https://curriculum-content.s3.amazonaws.com/python/flask-sqlalchemy-pt2-1.png
)

### Creating Our Views

Let's start working on displaying data in our Flask application.

We'll start by adding another view for pets, searched by ID.

```py
# server/app.py

from flask import Flask, make_response
from flask_migrate import Migrate

from models import db, Pet

# after index()

@app.route('/pets/<int:id>')
def pet_by_id(id):
    pet = Pet.query.filter(Pet.id == id).first()
    
    response_body = f'''
        <h1>Information for {pet.name}</h1>
        <h2>Pet Species is {pet.species}</h2>
        <h2>Pet Owner is {pet.owner.name}</h2>
    '''
    
    response = make_response(response_body, 200)

    return response

# if __name__ ...

```

Run the application again and navigate to [127.0.0.1:5555/pets/1](
127.0.0.1:5555/pets/1). Because we
generated data with Faker, you will probably not see the same names, but
your format should match below:

![h1 text Information for Ann. Line items for species (Hamster) and owner name
(Angel Rich).](
https://curriculum-content.s3.amazonaws.com/python/flask-sqlalchemy-pt2-2.png
)

Navigate now to 127.0.0.1:5555/pets/1000. You will see an error message that
suggests something went wrong on your server. We're not tracking 1000 pets right
now, but we still don't want our users to see error pages like this. Let's make
another small change to the `pet_by_id()` view to fix this:

```py
# server/app.py

from flask import Flask, make_response
from flask_migrate import Migrate

from models import db, Pet

# after index()

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

# if __name__ ...

```

404 is the status code for "Not Found". It is generally used for the case we
see here: an ID or username that went into the URL but does not exist. Our 404
page is quite minimal, but applications like Twitter and Facebook format them
with descriptive messages and the same style and formatting of their website as
a whole.

Let's finish out with a view for owners:

```py
# server/app.py

from flask import Flask, make_response
from flask_migrate import Migrate

from models import db, Pet, Owner

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

# if __name__ ...

```

Not all people have pets, but they still might be in our database if they had a
pet before or are inquiring about pets now. If an owner has no pets, we return a
message informing the user of this fact.

![Brittney Foster has no pets at this time.](
https://curriculum-content.s3.amazonaws.com/python/flask-sqlalchemy-pt2-3.png
)

If an owner _does_ have pets, we use an interpretation to collect the pets and
a for loop to add a new line item for each pet with its species and name.

![Veronica Frost has a hamster named Jerry and a Dog named Patricia](
https://curriculum-content.s3.amazonaws.com/python/flask-sqlalchemy-pt2-4.png
)

***

## Conclusion

You should now be able to use Flask-SQLAlchemy and Flask-Migrate to send and
receive information between databases, web servers, and clients far away. These
powerful tools require practice to get used to- our next lesson will give you
the chance to write a full-stack Flask application on your own.

If your application for this lesson still isn't working, don't worry! Refer to
the solution code below and meet with your peers, instructors, and coaches to
iron out any remaining wrinkles.

***

## Solution Code

```py
# server/app.py

from flask import Flask, make_response
from flask_migrate import Migrate

from models import db, Pet, Owner

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    response = make_response(
        '<h1>Welcome to the pet/owner directory!</h1>',
        200
    )
    return response

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

if __name__ == '__main__':
    app.run(port=5555, debug=True)

```

***

## Resources

- [Quickstart - Flask-SQLAlchemy][flask_sqla]
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)
- [Flask Extensions, Plug-ins, and Related Libraries - Full Stack Python](https://www.fullstackpython.com/flask-extensions-plug-ins-related-libraries.html)

[flask_sqla]: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#
