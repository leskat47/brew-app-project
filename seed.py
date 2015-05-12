from model import Hop, connect_to_db, db
from server import app
import xml.etree.ElementTree as ET




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

def load_misc():
    misc_tree = ET.parse("datasets/misc.html")
    root = misc_tree.getroot()
    for child in root: 
        name = child.find('NAME').text
        kind = child.find('TYPE').text
        use = child.find('USE').text
        amount_is_weight = child.find('AMOUNT_IS_WEIGHT')
        notes = child.find('NOTES')
        new_misc = Misc(name=name, kind=kind, use=use,
            amount_is_weight=amount_is_weight, notes=notes)
        db.session.add(new_hop)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_hops()
