from flask import Flask, render_template
app = Flask(__name__)

posts = [
    {
        'author': 'Trmúa Hmề',
        'title': 'Article 1',
        'content': 'Cách để trở thành Trmúa Hmề official',
        'date-posted': 'April 20, 2021'
    },
    {
        'author': 'Trmúa Hmề bủh',
        'title': 'Article 2',
        'content': 'Cách để trở thành Trmúa Hmề bủh',
        'date-posted': 'April 20, 2021'
    },
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts = posts)

@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

@app.route("/login")
def login():
    return "<h1>Login page</h1>"

if __name__ == '__main__':
    app.run(debug = True)