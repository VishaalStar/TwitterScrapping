from flask import Flask, render_template_string, jsonify
from scraper import TwitterScraper
import os
from datetime import datetime

app = Flask(__name__)

# Initialize scraper with credentials
scraper = TwitterScraper(
    twitter_username=os.getenv('TWITTER_USERNAME'),
    twitter_password=os.getenv('TWITTER_PASSWORD'),
)

# HTML template with improved formatting
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Twitter Trends Scraper</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            line-height: 1.6;
        }
        .button {
            background-color: #1DA1F2;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 20px 0;
        }
        .results {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .json-data {
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        .trend-list {
            list-style-type: none;
            padding-left: 0;
        }
        .trend-list li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .trend-list li:last-child {
            border-bottom: none;
        }
        .ip-address {
            background-color: #e9ecef;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <h1>Twitter Trending Topics Scraper</h1>
    
    {% if not results %}
    <a href="/scrape" class="button">Click here to run the script</a>
    {% endif %}
    
    {% if results %}
    <div class="results">
        <h2>These are the most happening topics as on {{ results.timestamp }}</h2>
        <ul class="trend-list">
            <li>{{ results.nameoftrend1 }}</li>
            <li>{{ results.nameoftrend2 }}</li>
            <li>{{ results.nameoftrend3 }}</li>
            <li>{{ results.nameoftrend4 }}</li>
            <li>{{ results.nameoftrend5 }}</li>
        </ul>
        
        <p>The IP address used for this query was <span class="ip-address">{{ results.ip_address }}</span></p>
        
        <h3>JSON extract from MongoDB:</h3>
        <div class="json-data">{{ results | tojson(indent=2) }}</div>
        
        <a href="/" class="button">Click here to run the query again</a>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape')
def scrape():
    try:
        results = scraper.run_scraper()
        if not results:
            raise ValueError("No results returned from scraper")
        return render_template_string(HTML_TEMPLATE, results=results)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to scrape trending topics. Please try again."
        }), 500

if __name__ == '__main__':
    app.run(debug=True)