from flask import Flask, render_template, redirect, request, flash, session, url_for, send_from_directory
from model import User, Recipe, Brew, Style, Extract, Hop, Misc, Yeast, Fermentable, YeastIns, HopIns, FermIns, MiscIns, ExtIns, connect_to_db, db
from feeder import load_recipes, load_hops_ins, load_ferm_ins, load_ext_ins, load_misc_ins, load_yeast_ins
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

# ROUTES:
# /explore      -> populate dropdown searches. On post, return recipe names
# /recipe/recipename -> collect recipe info and display it
# /mybrews      -> collect brews associated with user, show table of selected brew info,
#               populate dropdowns, return search results
# /addbrew      -> Passthrough route from recipe page that adds a brew and produces new brew_id
# /brew/brewid  -> populate brew page with associated brew data, display page. On post, route to update
# /deletebrew/brewid -> Ajax accessed to remove a brew from user's list
# /addrecipe    -> populate menus and display form. On post, prep inputs for database and commit to database.
# /check_recipename -> Ajax accessed to check whether recipe name entered in form is duplicated in db.
# /uploadrecipe -> Uploaded file saved to uploads folder, parsed and committed through feeder.py function
# /editrecipe   -> Get data for given recipe. Populate menus. Display form.


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template("homepage.html")


@app.route('/explore', methods=['GET', 'POST'])
def show_explore():

    selectlist_recipes, selectlist_styles, selectlist_user, sel_user_styles = get_selectlists()

    # If a submit button is clicked, post request is called. For selected style, show recipe list.
    # For recipe selected, show recipe.
    if request.method == "POST":
        # Render either recipe list for style selection or recipe
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

    return render_template("explore_brews.html", selectlist_recipes=selectlist_recipes,
                           selectlist_styles=selectlist_styles, selectlisrt_user=selectlist_user,
                           sel_user_styles=sel_user_styles)


def get_selectlists():
    # Create lists of recipes and styles which will show in the dropdown selections. list_recipes will
    # hold a list of recipes within a style when style type is selected.

    selectlist_recipes = []
    selectlist_styles = []
    selectlist_user = []
    selectlist_user_styles = []
    for recipe_obj in Recipe.query.filter_by(public="yes"):
        selectlist_recipes.append(recipe_obj.name)
    for style_obj in Style.query.all():
        selectlist_styles.append(style_obj.style_name)
    for brew_obj in Brew.query.filter_by(user_id=session["user_id"]):
        recipe = Recipe.query.filter_by(recipe_id=brew_obj.recipe_id).one()
        if recipe.name not in selectlist_user:
            selectlist_user.append(recipe.name)
        if recipe.style_name not in selectlist_user_styles:
            selectlist_user_styles.append(recipe.style_name)

    selectlist_recipes = sorted(selectlist_recipes)
    selectlist_styles = sorted(selectlist_styles)
    selectlist_user = sorted(selectlist_user)
    selectlist_user_styles = sorted(selectlist_user_styles)

    return (selectlist_recipes, selectlist_styles, selectlist_user, selectlist_user_styles)


@app.route('/recipe/<string:recipe>')
def get_recipes(recipe):
    name, source, style, batch_size, batch_units, notes, hop_steps, ext_steps, ferm_steps, misc_steps, yeast_steps = get_recipe_info(recipe)

    return render_template("recipe.html", name=name, source=source, style=style,
                           notes=notes, hop_steps=hop_steps, ext_steps=ext_steps, ferm_steps=ferm_steps,
                           misc_steps=misc_steps, yeast_steps=yeast_steps)


@app.route('/mybrews', methods=['GET', 'POST'])
def show_mybrews():
    selectlist_recipes, selectlist_styles, selectlist_user, sel_user_styles = get_selectlists()
    if Brew.query.filter_by(user_id=session["user_id"]).all() == []:
        return render_template("nobrews.html")
    # Get a list of all brew objects for our user
    all_brews = Brew.query.filter_by(user_id=session["user_id"]).all()
    print "allbrews: ", all_brews
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
        return render_template("mybrews.html", brewlist=brewlist, selectlist_recipes=selectlist_recipes)

        # Style search:
        if request.form.get("style"):
            request.form.get("style")
            recipes = Recipe.query.filter_by(style_name=style).all
            # Get brews from all brews where the recipe is in recipes
            for obj in all_brews:
                for recipe in recipes:
                    if obj.recipe_id == recipe.recipe_id:
                        filtered_brews.append(obj)
            brewlist = get_brewlist(filtered_brews)
        return render_template("mybrews.html", brewlist=brewlist, selectlist_recipes=selectlist_recipes)
    else:
        brewlist = get_brewlist(all_brews)
        print brewlist
        return render_template("mybrews.html", brewlist=brewlist, selectlist_styles=selectlist_styles,
                               selectlist_user=selectlist_user, sel_user_styles=sel_user_styles)


def get_brewlist(all_brews):
    brewlist = []
    for brew in all_brews:
        newbrew = {}
        newbrew["id"] = brew.id
        newbrew["name"] = Recipe.query.filter_by(recipe_id=brew.recipe_id).one().name
        newbrew["date"] = brew.date
        newbrew["notes"] = brew.notes
        if brew.end_date:
            newbrew["finished"] = brew.end_date
            newbrew["open_brew"] = True
        else:
            newbrew["finished"] = ""
            newbrew["open_brew"] = False
        newbrew["results_notes"] = brew.results_notes
        newbrew["rating"] = brew.rating
        newbrew["og"] = brew.og
        newbrew["fg"] = brew.fg
        newbrew["abv"] = brew.abv
        brewlist.append(newbrew)

    return brewlist


# @app.route('/checkbrew/')
#     recipe_id = Recipe.query.filter_by(name=recipe).one().recipe_id
#     new_brew = Brew(user_id=user_id, recipe_id=recipe_id, date=date)


@app.route('/addbrew/<string:recipe>')
def add_brew(recipe):
    user_id = session["user_id"]
    date = datetime.date.today()
    recipe_id = Recipe.query.filter_by(name=recipe).one().recipe_id
    new_brew = Brew(user_id=user_id, recipe_id=recipe_id, date=date)

    if Brew.query.filter_by(user_id=user_id, recipe_id=recipe_id, date=date):
        flash("The database already shows a brew for this recipe today. Adding another for you.")

    db.session.add(new_brew)
    db.session.commit()

    brew_id = new_brew.id

    brew_id = str(brew_id)
    return redirect('/brew/' + brew_id)


@app.route('/brew/<int:brew_id>', methods=['GET', 'POST'])
def brew_process(brew_id):
    brew = Brew.query.filter_by(id=brew_id).one()
    recipe = Recipe.query.filter_by(recipe_id=brew.recipe_id).one().name
    if request.method == "POST":
        brew_update = update_brew(brew)
        return redirect("/explore")
    else:
        recipe, batch_size, batch_units, times, timerset, boiltime, steep, yeast, secondary, extracts, og_min, og_max, notes, = show_brew_recipe(recipe)
        return render_template("brew.html", brew=brew, recipe=recipe, batch_size=batch_size, batch_units=batch_units,
                               times=times, timerset=timerset, boiltime=boiltime, steep=steep, yeast=yeast, secondary=secondary,
                               extracts=extracts, og_min=og_min, og_max=og_max, notes=notes)


def update_brew(brew):
    brew.user_id = session["user_id"]
    date_get = request.form.get('brew_date')
    brew.date = datetime.datetime.strptime(date_get, "%Y-%m-%d").date()
    brew.og = float(request.form.get('orig_gravity'))
    if request.form.get('final_gravity'):
        brew.fg = float(request.form.get('final_gravity'))
        brew.og = float(brew.og)
        brew.abv = (brew.og - brew.fg) * 131

    end_date_get = request.form.get('finished')
    if request.form.get("brew.end_date"):
        brew.end_date = datetime.datetime.strptime(end_date_get, "%Y-%m-%d").date()
    brew.notes = request.form.get('brew_notes')
    brew.results_notes = request.form.get('results_notes')
    brew.rating = request.form.get('rating')

    db.session.commit()

    brew_update = "Brew successfully updated"

    return brew_update


def show_brew_recipe(recipe):
    record = Recipe.query.filter_by(name=recipe).one()
    recipe_id = record.recipe_id
    if record.notes == "":
        notes = "No notes for this recipe"
    else:
        notes = record.notes

    style_name = record.style_name
    style_record = Style.query.filter_by(style_name=style_name).one()
    og_min = style_record.og_min
    og_max = style_record.og_max

    if record.batch_size == "":
        batch_size = 5
        batch_units = "gallons"
    else:
        batch_size = record.batch_size
        batch_units = record.batch_units

    # Boil list: This should only exist for hops and special ingredients.
    boil = []
    times = []
    boiltime = {}
    # Make a list of times in instructions. Prevent duplicates and sort descending.
    boil = HopIns.query.filter_by(phase="Boil", recipe_id=recipe_id).all() + MiscIns.query.filter_by(phase="Boil", recipe_id=recipe_id).all()
    for add in boil:
        if add.time not in times:
            times.append(add.time)
    sorted(times, reverse=True)
    iter = 0
    timerset = {}
    for time in times:
        boiltime[time] = []

        if iter < (len(times) - 2):
            timerset[time] = times[iter] - times[iter + 1]
        else:
            timerset[time] = time
        iter += 1

        for add in boil:
            new_ing = {}
            if (add.time == time) and (hasattr(add, 'hop_id')):
                ingredient = Hop.query.filter_by(hop_id=add.hop_id).one()
                new_ing["name"] = ingredient.name
                new_ing["amount"] = add.amount
                new_ing["units"] = add.units
            elif (add.time == time) and (hasattr(add, 'misc_id')):
                ingredient = Misc.query.filter_by(misc_id=add.misc_id).one()
                new_ing["name"] = ingredient.name
                new_ing["amount"] = add.amount
                new_ing["units"] = add.units
            boiltime[time].append(new_ing)

    def collect_instructions(list_name, cls_name, cls_ins_name, theid):
        instructions = cls_ins_name.query.filter_by(recipe_id=recipe_id).all()

        list_name = []

        for add in instructions:
            add_dict = {}
            add_dict["name"] = cls_name.query.filter_by(id=getattr(add, theid)).one().name
            add_dict["amount"] = add.amount
            if add.units is not None:
                add_dict["units"] = add.units
            else:
                add_dict["units"] = "ounces"

            list_name.append(add_dict)
            print "*******************************************************", list_name
            return list_name

    # Make a list of dicts for grain info
    steep = collect_instructions("grains", Fermentable, FermIns, "ferm_id")

    # Make a list of dicts for extract info
    extracts = collect_instructions("extract", Extract, ExtIns, "extract_id")

    # Make a list of dicts for yeast info sorted by stage: primary or secondary
    yeasts = YeastIns.query.filter_by(recipe_id=recipe_id).all()
    yeast = []
    secondary = []
    for add in yeasts:
        if add.phase == "primary":
            add_dict = {}
            add_dict["name"] = Yeast.query.filter_by(yeast_id=add.yeast_id).one().name
            add_dict["amount"] = add.amount
            if add.units is not None:
                add_dict["units"] = add.units
            else:
                add_dict["units"] = "ounces"
            yeast.append(add_dict)

        elif add.phase == "secondary":
            add_dict = {}
            add_dict["name"] = Yeast.query.filter_by(yeast_id=add.yeast_id).one().name
            add_dict["amount"] = add.amount
            if add.units is not None:
                add_dict["units"] = add.units
            else:
                add_dict["units"] = "ounces"

            secondary.append(add_dict)

    return (recipe, batch_size, batch_units, times, timerset, boiltime, steep, yeast, secondary,
            extracts, og_min, og_max, notes)

@app.route('/delete_brew/<int:brew_id>')
def delete_brew(brew_id):
    Brew.query.filter_by(id=brew_id).delete()
    db.session.commit()
    flash("Your brew was deleted")
    return redirect("/mybrews")


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

            new_hopsins = HopIns(recipe_id=recipe_id, hop_id=hop_id, amount=hop_amount, phase=hop_phase,
                                 time=time, kind=kind)
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
        for i in range(0, len(data['yeasts']), 4):
            yeast_name = yeasts[i]["value"]
            yeast_id = Yeast.query.filter_by(name=yeast_name)[0].yeast_id
            yeast_amount = yeasts[i+1]["value"]
            yeast_units = yeast[i+2]["value"]
            yeast_phase = yeast[i+3]["value"]
            new_yeastins = YeastIns(recipe_id=recipe_id, id=yeast_id, amount=yeast_amount, units=yeast_units, phase=yeast_phase)
            db.session.add(new_yeastins)
            db.session.commit

        return redirect("/recipe/%s" % name)

    grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles = feed_recipe_form()

    return render_template("recipeform.html", selectlist_styles=selectlist_styles, grain_choice=grain_choice, hop_choice=hop_choice,
                           extract_choice=extract_choice, misc_choice=misc_choice, yeast_choice=yeast_choice)


# Called from recipe form js to check for duplicate recipe names
@app.route('/check_recipe_name', methods=["POST"])
def check_name():
    test_name = request.form.get("name")
    if Recipe.query.filter_by(name=test_name).all() == []:
        return "okay"
    else:
        return "nope"


@app.route('/uploadrecipe', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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

                name = load_recipes(filepath, session["user_id"])
                load_ferm_ins(filepath)
                load_ext_ins(filepath)
                load_hops_ins(filepath)
                load_misc_ins(filepath)
                load_yeast_ins(filepath)
                recipes.append(name)

        for newfile in files:
            save_files(newfile)

        notice = "Files successfully uploaded"

        return render_template("uploadrecipe.html", notice=notice, recipes=recipes)

    return render_template("uploadrecipe.html")


@app.route('/editrecipe/<string:recipe>')
def editrecipe(recipe):
    name, source, style, batch_size, batch_units, notes, hop_steps, ext_steps, ferm_steps, misc_steps, yeast_steps = get_recipe_info(recipe)
    grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles = feed_recipe_form()
    public = Recipe.query.filter_by(name=recipe).one().public
    return render_template("editrecipe.html", name=name, source=source, style=style, batch_size=batch_size, batch_units=batch_units,
                           public=public, notes=notes, hop_steps=hop_steps, ext_steps=ext_steps, ferm_steps=ferm_steps,
                           misc_steps=misc_steps, yeast_steps=yeast_steps, grain_choice=grain_choice,
                           extract_choice=extract_choice, hop_choice=hop_choice, misc_choice=misc_choice,
                           yeast_choice=yeast_choice, selectlist_styles=selectlist_styles)


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


# Build lists for recipe form drop downs
def feed_recipe_form():
    selectlist_styles = []
    for style_obj in Style.query.all():
        if style_obj.style_name not in selectlist_styles:
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


def get_recipe_info(recipe):
    display_recipe = Recipe.query.filter_by(name=recipe).one()
    name = display_recipe.name
    source = display_recipe.source
    style = display_recipe.style_name
    batch_size = display_recipe.batch_size
    batch_units = display_recipe.batch_units
    if display_recipe.notes == "":
        notes = "There are no notes for this recipe."
    else:
        notes = display_recipe.notes

    hops = display_recipe.hins
    hop_dict = {}
    hop_steps = []
    for ingredient in hops:
        hop_dict["name"] = ingredient.hop.name
        hop_dict["form"] = ingredient.hop.form
        hop_dict["amount"] = ingredient.amount
        hop_dict["units"] = ingredient.units
        hop_dict["phase"] = ingredient.phase
        hop_dict["time"] = ingredient.time
        hop_dict["kind"] = ingredient.kind
        hop_steps.append(hop_dict.copy())

    extracts = display_recipe.eins
    ext_dict = {}
    ext_steps = []
    for ingredient in extracts:
        ext_dict["name"] = ingredient.extract.name
        ext_dict["kind"] = ingredient.extract.kind
        ext_dict["amount"] = ingredient.amount
        ext_dict["units"] = ingredient.units
        ext_dict["phase"] = "Boil"
        ext_steps.append(ext_dict.copy())

    ferms = display_recipe.fins
    ferm_dict = {}
    ferm_steps = []
    for ingredient in ferms:
        ferm_dict["name"] = ingredient.fermentable.name
        ferm_dict["kind"] = ingredient.fermentable.kind
        ferm_dict["amount"] = ingredient.amount
        ferm_dict["units"] = ingredient.units
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
            misc_dict["units"] = ingredient.units
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
        yeast_dict["units"] = ingredient.units
        yeast_steps.append(yeast_dict.copy())

    return (name, source, style, batch_size, batch_units, notes, hop_steps, ext_steps, ferm_steps, misc_steps, yeast_steps)

if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    app.run()
