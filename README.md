# AIML-Chatbot
This is a Aiml based chatbot which also has ML, Prolog, Neo4j, NLTK and many new technlogies.

*Chatbot Project*
This repository contains a chatbot project implemented using Python and Flask. The chatbot is built using AIML (Artificial Intelligence Markup Language) and incorporates various natural language processing (NLP) techniques.

# Features
🔴User authentication and signup
🔴Chatbot conversation and response generation
🔴Sentiment analysis of user input
🔴Definition lookup for specific words
🔴Gender prediction using machine learning
🔴Prolog-like knowledge base operations
🔴Integration with Neo4j graph database
# Prerequisites
Before running the project, make sure you have the following dependencies installed:

Python 3.x
Flask
py2neo
nltk
scikit-learn
joblib
bcrypt
You can install the required packages using pip:

shell
Copy code
pip install flask py2neo nltk scikit-learn joblib bcrypt
Setup
Clone the repository:

shell
Copy code
git clone https://github.com/your-username/chatbot-project.git
Change into the project directory:

shell
Copy code
cd chatbot-project
Set up the Neo4j database:

Install Neo4j locally and start the Neo4j server.

Modify the following line in main.py to match your Neo4j configuration:

python
Copy code
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))
Train the AIML models:

Place your AIML files inside the data directory.

Uncomment the line in main.py that loads the AIML files:

python
Copy code
# k.learn("data/" + filename)
Train the gender detection model:

Prepare a dataset containing names and their corresponding genders.
Train a gender detection model and save it as gender_detect.pkl.
Prepare a vocabulary for the CountVectorizer and save it as vocabulary.pkl.
Run the application:

shell
Copy code
python main.py
The chatbot will be accessible at http://localhost:8001.

Usage
Sign up: Visit http://localhost:8001/signup to create a new user account.
Log in: Visit http://localhost:8001/login to log in to an existing account.
Chat with the chatbot: Visit http://localhost:8001/chatbot to interact with the chatbot.
Contributing
Contributions to the project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

License
This project is licensed under the MIT License.
