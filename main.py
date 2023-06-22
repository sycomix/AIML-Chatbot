from flask import Flask, render_template, flash, redirect, url_for, request
from py2neo import Graph
import random
import aiml
import os
import nltk
from nltk.corpus import wordnet
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
import pprint
import joblib
import bcrypt

main = Flask(__name__)

main.config['SECRET_KEY'] = '12345678'
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))




word = ""
sid = SentimentIntensityAnalyzer()

k = aiml.Kernel()

for filename in os.listdir("../ChatBot_ff/data"):
    if filename.endswith(".aiml"):
#       k.learn("data/" + filename)

knowledge_base = [
    "likes(john, pizza).",
    "likes(sarah, ice_cream).",
    "likes(mary, pasta)."
]
# ---------------------------------------------------------------

model = joblib.load(os.path.abspath("ML/gender_detect.pkl"))
vectorizer = CountVectorizer()


def predict_gender(name):
    vocabulary = joblib.load(os.path.abspath("ML/vocabulary.pkl"))
    vectorizer.vocabulary_ = vocabulary

    name_vectorized = vectorizer.transform([name])
    predicted_gender = model.predict(name_vectorized)[0]
    return predicted_gender

# ---------------------------------------------------------------

def find_definition_word(query):
    if query.startswith("what is the definition of "):
        return query[26:]
    if query.startswith("define "):
        return query[7:]
    if query.startswith("tell me about "):
        return query[13:]
    return ""

# ---------------------------------------------------------------

def get_sentiment(text):
    sentiment_scores = sid.polarity_scores(text)
    compound_score = sentiment_scores["compound"]
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"

# ---------------------------------------------------------------

class User:
    def __init__(self, firstname, lastname, username, email, password, gender):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.email = email
        self.password = password
        self.gender = gender

# ---------------------------------------------------------------

@main.errorhandler(404)
def page_not_found(e):
    return render_template("error.html")

# ---------------------------------------------------------------

@main.route("/")
def index():
    return render_template("home.html")

# ---------------------------------------------------------------

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["uname"]
        password = request.form["passw"]

        # LOGIN CHECKS
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return redirect(url_for("login"))

        # Set the username as the value of the 'name' predicate
        k.setPredicate("name", username)

        q_get = "MATCH (u:User {username: $username}) RETURN u"
        result = graph.run(q_get, username=username).data()

        if result:
            user = result[0]['u']
            hashed_password = user['password']

            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                # Retrieve the user's gender from the database
                gender = user['gender']
                k.setPredicate("gender", gender)  # Set the gender as a predicate

                return redirect(url_for("chatbot"))
            else:
                flash("Invalid username or password.")
                return redirect(url_for("login"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("chatbot"))

    return render_template("login.html")

# ---------------------------------------------------------------

@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        confirmpassw = request.form['confirmpassw']
        gender = predict_gender(fname)

        # CHECK ALL FIELDS ARE FILLED
        if not fname or not lname or not uname or not mail or not passw:
            flash("Please fill in all fields.")
            return redirect(url_for("signup"))

        # Check if password and confirm password match
        if passw != confirmpassw:
            flash("Password and Confirm Password do not match.")
            return redirect(url_for("signup"))

        # Get the user's IP address
        ip_address = request.remote_addr

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt())

        q_create = '''
                   create (n:Users {firstname: $firstname, lastname: $lastname, username: $username,
                   email: $email, password: $password, gender: $gender, ip_address: $ip_address})
               '''

        graph.run(q_create, firstname=fname, lastname=lname, username=uname, email=mail,
                  password=hashed_password.decode('utf-8'), gender=gender, ip_address=ip_address)
        flash("Signup Complete.")
        return redirect(url_for("login"))

    return render_template("signup.html")
# ---------------------------------------------------------------

@main.route("/<query>")
def api(query):
    response = k.respond(query)

    if query.startswith("i "):
        parts = query.split()
        if len(parts) == 3:
            relation = parts[1]
            firstname = parts[2]

            # Create the relation between the user and the mentioned username
            # Assuming you have a User node with a "username" property:
            q_create_relation = '''
                   MATCH (u:User {firstname: $firstname})
                   MATCH (user:User {username: $chatbot_username})
                   MERGE (user)-[:RELATION]->(u)
               '''
            query_params = {
                "firstname": firstname,
                "chatbot_username": k.getPredicate("name"),
                "relation": relation
            }
            graph.run(q_create_relation, **query_params)

            return "Relation created successfully."


    sentences = nltk.sent_tokenize(query)
    bot_response = ""
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(tokens)
        sentiment = get_sentiment(sentence)
        pprint.pprint("Sentence: {}".format(sentence))
        pprint.pprint("Tokens: {}".format(tokens))
        pprint.pprint("POS Tags: {}".format(pos_tags))
        pprint.pprint("Sentiment: {}".format(sentiment))
        if query.lower() == "prolog":
            bot_response += "Bot: Prolog mode initiated. Options:\n"
            bot_response += "> prolog search\n"
            bot_response += "> prolog add\n"
        elif query.startswith("prolog search"):
            prolog_query = query[13:].strip()
            result_found = False
            for fact in knowledge_base:
                if prolog_query in fact:
                    result_found = True
                    bot_response += "Bot: Found result: {}\n".format(fact)
            if not result_found:
                bot_response += "Bot: No results found.\n"
        elif query.startswith("prolog add"):
            fact = query[10:].strip()
            knowledge_base.append(fact)
            bot_response += "Bot: Fact added to the knowledge base.\n"

        # Randomly ask if the chatbot knows a person based on matching IP addresses
        if random.random() < 1.0:  # Adjust the probability as desired
            ip_address = request.remote_addr

            q_check_person = "MATCH (u:User) WHERE u.ip_address = $ip_address RETURN u.username"
            result = graph.run(q_check_person, ip_address=ip_address).data()
            if result:
                username = result[0]['u.username']
                bot_response += f"Bot: Do you know {username}?"
                # Set the predicate "ipaddress" to "hostname"
                k.setPredicate("hostname", k.getPredicate("ipaddress"))

                # Check if the user knows the username and create a KNOWS relation in the chatbot database
                if query == "yes":
                    q_create_relation = '''
                        MATCH (u:User {username: $username})
                        CREATE (c:User {username: $chatbot_username})
                        MERGE (u)-[:KNOWS]->(c)
                    '''
                    graph.run(q_create_relation, username=username, chatbot_username=k.getPredicate("name"))

        for word, pos_tag in pos_tags:
            word = find_definition_word(query)
            if word:
                definition = ''
                synsets = wordnet.synsets(word)
                if synsets:
                    definition = synsets[0].definition()
                    k.setPredicate("definition", definition)
        bot_response += response
    return bot_response

# ---------------------------------------------------------------

@main.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    return render_template("chatbot.html")

# ---------------------------------------------------------------

if __name__ == "__main__":
    main.run(host='127.0.0.1', port=8001, debug=True)
