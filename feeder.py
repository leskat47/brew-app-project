from model import Hop, Fermentable, Yeast, Recipe, Style, User, Misc, Extract, ExtIns, YeastIns, HopIns, FermIns, MiscIns, connect_to_db, db
import xml.etree.ElementTree as ET


###########################################################################
# RECIPES
def load_recipes(filepath, user=999, share="yes"):
    tree = ET.parse(filepath)
    root = tree.getroot()
    for recipe in root:
        name = recipe.find('NAME').text
        if Recipe.query.filter_by(name=name).first():
            return "error", name
            break
        source = el_find_text(recipe, 'SOURCE', "")
        user_id = user
        public = share
        style = [elem.find('NAME').text for elem in recipe.iter() if elem.tag == "STYLE"]
        style_name = style[0]
        notes = el_find_text(recipe, 'NOTES', "")
        batch_size = el_find_text(recipe, 'BATCH_SIZE', "L")
        batch_units = "L"
        # srm = 0
        new_recipe = Recipe(name=name, source=source, user_id=user_id, public=public,
                            notes=notes, batch_size=batch_size, batch_units=batch_units,
                            style_name=style_name,
                            # srm=srm
                            )
        db.session.add(new_recipe)
    db.session.commit()
    load_hops_ins(filepath)
    load_ferm_ins(filepath)
    load_ext_ins(filepath)
    load_misc_ins(filepath)
    load_yeast_ins(filepath)

    recipe_id = Recipe.query.filter_by(name=name).one().recipe_id
    calc_color(recipe_id, batch_size, batch_units)

    return "success", name


###########################################################################
# INSTRUCTIONS

def load_hops_ins(filepath):
    hop_tree = ET.parse(filepath)
    root = hop_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        recipe_id = Recipe.query.filter_by(name=recipe)[0].recipe_id
        for subchild in child.findall('HOPS'):
            for hop in subchild.findall('HOP'):
                name = hop.find('NAME').text
                form = hop.find('FORM').text
                hop_id = Hop.query.filter_by(name=name, form=form)[0].hop_id
                amount = hop.find('AMOUNT').text
                units = "kg"
                phase = hop.find('USE').text
                time = int(float(hop.find('TIME').text))
                kind = hop.find('TYPE').text
                new_inst_item = HopIns(recipe_id=recipe_id, hop_id=hop_id, amount=amount,
                                       units=units, phase=phase, time=time, kind=kind)
                db.session.add(new_inst_item)
    db.session.commit()


def load_ferm_ins(filepath):
    ferm_tree = ET.parse(filepath)
    root = ferm_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        recipe_id = Recipe.query.filter_by(name=recipe)[0].recipe_id
        for subchild in child:
            for fermentable in subchild.findall('FERMENTABLE'):
                if fermentable.find('TYPE').text == "Grain":
                    name = fermentable.find('NAME').text
                    ferm_id = Fermentable.query.filter_by(name=name).first().id
                    amount = fermentable.find('AMOUNT').text
                    units = 'kg'
                    new_ferm_item = FermIns(recipe_id=recipe_id, ferm_id=ferm_id,
                                            amount=amount, units=units)
                    db.session.add(new_ferm_item)
    db.session.commit()


def load_ext_ins(filepath):
    ext_tree = ET.parse(filepath)
    root = ext_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        recipe_id = Recipe.query.filter_by(name=recipe)[0].recipe_id
        for subchild in child:
            for fermentable in subchild.findall('FERMENTABLE'):
                ext_types = ['Sugar', 'Extract', 'Dry Extract', 'Adjunct']
                if fermentable.find('TYPE').text in ext_types:
                    name = fermentable.find('NAME').text
                    extract_id = Extract.query.filter_by(name=name).first().id
                    amount = fermentable.find('AMOUNT').text
                    units = 'kg'
                    new_ferm_item = ExtIns(recipe_id=recipe_id, extract_id=extract_id, amount=amount,
                                           units=units)
                    db.session.add(new_ferm_item)
    db.session.commit()


def load_misc_ins(filepath):
    misc_tree = ET.parse(filepath)
    root = misc_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        recipe_id = Recipe.query.filter_by(name=recipe)[0].recipe_id
        for subchild in child:
            for misc_item in subchild.findall('MISC'):
                name = misc_item.find('NAME').text

                if Misc.query.filter_by(name=name).all() == []:     # Check to see if the item is in DB
                    kind = misc_item.find('TYPE').text              # If not in DB, add to DB first
                    use = misc_item.find('USE').text
                    notes = el_find_text(misc_item, 'NOTES', "")
                    new_misc = Misc(name=name, kind=kind, use=use,
                                    notes=notes)
                    db.session.add(new_misc)
                    db.session.commit()

                misc_id = Misc.query.filter_by(name=name)[0].misc_id
                phase = misc_item.find('USE').text
                amount = misc_item.find('AMOUNT').text
                if misc_item.find('TIME').text is None:
                    time = 0
                else:
                    time = misc_item.find('TIME').text
                if name == "Whirlfloc Tablets (Irish moss)":
                    units = "tablets"
                    if amount == "0" or amount == "0.0049289":
                        amount = int(1)
                else:
                    units = "units"
                new_misc_item = MiscIns(recipe_id=recipe_id, misc_id=misc_id, amount=amount,
                                        phase=phase, time=time, units=units)
                db.session.add(new_misc_item)
    db.session.commit()


def load_yeast_ins(filepath):
    misc_tree = ET.parse(filepath)
    root = misc_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        recipe_id = Recipe.query.filter_by(name=recipe)[0].recipe_id
        for subchild in child:
            for yeast in subchild.findall('YEAST'):
                name = yeast.find('NAME').text
                yeast_id = Yeast.query.filter_by(name=name)[0].yeast_id
                amount = yeast.find('AMOUNT').text
                units = 'kg'
                phase = 'primary'
                new_yeast = YeastIns(recipe_id=recipe_id, yeast_id=yeast_id, amount=amount,
                                     phase=phase)
                db.session.add(new_yeast)
    db.session.commit()


def el_find_text(el, tagstr, ifempty):
    found_el = el.find(tagstr)
    if (found_el is None):
        return(ifempty)
    else:
        return(found_el.text)

###########################################################################
# INSTRUCTIONS FOR MANUALLY ADDED RECIPE


def upload_ingredients(recipe_id, grains, extracts, hops, miscs, yeasts):
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
