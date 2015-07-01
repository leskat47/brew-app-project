from flask import Flask, render_template, redirect, request, flash, session, url_for, send_from_directory
from model import User, Recipe, Brew, Style, Extract, Hop, Misc, Yeast, Fermentable, YeastIns, HopIns, FermIns, MiscIns, ExtIns, connect_to_db, db
from feeder import load_recipes, load_hops_ins, load_ferm_ins, load_ext_ins, load_misc_ins, load_yeast_ins, calc_color
from builder import feed_recipe_form, get_recipe_info, get_selectlists, get_brewlist, show_brew_recipe, color_conversion
import xml.etree.ElementTree as ET
import os
from werkzeug import secure_filename
import json
import datetime

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

app.config['UPLOAD_FOLDER'] = '/tmp/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['xml'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# ROUTES:
# /explore      -> populate dropdown searches. On post, return recipe names
# /myrecipes    -> populate list of user recipes
# /recipe/recipename -> display recipe
# /check_brew   -> Check for duplicate brew
# /addbrew      -> Passthrough route from recipe page that adds a brew and produces new brew_id
# /delete_recipe-> Delete recipe and connected instructions

# /mybrews      -> collect brews for user, show table of selected brew info, build dropdowns, return search results
# /deletebrew/brewid -> Ajax accessed to remove a brew from user's list
# /boil         -> add boil (on change) to brew table in db

# /brew/brewid  -> populate brew page with associated brew data, display page. On post, route to update

# /addrecipe    -> populate menus and display form. On post, prep inputs for database and commit to database.
# /editrecipe   -> Get data for given recipe. Populate menus. Display form.
# /uploadrecipe -> Uploaded file saved to uploads folder, parsed and committed through feeder.py function
# /check_recipename -> Ajax accessed to check whether recipe name entered in form is duplicated in db.
# /colorcalc    -> Ajax accessed to calculate beer color


# ***************************************************************************************
# Home page

@app.route('/')
def index():
    return render_template("homepage.html")


# ***************************************************************************************
# Explore recipes selections

@app.route('/explore', methods=['GET', 'POST'])
def show_explore():

    if session:
        selectlist_recipes, selectlist_styles, selectlist_user, sel_user_styles = get_selectlists(session["user_id"])
        new = True
    else:
        selectlist_recipes, selectlist_styles, selectlist_user, sel_user_styles = get_selectlists(9999)
        new = True

    # For recipe selected, show recipe.
    if request.method == "POST":
        # Render either recipe list for style selection or recipe
        if request.form.get("style"):
            style = request.form.get("style")
            list_recipes = []
            for recipe in Recipe.query.filter_by(style_name=style).all():
                list_recipes.append(recipe.name)
            return render_template("explore_brews.html", list_recipes=list_recipes,
                                   selectlist_recipes=selectlist_recipes,
                                   selectlist_styles=selectlist_styles)
        elif request.form.get("recipe"):
            recipe = request.form.get("recipe")
            name, source, style, batch_size, batch_units, notes, hop_steps, ext_steps, ferm_steps, misc_steps, yeast_steps, srm_color = get_recipe_info(recipe)
            print "SERVER SRM ", srm_color
            color = color_conversion(srm_color)
            deleteable = False
            if session["user_id"] and Recipe.query.filter_by(name=recipe).one().user_id == session["user_id"]:
                deleteable = True
            return render_template("explore_brews.html", selectlist_recipes=selectlist_recipes, batch_size=batch_size,
                                   selectlist_styles=selectlist_styles, name=name, source=source, color=color, style=style,
                                   notes=notes, hop_steps=hop_steps, ext_steps=ext_steps, ferm_steps=ferm_steps,
                                   misc_steps=misc_steps, yeast_steps=yeast_steps, deleteable=deleteable)

    return render_template("explore_brews.html", new=new, selectlist_recipes=selectlist_recipes,
                           selectlist_styles=selectlist_styles, selectlisrt_user=selectlist_user,
                           sel_user_styles=sel_user_styles, session=session)


# ***************************************************************************************
# Explore Recipes right panel displays

# List user's recipes
@app.route('/myrecipes')
def get_my_recipes():
    selectlist_recipes, selectlist_styles, selectlist_user, sel_user_styles = get_selectlists(session["user_id"])
    recipe_list = Recipe.query.filter_by(user_id=session["user_id"]).all()
    recipes = []
    for recipe in recipe_list:
        recipes.append(recipe.name)

    return render_template("explore_brews.html", recipes=recipes, selectlist_recipes=selectlist_recipes,
                           selectlist_styles=selectlist_styles, selectlisrt_user=selectlist_user,
                           sel_user_styles=sel_user_styles)


#  Show details of a single recipe
@app.route('/recipe/<string:recipe>')
def get_recipes(recipe):
    selectlist_recipes, selectlist_styles, selectlist_user, sel_user_styles = get_selectlists(session["user_id"])
    deleteable = False
    if Recipe.query.filter_by(name=recipe).one().user_id == session["user_id"]:
        deleteable = True
    name, source, style, batch_size, batch_units, notes, hop_steps, ext_steps, ferm_steps, misc_steps, yeast_steps, srm_color = get_recipe_info(recipe)
    color = color_conversion(srm_color)
    return render_template("explore_brews.html", selectlist_recipes=selectlist_recipes, batch_size=batch_size,
                           selectlist_styles=selectlist_styles, name=name, source=source, color=color, style=style,
                           notes=notes, hop_steps=hop_steps, ext_steps=ext_steps, ferm_steps=ferm_steps,
                           misc_steps=misc_steps, yeast_steps=yeast_steps, deleteable=deleteable)


# Ajax called - Check for duplicate brew
@app.route('/check_brew', methods=['GET', 'POST'])
def check_brew():
    recipe = request.form.get("name")
    user_id = session["user_id"]
    date = datetime.date.today()

    recipe_id = Recipe.query.filter_by(name=recipe).one().recipe_id
    if Brew.query.filter_by(user_id=user_id, recipe_id=recipe_id, date=date).first():
        return "duplicate"
    else:
        return "not duplicate"


# Add new brew with today's date and route to brew page
@app.route('/addbrew/<string:recipe>')
def add_brew(recipe):
    user_id = session["user_id"]
    date = datetime.date.today()
    recipe_id = Recipe.query.filter_by(name=recipe).one().recipe_id
    new_brew = Brew(user_id=user_id, recipe_id=recipe_id, date=date)
    db.session.add(new_brew)
    db.session.commit()

    brew_id = str(new_brew.id)

    return redirect('/brew/' + brew_id)


# Delete recipe from database and delete associated instructions
@app.route("/deleterecipe/<string:recipe>")
def delete_recipe(recipe):
    recipe_obj = Recipe.query.filter_by(name=recipe).one()
    HopIns.query.filter_by(recipe_id=recipe_obj.recipe_id).delete()
    FermIns.query.filter_by(recipe_id=recipe_obj.recipe_id).delete()
    ExtIns.query.filter_by(recipe_id=recipe_obj.recipe_id).delete()
    MiscIns.query.filter_by(recipe_id=recipe_obj.recipe_id).delete()
    YeastIns.query.filter_by(recipe_id=recipe_obj.recipe_id).delete()
    Recipe.query.filter_by(name=recipe).delete()
    db.session.commit()

    flash("Recipe deleted")
    return redirect("/explore")


# ***************************************************************************************
# My Brews display and response to selections

@app.route('/mybrews', methods=['GET', 'POST'])
def show_mybrews():
    selectlist_recipes, selectlist_styles, selectlist_user, sel_user_styles = get_selectlists(session["user_id"])
    # Get a list of all brew objects for our user
    all_brews = Brew.query.filter_by(user_id=session["user_id"]).all()

    brewlist = []
    if request.method == "POST":
        filtered_brews = []
        # Recipe search:
        if request.form.get("recipe"):

            recipe = request.form.get("recipe")
            recipe_id = Recipe.query.filter_by(name=recipe).one().recipe_id
            for obj in all_brews:
                if obj.recipe_id == recipe_id:
                    filtered_brews.append(obj)
            brewlist = get_brewlist(filtered_brews)
            filtered = "Brews of " + recipe + ":"

            return render_template("mybrews.html", filtered=filtered, brewlist=brewlist, selectlist_user=selectlist_user,
                                   sel_user_styles=sel_user_styles)
        # Style search:
        if request.form.get("style"):
            style = request.form.get("style")
            recipes = Recipe.query.filter_by(style_name=style).all()
            # Get brews from all brews where the recipe is in recipes
            for obj in all_brews:
                for recipe in recipes:
                    if obj.recipe_id == recipe.recipe_id:
                        filtered_brews.append(obj)
            brewlist = get_brewlist(filtered_brews)
            filtered = style + " Style Brews:"

            return render_template("mybrews.html", filtered=filtered, brewlist=brewlist, selectlist_user=selectlist_user,
                                   sel_user_styles=sel_user_styles)
    else:
        brewlist = get_brewlist(all_brews)
        return render_template("mybrews.html", brewlist=brewlist,
                               selectlist_user=selectlist_user, sel_user_styles=sel_user_styles)


# Delete brew from database
@app.route('/delete_brew/<int:brew_id>')
def delete_brew(brew_id):
    Brew.query.filter_by(id=brew_id).delete()
    db.session.commit()
    flash("Your brew was deleted")
    return redirect("/mybrews")


# ***************************************************************************************
# Brew page

@app.route('/brew/<int:brew_id>', methods=['GET', 'POST'])
def brew_process(brew_id):
    brew = Brew.query.filter_by(id=brew_id).one()
    recipe = Recipe.query.filter_by(recipe_id=brew.recipe_id).one().name
    if request.method == "POST":
        brew_update = update_brew(brew)
        return redirect("/mybrews")
    else:
        recipe, batch_size, batch_units, times, timerset, boiltime, steep, yeast, secondary, extracts, og_min, og_max, notes, srm_color = show_brew_recipe(recipe)
        rating = brew.rating
        c_gravity = brew.cg
        c_gravity_date = brew.cg_date
        color = color_conversion(srm_color)

        return render_template("brew.html", brew=brew, recipe=recipe, batch_size=batch_size, batch_units=batch_units,
                               times=times, timerset=timerset, boiltime=boiltime, steep=steep, yeast=yeast, secondary=secondary,
                               extracts=extracts, og_min=og_min, og_max=og_max, c_gravity=c_gravity, c_gravity_date=c_gravity_date,
                               notes=notes, color=color, rating=rating)


# Ajax called -Store boil start time on change
@app.route('/boil', methods=["POST"])
def note_boil_time():
    boil_start = request.form.get("boil_start")
    brew_id = request.form.get("brew_id")
    startformat = '%H:%M'

    boil_start = datetime.datetime.strptime(boil_start, startformat).time()
    Brew.query.filter_by(id=brew_id).one().boil_start = boil_start
    db.session.commit()


# Save brew data to database
def update_brew(brew):
    brew.user_id = session["user_id"]
    date_get = request.form.get('brew_date')
    brew.date = datetime.datetime.strptime(date_get, "%Y-%m-%d").date()
    time_get = request.form.get("boil_start")
    if request.form.get("curr_gravity"):
        brew.cg = request.form.get("curr_gravity")
    if request.form.get("cg_date"):
        cg_date_get = request.form.get("cg_date")
        brew.cg_date = datetime.datetime.strptime(cg_date_get, "%Y-%m-%d").date()

    if (request.form.get('orig_gravity')):
        brew.og = float(request.form.get('orig_gravity'))
    if request.form.get('final_gravity'):
        brew.fg = float(request.form.get('final_gravity'))
        brew.og = float(brew.og)
        brew.abv = (brew.og - brew.fg) * 131

    if request.form.get("finished"):
        end_date_get = request.form.get('finished')
        brew.end_date = datetime.datetime.strptime(end_date_get, "%Y-%m-%d").date()
    brew.notes = request.form.get('brew_notes')
    brew.results_notes = request.form.get('results_notes')
    brew.rating = request.form.get('rating')

    db.session.commit()

    brew_update = "Brew successfully updated"

    return brew_update


# ***************************************************************************************
# Add new recipes

# Get  - display add recipe. Post - Add recipe and edit recipe pages info routed here for processing and uploading to db
@app.route('/addrecipe', methods=['GET', 'POST'])
def enter_recipe():
    if request.method == "POST":
        data = request.get_json()
        # print "*****************************************************", data
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
        batch_units = data["units"]
        new_recipe = Recipe(name=name, source=source, user_id=user_id, public=public,
                            notes=notes, style_name=style_name, batch_size=batch_size,
                            batch_units=batch_units)

        db.session.add(new_recipe)
        db.session.commit()

        # Recipe_id will be used in all instructions uploads
        recipe_id = Recipe.query.filter_by(name=name, user_id=user_id)[0].recipe_id

        # Grain Instructions
        for i in range(0, len(data['grains']), 3):
            grain_name = grains[i]["value"]
            ferm_id = Fermentable.query.filter_by(name=grain_name)[0].id
            grain_amount = grains[i+1]["value"]
            grain_units = grains[i+2]["value"]
            new_fermins = FermIns(recipe_id=recipe_id, ferm_id=ferm_id, amount=grain_amount,
                                  units=grain_units, )
            db.session.add(new_fermins)
            db.session.commit()

        # Extract Instructions
        if extracts:
            for i in range(0, len(data['extracts']), 3):
                extract_name = extracts[i]["value"]
                extract_id = Extract.query.filter_by(name=extract_name)[0].id
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

            new_hopsins = HopIns(recipe_id=recipe_id, hop_id=hop_id, amount=hop_amount, phase=hop_phase,
                                 time=time, kind=kind)
            db.session.add(new_hopsins)
            db.session.commit()

        # Misc Instructions
        if miscs != []:
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
        for i in range(0, len(data['yeasts']), 4):
            yeast_name = yeasts[i]["value"]
            yeast_id = Yeast.query.filter_by(name=yeast_name)[0].yeast_id
            yeast_amount = yeasts[i+1]["value"]
            yeast_units = yeasts[i+2]["value"]
            yeast_phase = yeasts[i+3]["value"]
            new_yeastins = YeastIns(recipe_id=recipe_id, yeast_id=yeast_id, amount=yeast_amount, units=yeast_units, phase=yeast_phase)
            db.session.add(new_yeastins)
            db.session.commit

        calc_color(recipe_id, batch_size, batch_units)
        print "recipe added"

        message = "Your recipe has been added."
        return message

    grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles = feed_recipe_form()

    return render_template("recipeform.html", selectlist_styles=selectlist_styles, grain_choice=grain_choice, hop_choice=hop_choice,
                           extract_choice=extract_choice, misc_choice=misc_choice, yeast_choice=yeast_choice)


# Display edit recipe page
@app.route('/editrecipe/<string:recipe>')
def editrecipe(recipe):
    name, source, style, batch_size, batch_units, notes, hop_steps, ext_steps, ferm_steps, misc_steps, yeast_steps, srm_color = get_recipe_info(recipe)
    grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles = feed_recipe_form()

    public = Recipe.query.filter_by(name=recipe).one().public
    return render_template("editrecipe.html", name=name, source=source, style=style, batch_size=batch_size, batch_units=batch_units,
                           public=public, notes=notes, hop_steps=hop_steps, ext_steps=ext_steps, ferm_steps=ferm_steps,
                           misc_steps=misc_steps, yeast_steps=yeast_steps, grain_choice=grain_choice,
                           extract_choice=extract_choice, hop_choice=hop_choice, misc_choice=misc_choice,
                           yeast_choice=yeast_choice, selectlist_styles=selectlist_styles)


# Display page for recipe upload and process uploaded recipe. Return either error page or recipe page.
@app.route('/uploadrecipe', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        share = request.form.get('share')
        files = []
        recipes = []
        files.append(request.files['file-input1'])
        files.append(request.files['file-input2'])
        files.append(request.files['file-input3'])
        files.append(request.files['file-input4'])
        files.append(request.files['file-input5'])

        def save_files(newfile):
            if newfile and allowed_file(newfile.filename):
                filename = secure_filename(newfile.filename)
                newfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filepath = "/tmp/uploads/" + filename

                status, name = load_recipes(filepath, session["user_id"], share)
                if status == "error":
                    error_names.append(name)
                else:
                    recipes.append(name)

        error_names = []
        session['error_list'] = []

        for newfile in files:
            save_files(newfile)

        if error_names != []:
            session['error_list'] = error_names
            return render_template("uploaderror.html")
        else:
            notice = "Recipe(s) successfully added!"
            return render_template("uploadrecipe.html", notice=notice, recipes=recipes)

    return render_template("uploadrecipe.html")


# Ajax called - Check for duplicate recipe names
@app.route('/check_recipe_name', methods=["POST"])
def check_name():
    test_name = request.form.get("name")
    if Recipe.query.filter_by(name=test_name).all() == []:
        return "okay"
    else:
        return "nope"


# Ajax called -Calculate color for recipe
@app.route('/colorcalc', methods=['GET', 'POST'])
def calculate_color():
    data = request.get_json()
    grains = data['grains']
    print grains
    extracts = data['extracts']
    batch_size = float(data["batch_size"])
    batch_units = data["units"]
    if batch_units not in ["gallon", "gallons", "Gallons", "g"]:
        batch_size = float(batch_size) * 0.26417    # Convert to pounds

    def get_each_srm(cls, ingredient_list, batch_size):
        srm_color = 0
        for i in range(0, len(ingredient_list), 3):
            name = ingredient_list[i]["value"]
            color = cls.query.filter_by(name=name)[0].color
            amount = float(ingredient_list[i+1]["value"])
            units = ingredient_list[i+2]["value"]
            # Convert amount to pounds
            if units in ["oz", "ounces"]:
                amount = amount * 0.062500
            elif units in ["g", "grams"]:
                amount = amount * 0.0022046
            else:
                amount = amount * 2.20462
            print "color", color, "amount ", amount, "batch_size ", batch_size
            mcu = (color * amount) / batch_size
            print mcu
            srm_color += 1.4922 * (mcu ** .6859)

        srm_color = int(round(srm_color))
        return srm_color
    srm = get_each_srm(Fermentable, grains, batch_size) + get_each_srm(Extract, extracts, batch_size)
    print srm
    color = color_conversion(srm)
    return color


# ***************************************************************************************
# Register and Log In

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
            return redirect("/login")

    return render_template("registration.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        pw_in_db = User.query.filter_by(username=username).all()

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

# ***************************************************************************************

if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    app.run()
