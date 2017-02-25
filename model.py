from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
# from SQLAlchemy import UniqueConstraint

db = SQLAlchemy()

###########################################################
# STYLE


class Style(db.Model):

    __tablename__ = "styles"

    style_id = db.Column(db.Integer, primary_key=True, nullable=False)
    style_name = db.Column(db.String, unique=True)
    category = db.Column(db.String)
    aroma = db.Column(db.String)
    appearance = db.Column(db.String)
    flavor = db.Column(db.String)
    mouthfeel = db.Column(db.String)
    impression = db.Column(db.String)
    comments = db.Column(db.String)
    ingredients = db.Column(db.String)
    abv_min = db.Column(db.Float)
    abv_max = db.Column(db.Float)
    ibu_min = db.Column(db.Float)
    ibu_max = db.Column(db.Float)
    og_min = db.Column(db.Float)
    og_max = db.Column(db.Float)
    fg_min = db.Column(db.Float)
    fg_max = db.Column(db.Float)
    srm_min = db.Column(db.Float)
    srm_max = db.Column(db.Float)
    examples = db.Column(db.String)


###########################################################
# RECIPE


class Recipe(db.Model):

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    source = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    public = db.Column(db.String, nullable=False)
    style_name = db.Column(db.String, db.ForeignKey('styles.style_name'))
    notes = db.Column(db.String, nullable=True)
    batch_size = db.Column(db.Float, nullable=False)
    batch_units = db.Column(db.String, nullable=False)

    def calc_color(self):
        fermins = FermIns.query.filter_by(recipe_id=self.recipe_id).all()
        extins = ExtIns.query.filter_by(recipe_id=self.recipe_id).all()
        srm_color = 0
        if self.batch_units not in ["gallons", "Gallons", "g"]:
            batch_size = float(self.batch_size) * 0.26417
        else:
            batch_size = float(self.batch_size)

        srm_color = 0.0

        for ins in fermins:
            srm_color += Fermentable.calc_srm_color(ins.fermentable.name, ins.amount, ins.units, batch_size)
        for ins in extins:
            srm_color += Extract.calc_srm_color(ins.extract.name, ins.amount, ins.units, batch_size)

        return(int(round(srm_color)))

    def __repr__(self):
        return "Recipe_id: %s, recipe_name: %s" % (self.recipe_id, self.name)


class Brew(db.Model):

    __tablename__ = "brews"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    og = db.Column(db.Float, nullable=True)
    cg = db.Column(db.Float, nullable=True)
    cg_date = db.Column(db.Date, nullable=True)
    fg = db.Column(db.Float, nullable=True)
    abv = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False)
    boil_start = db.Column(db.Time, nullable=True)
    notes = db.Column(db.String, nullable=True)
    results_notes = db.Column(db.String, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    recipe = db.relationship('Recipe', backref=db.backref('brews', order_by=id))


###########################################################
# USERS


class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    def __repr__(self):
        return "user_id: %s, username: %s, password: %s" % (self.user_id, self.username, self.password)


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
    units = db.Column(db.String)

    recipe = db.relationship('Recipe', backref=db.backref('hins', order_by=id))
    hop = db.relationship('Hop', backref=db.backref('hins', order_by=id))


class FermIns(db.Model):

    __tablename__ = "fermsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    ferm_id = db.Column(db.Integer, db.ForeignKey('ferms.id'))
    amount = db.Column(db.Float)
    units = db.Column(db.String)
    recipe = db.relationship('Recipe', backref=db.backref('fins', order_by=id))
    fermentable = db.relationship('Fermentable', backref=db.backref('fins', order_by=id))


class ExtIns(db.Model):

    __tablename__ = "extsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    extract_id = db.Column(db.Integer, db.ForeignKey('extracts.id'))
    amount = db.Column(db.Float)
    units = db.Column(db.String)
    recipe = db.relationship('Recipe', backref=db.backref('eins', order_by=id))
    extract = db.relationship('Extract', backref=db.backref('eins', order_by=id))


class MiscIns(db.Model):

    __tablename__ = "miscsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    misc_id = db.Column(db.Integer, db.ForeignKey('misc.misc_id'))
    phase = db.Column(db.String)
    amount = db.Column(db.Float)
    time = db.Column(db.Integer)
    recipe = db.relationship('Recipe', backref=db.backref('mins', order_by=id))
    misc = db.relationship('Misc', backref=db.backref('mins', order_by=id))
    units = db.Column(db.String)


class YeastIns(db.Model):

    __tablename__ = "yeastsins"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    yeast_id = db.Column(db.Integer, db.ForeignKey('yeasts.yeast_id'))
    amount = db.Column(db.Float)
    phase = db.Column(db.String, nullable=False)
    units = db.Column(db.String)
    recipe = db.relationship('Recipe', backref=db.backref('yins', order_by=id))
    yeast = db.relationship('Yeast', backref=db.backref('yins', order_by=id))


###########################################################
# MIXINS


class CalcSRMColorMixin(object):
    @classmethod
    def calc_srm_color(cls, name, amount, units, batch_size):
        """
        Calculate the color contribution of various ingredients
        """
        color = cls.query.filter_by(name=name)[0].color

        # Convert amount to pounds
        if units in ["oz", "ounces"]:
            amount = amount * 0.062500
        elif units in ["g", "grams"]:
            amount = amount * 0.0022046
        else:
            amount = amount * 2.20462
        mcu = (color * amount) / float(batch_size)
        srm_color = 1.4922 * (mcu ** .6859)

        return srm_color


    @classmethod
    def get_srm_from_ingredient_list(cls, ingredient_list, batch_size, batch_units):
        srm_value = 0
        for i in range(0, len(ingredient_list), 3):
            name = ingredient_list[i]["value"]
            amount = float(ingredient_list[i+1]["value"])
            units = ingredient_list[i+2]["value"]
            srm_value += cls.calc_srm_color(name, amount, units, batch_size)

        return srm_value

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
    # __table_args__ = (UniqueConstraint('name', 'form'))

    def __repr__(self):
        return "Hop_id: %s, hop_name: %s" % (self.hop_id, self.name)


class Extract(db.Model, CalcSRMColorMixin):

    __tablename__ = "extracts"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    supplier = db.Column(db.String)
    origin = db.Column(db.String)
    notes = db.Column(db.String)
    color = db.Column(db.Float)
    kind = db.Column(db.String)
    phase = db.Column(db.String)
    ex_yield = db.Column(db.Float)
    color = db.Column(db.Float)


class Fermentable(db.Model, CalcSRMColorMixin):

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
    # ibu_gal_per_lb = db.Column(db.Float, nullable=True)
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
    min_temperature = db.Column(db.Float, nullable=True)
    max_temperature = db.Column(db.Float, nullable=True)
    flocculation = db.Column(db.String, nullable=True)
    attenuation = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String, nullable=True)


####################################################################


def connect_to_db(app):
    """Connect the database to Flask app."""

    # Configure to use SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipes'
    db.app = app
    db.init_app(app)

####################################################################

if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."
