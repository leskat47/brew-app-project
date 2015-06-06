from model import Hop, Fermentable, Yeast, Recipe, Style, User, Misc, Extract, YeastIns, HopIns, ExtIns, FermIns, MiscIns, connect_to_db, db
from server import app
import xml.etree.ElementTree as ET
import re

###########################################################################
# STYLES

def load_styles(datafile):
    tree = ET.parse(datafile)
    root = tree.getroot()
    for cls in root:
        if (cls.attrib["type"] == "beer"):  # parse only the class of beer
            for cat in cls:
                category = cat.find('name').text
                for subcat in cat:  # subcat is the same as the beer style
                    if (subcat.tag == 'subcategory'):
                        style_name = subcat.find('name').text
                        aroma_node = subcat.find('aroma')
                        aroma = all_text_fragments(aroma_node)
                        appearance = subcat.find('appearance').text
                        flavor = subcat.find('flavor').text
                        mouthfeel = subcat.find('mouthfeel').text
                        impression = subcat.find('impression').text
                        comments = el_find_text(subcat, 'comments', "")
                        ingredients = el_find_text(subcat, 'ingredients', "")
                        examples = subcat.find('examples').text
                        for reading in subcat:
                            for limit in reading:
                                og_min = el_find_text(limit, 'low', 0)
                                og_max = el_find_text(limit, 'high', 99)
                            for limit in reading:
                                fg_min = el_find_text(limit, 'low', 0)
                                fg_max = el_find_text(limit, 'high', 0)
                            for limit in reading:
                                ibu_min = el_find_text(limit, 'low', 0)
                                ibu_max = el_find_text(limit, 'high', 0)
                            for limit in reading:
                                srm_min = el_find_text(limit, 'low', 0)
                                srm_max = el_find_text(limit, 'high', 0)
                            for limit in reading:
                                abv_min = el_find_text(limit, 'low', 0)
                                abv_max = el_find_text(limit, 'high', 0)

                        new_style = Style(style_name=style_name, category=category, aroma=aroma,
                                          appearance=appearance, flavor=flavor, mouthfeel=mouthfeel,
                                          ingredients=ingredients, impression=impression, og_min=og_min,
                                          examples=examples, comments=comments, og_max=og_max,
                                          fg_min=fg_min, fg_max=fg_max, abv_min=abv_min, abv_max=abv_max,
                                          srm_min=srm_min, srm_max=srm_max, ibu_min=ibu_min, ibu_max=ibu_max)
                        db.session.add(new_style)
                    db.session.commit()


###########################################################################
# RECIPES

def load_recipes(filename, user=999, share="yes"):
    tree = ET.parse(filename)
    root = tree.getroot()
    for recipe in root:
        name = recipe.find('NAME').text
        source = el_find_text(recipe, 'SOURCE', "")
        user_id = user
        public = share
        style = [elem.find('NAME').text for elem in recipe.iter() if elem.tag == "STYLE"]
        style_name = style[0]
        notes = el_find_text(recipe, 'NOTES', "")
        batch_size = el_find_text(recipe, 'BATCH_SIZE', "")
        batch_units = el_find_text(recipe, 'BATCH_UNITS', "L")
        srm = 0
        new_recipe = Recipe(name=name, source=source, user_id=user_id, public=public,
                            notes=notes, batch_size=batch_size, batch_units=batch_units,
                            style_name=style_name, srm=srm)
        db.session.add(new_recipe)
    db.session.commit()
    load_hops_ins(filepath)
    load_ferm_ins(filepath)
    load_ext_ins(filepath)
    load_misc_ins(filepath)
    load_yeast_ins(filepath)

    recipe_id = Recipe.query.filter_by(name=name).one().recipe_id
    calc_color(recipe_id, batch_size, batch_units)


def calc_color(recipe_id, batch_size, batch_units):
    fermins = FermIns.query.filter_by(recipe_id=recipe_id).all()
    extins = ExtIns.query.filter_by(recipe_id=recipe_id).all()

    if batch_units not in ["gallons", "Gallons", "g"]:
        batch_size = float(batch_size) * 0.26417

    srm_color = 0
    for ins in fermins:
        amount_in_lbs = ins.amount * 2.2046
        ferm_id = ins.ferm_id
        color = Fermentable.query.filter_by(id=ferm_id).one().color
        mcu = (color * amount_in_lbs) / batch_size
        srm_color += 1.4922 * (mcu ** .6859)

    for ins in extins:
        amount_in_lbs = ins.amount * 2.2046
        extract_id = ins.extract_id
        color = Extract.query.filter_by(id=extract_id).one().color
        print color, amount_in_lbs, batch_size
        mcu = (color * amount_in_lbs) / batch_size
        srm_color += 1.4922 * (mcu ** .6859)

    color = int(round(srm_color))

    Recipe.query.filter_by(recipe_id=recipe_id).one().srm=color
    db.session.commit()

###########################################################################
# INGREDIENTS


def load_hops(datafile):
    hop_tree = ET.parse(datafile)
    root = hop_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        origin = child.find('ORIGIN').text
        alpha = child.find('ALPHA').text
        beta = child.find('BETA').text
        form = child.find('FORM').text
        hsi = child.find('HSI').text
        notes = child.find('NOTES').text
        new_hop = Hop(name=name, origin=origin, alpha=alpha, beta=beta,
                      form=form, hsi=hsi, notes=notes)
        db.session.add(new_hop)
    db.session.commit()


def load_extracts(datafile):
    ext_tree = ET.parse(datafile)
    root = ext_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        supplier = child.find('SUPPLIER').text
        origin = child.find('ORIGIN').text
        kind = el_find_text(child, 'KIND', "")
        ex_yield = child.find('YIELD').text
        notes = child.find('NOTES').text
        phase = "boil"
        color = child.find('COLOR').text
        new_ext = Extract(name=name, supplier=supplier, origin=origin, kind=kind,
                          ex_yield=ex_yield, notes=notes, phase=phase, color=color)
        db.session.add(new_ext)
    db.session.commit

# def load_adjuncts(datafile):
#     ext_tree = ET.parse(datafile)
#     root = ext_tree.getroot()
#     for child in root:
#         name = child.find('NAME').text
#         supplier = child.find('SUPPLIER').text
#         origin = child.find('ORIGIN').text
#         kind = el_find_text(child, 'KIND', "")
#         ex_yield = child.find('YIELD').text
#         notes = child.find('NOTES').text
#         phase = "boil"
#         print "Extract: ", name
#         new_ext = Extract(name=name, supplier=supplier, origin=origin, kind=kind,
#                           ex_yield=ex_yield, notes=notes, phase=phase)
#         db.session.add(new_ext)
#     db.session.commit


def load_ferms(datafile):
    ferm_tree = ET.parse(datafile)
    root = ferm_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        ayield = child.find('YIELD').text
        kind = child.find('TYPE').text
        supplier = child.find('SUPPLIER').text
        color = child.find('COLOR').text
        origin = child.find('ORIGIN').text
        coarse_fine_diff = child.find('COARSE_FINE_DIFF').text
        moisture = child.find('MOISTURE').text
        diastatic_power = child.find('DIASTATIC_POWER').text
        protein = child.find('PROTEIN').text
        max_in_batch = child.find('MAX_IN_BATCH').text
        recommend_mash = child.find('RECOMMEND_MASH').text
        if child.find('POTENTIAL') is not None:
            potential = child.find('POTENTIAL').text
        else:
            potential = None
        if child.find('DISPLAY_COLOR') is not None:
            display_color = child.find('DISPLAY_COLOR').text
        else:
            display_color = None
        if child.find('EXTRACT_SUBSTITUTE') is not None:
            extract_substitute = child.find('EXTRACT_SUBSTITUTE').text
        else:
            extract_substitute = None
        notes = child.find('NOTES').text
        new_ferm = Fermentable(name=name, ayield=ayield, kind=kind, supplier=supplier,
                               color=color, origin=origin, coarse_fine_diff=coarse_fine_diff,
                               moisture=moisture, diastatic_power=diastatic_power, protein=protein,
                               max_in_batch=max_in_batch, recommend_mash=recommend_mash,
                               potential=potential, display_color=display_color,
                               extract_substitute=extract_substitute, notes=notes)
        db.session.add(new_ferm)
    db.session.commit()


def load_misc(datafile):
    misc_tree = ET.parse(datafile)
    root = misc_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        kind = child.find('TYPE').text
        use = child.find('USE').text
        # amount_is_weight = child.find('AMOUNT_IS_WEIGHT').text
        notes = child.find('NOTES').text
        new_misc = Misc(name=name, kind=kind, use=use,
                        notes=notes)
        db.session.add(new_misc)
    db.session.commit()


def load_yeasts(datafile):
    misc_tree = ET.parse(datafile)
    root = misc_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        kind = child.find('TYPE').text
        form = child.find('FORM').text
        lab = child.find('LABORATORY').text
        product_id = child.find('PRODUCT_ID').text
        # amount_is_weight = child.find('AMOUNT_IS_WEIGHT').text
        min_temperature = child.find('MIN_TEMPERATURE').text
        max_temperature = child.find('MAX_TEMPERATURE').text
        flocculation = child.find('FLOCCULATION').text
        attenuation = child.find('ATTENUATION').text
        notes = child.find('NOTES').text
        new_yeast = Yeast(name=name, kind=kind, form=form, lab=lab, product_id=product_id,
                          min_temperature=min_temperature, flocculation=flocculation,
                          attenuation=attenuation, notes=notes)
        db.session.add(new_yeast)
    db.session.commit()

###########################################################################
# INSTRUCTIONS

def load_hops_ins(filepath):
    misc_tree = ET.parse(filepath)
    root = misc_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        recipe_id = Recipe.query.filter_by(name=recipe)[0].recipe_id
        for subchild in child:
            for hop in subchild.findall('HOP'):
                name = hop.find('NAME').text
                form = hop.find('FORM').text
                hop_id = Hop.query.filter_by(name=name, form=form)[0].hop_id
                amount = hop.find('AMOUNT').text
                units = "kg"
                phase = hop.find('USE').text
                time = hop.find('TIME').text
                kind = hop.find('TYPE').text
                new_inst_item = HopIns(recipe_id=recipe_id, hop_id=hop_id, amount=amount,
                                       units=units, phase=phase, time=time, kind=kind)
                db.session.add(new_inst_item)
    db.session.commit()


def load_ferm_ins(filepath):
    misc_tree = ET.parse(filepath)
    root = misc_tree.getroot()
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
                    print "to be uploaded: ", recipe_id, ferm_id, amount, units
                    new_ferm_item = FermIns(recipe_id=recipe_id, ferm_id=ferm_id,
                                            amount=amount, units=units)
                    db.session.add(new_ferm_item)
    db.session.commit()


def load_ext_ins(filepath):
    misc_tree = ET.parse(filepath)
    root = misc_tree.getroot()
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

                if Misc.query.filter_by(name=name).all() == []: # Check to see if the item is in DB
                    kind = misc_item.find('TYPE').text          # If not in DB, add to DB first
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
                new_misc_item = MiscIns(recipe_id=recipe_id, misc_id=misc_id, amount=amount,
                                        phase=phase)
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

########################################################################
# Helper functions


def el_find_text(el, tagstr, ifempty):
    found_el = el.find(tagstr)
    if (found_el is None):
        return(ifempty)
    else:
        return(found_el.text)

doublespace_patt = re.compile(r'\s{2}')
endline_patt = re.compile(r'\n')

def all_text_fragments(et):
    ' Returns all fragments of text contained in a subtree, as a list of strings '
    r = []
    for e in et.getiterator():  # walks the subtree
        if e.text is not None:
            substr = (e.text)
            r.append(substr)
        if e.tail is not None:
            tailstr = (e.tail)
            r.append(e.tail)
    alltext = ' '.join(r)

    # Clean up the joined text fragments
    # Remove any line endings
    alltext = re.sub(endline_patt, "", alltext)
    # Remove extra whitespace
    alltext = re.sub(doublespace_patt, "", alltext)

    return alltext


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    filepath = "datasets/beerxml/recipe.xml"

    load_styles("datasets/beerxml/styleguide.xml")
    load_hops("datasets/beerxml/hops.xml")
    load_extracts("datasets/beerxml/adjuncts.xml")
    load_extracts("datasets/beerxml/extracts.xml")
    load_misc("datasets/beerxml/special.xml")
    load_yeasts("datasets/beerxml/yeast.xml")
    load_ferms("datasets/beerxml/grains.xml")
    load_recipes(filepath)
