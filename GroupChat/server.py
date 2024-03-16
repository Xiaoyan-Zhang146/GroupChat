import bson
from flask import Flask, jsonify, abort, make_response, request
from flask_cors import CORS, cross_origin
import pymongo
import json
from bson import json_util

app = Flask(__name__)
cors = CORS(app)
CORS(app, origins=r"*")
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.test


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': error.description}), 400)


@app.route('/<path:myPath>.json', methods=['GET'])
def get_task(myPath):
    path = str(myPath).split("/")
    collection = db[path[0]]
    tasks = []

    if len(path) == 1:
        condition = {}
        orderBy = request.args.get('orderBy')
        equalTo = request.args.get('equalTo')
        startAt = request.args.get('startAt')
        endAt = request.args.get('endAt')
        limitToFirst = request.args.get('limitToFirst')
        limitToLast = request.args.get('limitToLast')
        if orderBy:
            orderBy = orderBy.replace('"', '')
            try:
                condition[orderBy] = {}
                if equalTo:
                    if equalTo.isdigit():
                        condition[orderBy] = int(equalTo)
                    else:
                        condition[orderBy] = equalTo.replace('"', '')
                if startAt:
                    if startAt.isdigit():
                        condition[orderBy]["$gte"] = int(startAt)
                    else:
                        condition[orderBy]["$gte"] = startAt.replace('"', '')
                if endAt:
                    if endAt.isdigit():
                        condition[orderBy]["$lte"] = int(endAt)
                    else:
                        condition[orderBy]["$lte"] = endAt.replace('"', '')
                if not condition[orderBy]:
                    condition = {}

                cursor = collection.find(condition).sort(orderBy, pymongo.ASCENDING)
                size = len(list(cursor))
                cursor = collection.find(condition).sort(orderBy, pymongo.ASCENDING)
                if limitToFirst:
                    cursor.limit(int(limitToFirst))
                elif limitToLast:
                    cursor.skip(size - int(limitToLast)).limit(int(limitToLast))
                for doc in cursor:
                    tasks.append(doc)
            except ValueError:
                abort(400, "limitToFirst and limitToLast must be an integer")
            except:
                abort(400, "orderBy must be a valid JSON encoded path")
        else:
            if equalTo or startAt or endAt or limitToFirst or limitToLast:
                abort(400, "orderBy must be defined when other query parameters are defined")
            cursor = collection.find(condition)
            for doc in cursor:
                tasks.append(doc)
    else:
        cursor = collection.find({'_id': path[1]})
        for doc in cursor:
            tasks.append(doc)
        if len(tasks) == 0:
            abort(404)
    return jsonify(json.loads(json_util.dumps(tasks)))

    '''
        try:
        if orderBy:
            condition[orderBy] = {}
        if equalTo:
            condition[orderBy] = int(equalTo)
            if not orderBy:
                abort(400, "orderBy must be defined when other query parameters are defined")
        if startAt:
            condition[orderBy]["$gte"] = int(startAt)
            if not orderBy:
                abort(400, "orderBy must be defined when other query parameters are defined")
        if endAt:
            condition[orderBy]["$lte"] = int(endAt)
            if not orderBy:
                abort(400, "orderBy must be defined when other query parameters are defined")

    except:
        abort(400, "orderBy must be a valid JSON encoded path")

    print(condition)
    if orderBy:
        cursor = collection.find(condition).sort(orderBy, pymongo.ASCENDING)
    else:
        cursor = collection.find(condition)
    tasks = []
    if limitToFirst:
        for doc in cursor[:int(limitToFirst)]:
            task = json.dumps(doc, default=json_util.default)
            tasks.append(task)
    if limitToLast:
        for doc in cursor[len(cursor)-limitToLast:]:
            task = json.dumps(doc, default=json_util.default)
            tasks.append(task)
    else:
        for doc in cursor:
            task = json.dumps(doc, default=json_util.default)
            tasks.append(task)
    return jsonify(tasks)
    '''


@app.route('/<key>.json', methods=['POST'])
def create_task(key):
    collection = db[key]
    if not request.get_data():
        abort(400, "Invalid data; couldn't parse JSON object, array, or value.")
    try:
        temp = request.get_data().decode('utf-8')
        jsons = json.loads(temp)
        print(jsons)
        if not isinstance(jsons, list):
            dic = jsons
            jsons = [dic]
        tasks = []
        for task in jsons:
            task["_id"] = str(bson.ObjectId())
            tasks.append(task)
    except json.decoder.JSONDecodeError:
        abort(400, "Invalid data; couldn't parse JSON object, array, or value.")

    collection.insert_many(tasks)
    return jsonify(json.loads(json_util.dumps(tasks)))


@app.route('/<path:myPath>.json', methods=['DELETE'])
def delete_task(myPath):
    path = str(myPath).split("/")
    collection = db[path[0]]
    if len(path) == 1:
        collection.delete_many({})
    else:
        result = collection.delete_one({"_id": path[1]})
        if result.deleted_count == 0:
            abort(404)
    return jsonify(json.loads(json_util.dumps({'result': True})))


@app.route('/<key>/<task_id>.json', methods=['PATCH'])
def update_task(key, task_id):
    collection = db[key]
    condition = {"_id": str(task_id)}
    task = collection.find_one(condition)
    if not task:
        abort(404)
    temp = request.get_data().decode('utf-8')
    jsons = json.loads(temp)
    for json_key in jsons:
        task[json_key] = jsons[json_key]
    collection.update_one(condition, {"$set": task})
    return jsonify(json.loads(json_util.dumps(jsons)))


@app.route('/<path:myPath>.json', methods=['PUT'])
def put_task(myPath):
    path = str(myPath).split("/")
    if len(path) == 1:
        delete_task(myPath)
        return create_task(path[0])
    else:
        collection = db[path[0]]
        collection.delete_one({"_id": path[1]})
        temp = request.get_data().decode('utf-8')
        jsons = json.loads(temp)
        jsons["_id"] = path[1]
        collection.insert_one(jsons)
        return jsonify(json.loads(json_util.dumps(jsons)))


## db.users.aggregate([{"$group":{_id:"1",messages:{$addToSet:"$message"}}}, {$project:{_id:0,"messages":{$reduce:{input:"$messages","initialValue":[],"in":{ "$concatArrays":["$$value","$$this"]}}}}},{$sort:{"message.time":1}}])
## 查询消息顺序

@app.route('/<path:myPath>.json/message', methods=['GET'])
def get_message(myPath):
    path = str(myPath).split("/")
    collection = db[path[0]]
    tasks = []
    pipeline = [
        {'$group': {'_id': '1', 'messages': {'$addToSet': '$message'}}},
        {'$project': {'_id': 0,
                      'messages': {
                          '$reduce': {
                              'input': '$messages',
                              'initialValue': [],
                              "in": {"$concatArrays": ["$$value", "$$this"]}
                          }
                      }
                      }
         }
    ]
    cursor = collection.aggregate(pipeline)
    for doc in cursor:
        tasks.append(doc)

    newTasks = tasks[0]["messages"]
    newTasks.sort(key=taskSort)
    return jsonify(json.loads(json_util.dumps(newTasks)))


@app.route('/<key>.json/message', methods=['POST', 'OPTIONS'])
@cross_origin()
def save_message(key):
    collection = db[key]
    usersID = request.args.get('_id')
    condition = {}
    if not request.get_data():
        abort(400, "Invalid data; couldn't parse JSON object, array, or value.")
    condition["_id"] = usersID
    cursor = collection.find_one(condition)

    temp = request.get_data().decode('utf-8')
    jsons = json.loads(temp)
    cursor['message'].append(jsons)
    print(cursor)
    newValues = {"$set": cursor}

    try:
        collection.update_one(condition, newValues)
        return jsonify(json.loads(json_util.dumps({"State": True})))
    except:
        return jsonify(json.loads(json_util.dumps({"State": False})))


@app.route('/<key>.json/register', methods=['POST'])
def register(key):
    collection = db[key]

    if not request.get_data():
        abort(400, "Invalid data; couldn't parse JSON object, array, or value.")
    try:
        temp = request.get_data().decode('utf-8')
        jsons = json.loads(temp)

        email = jsons["email"]
        users = collection.find({"email": email})
        for user in users:
            if user:
                return jsonify(json.loads(json_util.dumps({"state": False,
                                                           "reason": "This email address has been registered"})))

        jsons["_id"] = str(bson.ObjectId())
        jsons["message"] = []
    except json.decoder.JSONDecodeError:
        abort(400, "Invalid data; couldn't parse JSON object, array, or value.")
    try:
        collection.insert_one(jsons)
        jsons["state"] = True
    except:
        jsons["state"] = False
    return jsonify(json.loads(json_util.dumps(jsons)))


@app.route('/<path:myPath>.json/login', methods=['GET'])
def login(myPath):
    path = str(myPath).split("/")
    collection = db[path[0]]
    email = request.args.get('email')
    password = request.args.get('password')
    users = collection.find({"email": email})
    for user in users:
        if user["password"] == password:
            return jsonify(json.loads(json_util.dumps({"state": True,
                                                       "reason": "Login Successful",
                                                       "_id": user["_id"]})))
        else:
            return jsonify(json.loads(json_util.dumps({"state": False,
                                                       "reason": "Email or password is incorrect"})))
    return jsonify(json.loads(json_util.dumps({"state": False,
                                               "reason": "Email or password is incorrect"})))


def taskSort(alist):
    print(alist)
    return alist["time"]


if __name__ == '__main__':
    app.run(debug=True)
