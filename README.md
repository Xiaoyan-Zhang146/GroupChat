# GroupChat
A group chat web app can store the message.

## Server.py

1. GET:
    * orderBy 
    * equalTo
    * startAt
    * endAt
    * limitToFirst (must be interger)
    * limitToLast (must be interger)
    * Error Code 400 "limitToFirst and limitToLast must be an integer"
    * Error Code 400 "orderBy must be defined when other query parameters are defined"

    * Example: curl -X GET 'http://localhost:5000/users.json?orderBy=age&startAt=100&endAt=100&limitToLast=1'
2. POST:
   * Only supports JSON format (List is also a type of JSON)
   * Automatically generate _id (UUID)
   * Error Code 400 "Invalid data; couldn't parse JSON object, array, or value"
   * Example: curl -X POST 'http://localhost:5000/users.json' -d '{"name": "A", "email": "A@gmail.com", "password":"AAAAA"}'


3. DELETE:
   * Two DELETE methods:
     1. curl -X DELETE 'http://localhost:5000/users.json' (DELETE ALL)
     2. curl -X DELETE 'http://localhost:5000/users/\<id>.json' (DELETE specific user by ID)

4. PATCH
   * curl -X PATCH http://localhost:5000/users/\<id>.json' (update specific user by ID)
   * Error Code 400 "Not found"

5. PUT
   * Two PUT methods:
      1. curl -X PUT 'http://localhost:5000/users.json' (overwrite all data)
      2. curl -X PUT 'http://localhost:5000/users/\<id>.json' (Add specific user by given ID)


## Run the Python Code in the background
1. export FLASK_APP=server.py 
2. nohup flask run --host=0.0.0.0 --port=5000 > flask.log 2>&1 &
3. nohup python3 websocket-server.py > websocket-server.log 2>&1 &
chack the Python running: ps -ef|grep python

## EC2
* You can Connect to EC2 instance by:"ssh -i "Project551.pem" ubuntu@ec2-54-215-32-190.us-west-1.compute.amazonaws.com"
