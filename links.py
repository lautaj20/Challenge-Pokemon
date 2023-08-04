from flask import Flask, render_template, jsonify, request
import requests
import random

app = Flask(__name__)

# Función para obtener el tipo de un Pokémon según su nombre
def get_pokemon_type(name):
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

# Ruta para obtener el tipo de un Pokémon según su nombre
@app.route('/pokemon/type', methods=['GET'])
def pokemon_type():
    name = request.args.get("name")

    if not name:
        name = input("Por favor, ingrese el nombre del Pokémon: ")

    return get_pokemon_type(name)

# Ruta para obtener un Pokémon al azar de un tipo específico
@app.route('/pokemon/random', methods=['GET'])
def random_pokemon_by_type():
    pokemon_type = request.args.get("type")

    if not pokemon_type:
        return jsonify({"error": "Debe proporcionar el tipo de Pokémon"}), 400

    # Hacemos una solicitud a la Poké API para obtener los Pokémon del tipo especificado
    url = f"https://pokeapi.co/api/v2/type/{pokemon_type.lower()}"
    response = requests.get(url)

    if response.status_code == 404:
        return jsonify({"error": "Tipo de Pokémon no encontrado"}), 404
    elif response.status_code != 200:
        return jsonify({"error": "Error al obtener los datos del tipo de Pokémon"}), response.status_code

    data = response.json()
    pokemon_list = data["pokemon"]
    
    # Obtenemos un Pokémon aleatorio del tipo específico
    random_pokemon = random.choice(pokemon_list)["pokemon"]["name"]

    return get_pokemon_type(random_pokemon)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_function = request.form['function']
        if selected_function == 'get_pokemon_type':
            name = request.form['pokemon_name']
            return get_pokemon_type(name)
        elif selected_function == 'random_pokemon_by_type':
            pokemon_type = request.form['pokemon_type']
            # ... código para obtener un Pokémon al azar de un tipo específico ...
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
