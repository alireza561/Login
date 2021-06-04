from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt   # pip install pyJWT
import datetime
import os






app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'

file_dir = os.path.dirname(__file__)  
goal_route = os.path.join(file_dir, 'app.db')  
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + goal_route

db = SQLAlchemy(app)




# ============================       MODEL      ==================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(70))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


# db.create_all()



# ============================      ROUT        ==========================================

@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'users' : output})




@app.route('/user/<public_id>', methods=['GET'])
def get_one_ser(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({ 'message' : 'uesr not founf' })
    
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({ 'user' : user_data })





@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()) , name=data['name'] , password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({ 'message' : 'new user created' })




@app.route('/user/<public_id>', methods=['PUT'])
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({ 'message' : 'uesr not founf' })
    
    user.admin = True
    db.session.commit()

    return jsonify({ 'message' : 'user has been updated' })




@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({ 'message' : 'uesr not founf' })
    db.session.delete(user)
    db.session.commit()
    return jsonify({ 'message' : 'the user has been deleted' })




@app.route('/login')
def login():
    auth = request.authorization
    user = User.query.filter_by(name=auth.username).first()

    if  not user or not auth or not auth.username or not auth.password  :
        return make_response('could not verify')

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({ 'public_id' : user.public_id, 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)} , app.config['SECRET_KEY'])
        return jsonify({ 'token' : token})

    return make_response('could not verify' )





# if __name__ == '__main__':
#     app.run(debug=True)