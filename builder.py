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


def feed_recipe_form():
    """ Create lists for dropdown choices on recipe form """

    selectlist_styles = sorted({style_obj.style_name for style_obj in Style.query.all()})

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


def get_selectlists(user_id):
    """ Create lists for dropdown displays for recipes and styles, or the user's 
    recipes and styles."""

    selectlist_recipes = Recipe.query.filter_by(public="yes").order_by(Recipe.name).all()
    selectlist_styles = Style.query.order_by(Style.style_name).all()

    my_brews = Brew.query.filter_by(user_id=user_id).all()
    selectlist_user = sorted({brew.recipe.name for brew in my_brews})
    selectlist_user_styles = sorted({brew.recipe.style_name for brew in my_brews})

    return (selectlist_recipes, selectlist_styles, selectlist_user, selectlist_user_styles)


def color_conversion(srm):
    """ Convert srm color to a hexidecimal value """

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
    
    record.notes == record.notes or "No notes for this recipe"
    record.srm_color = record.calc_color()

    style_record = Style.query.filter_by(style_name=record.style_name).one()
    record.batch_size, record.batch_units =  normalize_batch_size(record.batch_size, record.batch_units)

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

    boil = HopIns.query.filter_by(phase="Boil", recipe_id=record.recipe_id).all() + MiscIns.query.filter_by(phase="Boil", recipe_id=record.recipe_id).all()

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

    # Get instructions per ingredient type
    steep_instructions = FermIns.query.filter_by(recipe_id=record.recipe_id).all()
    convert_amounts(steep_instructions)

    extract_instructions = ExtIns.query.filter_by(recipe_id=record.recipe_id).all()
    convert_amounts(extract_instructions)

    yeast_primary_instructions = YeastIns.query.filter_by(recipe_id=record.recipe_id, phase="primary").all()
    yeast_secondary_instructions = YeastIns.query.filter_by(recipe_id=record.recipe_id, phase="secondary").all()

    # Add ounces as unit if missing for yeasts
    for yeast in yeast_primary_instructions:
        if not yeast.units:
            yeast.units = "ounces"

    for yeast in yeast_secondary_instructions:
        if not yeast.units:
            yeast.units = "ounces"

    return(record, times, timerset, boiltime, steep_instructions, yeast_primary_instructions, yeast_secondary_instructions, extract_instructions)
