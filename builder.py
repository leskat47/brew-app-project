from model import User, Recipe, Brew, Style, Extract, Hop, Misc, Yeast, Fermentable, YeastIns, HopIns, FermIns, MiscIns, ExtIns, connect_to_db, db


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
    print "Hop choice ", hop_choice
    misc_choice = sorted(misc_choice)
    yeast_choice = sorted(yeast_choice)
    selectlist_styles = sorted(selectlist_styles)

    return grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles

def get_selectlists(user_id):
    # Create lists of recipes and styles which will show in the dropdown selections. list_recipes will
    # hold a list of recipes within a style when style type is selected.

    selectlist_recipes = []
    selectlist_styles = []
    selectlist_user = []
    selectlist_user_styles = []
    for recipe_obj in Recipe.query.filter_by(public="yes").all():
        selectlist_recipes.append(recipe_obj.name)
    for style_obj in Style.query.all():
        selectlist_styles.append(style_obj.style_name)
    for brew_obj in Brew.query.filter_by(user_id=user_id).all():
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

    
def get_recipe_info(recipe):
    display_recipe = Recipe.query.filter_by(name=recipe).one()
    name = display_recipe.name
    source = display_recipe.source
    style = display_recipe.style_name
    batch_size = display_recipe.batch_size
    batch_units = display_recipe.batch_units
    if batch_units == "L" or batch_units is None:
        batch_size = round((batch_size * 0.26417), 2)
        batch_units = "gallons"
    if display_recipe.notes == "":
        notes = "There are no notes for this recipe."
    else:
        notes = display_recipe.notes

    hops = display_recipe.hins
    hop_dict = {}
    hop_steps = []
    for ingredient in hops:
        hop_dict["name"] = ingredient.hop.name
        print "hop_steps ", hop_dict["name"]
        hop_dict["form"] = ingredient.hop.form
        hop_dict["amount"] = ingredient.amount
        hop_dict["units"] = ingredient.units
        if hop_dict["units"] == "kg" or hop_dict["units"] == None:
            hop_dict["amount"] = round((hop_dict["amount"] * 35.274), 2)
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
        if (ext_dict["units"] == "kg") or (ext_dict["units"] is None):
            ext_dict["amount"] = round((ext_dict["amount"] * 35.274), 2)
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
        if (ferm_dict["units"] == "kg") or (ferm_dict["units"] is None):
            ferm_dict["amount"] = round((ferm_dict["amount"] * 35.274), 2)
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
            if ingredient.time is None:
                misc_dict["time"] = 0
            else:
                misc_dict["time"] = ingredient.time
            print misc_dict["time"]
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