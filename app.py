from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import uuid
import os

from dotenv import load_dotenv
from boto3.dynamodb.conditions import Attr
import boto3

# Load environment variables
load_dotenv()

# Flask App Setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fleetsync_secret_key_2024")

# AWS Configuration
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME", "us-east-1")

# Email Configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
ENABLE_EMAIL = os.environ.get("ENABLE_EMAIL", "false").lower() == "true"

# Table Names from Environment
USERS_TABLE_NAME = os.environ.get("USERS_TABLE_NAME", "FleetSyncUsers")
VEHICLES_TABLE_NAME = os.environ.get("VEHICLES_TABLE_NAME", "FleetSyncVehicles")
MAINTENANCE_TABLE_NAME = os.environ.get("MAINTENANCE_TABLE_NAME", "FleetSyncMaintenance")
TRIPS_TABLE_NAME = os.environ.get("TRIPS_TABLE_NAME", "FleetSyncTrips")

# Initialize DynamoDB Resource
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION_NAME)

# Connect to Users Table
users_table = dynamodb.Table(USERS_TABLE_NAME)

# Route: Home
@app.route('/')
def index():
    return render_template("index.html")

# Route: Register User
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        if not name or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for('register'))

        try:
            # Insert user into DynamoDB
            users_table.put_item(
                Item={
                    'email': email,
                    'name': name
                }
            )
            flash("User registered successfully!", "success")
        except Exception as e:
            flash(f"Error inserting into DynamoDB: {str(e)}", "danger")

        return redirect(url_for('register'))

    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)