import httpx
from typing import Dict


async def classificar_zona(lat:float, lon:float, raio:float=200) -> str:
    query = f"""
    [out:json];
    (
    way(around:{raio},{lat},{lon})["landuse"];
    relation(around:{raio},{lat},{lon})["landuse"];
    );
    out tags center;
    """
    url = "https://overpass-api.de/api/interpreter"

    if raio > 1000: return 'desconhecida'
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, data={'data': query})
            data = response.json()

            if data['elements']:
                landuse_tags = [elem['tags'].get('landuse') for elem in data['elements'] if 'tags' in elem and 'landuse' in elem['tags']]
                if landuse_tags: return landuse_tags[0]

            return await classificar_zona(lat, lon, raio + 50)
        
        except Exception as e:
            return await classificar_zona(lat, lon, raio + 50)


async def obter_endereco(lat:float, lon:float) -> tuple[str, str]:
    url = 'https://nominatim.openstreetmap.org/reverse'
    params:Dict[str, float | str] = {	
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {
        'User-Agent': 'MinhaAplicacaoPython/1.0 (seu-email@exemplo.com)'  # obrigatório
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            dados = response.json()

            if 'address' in dados:
                endereco = dados['address']
                rua = endereco.get('road', 'Rua não encontrada')
                tipo_zona = await classificar_zona(lat, lon)
                return rua, tipo_zona
            else:
                return 'Rua não encontrada', 'desconhecida'
            
        except Exception as e:
            return 'Rua não encontrada', 'desconhecida'