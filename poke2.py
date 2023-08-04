from flask import Flask, jsonify, request, render_template, session, redirect
import requests
import random
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate  # Importamos Flask-Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)  # Inicializamos Flask-Migrate con la aplicación y la base de datos


# Modelo de datos para la tabla de usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)  # Agregamos la columna password_hash

    def __repr__(self):
        return f'<User {self.username}>'

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

# Ruta para el registro de usuarios y la página de inicio
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

    # Si el usuario no está autenticado, redirigir a la página de registro
    if 'authenticated' not in session:
        return redirect('/register')

    # ... (resto del código de autenticación)

    # Código HTML para el menú y formulario
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API de Pokémon</title>
    </head>
    <body>
        <h1>API de Pokémon</h1>
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
    </body>
    </html>
    '''

# Ruta para el registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({"error": "Nombre de usuario y contraseña requeridos"}), 400

        if username == 'Adminml' and password == 'desafio':  # Usuario y contraseña predefinidos
            session['authenticated'] = True
            return redirect('/')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['authenticated'] = True
        return redirect('/')

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registro de Usuarios</title>
    </head>
    <body>
        <h1>Registro de Usuarios</h1>
        <form action="/register" method="post">
            <label for="username">Nombre de usuario:</label>
            <input type="text" id="username" name="username" required>
            <br>
            <label for="password">Contraseña:</label>
            <input type="password" id="password" name="password" required>
            <br>
            <input type="submit" value="Registrarse">
        </form>
    </body>
    </html>
    '''


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
