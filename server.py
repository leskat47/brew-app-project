from flask import Flask, render_template, redirect, request, flash, session
from model import User, Recipe, Style, connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"



@app.route('/')
def index():

    return render_template("homepage.html")


@app.route('/explore', methods=['GET', 'POST'])
def show_explore():
    # Create lists of recipes and styles which will show in the dropdown selections. list_recipes will
    # hold a list of recipes within a style when style type is selected.
    selectlist_recipes = []
    selectlist_styles = []
    list_recipes = []
    for recipe_obj in Recipe.query.all():
        selectlist_recipes.append(recipe_obj.name)
    for style_obj in Style.query.all():
        selectlist_styles.append(style_obj.style_name)

    # If a submit button is clicked, post request is called. For selected style, show recipe list.
    # For recipe selected, show recipe.
    if request.method == "POST":
        # Prevent an error if select is clicked with no value selected
        # try:
        #     request.form.get("style")
        # except ValueError:
        #     flash("Please make a selection first")
        #     return redirect("/explore", selectlist_recipes=selectlist_recipes, selectlist_styles=selectlist_styles)
        # Render either recipe list for style selection or recipe
        # if request.form.get("style") == None:
        #     flash("Please make a selection first")
        #     return redirect("/explore", selectlist_recipes=selectlist_recipes, selectlist_styles=selectlist_styles)
        if request.form.get("style"):
            style = request.form.get("style")
            for recipe in Recipe.query.filter_by(style_name=style).all():
                list_recipes.append(recipe.name)
            return render_template("explore_brews.html", list_recipes=list_recipes, selectlist_recipes=selectlist_recipes, selectlist_styles=selectlist_styles)
        elif request.form.get("recipe"):
            recipe = request.form.get("recipe")
            display_recipe = Recipe.query.filter_by(name=recipe).one()
            name = display_recipe.name
            return render_template("explore_brews.html", selectlist_recipes=selectlist_recipes,
                                   selectlist_styles=selectlist_styles, name=name)
        elif request.form.get("all"):
            names = []
            for recipe in Recipe.query.all():
                names.append(recipe.name)
            return render_template("explore_brews.html", selectlist_recipes=selectlist_recipes,
                                   selectlist_styles=selectlist_styles, names=names)

    return render_template("explore_brews.html", selectlist_recipes=selectlist_recipes, selectlist_styles=selectlist_styles)


@app.route('/recipe/<string:recipe>')
def get_recipes(recipe):
    display_recipe = Recipe.query.filter_by(name=recipe).one()
    name = display_recipe.name
    source = display_recipe.source
    style = display_recipe.style_name
    notes = display_recipe.notes

    hops = display_recipe.hins
    hop_dict = {}
    hop_steps = []
    for ingredient in hops:
        hop_dict["name"] = ingredient.hop.name
        hop_dict["form"] = ingredient.hop.form
        hop_dict["amount"] = ingredient.amount
        hop_dict["phase"] = ingredient.phase
        hop_dict["time"] = ingredient.time
        hop_dict["kind"] = ingredient.kind
        hop_steps.append(hop_dict.copy())
    print hop_dict

    ferms = display_recipe.fins
    ferm_dict = {}
    ferm_steps = []
    for ingredient in ferms:
        ferm_dict["name"] = ingredient.fermentable.name
        ferm_dict["kind"] = ingredient.fermentable.kind
        ferm_dict["amount"] = ingredient.amount
        ferm_dict["phase"] = "Steep"
        ferm_steps.append(ferm_dict.copy())

    if display_recipe.mins:
        misc = display_recipe.mins
        misc_dict = {}
        misc_steps = []
        for ingredient in misc:
            misc_dict["name"] = ingredient.misc.name
            misc_dict["kind"] = ingredient.misc.kind
            misc_dict["phase"] = ingredient.misc.use
            misc_dict["amount"] = ingredient.amount
            misc_dict["time"] = ingredient.time
            misc_steps.append(misc_dict.copy())
    else:
        misc_steps = None

    yeasts = display_recipe.yins
    yeast_dict = {}
    yeast_steps = []
    for ingredient in yeasts:
        yeast_dict["name"] = ingredient.yeast.name
        yeast_dict["amount"] = ingredient.amount
        yeast_dict["kind"] = ingredient.yeast.kind
        yeast_dict["form"] = ingredient.yeast.form
        yeast_steps.append(yeast_dict.copy())

    return render_template("recipe.html", name=name, source=source, style=style,
                            notes=notes, hop_steps=hop_steps, ferm_steps=ferm_steps,
                            misc_steps=misc_steps, yeast_steps=yeast_steps)


@app.route('/mybrews')
def show_mybrews():
    return render_template("mybrews.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")
        first_name = request.form.get("fname")
        last_name = request.form.get("lname")

        # Check to see if email address is taken
        if (User.query.filter_by(email=email).all()) != []:
            flash("Sorry, that email address already has an account")
            return redirect('/register')
        elif (User.query.filter_by(username=username).all()) != []:
            flash("Sorry, that username is already in use")
            return redirect('/register')
        else:
            # Creating instance of User class with associated info
            current_person = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)

            # adding the user's info to the DB
            db.session.add(current_person)
            db.session.commit()

            flash("You were successfully registered!")
            return redirect("/")

    return render_template("registration.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print username
        pw_in_db = User.query.filter_by(username=username).all()
        print pw_in_db

        if pw_in_db == []:
            flash("This username is not registered - please create an account.")
            return redirect("/register")
        else:
            if pw_in_db[0].password == password:
                session["username"] = username
                session["password"] = password
                user_id = User.query.filter_by(username=username).one().user_id
                print session["username"]
                flash("You were successfully logged in!")
                return redirect("/")
            else:
                flash("User name and password do not match.")
                return redirect("/login")

    return render_template("login.html")


@app.route('/logout', methods=["GET"])
def logout():
    print "LOGGED OUT"
    session["username"] = None
    session["password"] = None

    flash("Logged you out!")
    return redirect("/")
    
# @app.route('/getstarted')
# 	pass




if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    app.run()
