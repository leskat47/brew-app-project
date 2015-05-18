from flask import Flask, render_template, redirect, request, flash, session
from model import User, Recipe, Style, Extract, Hop, Misc, Yeast, Fermentable, YeastIns, HopIns, FermIns, MiscIns, connect_to_db, db


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


@app.route('/addrecipe', methods=['GET', 'POST'])
def enter_recipe():
    if request.method == "POST":

        # Recipe values
        name = request.form.get('name')
        user_id = session["user_id"]
        source = request.form.get('source')
        public = request.form.get('share')
        style_name = request.form.get('style')
        notes = request.form.get('notes')
        batch_size = request.form.get('batch_size')
        new_recipe = Recipe(name=name, source=source, user_id=user_id, public=public,
                            notes=notes, style_name=style_name, batch_size=batch_size)
        db.session.add(new_recipe)
        db.session.commit()

        # Recipe_id will be used in all instructions uploads
        recipe_id = Recipe.query.filter_by(name=name, user_id=user_id)[0].recipe_id

        # Grain Instructions
        # TODO: for grain in grain_list: TBD how to get ingredient data from form
        grain_name = request.form.get('grain')
        ferm_id = Fermentable.query.filter_by(name=grain_name)[0].id
        grain_amount = request.form.get('grain_amount')
        new_fermins = FermIns(recipe_id=recipe_id, ferm_id=ferm_id, amount=grain_amount, )
        db.session.add(new_fermins)
        db.session.commit()

        # Hops Instructions
        # TODO: for hop in hop_list: TBD how to get ingredient data from form
        hop_name = request.form.get('hop')
        hop_id = Hop.query.filter_by(name=hop_name)[0].hop_id
        hop_amount = request.form.get('hop_amount')
        hop_phase = request.form.get('hop_phase')
        time = request.form.get('hop_time')
        kind = request.form.get('kind')
        new_hopsins = HopIns(recipe_id=recipe_id, hop_id=hop_id, amount=hop_amount, phase=hop_phase, time=time, kind=kind)
        db.session.add(new_hopsins)
        db.session.commit()

        # Misc Instructions
        # TODO: for misc in misc_list: TBD how to get multiple ingredient data from form

        misc_name = request.form.get('misc')
        misc_id = Misc.query.filter_by(name=misc_name)[0].misc_id
        misc_phase = request.form.get('misc_phase')
        misc_amount = request.form.get('misc_amount')
        new_miscins = MiscIns(recipe_id=recipe_id, misc_id=misc_id, phase=misc_phase, amount=misc_amount)
        db.session.add(new_miscins)
        db.session.commit()

 
    grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles = feed_recipe_form()


    return render_template("recipeform.html", selectlist_styles=selectlist_styles, grain_choice=grain_choice, hop_choice=hop_choice,
                           extract_choice=extract_choice, misc_choice=misc_choice, yeast_choice=yeast_choice)


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
    print extract_choice
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
    return grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles




if __name__ == "__main__":

    app.debug = True

    connect_to_db(app)

    app.run()
