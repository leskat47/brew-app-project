from flask_sqlalchemy import SQLAlchemy
# from SQLAlchemy import UniqueConstraint

db = SQLAlchemy()

###########################################################
# STYLE


class Style(db.Model):

    __tablename__ = "styles"

    style_id = db.Column(db.Integer, primary_key=True, nullable=False)
    style_name = db.Column(db.String)
    category = db.Column(db.String)
    style_guide = db.Column(db.String)
    kind = db.Column(db.String)
    og_min = db.Column(db.Float)
    og_max = db.Column(db.Float)
    fg_min = db.Column(db.Float)
    fg_max = db.Column(db.Float)
    abv_min = db.Column(db.Float)
    abv_max = db.Column(db.Float)
    ibu_min = db.Column(db.Float)
    ibu_max = db.Column(db.Float)
    color_min = db.Column(db.Float)
    color_max = db.Column(db.Float)
    notes = db.Column(db.String)
    profile = db.Column(db.String)
    ingredients = db.Column(db.String)
    examples = db.Column(db.String)


###########################################################
# RECIPE


class Recipe(db.Model):

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    source = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    public = db.Column(db.String)
    style_name = db.Column(db.Integer, db.ForeignKey('styles.style_name'))
    notes = db.Column(db.String)


class Brew(db.Model):

    __tablename__ = "brews"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    recipe = db.Column(db.String, db.ForeignKey('recipes.name'))
    date = db.Column(db.Date)
    notes = db.Column(db.String)


###########################################################
# USERS


class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    handle = db.Column(db.String)
    password = db.Column(db.String)

###########################################################
# INSTRUCTIONS


class HopIns(db.Model):

    __tablename__ = "hopsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    hop_id = db.Column(db.Integer, db.ForeignKey('hops.hop_id'))
    amount = db.Column(db.Float)
    phase = db.Column(db.String)
    time = db.Column(db.Integer)
    kind = db.Column(db.String)


class FermIns(db.Model):

    __tablename__ = "fermsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    ferm_id = db.Column(db.Integer, db.ForeignKey('ferms.id'))
    amount = db.Column(db.Float)
    after_boil = db.Column(db.String, nullable=False)
    kind = db.Column(db.String)


class MiscIns(db.Model):

    __tablename__ = "miscsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    misc_id = db.Column(db.Integer, db.ForeignKey('misc.misc_id'))
    kind = db.Column(db.String)
    phase = db.Column(db.String)
    amount = db.Column(db.Float)
    time = db.Column(db.Integer)


class YeastIns(db.Model):

    __tablename__ = "yeastsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    yeast_id = db.Column(db.Integer, db.ForeignKey('yeasts.yeast_id'))
    amount = db.Column(db.Float)
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
    # unicon = db.UniqueConstraint('name', 'form')

    def __repr__(self):
        return "Hop_id: %s, hop_name: %s" % (self.hop_id, self.hop_name)


class Fermentable(db.Model):

    __tablename__ = "ferms"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    ayield = db.Column(db.Float)
    kind = db.Column(db.String)
    supplier = db.Column(db.String)
    color = db.Column(db.Float)
    origin = db.Column(db.String)
    coarse_fine_diff = db.Column(db.String)
    moisture = db.Column(db.Float)
    diastatic_power = db.Column(db.Float, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    max_in_batch = db.Column(db.Float, nullable=True)
    recommend_mash = db.Column(db.String, nullable=True)
    ibu_gal_per_lb = db.Column(db.Float, nullable=True)
    potential = db.Column(db.Float, nullable=True)
    display_color = db.Column(db.String, nullable=True)
    extract_substitute = db.Column(db.String, nullable=True)
    notes = db.Column(db.String)


class Misc(db.Model):

    __tablename__ = "misc"

    misc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    kind = db.Column(db.String)
    use = db.Column(db.String)
    amount_is_weight = db.Column(db.String)
    notes = db.Column(db.String, nullable=True)


class Yeast(db.Model):

    __tablename__ = "yeasts"

    yeast_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    kind = db.Column(db.String, nullable=True)
    form = db.Column(db.String, nullable=True)
    lab = db.Column(db.String, nullable=True)
    product_id = db.Column(db.String, nullable=True)
    amount_is_weight = db.Column(db.String, nullable=True)
    min_temperature = db.Column(db.Float, nullable=True)
    max_temperature = db.Column(db.Float, nullable=True)
    flocculation = db.Column(db.String, nullable=True)
    attenuation = db.Column(db.Float, nullable=True)
    best_for = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)


def connect_to_db(app):
    """Connect the database to Flask app."""

    # Configure to use SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
    db.app = app
    db.init_app(app)

####################################################################

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."
