from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


###########################################################
# INSTRUCTIONS


class HopIns(db.Model):

    __tablename__ = hopsins

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    hop_id = db.Column(db.Integer, db.ForeignKey('hops.hop_id'))
    amount = db.Column(db.Float)
    phase = db.Column(db.String)
    time = db.Column(db.Interval)
    kind = db.Column(db.String)


class GrainsIns(db.Model):

    __tablename__ = fermsins

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    grain_id = db.Column(db.Integer, db.ForeignKey('ferms.id'))
    phase = db.Column(db.String, nullable=False)
    time = db.Column(db.Interval)


class MiscIns(db.Model):

    __tablename__ = miscsins

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    misc_id = db.Column(db.Integer, db.ForeignKey('misc.misc_id'))
    phase = db.Column(db.String, nullable=False)
    amount = db.Columns(db.Float)
    time = db.Column(db.Interval)


class YeastIns(db.Model):

    __tablename__ = yeastsins

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    yeast_id = db.Column(db.Integer, db.ForeignKey('yeasts.yeast_id'))
    amount = db.Columns(db.Float)
    phase = db.Column(db.String, nullable=False)

###########################################################
# INGREDIENTS


class Hop(db.Model):

    __tablename__ = "hops"

    hop_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    origin = db.Column(db.String)
    alpha = db.Column(db.Float)
    beta = db.Column(db.Float)
    form = db.Column(db.String)
    hsi = db.Column(db.Float)
    notes = db.Column(db.String)

    def __repr__(self):
        return "Hop_id: %s, hop_name: %s" % (self.hop_id, self.hop_name)


class Fermentables(db.Model):

    __tablename__ = "ferms"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    yield = db.Column(db.Float)
    kind = db.Column(db.String)
    supplier = db.Column(db.String)
    color = db.Column(db.Float)
    origin = db.Column(db.String)
    coarse_fine_diff = db.Column(db.Float)
    moisture = db.Column(db.Float)
    diastatic_power = db.Column(db.Float)
    protein = db.Column(db.Float)
    max_in_batch = db.Column(db.Float)
    recommended_mash = db.Column(db.Boolean)
    ibu_gal_per_lb = db.Column(db.Float)
    potential = db.Column(db.Float)
    display_color = db.Column(db.String)
    extract_substitute = db.Column(db.String)
    notes = db.Column(db.String)


class Misc(db.Model):

    __tablename__ = "misc"

    misc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    kind = db.Column(db.String)
    use = db.Column(db.String)
    amount_is_weight = db.Column(db.Boolean)
    notes = db.Column(db.String)


class Yeast(db.Model):

    __tablename__ = "yeasts"

    yeast_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    kind = db.Column(db.String)
    form = db.Column(db.String)
    lab = db.Column(db.String)
    product_id = db.Column(db.String)
    amount_is_weight = db.Column(db.Boolean)
    min_temperature = db.Column(db.Float)
    max_temperature = db.Column(db.Float)
    flocculation = db.Column(db.String)
    attenuation = db.Column(db.Float)
    best_for = db.Column(db.String)
    notes = db.Column(db.String)


def connect_to_db(app):
    """Connect the database to Flask app."""

    # Configure to use SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hops.db'
    db.app = app
    db.init_app(app)

####################################################################

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."
