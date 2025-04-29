import requests

def obter_endereco(lat, lon):
    url = 'https://nominatim.openstreetmap.org/reverse'
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {
        'User-Agent': 'MinhaAplicacaoPython/1.0 (seu-email@exemplo.com)'  # obrigatório
    }

    response = requests.get(url, params=params, headers=headers)
    dados = response.json()

    if 'address' in dados:
        endereco = dados['address']
        rua = endereco.get('road', 'Rua não encontrada')
        return rua
    else:
        return 'Rua não encontrada'