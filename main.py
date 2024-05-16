from flask import Flask, url_for, render_template, redirect, request, send_file
import random
import psycopg2
import psycopg2.extras
import pandas as pd

app = Flask(__name__)

DB_HOST = 'database-1.c7wkuk64cpv6.us-east-1.rds.amazonaws.com'
DB_NAME = 'procesosFinal'
DB_USER = 'postgres'
DB_PASS = 'Javeriana1299'

conn = psycopg2.connect(dbname=DB_NAME, user = DB_USER, password = DB_PASS, host = DB_HOST)
# Información
dron1 = ["50m", "Juan David Aycardi", 
		 "5 m/s", "documentos académicos de la facultad de ingeniería"]
dron2 = ["45m", "Jedemías Villarica",
		 "25 m/s", "comida de la cafetería, papas con queso y tocino"]
envio1 = ["4565", "Juan David Aycardi",
		  "documentos académicos", "Entrada Principal",
		  "formatos de despido para el profesor encargado de Sistemas Inteligentes"]
envio2 = ["6969", "Jedemías Villarica",
		  "comida de la cafetería, papas con queso y tocino", "Portería Cedro",
		  "Hambre"]
metros = 100	 

# Variables Globales
fallo = False
usuarios = {"messirve": "Luis"}
contrasenas = {"messirve": "1234"}
usuario_activo = ""

# Funciones Principales
@app.route("/")
def login():
    global fallo
    texto = ""
    if fallo:
        texto = "Por favor digite un usuario existente."
        fallo = False
    return render_template("login.html", content = texto)

@app.route('/reporteUsuario/descarga/excel')
def reporte():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM usuario")
    result = cur.fetchall()

    # Crear un DataFrame a partir de los resultados de la consulta
    df = pd.DataFrame(result, columns=[desc[0] for desc in cur.description])

    # Guardar el DataFrame como un archivo Excel
    ruta_archivo = "reporte_usuarios.xlsx"
    df.to_excel(ruta_archivo, index=False)

    return redirect(url_for('static', filename=ruta_archivo))

@app.route('/reporteReserva/descarga/excel')
def reporteReserva():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM reserva")
    result = cur.fetchall()

    # Crear un DataFrame a partir de los resultados de la consulta
    df = pd.DataFrame(result, columns=[desc[0] for desc in cur.description])

    # Guardar el DataFrame como un archivo Excel
    ruta_archivo = "reporte_reserva.xlsx"
    df.to_excel(ruta_archivo, index=False)

    return redirect(url_for('static', filename=ruta_archivo))

# Home
@app.route("/home", methods = ["GET", "POST"])
def home():
    global usuario_activo
    if request.method == 'POST':
        if 'usuario' in request.form:
            usuario = request.form["usuario"]
            if(usuario in usuarios): usuario_activo = usuarios[usuario]
        if all(item in request.form for item in ["nombre", "pedido", "lugar", "motivo"]):
            temp = []
            temp.append(request.form["nombre"])
            temp.append(request.form["pedido"])
            temp.append(request.form["lugar"])
            temp.append(request.form["motivo"])
            print("Pedido realizado: {}".format(temp))
    return render_template("home.html", usuario = usuario_activo)

# Drones
@app.route("/drones", methods = ["GET", "POST"])
def drones():
	return render_template("drones.html", usuario = usuario_activo)

@app.route("/drones/1", methods = ["GET", "POST"])
def dron_aumentado1():
	return render_template("dron_aumentado.html", usuario = usuario_activo, numero = "1",
												  info = dron1)

@app.route("/drones/2", methods = ["GET", "POST"])
def dron_aumentado2():
	return render_template("dron_aumentado.html", usuario = usuario_activo, numero = "2",
												  info = dron2)

# Reservas
@app.route("/reservas", methods = ["GET", "POST"])
def reservas():
	return render_template("reserva.html", usuario = usuario_activo)

@app.route("/reservaRegis", methods=["GET","POST"])
def registrar_reserva():
    if request.method == "POST":
        # Obtener los datos del formulario enviado por el usuario
        id_reserva = request.form.get("id")
        usuario_id = request.form.get("usuario_id")
        altura = request.form.get("altura")
        velocidad = request.form.get("velocidad")
        descripcion = request.form.get("descripcion")

        # Insertar los datos en la tabla reserva
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO reserva (id, usuario_id, altura, velocidadpro, descripcionencargo) VALUES (%s, %s, %s, %s, %s)",
                        (id_reserva, usuario_id, altura, velocidad, descripcion))
            conn.commit()
            mensaje = "La reserva se ha registrado correctamente."
        except Exception as e:
            conn.rollback()
            mensaje = f"Error al registrar la reserva: {str(e)}"

        # Renderizar la plantilla de respuesta
        return render_template("reservaRegis.html", mensaje=mensaje)


# Envios
@app.route("/envios", methods = ["GET", "POST"])
def envios():
	return render_template("envios.html", usuario = usuario_activo)

@app.route("/envios/4565", methods = ["GET", "POST"])
def envio_aumentado1():
	return render_template("envio_aumentado.html", usuario = usuario_activo, envio = envio1)

@app.route("/envios/6969", methods = ["GET", "POST"])
def envio_aumentado2():
	return render_template("envio_aumentado.html", usuario = usuario_activo, envio = envio2)

# Rutas
@app.route("/rutas", methods = ["GET", "POST"])
def rutas():
	return render_template("rutas.html", usuario = usuario_activo)

@app.route("/rutas/1", methods = ["GET", "POST"])
def ruta_aumentado():
	global metros
	if(metros >= 0): metros -= random.randint(1, 10)
	else: metros = 0
	return render_template("ruta_aumentado.html", usuario = usuario_activo, metros = metros)

if __name__ == "__main__":
	app.run(debug = True)