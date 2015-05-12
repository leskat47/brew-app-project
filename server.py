from flask import Flask

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"


# if __name__ == "__main__":

#     app.debug = True

#     connect_to_db(app)

#     app.run()
