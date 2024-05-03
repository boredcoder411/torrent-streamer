from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory
import subprocess
import os

app = Flask(__name__)

# User database (in reality, you would use a proper database)
users = {
    "userr": "ssss"
}

def download_with_aria2(magnet_link, download_dir):
    command = ["aria2c", "--seed-time=0", "--dir=" + download_dir, magnet_link]
    subprocess.run(command)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            # Set a cookie to indicate the user is logged in
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie('username', username)
            return resp
        else:
            error = "Invalid credentials. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Check if the user is logged in by checking the cookie
    username = request.cookies.get('username')
    if username and username in users:
        if request.method == 'POST':
            magnet_link = request.form['magnet_link']
            download_dir = f"./downloads/{username}"  # Changed download directory
            download_with_aria2(magnet_link, download_dir)
            return "Download finished", 200  # Send a 200 response
        # Get user's folders if available
        folders = os.listdir(f"./downloads/{username}")
        return render_template('dashboard.html', username=username, folders=folders)
    else:
        return redirect(url_for('login'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Check if user already exists
        if username in users:
            error = "Username already exists. Please choose a different one."
            return render_template("signup.html", error=error)
        # Add the new user to the users dictionary
        users[username] = password
        os.mkdir(f"./downloads/{username}")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route('/show_files/<folder>')
def show_files(folder):
    username = request.cookies.get('username')
    user_folder = os.path.join("./downloads", username, folder)
    files = os.listdir(user_folder)
    return render_template('folder.html', username=username, files=files, folder=folder)

@app.route('/download_file/<folder>/<file>')
def download_file(folder, file):
    username = request.cookies.get("username")
    return send_from_directory(os.path.join("./downloads", username, folder), file)

if __name__ == '__main__':
    app.run(debug=True)

