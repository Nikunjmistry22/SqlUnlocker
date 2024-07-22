from flask import Flask, render_template, request, url_for
import requests
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION")
source = os.getenv("SOURCE")

client = MongoClient(uri)
db = client[db_name]
collection = db[collection_name]

app = Flask(__name__, template_folder='template', static_folder='static')


def get_range(number):
    start = (number // 100) * 100
    end = start + 99
    return f"{start:04d}-{end:04d}"


@app.route('/')
def index():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Number of items per page
        skip = (page - 1) * per_page

        # Sorting parameters
        sort_by = request.args.get('sort', 'ID')
        order = request.args.get('order', 'asc')
        sort_order = 1 if order == 'asc' else -1

        # Fetch records with pagination and sorting
        records = list(collection.find().sort(sort_by, sort_order).skip(skip).limit(per_page))
        total_records = collection.count_documents({})

        return render_template(
            'index.html',
            records=records,
            page=page,
            per_page=per_page,
            total_records=total_records,
            sort_by=sort_by,
            order=order
        )
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/<int:id>', methods=["GET"])
def element(id):
    try:
        document = collection.find_one({'ID': id})
        if document is None:
            return "Item not found", 404

        id_str = f"{document['ID']:04d}"
        title_str = document['Title'].replace(" ", "%20")
        range_str = get_range(document['ID'])

        url = f"{source}/{range_str}/{id_str}.{title_str}/README_EN.md"

        response = requests.get(url)
        if response.status_code == 200:
            readme_content = response.text
            split_content = readme_content.split("## Solutions")[0]
            current_content = split_content.split("## Description")[1]
            return render_template('index.html', content=current_content, item=document)
        else:
            return f"Failed to retrieve the Leetcode Problem. Status code: {response.status_code}"
    except Exception as e:
        return f"Error: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
