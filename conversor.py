import os
import time
import hashlib
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DEFAULT_APP_ID = os.environ.get("SHOPEE_APP_ID", "18358780307")
DEFAULT_SECRET = os.environ.get("SHOPEE_SECRET", "KYCQECZPABRWOGUKD7R3SURIKMDYYJAU")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def api_convert():
    data = request.json or {}
    origin_url = data.get('url', '').strip()
    
    app_id = DEFAULT_APP_ID
    secret = DEFAULT_SECRET

    if not origin_url:
        return jsonify({'success': False, 'error': 'URL não informada.'}), 400

    try:
        short_link, product_name = gerar_link_shopee_api(origin_url, app_id, secret)
        return jsonify({
            'success': True, 
            'convertedUrl': short_link, 
            'productName': product_name if product_name else "PRODUTO SHOPEE",
            'method': 'API GraphQL Oficial (Python Backend)'
        })
    except Exception as e:
        fallback_url = construir_fallback(origin_url, app_id)
        return jsonify({
            'success': True, 
            'convertedUrl': fallback_url, 
            'productName': "PRODUTO SHOPEE",
            'method': 'Fallback Inteligente (Universal Tag)'
        })

def gerar_link_shopee_api(origin_url, app_id, secret):
    endpoint = "https://open-api.affiliate.shopee.com.br/graphql"
    timestamp = int(time.time())
    
    # Mutação GraphQL solicitando o link curto e opcionalmente metadados se suportado pela API
    payload_body = f'{{"query": "mutation {{ generateShortLink(input: {{ originUrl: \\"{origin_url}\\" }}) {{ shortLink }} }}"}}'
    
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
            short_link = res_data['data']['generateShortLink']['shortLink']
            
            # Tentativa de extrair o nome do produto da URL original para exibição amigável caso a API não retorne o título direto
            parsed_name = "PRODUTO SHOPEE"
            if "shopee.com.br/" in origin_url:
                parts = origin_url.split("shopee.com.br/")
                if len(parts) > 1:
                    path_part = parts[1].split("?")[0]
                    clean_name = path_part.split("-i.")[0].replace("-", " ").strip()
                    if clean_name:
                        parsed_name = clean_name.upper()

            return short_link, parsed_name
            
    raise Exception(f"Erro na resposta da API GraphQL: {response.text}")

def construir_fallback(url, app_id):
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}utm_source=an_${app_id}&af_siteid={app_id}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
