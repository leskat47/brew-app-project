from model import User, Recipe, Brew, Style, Extract, Hop, Misc, Yeast, Fermentable, YeastIns, HopIns, FermIns, MiscIns, ExtIns, connect_to_db, db


def normalize_batch_size(batch_size, batch_units):
    """
    Normalize the batch size to gallons
    """
    # Handle empty case
    if batch_size == "":
        normalized_size = 5
        normalized_units = "gallons"
    elif batch_units not in ["gallon", "gallons", "Gallons", "g"]:
        normalized_size = round(float(batch_size) * 0.26417, 2)    # 0.26 gallons / liter, round to 2 decimal places
        normalized_units = "gallons"
    else:
        normalized_size = batch_size
        normalized_units = "gallons"

    return (normalized_size, normalized_units)


# Build lists for recipe form drop downs
def feed_recipe_form():
    selectlist_styles = []
    for style_obj in Style.query.all():
        if style_obj.style_name not in selectlist_styles:
            selectlist_styles.append(style_obj.style_name)

    def make_alpha_lists(query_list):
        choices = set()
        for obj in query_list:
            choices.add(obj.name)
        return sorted(choices)

    grain_choice = make_alpha_lists(Fermentable.query.all())
    extract_choice = make_alpha_lists(Extract.query.all())
    hop_choice = make_alpha_lists(Hop.query.all())
    misc_choice = make_alpha_lists(Misc.query.all())
    yeast_choice = make_alpha_lists(Yeast.query.all())

    print "feed recipe form ran"

    return grain_choice, extract_choice, hop_choice, misc_choice, yeast_choice, selectlist_styles


# Create lists of recipes and styles which will show in the dropdown selections. list_recipes will
# hold a list of recipes within a style when style type is selected.
def get_selectlists(user_id):

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


# Get list of brew dictionaries based on brew objects provided
def get_brewlist(all_brews):
    brewlist = []
    for brew in all_brews:
        newbrew = {}
        newbrew["id"] = brew.id
        recipe_obj = Recipe.query.filter_by(recipe_id=brew.recipe_id).one()
        newbrew["name"] = recipe_obj.name
        color = recipe_obj.calc_color()
        newbrew["color"] = color_conversion(color)
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


# Convert srm color to a hexidecimal value
def color_conversion(srm):

    color_ref = {1: "#ffe699", 2: "#ffd878", 3: "#ffca5a", 4: "#ffbf42", 5: "#fbb123",
                 6: "#f8a600", 7: "#f39c00", 8: "#ea8f00", 9: "#e58500", 10: "#de7c00",
                 11: "#d77200", 12: "#cf6900", 13: "#cb6200", 14: "#c35900", 15: "#bb5100",
                 16: "#b54c00", 17: "#b04500", 18: "#a63e00", 19: "#a13700", 20: "#9b3200",
                 21: "#952d00", 22: "#8e2900", 23: "#882300", 24: "#821e00", 25: "#7b1a00",
                 26: "#771900", 27: "#701400", 28: "#6a0e00", 29: "#660d00", 30: "#5e0b00",
                 31: "#5a0a02", 32: "#600903", 33: "#520907", 34: "#4c0505", 35: "#470606",
                 36: "#440607", 37: "#3f0708", 38: "#3b0607", 39: "#3a070b", 40: "#36080a"}

    # Convert to integer if required.
    try:
        rounded_srm = int(round(srm))
    except TypeError:
        rounded_srm = int(srm)

    if rounded_srm <= 40:
        color = color_ref[rounded_srm]
    else:
        color = "#200406"
    return color

def get_recipe_instructions(recipe):
    """ Get all instructions for a given recipe with conversions where necessary """

    recipe = Recipe.query.filter_by(name=recipe).one()
    srm_color = recipe.calc_color()
    recipe.batch_size, recipe.batch_units = normalize_batch_size(recipe.batch_size, recipe.batch_units)

    if not recipe.notes:
        recipe.notes = "There are no notes for this recipe."
    hop_steps = recipe.hins
    ext_steps = recipe.eins
    ferm_steps = recipe.fins
    yeast_steps = recipe.yins

    for misc_ins in recipe.mins:
        if not misc_ins.time:
            misc_ins.time = 0

    convert_amounts(recipe.hins)
    convert_amounts(recipe.eins)
    convert_amounts(recipe.fins)

    return (recipe, srm_color)


def convert_amounts(ingredients):
    for ingredient in ingredients:
        if ingredient.units == "kg" or ingredient.units is None:
            ingredient.amount = round((ingredient.amount * 35.274), 2)
    return


def show_brew_recipe(recipe):
    """ Collect recipe information to display as a brew """
    record = Recipe.query.filter_by(name=recipe).one()
    recipe_id = record.recipe_id
    if record.notes == "":
        notes = "No notes for this recipe"
    else:
        notes = record.notes

    srm_color = record.calc_color()

    style_name = record.style_name
    style_record = Style.query.filter_by(style_name=style_name).one()
    og_min = style_record.og_min
    og_max = style_record.og_max

    batch_size, batch_units = normalize_batch_size(record.batch_size, record.batch_units)

    # Boil list -> Hops and special ingredients that go in the boil.
    boil = []
    #  times -> Each time event in the boil
    times = []
    # boiltime -> List of dictionaries of instructions data
    boiltime = {}
    # iter -> iterator for building timerset
    iter = 0
    # timerset -> Dictionary of time event and delta to next event
    timerset = {}

    boil = HopIns.query.filter_by(phase="Boil", recipe_id=recipe_id).all() + MiscIns.query.filter_by(phase="Boil", recipe_id=recipe_id).all()

    # Make a list of times in instructions. Prevent duplicates and sort descending.
    for add in boil:
        if add.time not in times and add.time is not None:
            times.append(add.time)
        if add.time is None and 0 not in times:
            times.append(0)
    sorted(times, reverse=True)

    # For each time instruction, collect ingredient details as a dictionary, and add to boiltime
    for time in times:
        boiltime[time] = []

        # Find delta between boil times for timers
        if iter < (len(times) - 1):
            timerset[time] = times[iter] - times[iter + 1]
        else:
            timerset[time] = time
        iter += 1

        for add in boil:
            new_ing = {}
            if add.time is None:
                add.time == 0
            if ((add.time == time) or add.time is None) and (hasattr(add, 'hop_id')):
                ingredient = Hop.query.filter_by(hop_id=add.hop_id).one()
                new_ing["name"] = ingredient.name
                new_ing["amount"] = add.amount
                if add.units == 'kg' or add.units is None:
                    new_ing['amount'] = round((new_ing['amount'] * 35.274), 2)
                    new_ing['units'] = "oz"

            elif ((add.time == time) or add.time is None) and (hasattr(add, 'misc_id')):
                ingredient = Misc.query.filter_by(misc_id=add.misc_id).one()
                new_ing["name"] = ingredient.name
                new_ing["amount"] = add.amount
                new_ing["units"] = add.units
            boiltime[time].append(new_ing)

    # Make a list of dicts for grain info
    instructions = FermIns.query.filter_by(recipe_id=recipe_id).all()
    steep = []

    for add in instructions:
        add_dict = {}
        add_dict["name"] = Fermentable.query.filter_by(id=add.ferm_id).one().name
        add_dict["amount"] = add.amount
        if add.units == 'kg' or add.units is None:
            add_dict["amount"] = round((add_dict['amount'] * 35.274), 2)
            add_dict['units'] = "oz"
        else:
            add_dict["units"] = add.units
        steep.append(add_dict)

    # Make a list of dicts for extract info
    # extracts = collect_instructions("extract", Extract, ExtIns, "extract_id")
    extracts = ExtIns.query.filter_by(recipe_id=recipe_id).all()
    extract = []

    for add in extracts:
        add_dict = {}
        add_dict["name"] = Extract.query.filter_by(id=add.extract_id).one().name
        add_dict["amount"] = add.amount
        if add.units == 'kg' or add.units is None:
            add_dict["amount"] = round((add_dict['amount'] * 35.274), 2)
            add_dict['units'] = "oz"
        else:
            add_dict["units"] = add.units

        extract.append(add_dict)

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
            extract, og_min, og_max, notes, srm_color)
