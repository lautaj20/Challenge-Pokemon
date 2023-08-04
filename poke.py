from flask import Flask, jsonify, request, render_template
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

# Función para obtener un Pokémon al azar de un tipo específico
def get_random_pokemon_by_type(pokemon_type):
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

# Función para obtener el Pokémon con el nombre más largo de cierto tipo
def get_longest_name_pokemon_by_type(pokemon_type):
    # Hacemos una solicitud a la Poké API para obtener los Pokémon del tipo especificado
    url = f"https://pokeapi.co/api/v2/type/{pokemon_type.lower()}"
    response = requests.get(url)

    if response.status_code == 404:
        return jsonify({"error": "Tipo de Pokémon no encontrado"}), 404
    elif response.status_code != 200:
        return jsonify({"error": "Error al obtener los datos del tipo de Pokémon"}), response.status_code

    data = response.json()
    pokemon_list = data["pokemon"]

    # Buscamos el Pokémon con el nombre más largo en la lista
    longest_name_pokemon = max(pokemon_list, key=lambda p: len(p["pokemon"]["name"]))
    longest_name = longest_name_pokemon["pokemon"]["name"]

    return get_pokemon_type(longest_name)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_function = request.form['function']
        if selected_function == 'get_pokemon_type':
            name = request.form['pokemon_name']
            return get_pokemon_type(name)
        elif selected_function == 'random_pokemon_by_type':
            pokemon_type = request.form['pokemon_type']
            return get_random_pokemon_by_type(pokemon_type)
        elif selected_function == 'longest_name_pokemon_by_type':
            pokemon_type = request.form['pokemon_type']
            return get_longest_name_pokemon_by_type(pokemon_type)
    return '''
    <form action="/" method="post">
        <label for="function">Elige una función:</label>
        <select id="function" name="function">
            <option value="get_pokemon_type">Obtener el tipo de un Pokémon por su nombre</option>
            <option value="random_pokemon_by_type">Obtener un Pokémon al azar de un tipo específico</option>
            <option value="longest_name_pokemon_by_type">Obtener el Pokémon con nombre más largo de cierto tipo</option>
        </select>
        <br>
        <div id="name_input" style="display:none;">
            <label for="pokemon_name">Nombre del Pokémon:</label>
            <input type="text" id="pokemon_name" name="pokemon_name">
            <br>
        </div>
        <div id="type_input" style="display:none;">
            <label for="pokemon_type">Tipo de Pokémon:</label>
            <input type="text" id="pokemon_type" name="pokemon_type">
            <br>
        </div>
        <input type="submit" value="Enviar">
    </form>

    <script>
        const functionSelect = document.getElementById("function");
        const nameInput = document.getElementById("name_input");
        const typeInput = document.getElementById("type_input");

        functionSelect.addEventListener("change", function() {
            const selectedFunction = functionSelect.value;

            if (selectedFunction === "get_pokemon_type") {
                nameInput.style.display = "block";
                typeInput.style.display = "none";
            } else if (selectedFunction === "random_pokemon_by_type" || selectedFunction === "longest_name_pokemon_by_type") {
                nameInput.style.display = "none";
                typeInput.style.display = "block";
            }
        });
    </script>
    '''

if __name__ == '__main__':
    app.run(debug=True)
