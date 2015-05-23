from model import Hop, Fermentable, Yeast, Recipe, Style, User, Misc, Extract, YeastIns, HopIns, FermIns, MiscIns, connect_to_db, db
import xml.etree.ElementTree as ET



def load_recipes(filepath, user):
    print filepath
    tree = ET.parse(filepath)
    root = tree.getroot()
    for recipe in root:
        name = recipe.find('NAME').text
        source = el_find_text(recipe, 'SOURCE', "")
        user_id = user
        public = el_find_text(recipe, 'public', "yes")
        style = [elem.find('NAME').text for elem in recipe.iter() if elem.tag == "STYLE"]
        style_name = style[0]
        notes = el_find_text(recipe, 'NOTES', "")
        batch_size = el_find_text(recipe, 'BATCH_SIZE', "")
        new_recipe = Recipe(name=name, source=source, user_id=user_id, public=public,
                            notes=notes, style_name=style_name)
        db.session.add(new_recipe)
        print "SUCCESS", name
        return name
    db.session.commit()


###########################################################################
# INGREDIENTS


def load_hops():
    hop_tree = ET.parse("datasets/hops.xml")
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


def load_extracts():
    ext_tree = ET.parse("datasets/beerxml/extracts.xml")
    root = ext_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        supplier = child.find('SUPPLIER').text
        origin = child.find('ORIGIN').text
        kind = el_find_text(child, 'KIND', "")
        ex_yield = child.find('YIELD').text
        notes = child.find('NOTES').text
        new_ext = Extract(name=name, supplier=supplier, origin=origin, kind=kind,
                          ex_yield=ex_yield, notes=notes)
        db.session.add(new_ext)
    db.session.commit


def load_ferms():
    ferm_tree = ET.parse("datasets/beerxml/grains.xml")
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


def load_misc():
    sources = ["datasets/beerxml/special.xml", "datasets/miscs.xml"]
    for source in sources:
        misc_tree = ET.parse(source)
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


def load_yeasts():
    misc_tree = ET.parse("datasets/yeast.xml")
    root = misc_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        kind = child.find('TYPE').text
        form = child.find('FORM').text
        lab = child.find('LABORATORY').text
        product_id = child.find('PRODUCT_ID').text
        amount_is_weight = child.find('AMOUNT_IS_WEIGHT').text
        min_temperature = child.find('MIN_TEMPERATURE').text
        max_temperature = child.find('MAX_TEMPERATURE').text
        flocculation = child.find('FLOCCULATION').text
        attenuation = child.find('ATTENUATION').text
        best_for = child.find('BEST_FOR').text
        notes = child.find('NOTES').text
        new_yeast = Yeast(name=name, kind=kind, form=form, lab=lab, product_id=product_id,
                          amount_is_weight=amount_is_weight, min_temperature=min_temperature,
                          flocculation=flocculation, attenuation=attenuation, best_for=best_for,
                          notes=notes)
        db.session.add(new_yeast)
    db.session.commit()

###########################################################################
# INSTRUCTIONS

filepath = "datasets/recipes.xml"
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
                phase = hop.find('USE').text
                time = hop.find('TIME').text
                kind = hop.find('TYPE').text
                new_inst_item = HopIns(recipe_id=recipe_id, hop_id=hop_id, amount=amount, phase=phase,
                                       time=time, kind=kind)
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
                name = fermentable.find('NAME').text
                ferm_id = Fermentable.query.filter_by(name=name).first().id
                amount = fermentable.find('AMOUNT').text
                new_ferm_item = FermIns(recipe_id=recipe_id, ferm_id=ferm_id, amount=amount)
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
                name = fermentable.find('NAME').text
                ferm_id = Fermentable.query.filter_by(name=name).first().id
                amount = fermentable.find('AMOUNT').text
                new_ferm_item = FermIns(recipe_id=recipe_id, ferm_id=ferm_id, amount=amount)
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
                misc_id = Misc.query.filter_by(name=name)[0].misc_id
                phase = misc_item.find('USE').text
                amount = misc_item.find('AMOUNT').text
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
