from flask import Flask, redirect, jsonify
from generate_data import generate_data

# create the application object
app = Flask(__name__)

@app.route('/')
def static_page():
    return redirect("static/index.html")

@app.route('/api/regenerate-data')
def regenerate_data():
    generate_data()
    return jsonify({ "regenerated": True })

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)