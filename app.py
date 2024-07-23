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
        page = request.args.get('page', 1, type=int)
        per_page = 20
        skip = (page - 1) * per_page

        sort_by = request.args.get('sort', 'ID')
        order = request.args.get('order', 'asc')
        sort_order = 1 if order == 'asc' else -1

        records = list(collection.find().sort(sort_by, sort_order).skip(skip).limit(per_page))
        total_records = collection.count_documents({})
        total_pages = (total_records // per_page) + 1

        # Determine the range of pages to display
        start_page = max(1, page - 1)
        end_page = min(total_pages, start_page + 2)
        if end_page - start_page < 2:
            start_page = max(1, end_page - 2)

        return render_template(
            'index.html',
            records=records,
            page=page,
            per_page=per_page,
            total_records=total_records,
            sort_by=sort_by,
            order=order,
            total_pages=total_pages,
            start_page=start_page,
            end_page=end_page
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

        question_url = f"{source}/{range_str}/{id_str}.{title_str}/README_EN.md"
        solution_url = f"{source}/{range_str}/{id_str}.{title_str}/Solution.sql"

        question_response = requests.get(question_url)
        solution_response = requests.get(solution_url)

        if question_response.status_code == 200 and solution_response.status_code == 200:
            readme_content = question_response.text
            solution_content = solution_response.text

            split_content = readme_content.split("## Solutions")[0]
            question_content = split_content.split("## Description")[1]
            return render_template('index.html', question_content=question_content, solution_content=solution_content, item=document)
        else:
            return f"Failed to retrieve the Leetcode Problem. Status code: {question_response.status_code if question_response.status_code != 200 else solution_response.status_code}"
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
