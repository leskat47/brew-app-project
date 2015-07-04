from model import Hop, Fermentable, Yeast, Recipe, Style, User, Misc, Extract, YeastIns, HopIns, ExtIns, FermIns, MiscIns, connect_to_db, db
from feeder import calc_color, load_recipes, load_hops_ins, load_ferm_ins, load_ext_ins, load_misc_ins, load_yeast_ins
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


def load_adjuncts(datafile):
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
        print "Extract: ", name
        new_ext = Extract(name=name, supplier=supplier, origin=origin, kind=kind,
                          ex_yield=ex_yield, notes=notes, phase=phase)
        db.session.add(new_ext)
    db.session.commit


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

########################################################################
def seed_db():
    load_styles("datasets/styleguide.xml")
    load_hops("datasets/hops.xml")
    load_extracts("datasets/adjuncts.xml")
    load_extracts("datasets/extracts.xml")
    load_misc("datasets/special.xml")
    load_yeasts("datasets/yeast.xml")
    load_ferms("datasets/grains.xml")
    load_recipes("datasets/recipe.xml")

def connect_to_db():
    connect_to_db(app)
    db.create_all()

def main():
    connect_to_db()
    seed_db()

if __name__ == "__main__":
    main()
