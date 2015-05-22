from flask import Flask, render_template, redirect, request, flash, session
from model import User, Recipe, Style, Extract, Hop, Misc, Yeast, Fermentable, YeastIns, HopIns, FermIns, MiscIns, ExtIns, connect_to_db, db
import json
from itertools import izip_longest, chain, repeat

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

    selectlist_recipes = sorted(selectlist_recipes)
    selectlist_styles = sorted(selectlist_styles)
    # for brew_obj in Style.query.filter_by(userid=session["user_id"]):
    #     selectlist_userrecipes.append(brew_obj.)

    # If a submit button is clicked, post request is called. For selected style, show recipe list.
    # For recipe selected, show recipe.
    if request.method == "POST":
        print ("POST HAPPENED")
        # Prevent an error if select is clicked with no value selected
        # try:
        #     request.form.get("style")
        # except ValueError:
        #     flash("Please make a selection first")
        #     return redirect("/explore", selectlist_recipes=selectlist_recipes, selectlist_styles=selectlist_styles)

        # Render either recipe list for style selection or recipe
        if request.form.get("style"):
            print("STYLE RAN")
            style = request.form.get("style")
            for recipe in Recipe.query.filter_by(style_name=style).all():
                list_recipes.append(recipe.name)
            return render_template("explore_brews.html", list_recipes=list_recipes, selectlist_recipes=selectlist_recipes, selectlist_styles=selectlist_styles)
        elif request.form.get("recipe"):
            print("RECIPE RAN")
            recipe = request.form.get("recipe")
            display_recipe = Recipe.query.filter_by(name=recipe).one()
            name = display_recipe.name
            return render_template("explore_brews.html", selectlist_recipes=selectlist_recipes,
                                   selectlist_styles=selectlist_styles, name=name)
        # elif request.form.get("brew"):
        #     recipe = request.form.get("recipe")
        #     display_recipe = Recipe.


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


@app.route('/addrecipe', methods=['GET', 'POST'])
def enter_recipe():
    if request.method == "POST":
        data = request.get_json()

        grains = data['grains']
        extracts = data['extracts']
        hops = data['hops']
        miscs = data['miscs']
        yeasts = data['yeasts']

        # Recipe values
        name = data["name"]
        user_id = session["user_id"]
        source = data["source"]
        public = data["share"]
        style_name = data["style"]
        notes = data["notes"]
        batch_size = data["batch_size"]
        new_recipe = Recipe(name=name, source=source, user_id=user_id, public=public,
                            notes=notes, style_name=style_name, batch_size=batch_size)
        db.session.add(new_recipe)
        db.session.commit()

        # Recipe_id will be used in all instructions uploads
        recipe_id = Recipe.query.filter_by(name=name, user_id=user_id)[0].recipe_id

        # Grain Instructions
        for i in range(0, len(data['grains']), 3):
            grain_name = grains[i]["value"]
            print grain_name
            ferm_id = Fermentable.query.filter_by(name=grain_name)[0].id
            grain_amount = grains[i+1]["value"]
            grain_units = grains[i+2]["value"]
            new_fermins = FermIns(recipe_id=recipe_id, ferm_id=ferm_id, amount=grain_amount,
                                  units=grain_units, )
            db.session.add(new_fermins)
            db.session.commit()

        # Extract Instructions
        for i in range(0, len(data['extracts']), 3):
            extract_name = extracts[i]["value"]
            print extract_name
            extract_id = Extract.query.filter_by(name=extract_name)[0].extract_id
            extract_amount = extracts[i+1]["value"]
            extract_units = extracts[i+2]["value"]

            new_extins = ExtIns(recipe_id=recipe_id, extract_id=extract_id, amount=extract_amount,
                                units=extract_units)
            db.session.add(new_extins)
            db.session.commit()

        # Hops Instructions
        for i in range(0, len(data['hops']), 6):
            hop_name = hops[i]["value"]
            hop_id = Hop.query.filter_by(name=hop_name)[0].hop_id
            hop_amount = hops[i+1]["value"]
            hop_units = hops[i+2]["value"]
            hop_phase = hops[i+3]["value"]
            time = hops[i+4]["value"]
            kind = hops[i+5]["value"]

            new_hopsins = HopIns(recipe_id=recipe_id, hop_id=hop_id, amount=hop_amount, phase=hop_phase, time=time, kind=kind)
            db.session.add(new_hopsins)
            db.session.commit()

        # Misc Instructions
        for i in range(0, len(data['miscs']), 5):
            misc_name = miscs[i]["value"]
            misc_id = Misc.query.filter_by(name=misc_name)[0].misc_id
            misc_amount = miscs[i+1]["value"]
            misc_phase = miscs[i+2]["value"]
            misc_time = miscs[i+3]["value"]
            misc_units = miscs[i+4]["value"]
            new_miscins = MiscIns(recipe_id=recipe_id, misc_id=misc_id, phase=misc_phase, amount=misc_amount,
                                  time=misc_time, units=misc_units)
            db.session.add(new_miscins)
            db.session.commit()

        # Yeast Instructions
        for i in range(0, len(data['yeasts']), 3):
            yeast_name = yeasts[i]["value"]
            yeast_id = Yeast.query.filter_by(name=yeast_name)[0].yeast_id
            yeast_amount = yeasts[i+1]["value"]
            yeast_units = yeast[i+2]["value"]
            new_yeastins = YeastIns(recipe_id=recipe_id, id=yeast_id, amount=yeast_amount, units=yeast_units)
            db.session.add(new_yeastins)
            db.session.commit

        return redirect("/recipe/%s" % name)

    grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles = feed_recipe_form()

    return render_template("recipeform.html", selectlist_styles=selectlist_styles, grain_choice=grain_choice, hop_choice=hop_choice,
                           extract_choice=extract_choice, misc_choice=misc_choice, yeast_choice=yeast_choice)


@app.route('/formrows')
def formsource():
    return render_template('formsource.html')


@app.route('/check_recipe_name', methods=["POST"])
def check_name():
    print request.form
    test_name = request.form.get("name")
    print "TEST NAME:", test_name
    if Recipe.query.filter_by(name=test_name).all() == []:
        return "okay"
    else:
        return "nope"

# @app.route('/uploadrecipe')
# def upload():


# @app.route('/editrecipe/<string:recipe>')
# def editrecipe():
#     pass


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
                session["user_id"] = user_id

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
    session["user_id"] = None

    flash("Logged you out!")
    return redirect("/")


def feed_recipe_form():
    selectlist_styles = []
    for style_obj in Style.query.all():
        selectlist_styles.append(style_obj.style_name)
    grains = Fermentable.query.all()
    extracts = Extract.query.all()
    hops = Hop.query.all()
    miscs = Misc.query.all()
    yeasts = Yeast.query.all()

    grain_choice = []
    for g in grains:
        if g.name not in grain_choice:
            grain_choice.append(g.name)
    extract_choice = []
    for e in extracts:
        if e.name not in extract_choice:
            extract_choice.append(e.name)
    hop_choice = []
    for h in hops:
        if h.name not in hop_choice:
            hop_choice.append(h.name)
    misc_choice = []
    for m in miscs:
        if m.name not in misc_choice:
            misc_choice.append(m.name)
    yeast_choice = []
    for y in yeasts:
        if y.name not in yeast_choice:
            yeast_choice.append(y.name)

    grain_choice = sorted(grain_choice)
    extract_choice = sorted(extract_choice)
    hop_choice = sorted(hop_choice)
    misc_choice = sorted(misc_choice)
    yeast_choice = sorted(yeast_choice)
    selectlist_styles = sorted(selectlist_styles)

    return grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles


if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    app.run()
