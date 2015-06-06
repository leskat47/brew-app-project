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
    misc_choice = sorted(misc_choice)
    yeast_choice = sorted(yeast_choice)
    selectlist_styles = sorted(selectlist_styles)
    print "feed recipe form ran"

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
        recipe_obj = Recipe.query.filter_by(recipe_id=brew.recipe_id).one()
        newbrew["name"] = recipe_obj.name
        color = recipe_obj.srm
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

def color_conversion(srm):
    color_ref = {1: "#F3F993", 2: "#F5F75C", 3: "#F6F513", 4: "#EAE615", 5: "#E0D01B",
                 6: "#D5BC26", 7: "#CDAA37", 8: "#C1963C", 9: "#BE8C3A", 10: "#BE823A",
                 11: "#C17A37", 12: "#BF7138", 13: "#BC6733", 14: "#B26033", 15: "#A85839",
                 16: "#985336", 17: "#8D4C32", 18: "#7C452D", 19: "#6B3A1E", 20: "#5D341A",
                 21: "#4E2A0C", 23: "#361F1B", 24: "#261716", 25: "#231716", 26: "#19100F",
                 27: "#16100F", 28: "#120D0C", 29: "#100B0A", 30: "#050B0A", 31: "5AOAO2",
                 32: "#560A05", 33: "#520907", 34: "#4C0505", 35: "#470606", 36: "#440607",
                 37: "#3F0708", 38: "#3B0607", 39: "#3A070B", 40: "#36080A"}
    print type(srm)
    if srm <= 40:
        color = color_ref[srm]
    else:
        color = "#050b0a"
    return color

def get_recipe_info(recipe):
    display_recipe = Recipe.query.filter_by(name=recipe).one()
    name = display_recipe.name
    source = display_recipe.source
    style = display_recipe.style_name
    batch_size = display_recipe.batch_size
    batch_units = display_recipe.batch_units
    srm_color = display_recipe.srm
    # print "SRM", srm_color
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
            ferm_dict["units"] = "oz"
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

    return (name, source, style, batch_size, batch_units, notes, hop_steps, ext_steps, ferm_steps, misc_steps, yeast_steps, srm_color)


def show_brew_recipe(recipe):
    record = Recipe.query.filter_by(name=recipe).one()
    recipe_id = record.recipe_id
    if record.notes == "":
        notes = "No notes for this recipe"
    else:
        notes = record.notes

    srm_color = record.srm

    style_name = record.style_name
    style_record = Style.query.filter_by(style_name=style_name).one()
    og_min = style_record.og_min
    og_max = style_record.og_max

    if record.batch_size == "":
        batch_size = 5
        batch_units = "gallons"
    elif record.batch_units == "L":
        batch_size = round((record.batch_size * 0.26417), 2)
        batch_units = "gallons"

    # Boil list: This should only exist for hops and special ingredients.
    boil = []
    times = []
    boiltime = {}
    boil = HopIns.query.filter_by(phase="Boil", recipe_id=recipe_id).all() + MiscIns.query.filter_by(phase="Boil", recipe_id=recipe_id).all()

    # Make a list of times in instructions. Prevent duplicates and sort descending.
    for add in boil:
        if add.time not in times and add.time is not None:
            times.append(add.time)
        if add.time is None and 0 not in times:
            times.append(0)
    print times
    sorted(times, reverse=True)
    iter = 0
    timerset = {}
    for time in times:
        boiltime[time] = []

        if iter < (len(times) - 1):
            timerset[time] = times[iter] - times[iter + 1]
        else:
            timerset[time] = time
        iter += 1

        for add in boil:
            new_ing = {}
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

    print timerset

    def collect_instructions(list_name, cls_name, cls_ins_name, theid):
        instructions = cls_ins_name.query.filter_by(recipe_id=recipe_id).all()

        list_name = []

        for add in instructions:
            add_dict = {}
            add_dict["name"] = cls_name.query.filter_by(id=getattr(add, theid)).one().name
            add_dict["amount"] = add.amount
            lbs_weight = add.amount * 2.2046
            if add.units == 'kg' or add.units is None:
                add_dict["amount"] = round((add_dict['amount'] * 35.274), 2)
                add_dict['units'] = "oz"
            else:
                add_dict["units"] = add.units

            list_name.append(add_dict)
            return list_name

    # Make a list of dicts for grain info
    # steep = collect_instructions("grains", Fermentable, FermIns, "ferm_id")
    instructions = FermIns.query.filter_by(recipe_id=recipe_id).all()
    steep = []

    for add in instructions:
        add_dict = {}
        add_dict["name"] = Fermentable.query.filter_by(id=add.ferm_id).one().name
        add_dict["amount"] = add.amount
        lbs_weight = add.amount * 2.2046
        if add.units == 'kg' or add.units is None:
            add_dict["amount"] = round((add_dict['amount'] * 35.274), 2)
            add_dict['units'] = "oz"
        else:
            add_dict["units"] = add.units
        steep.append(add_dict)

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
            extracts, og_min, og_max, notes, srm_color)
