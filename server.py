from flask import Flask, render_template, redirect, request, flash, session
from model import connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"



@app.route('/')
def index():

    return render_template("homepage.html")


@app.route('/explore')
def show_explore():
    return render_template("explore_brews.html")

@app.route('/mybrews')
def show_mybrews():
    return render_template("mybrews.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")
        zipcode = request.form.get("zipcode")

        # Check to see if email address is taken
        if (User.query.filter_by(email=email).all()) != {}:
            flash("Sorry, that email address already has an account")
            return redirect('/registration')
        elif (User.query.filter_by(username=username).one()) is not Nome:
            flash("Sorry, that username is already in use")
            return redirect('/registration')
        else:
            # Creating instance of User class with associated info
            current_person = User(email=email, password=password, username=username, zipcode=zipcode)

            # adding the user's info to the DB
            db.session.add(current_person)
            db.session.commit()

            flash("You were successfully registered!")
            return redirect("/")

    return render_template("registration.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        pw_in_db = User.query.filter_by(email=email).all()

        if pw_in_db == []:
            flash("This email is not registered - please create an account.")
            return redirect("/registration")
        else:
            if pw_in_db[0].password == password:
                session["email"] = email
                session["password"] = password
                user_id = User.query.filter_by(email=email).one().user_id
                path = "/users/" + str(user_id)
                flash("You were successfully logged in!")
                return redirect("/")
            else:
                flash("User name and password do not match.")
                return redirect("/login")

    return render_template("login.html")


# @app.route('/getstarted')
# 	pass




if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    app.run()
