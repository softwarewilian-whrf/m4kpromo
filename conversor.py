import os
import time
import hashlib
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Lê do Render se existir, caso contrário usa o padrão/fallback
DEFAULT_APP_ID = os.environ.get("SHOPEE_APP_ID", "18358780307")
DEFAULT_SECRET = os.environ.get("SHOPEE_SECRET", "KYCQECZPABRWOGUKD7R3SURIKMDYYJAU")