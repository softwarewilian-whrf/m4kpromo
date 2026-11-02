import time
import hashlib
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Credenciais oficiais da Shopee
DEFAULT_APP_ID = "18358780307"
DEFAULT_SECRET = "KYCQECZPABRWOGUKD7R3SURIKMDYYJAU"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def api_convert():
    data = request.json or {}
    origin_url = data.get('url', '').strip()
    sub_id = data.get('subId', '').strip()
    
    app_id = data.get('appId', '').strip() or DEFAULT_APP_ID
    secret = data.get('secret', '').strip() or DEFAULT_SECRET

    if not origin_url:
        return jsonify({'success': False, 'error': 'URL não informada.'}), 400

    try:
        short_link = gerar_link_shopee_api(origin_url, sub_id, app_id, secret)
        return jsonify({'success': True, 'convertedUrl': short_link, 'method': 'API GraphQL Oficial (Python Backend)'})
    except Exception as e:
        fallback_url = construir_fallback(origin_url, sub_id, app_id)
        return jsonify({'success': True, 'convertedUrl': fallback_url, 'method': 'Fallback Inteligente (Universal Tag)'})

def gerar_link_shopee_api(origin_url, sub_id, app_id, secret):
    endpoint = "https://open-api.affiliate.shopee.com.br/graphql"
    timestamp = int(time.time())
    
    sub_ids_str = f', subIds: ["{sub_id}"]' if sub_id else ''
    payload_body = f'{{"query": "mutation {{ generateShortLink(input: {{ originUrl: \\"{origin_url}\\"{sub_ids_str} }}) {{ shortLink }} }}"}}'
    
    factor = f"{app_id}{timestamp}{payload_body}{secret}"
    signature = hashlib.sha256(factor.encode('utf-8')).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}'
    }
    
    response = requests.post(endpoint, headers=headers, data=payload_body, timeout=10)
    if response.status_code == 200:
        res_data = response.json()
        if 'data' in res_data and res_data['data'] and res_data['data']['generateShortLink']:
            return res_data['data']['generateShortLink']['shortLink']
    
    raise Exception(f"Erro na resposta da API GraphQL: {response.text}")

def construir_fallback(url, sub_id, app_id):
    separator = '&' if '?' in url else '?'
    sub_param = f"&sub_id={sub_id}" if sub_id else ""
    return f"{url}{separator}utm_source=an_{app_id}&af_siteid={app_id}{sub_param}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)