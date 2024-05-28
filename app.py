#source1 : https://www.geeksforgeeks.org/build-blog-website-using-flask/

from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)   #setup app referencing this file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'    #Database - tells app where DB is located & using sqlite
    #3 /// is relative path & 4 is absolute
db = SQLAlchemy(app)   #initialize database

class Todo(db.Model):                                       
    id = db.Column(db.Integer, primary_key=True)                    #id references the unique ID of each goal
    content = db.Column(db.String(200), nullable=False)             #user enters text and can't be left blank
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  #automatically sets date to when goal is created

    def __repr__(self):                             #return string of Goal & the id for that goal created
        return '<Goal %r>' % self.id

#setup index route to avoid ERROR 404 - CREATE
@app.route('/', methods=['POST', 'GET'])            #we can POST and GET to this route
def index():
    if request.method == 'POST':                    #if request sent to route is POST
        goal_content = request.form['content']      #goal content set to the form input for the content
        new_goal = Todo(content=goal_content)       

        try:                                        #add to DATABASE, add, commit and redirect to the index
            db.session.add(new_goal)
            db.session.commit()
            return redirect('/')
        except:
            return 'Unable to add, error...'
    else:
        goals = Todo.query.order_by(Todo.date_created).all()        #returns all in order by date (new to old)
        return render_template('index.html', goals=goals)           #render_template renders the index.html from templates folder

# get goals function to work with the tkinter app added
@app.route('/api/goals', methods=['GET'])
def get_goals():
    goals = Todo.query.order_by(Todo.date_created).all()
    goals_list = [{"id": goal.id, "content": goal.content, "date_created": goal.date_created.strftime("%Y-%m-%d %H:%M:%S")} for goal in goals]
    return jsonify(goals_list)

#DELETE 
@app.route('/delete/<int:id>')                 #deletes based on the id - integer id
def delete(id):
    goal_to_delete = Todo.query.get_or_404(id)    #get the goal based on the id, if not exist - error 404

    try:
        db.session.delete(goal_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Could not Delete!'

#UPDATE
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    goal = Todo.query.get_or_404(id)

    if request.method == 'POST':
        goal.content = request.form['content']

        try:
            db.session.commit()         #nothing else needed, just commit to update
            return redirect('/')
        except:
            return 'Error updating goal'
    else:
        return render_template('update.html', goal=goal)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database and tables are created within the application context
    app.run(debug=True, port=5000)     #any errors will pop up on the page for us to see
