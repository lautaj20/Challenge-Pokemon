from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Ruta para obtener el tipo de un Pokémon según su nombre
@app.route('/pokemon/type', methods=['GET'])
def get_pokemon_type():
    # Obtenemos el nombre del Pokémon desde el parámetro 'name' en la URL
    name = request.args.get("name")

    if not name:
        return jsonify({"error": "Debe proporcionar el nombre del Pokémon"}), 400

    # Hacemos una solicitud a la Poké API para obtener los detalles del Pokémon
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)

    if response.status_code == 404:
        return jsonify({"error": "Pokémon no encontrado"}), 404
    elif response.status_code != 200:
        return jsonify({"error": "Error al obtener los datos del Pokémon"}), response.status_code

    # Extraemos el tipo del Pokémon de la respuesta de la Poké API
    data = response.json()
    types = [t["type"]["name"] for t in data["types"]]
    
    return jsonify({"name": name, "types": types})

if __name__ == '__main__':
    app.run(debug=True)


