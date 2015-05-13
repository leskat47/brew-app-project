from model import Hop, Fermentable, Yeast, Recipe, Style, User, Misc, YeastIns, HopIns, FermIns, MiscIns, connect_to_db, db
from server import app
import xml.etree.ElementTree as ET

###########################################################################
# STYLES


def load_styles():
    tree = ET.parse("datasets/styles.xml")
    root = tree.getroot()
    for child in root:
        style_name = child.find('NAME').text
        category = child.find('CATEGORY').text
        style_guide = child.find('STYLE_GUIDE').text
        kind = child.find('TYPE').text
        og_min = child.find('OG_MIN').text
        og_max = child.find('OG_MAX').text
        fg_min = child.find('FG_MIN').text
        fg_max = child.find('FG_MAX').text
        abv_min = child.find('ABV_MIN').text
        abv_max = child.find('ABV_MAX').text
        ibu_min = child.find('IBU_MIN').text
        ibu_max = child.find('IBU_MAX').text
        color_min = child.find('COLOR_MIN').text
        color_max = child.find('COLOR_MAX').text
        notes = child.find('NOTES').text
        profile = child.find('PROFILE').text
        ingredients = child.find('INGREDIENTS').text
        examples = child.find('EXAMPLES').text
        new_style = Style(style_name=style_name, category=category, style_guide=style_guide,
                          kind=kind, og_min=og_min, og_max=og_max, fg_min=fg_min, fg_max=fg_max, abv_min=abv_min,
                          abv_max=abv_max, ibu_min=ibu_min, ibu_max=ibu_max, color_min=color_min,
                          color_max=color_max, profile=profile, ingredients=ingredients,
                          examples=examples, notes=notes)
        db.session.add(new_style)
    db.session.commit()

###########################################################################
# RECIPES
def load_recipes(user=1, public_use=True):
    tree = ET.parse("datasets/recipes.xml")
    root = tree.getroot()
    for child in root:
        name = child.find('NAME').text
        if child.find('SOURCE') is not None:
            source = child.find('SOURCE').text
        else:
            source = None
        user_id = user
        public = public_use
        notes = child.find('NOTES').text
        style_name = child.find('STYLE').find('NAME').text
        new_recipe = Recipe(name=name, source=source, user_id=user_id, public=public,
                            notes=notes, style_name=style_name)
        db.session.add(new_recipe)
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


def load_ferms():
    ferm_tree = ET.parse("datasets/grain.xml")
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
        ibu_gal_per_lb = child.find('IBU_GAL_PER_LB').text
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
                               ibu_gal_per_lb=ibu_gal_per_lb, potential=potential, display_color=display_color,
                               extract_substitute=extract_substitute, notes=notes)
        db.session.add(new_ferm)
    db.session.commit()


def load_misc():
    misc_tree = ET.parse("datasets/miscs.xml")
    root = misc_tree.getroot()
    for child in root:
        name = child.find('NAME').text
        kind = child.find('TYPE').text
        use = child.find('USE').text
        amount_is_weight = child.find('AMOUNT_IS_WEIGHT').text
        notes = child.find('NOTES').text
        new_misc = Misc(name=name, kind=kind, use=use,
                        amount_is_weight=amount_is_weight, notes=notes)
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


def load_hops_ins():
    misc_tree = ET.parse("datasets/recipes.xml")
    root = misc_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        for subchild in child:
            for hop in subchild.findall('HOP'):
                name = hop.find('NAME').text
                amount = hop.find('AMOUNT').text
                phase = hop.find('USE').text
                time = hop.find('TIME').text
                kind = hop.find('TYPE').text
                new_inst_item = HopIns(recipe=recipe, name=name, amount=amount, phase=phase,
                                       time=time, kind=kind)
                db.session.add(new_inst_item)
    db.session.commit()


def load_ferm_ins():
    misc_tree = ET.parse("datasets/recipes.xml")
    root = misc_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        for subchild in child:
            for fermentable in subchild.findall('FERMENTABLE'):
                name = fermentable.find('NAME').text
                amount = fermentable.find('AMOUNT').text
                after_boil = fermentable.find('ADD_AFTER_BOIL').text
                kind = fermentable.find('TYPE').text
                new_ferm_item = FermIns(recipe=recipe, name=name, amount=amount,
                                        after_boil=after_boil, kind=kind)
                db.session.add(new_ferm_item)
    db.session.commit()


def load_misc_ins():
    misc_tree = ET.parse("datasets/recipes.xml")
    root = misc_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        for subchild in child:
            for misc_item in subchild.findall('MISC'):
                name = misc_item.find('NAME').text
                phase = misc_item.find('USE').text
                amount = misc_item.find('AMOUNT').text
                kind = misc_item.find('TYPE').text
                new_misc_item = MiscIns(recipe=recipe, name=name, amount=amount,
                                        phase=phase, kind=kind)
                db.session.add(new_misc_item)
    db.session.commit()


def load_yeast_ins():
    misc_tree = ET.parse("datasets/recipes.xml")
    root = misc_tree.getroot()
    for child in root:
        recipe = child.find('NAME').text
        for subchild in child:
            for yeast in subchild.findall('YEAST'):
                name = yeast.find('NAME').text
                amount = yeast.find('AMOUNT').text
                phase = 'primary'
                new_yeast = YeastIns(recipe=recipe, name=name, amount=amount,
                                     phase=phase)
                db.session.add(new_yeast)
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_styles()
    load_recipes()
    load_hops()
    load_misc()
    load_yeasts()
    load_ferms()
    load_hops_ins()
    load_ferm_ins()
    load_misc_ins()
    load_yeast_ins()

