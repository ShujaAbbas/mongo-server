from flask import jsonify, abort, make_response, request, render_template
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth
from config import Config
from app import app
import webbrowser

app.config.from_object(Config)
mongo = PyMongo(app, config_prefix = 'MONGO')
auth = HTTPBasicAuth();

@auth.get_password
def get_password(username):
	response = mongo.db.users.find({"name": username}, 
		{"password": 1, "_id": 0})
	return response[0].get("password", "")

@auth.error_handler
def unauthorized():
	return make_response(jsonify({"error": "Unauthorized Access"}), 401)


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({"error": "Not found"}), 404)
@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({"error": "Bad request"}), 400)

@app.route("/")
def index():
	return render_template("form.html")

@app.route('/todo/api/v1.0/all_tasks', methods=['GET'])
@auth.login_required
def get_all_tasks():
        tasks = [task for task in mongo.db.tasks.find({}, 
        {"_id":0, "uname": 0})]
        return jsonify({"tasks": tasks})

@app.route('/todo/api/v1.0/tasks', methods=['GET', 'POST'])
def get_tasks():
	username = request.args.get("username")
	print ("\n\n Request: {} \n\n".format(username))
	tasks = [task for task in mongo.db.tasks.find({"uname": username}, 
	{"_id":0, "uname": 0})]
	#return jsonify({"tasks": tasks})
	return render_template("hello.html")

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_tasks_id(task_id):
	task = [task for task in mongo.db.tasks.find({"id": task_id}, {"_id": 0})]
	if len(task) == 0:
		abort(404)
	return jsonify({"task": task[0]})


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	
	id = mongo.db.tasks.count() + 1,
	title = request.json.get('title', ''),
	desc = request.json.get('description', ''), 
	
	mongo.db.tasks.insert({"id": id, "title": title, "description": desc, "done": False})
	return jsonify({'Inserted': "True"}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	task = [task for task in mongo.db.tasks.find({"id": task_id}, {"_id": 0})]
	if len(task) == 0:
		abort(400)
	
	title = request.json.get('title', task[0]['title'])
	desc = request.json.get('description', task[0]['description'])
	done = request.json.get('done', task[0]['done'])
	
	mongo.db.tasks.update({"id": task_id}, {'id': task_id, 'title': title, "description": desc, "done": done})
	return jsonify({"Updated": "True"})

@app.route("/todo/api/v1.0/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
	
	mongo.db.tasks.remove({'id': task_id})
	return jsonify({'result': "True"})

@app.route("/todo/api/v1.0/tasks/greet", methods=["POST", "GET", "OPTIONS"])
def greet():
	
	print "\n\nHello world of {}\n\n".format(request)
	
	try:
		username = request.json[0].get("value", "")
		password = request.json[1].get("value", "")

		response = mongo.db.users.find({"name": username}, 
                	{"password": 1, "_id": 0})
		if response is None:
			abort(400)


		if response[0].get("password", "") == password:
			return jsonify({"result": "True"}), 200
		else:
			return jsonify({"result": "False"}), 200

		return jsonify({"result": "False"}), 200

	except Exception as e:
		print str(e)
		return jsonify({"result": "False"}), 200
	

@app.route("/test", methods=["GET"])
def test():
	return render_template("hello.html")

if __name__ == '__main__':
	app.run(debug=False)
