from bson import ObjectId
from flask import Flask, jsonify, request, Response
import matplotlib.pyplot as plt
import pymongo
import datetime
from datetime import timedelta
from matplotlib.ticker import MaxNLocator

app = Flask(__name__)

# Establish a connection to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["Information_details"]

# vaccine_manufacturer = {'Pfizer', 'Moderna', 'AstraZeneca','Novavax'}
# amount_not_vaccinated = 0
# recovery_time = 14

vaccine_manufacturer = (db["mycollection"]).find()[0]['vaccine_manufacturer']
amount_not_vaccinated = (db["mycollection"]).find()[0]['amount_not_vaccinated']
recovery_time = (db["mycollection"]).find()[0]['recovery_time']



@app.route('/summary_view', methods=['VIEW'])
def get_summary():
    # Calculate the start and end dates for the past 30 days
    end_date = datetime.datetime.now().today().date()
    start_date = end_date - timedelta(days=29)
    # Create a list of dates for the past 30 days
    date_list = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    ill_counts = [0 for _ in range(30)]
    # Retrieve data from database
    data = collection.find()
    for record in data:
        # Parse the dates of illness and recovery from the record
        if record['corona_virus_details']['positive_result'].get('date_received'):
            date_received = datetime.datetime.strptime(
                record['corona_virus_details']['positive_result']['date_received'], '%Y-%m-%d')
            recovery_date = datetime.datetime.strptime(
                record['corona_virus_details']['positive_result']['recovery_date'], '%Y-%m-%d')
            delta = recovery_date - date_received
            # Updating the relevant days for the graph
            for i in range(delta.days + 1):
                date = (date_received + timedelta(days=i)).strftime('%Y-%m-%d')
                if date in date_list:
                    ill_counts[date_list.index(date)] += 1

    # Create the graph
    fig, ax = plt.subplots()
    ax.plot([i[5:] for i in date_list], ill_counts)
    ax.set(xlabel='Date', ylabel='Number of Sick People',
           title='The number of people who are not vaccinated:' + str(
               amount_not_vaccinated) + '\nNumber of Sick People by Day in 30 Last Days:')
    ax.grid()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', labelsize=4)

    # Convert the graph to a PNG image
    fig.savefig('Sick_people_graph.png')
    # Return the image in the Flask response
    with open('Sick_people_graph.png', 'rb') as f:
        image = f.read()
    return Response(image, mimetype='image/png')


@app.route('/insert', methods=['POST'])
def insert_document():
    global amount_not_vaccinated
    # Parse the request body to extract the data
    data = request.get_json()

    # Check that the required fields are present in the request body
    if not data.get('first_name') or not data.get('last_name') or not data.get('id_number') or not data.get(
            'address') or not data.get('date_of_birth') or not data.get('telephone') or not data.get(
        'mobile_phone') or not data.get('corona_virus_details'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check that the data types of the personal details are correct
    if not isinstance(data['first_name'], str) or not isinstance(data['last_name'], str) or not isinstance(
            data['id_number'], str) or not isinstance(data['address'], dict) or not isinstance(
        data['telephone'], str) or not isinstance(data['mobile_phone'], str):
        return jsonify({'error': 'Invalid data types for personal details'}), 400

    if not len(data['id_number']) == 9:
        return jsonify({'error': 'Invalid length of id number'}), 400

    # Check that the date_of_birth field is a valid date string in the format YYYY-MM-DD
    try:
        date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date of birth (dob should be a date string in the format YYYY-MM-DD)'}), 400

    # Check that the address field contains the required subfields
    if not data['address'].get('city') or not data['address'].get('street') or not data['address'].get('number'):
        return jsonify({'error': 'Missing required subfields in address'}), 400

    # Check if the id_number already exists in the collection
    if collection.find_one({'id_number': data['id_number']}):
        return jsonify({'error': 'id_number already exists'}), 400

    # Check that the data types of the corona virus details are correct
    if not isinstance(data['corona_virus_details'], dict):
        return jsonify({'error': 'Invalid data type for corona virus details'}), 400
    if data['corona_virus_details'].get('vaccine_details'):
        if not isinstance(data['corona_virus_details']['vaccine_details'], list):
            return jsonify({'error': 'Invalid data type for vaccine details'}), 400

        if not isinstance(data['corona_virus_details']['positive_result'], dict):
            return jsonify({'error': 'Invalid data type for positive result'}), 400

        if len(data['corona_virus_details']['vaccine_details']) > 4:
            return jsonify({'error': 'Invalid amount of vaccines'}), 400

        if not len(data['corona_virus_details']['vaccine_details']):
            amount_not_vaccinated += 1

        for vaccine_detail in data['corona_virus_details']['vaccine_details']:
            if not isinstance(vaccine_detail, dict):
                return jsonify({'error': 'Invalid data type for vaccine detail'}), 400
            if not vaccine_detail.get('date_received') or not vaccine_detail.get('manufacturer'):
                return jsonify({'error': 'Missing required subfields in vaccine detail'}), 400
            # Check that the date_received field is a valid date string in the format YYYY-MM-DD
            try:
                date_received = datetime.datetime.strptime(vaccine_detail['date_received'], '%Y-%m-%d')
            except ValueError:
                return jsonify(
                    {
                        'error': 'Invalid date received (date_received should be a date string in the format YYYY-MM-DD)'}), 400

            if vaccine_detail['manufacturer'] not in vaccine_manufacturer:
                return jsonify({'error': 'Vaccine manufacturer is not exist'}), 400
        # sort the vaccine by dates
        data['corona_virus_details']['vaccine_details'].sort(key=lambda x: list(x.values())[0])
    else:
        amount_not_vaccinated +=1

    if data['corona_virus_details'].get('positive_result'):
        if data['corona_virus_details']['positive_result'].get('date_received'):
            # Check that the date_received field is a valid date string in the format YYYY-MM-DD
            try:
                date_received = datetime.datetime.strptime(
                    data['corona_virus_details']['positive_result']['date_received'], '%Y-%m-%d')
            except ValueError:
                return jsonify(
                    {
                        'error': 'Invalid date received (date_received should be a date string in the format YYYY-MM-DD)'}), 400

        if data['corona_virus_details']['positive_result'].get('recovery_date'):
            # Check that the recovery_date field is a valid date string in the format YYYY-MM-DD
            try:
                date_received = datetime.datetime.strptime(
                    data['corona_virus_details']['positive_result']['recovery_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify(
                    {
                        'error': 'Invalid recovery date (recovery_date should be a date string in the format YYYY-MM-DD)'}), 400
        if data['corona_virus_details']['positive_result'].get('date_received') and not data['corona_virus_details'][
            'positive_result'].get('recovery_date'):
            recovery_date = date_received + timedelta(days=recovery_time)
            data['corona_virus_details']['positive_result']['recovery_date'] = recovery_date.strftime("%Y-%m-%d")

    # Insert the document into the MongoDB collection
    result = collection.insert_one(data)

    # Return a JSON response with the ID of the inserted document
    return jsonify({'_id': str(result.inserted_id)}), 201

# Route for getting all documents from the collection
@app.route('/get_all', methods=['GET'])
def get_all_documents():
    # Find all the documents in the collection
    results = collection.find()

    # Convert the results to a list of dictionaries
    documents = []
    for result in results:
        document = {
            'first name': result['first_name'],
            'last name': result['last_name'],
            'id number': result['id_number'],
            'address': result['address'],
            'date of birth': result['date_of_birth'],
            'telephone': result['telephone'],
            'mobile phone': result['mobile_phone'],
            'corona virus details': result['corona_virus_details'],
        }
        documents.append(document)

    # Return the documents as a JSON response
    return jsonify(documents)


# Route for getting documents from the collection according id
@app.route('/get', methods=['GET'])
def get_documents():
    # Get the query parameter from the request URL
    id_number = request.args.get('id_number')

    # Create a query to find documents with the specified name
    query = {"id_number": id_number}

    # Find the documents in the collection
    results = collection.find(query)

    # Convert the results to a list of dictionaries
    documents = []
    for result in results:
        document = {
            'first name': result['first_name'],
            'last name': result['last_name'],
            'id number': result['id_number'],
            'address': result['address'],
            'date of birth': result['date_of_birth'],
            'telephone': result['telephone'],
            'mobile phone': result['mobile_phone'],
            'corona virus details': result['corona_virus_details'],

        }
        documents.append(document)
    if not len(documents):
        return jsonify({'error': 'id number not exists'}), 400

    # Return the documents as a JSON response
    return jsonify(documents)


if __name__ == '__main__':
    app.run(debug=True)
