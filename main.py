from flask import Flask, url_for, render_template, redirect, request, send_file
import random
import psycopg2
import psycopg2.extras
import pandas as pd
import boto3

import logging

app = Flask(__name__)

DB_HOST = 'database-1.c7wkuk64cpv6.us-east-1.rds.amazonaws.com'
DB_NAME = 'procesosFinal'
DB_USER = 'postgres'
DB_PASS = 'Javeriana1299'

ubi = ["Bodega","Bodega","Bodega","Bodega"]
conn = psycopg2.connect(dbname=DB_NAME, user = DB_USER, password = DB_PASS, host = DB_HOST)
int1 = ["Reparacion, 01/06/2024, Ing Stefania: Cambio de aspa por rotura",
		"Actualización 16/05/2024, Ing Juan Jose: ajustes de seguridad"]
int2 = ["Reparacion 02/03/2024, Ing Johan: Cambio de aspa por rotura",
		"Reparacion 18/03/2024, Ing Crhistian: Cambio de camara"]
int3 = ["Reparacion 02/03/2024, Ing Johan: Cambio de llanta"]
int4 = ["No hay mantenimientos hasta el momento"]
# Información
dron1 = ["50m", "1", 
            "15 m/s", "Dron de color plateado,rapido, para carga liviana,camara 4k","Dron",ubi[0]]

dron2 = ["45m", "2",
            "5 m/s", "Dron de color blanco,velocidad moderada, para carga liviana,camara 2k","Dron",ubi[1]]

robot1 = ["0", "3",
            "2.7 m/s", "Robot de color negro, velocidad baja, semi-autonomo","Robot",ubi[2]]

robot2 = ["0", "4",
            "3.5 m/s", "Robot de color blanco y negro, velocidad media, semi-autonomo","Robot",ubi[3]]

envio1 = ["4565", "Kafeliest",
		  "documentos académicos", "Entrada Principal",
		  "formatos de despido para el profesor encargado de Sistemas Inteligentes"]
envio2 = ["6969", "Juan Marin",
		  "comida de la cafetería, papas con queso y tocino", "Portería Cedro",
		  "Hambre"]
metros = 100	 

# Variables Globales
fallo = False
usuarios = {"messirve": "Stefania"}
contrasenas = {"messirve": "1234"}
usuario_activo = ""
s3 = boto3.client('s3',
                  region_name='us-east-1',
                  aws_access_key_id='stefania-at-339712777431',
                  aws_secret_access_key='GAKnVNsDCxeptfBsIEXD8LfrK/lSAveBde8jW7ibfVF0j6cirVqEVgM10Mk=')

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

    return send_file('reporte_usuarios.xlsx', as_attachment=True)

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

    return send_file('reporte_reserva.xlsx', as_attachment=True)

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

# Drones
@app.route("/drones", methods = ["GET", "POST"])
def drones():

	return render_template("drones.html", usuario = usuario_activo)

@app.route("/drones/1", methods = ["GET", "POST"])
def dron_aumentado1():
	
	return render_template("dron_aumentado.html", usuario = usuario_activo, numero = "1",
												  info = dron1,mant =int1 )

@app.route("/drones/2", methods = ["GET", "POST"])
def dron_aumentado2():
	return render_template("dron_aumentado.html", usuario = usuario_activo, numero = "2",
												  info = dron2,mant =int2)

@app.route("/drones/3", methods = ["GET", "POST"])
def dron_aumentado3():
	return render_template("dron_aumentado.html", usuario = usuario_activo, numero = "3",
												  info = robot1,mant =int3)
@app.route("/drones/4", methods = ["GET", "POST"])
def dron_aumentado4():
	return render_template("dron_aumentado.html", usuario = usuario_activo, numero = "4",
												  info = robot2,mant = int4)

# Reservas
@app.route("/reservas", methods = ["GET", "POST"])
def reservas():
	return render_template("reserva.html", usuario = usuario_activo)

@app.route("/reservaRegis", methods=["GET", "POST"])
def registrar_reserva():
    if request.method == "POST":
        # Obtener los datos del formulario enviado por el usuario
        id_reserva = request.form.get("id_reserva")
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
        finally:
            cur.close()

        # Renderizar la plantilla de respuesta
        return render_template("reserva.html", mensaje=mensaje)

    # Si no es una solicitud POST, solo renderizar la plantilla de formulario
    return render_template("reserva.html")


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

'''@app.route("/reservaRegis", methods = ["GET", "POST"])
def reservas1():
    lugares = { '0': "Entrada Central", '1':"Portería Acacias", '2':"Portería Lago", '3':"Portería Cedro" }
    if request.method == 'POST':
        if all(item in request.form for item in ["nombre", "pedido", "lugar", "motivo"]):
            temp = []
            temp.append(request.form["nombre"])
            temp.append(request.form["pedido"])
            temp.append(lugares[request.form["lugar"]]) 
            temp.append(request.form["motivo"])
            print("Pedido realizado: {}".format(temp))

            # Escribe los datos del formulario en un archivo
            with open('reservas.txt', 'a') as f:
                f.write(str(temp) + '\n')

            # Carga el archivo en tu bucket de S3
            try:
                with open('reservas.txt', 'rb') as data:
                    s3.upload_fileobj(data, 's3procesos', 'reservas.txt')
                logging.info('Archivo reservas.txt cargado correctamente en S3')
            except Exception as e:
                logging.error('Error al cargar el archivo en S3: {}'.format(e))

    return render_template("reserva.html", usuario = usuario_activo)'''

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