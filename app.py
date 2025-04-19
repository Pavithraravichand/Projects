from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure SQLAlchemy for MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/user_db'

db = SQLAlchemy(app)

# SQLAlchemy model
class User(db.Model):
    __tablename__ = 'users'
    auto_id_0 = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer)
    qualification = db.Column(db.String(100))
    interests = db.Column(db.String(255))
    dob = db.Column(db.Date)

    def to_dict(self):
        return {
            "auto_id_0": self.auto_id_0,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "qualification": self.qualification,
            "interests": self.interests,
            "dob": self.dob.strftime('%Y-%m-%d') if self.dob else None
        }

with app.app_context():
    db.create_all()

@app.route('/view', methods=['GET'])
def view_users():
    try:
        users = User.query.all()
        result = [user.to_dict() for user in users]
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@app.route('/get_user/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.get(id)
        if user:
            data = user.to_dict()
            data['dob'] = user.dob.strftime('%d-%m-%Y') if user.dob else None  # return dob as dd-mm-yyyy
            return jsonify({"success": True, "data": data})
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/add', methods=['POST'])
def add_user():
    try:
        data = request.get_json() if request.is_json else request.form

        name = data.get('name')
        email = data.get('email')
        age = data.get('age')
        qualification = data.get('qualification')
        interests = data.get('interests')
        dob = data.get('dob')

        if not all([name, email, age, qualification, interests, dob]):
            return jsonify({"success": False, "message": "All fields are required."}), 400

        try:
            dob_obj = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"success": False, "message": "Invalid date format for dob. Use YYYY-MM-DD."}), 400

        new_user = User(
            name=name,
            email=email,
            age=age,
            qualification=qualification,
            interests=interests,
            dob=dob_obj
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": True, "message": "User added successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/edit/<int:id>', methods=['POST'])
def edit_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        qualification = request.form.get('qualification')
        interests = request.form.get('interests')
        dob_str = request.form.get('dob')

        if name:
            user.name = name
        if email:
            user.email = email
        if age:
           user.age=age
        if qualification:
            user.qualification = qualification
        if interests:
            user.interests = interests
        if dob_str:
            try:
                user.dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"success": False, "message": "Invalid date format for dob. Use %Y-%m-%d."}), 400
        elif dob_str == "":
            user.dob = None  

        db.session.commit()
        return jsonify({"success": True, "message": "User updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/delete/<int:id>', methods=['GET'])
def delete_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "User deleted successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
