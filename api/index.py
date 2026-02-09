from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def index():
    return render_template('index.html')

# Vercel requires the app to be called 'app'
if __name__ == '__main__':
    app.run(debug=True)
