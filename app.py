from tkinter.tix import FileSelectBox
from flask import Flask, jsonify, render_template, request, redirect, send_file
from models import db, datitos, marcaciones
from logging import exception
import sqlalchemy as based
import datetime

app = Flask(__name__)

#COFIGURAMOS EL ACCESO A LA BASE DE DATOS
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///databases/datitos.db" #Direccion abs en linux
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

#CONFIGURAMOS LA RUTA PARA INDEX
@app.route("/")
def home():
    return render_template("index.html") #renderiza la pagina index.html que contiene el formulario que redirige a /api/agregardatos

# Recibimos los datos desde index para agregar los datos principales a la base de datos y redirigimos a /bienvenido? y como parametro el nombre del usuario.
#Obs: No está validando que ya exista el dato antes de cargar de vuelta
@app.route("/api/agregardatos", methods=["POST"])
def addPersona():
    try:
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        deitaim = datetime.datetime.now()
        fecha = deitaim.strftime("%d-%m-%Y")
        hora = deitaim.strftime("%H:%M:%S")
        numero = request.form["numero"]
        persona = datitos(nombre, apellido, fecha, hora, numero)
        db.session.add(persona)
        db.session.commit()

        return redirect('/bienvenido?nombre='+nombre)
    except Exception as k:
        print(k)
        exception("[SERVER]: Error in route  /api/addPersona, Log: \n")
        return jsonify({"msg": "Algo ha salido mal"}),500

#Se renderiza la página de bienvenido al usuario que se registra por primera vez
@app.route("/bienvenido", methods=["GET"])
def bienvenido():
        namePersona = request.args["nombre"]
        datos = {}
        datos["perfil"] = datitos.query.filter_by(nombre=namePersona).first()
        return render_template("bienvenido.html", data=namePersona)


#Se renderiza la pagina de Registro de Entrada y recibe el dato de numero de ID del usuario y envia a /api/search4per para buscarlo en la base de datos.
@app.route("/registro_ent", methods=["GET"])
def registro_ent():
    return render_template("registro_participantes.html")

#La siguiente funcion verifica la tabla datitos por la persona que fue ingresada en el menu anterior y si existe registro lo devuelve en gracias.html "Gracias por volver a Penguin" + el nombre de la persona y agrega el registro de entrada a la tabla marcaciones.
@app.route("/api/search4per", methods=["POST", "GET"])
def search4per():
    try:
        numeroPersona = request.form["numero"]

        db.session.commit()
        datox = datitos.query.filter(datitos.numero.like(f"%{numeroPersona}%")).first()
        if not datox:
            return jsonify({"msg": "Esta persona no existe"}),200
        else:
            deitaim = datetime.datetime.now()
            fecha = deitaim.strftime("%d-%m-%Y")
            hora = deitaim.strftime("%H:%M:%S")
            persona = marcaciones(fecha, hora, numeroPersona)
            db.session.add(persona)
            db.session.commit()
            filter = datitos.query.filter_by(numero=numeroPersona)
            toReturn = [datox.serialize() for datox in filter]
            return render_template("gracias.html", data=toReturn[0]["nombre"])

    except Exception:
        exception("[SERVER]: Error in route api/search4per")
        return jsonify({"msg": "Ha ocurrido un error"}),500

#Con la siguiente funcion se renderiza la pagina de busqueda de registros por numero ID de usuario y realiza la consulta a la funcion /api/buscar 
@app.route("/busqueda", methods=["POST", "GET"])
def busqueda():
    return render_template("buscar.html")

#Aca realiza la busqueda en la tabla marcaciones teniendo el cuenta numeroID y devuelve los registros de entrada y salida de la persona.
@app.route("/api/buscar", methods=["POST", "GET"])
def buscar():
    try:
        numeroPersona = request.form["numero"]
        datox = marcaciones.query.filter(marcaciones.numero.like(f"%{numeroPersona}%"))
        if not datox:
            return jsonify({"msg": "Esta persona no existe"}),200
        else:
            filter = marcaciones.query.filter_by(numero=numeroPersona).all()
            return render_template("resultado_busqueda.html", data=filter)

    except Exception:
        exception("[SERVER]: Error in route api/search4per")
        return jsonify({"msg": "Ha ocurrido un error"}),500


#ACA ESTE COSO ES DE PRUEBA Y ME SIRVE PARA AGARRAR LOS DATOS QUE NECESITAMOS DE LA BASE DE DATOS Y LO CONVERTIRLO A JSON
@app.route("/api/datitos", methods=["GET"]) #get porque solo queremos hacer lectura de datos
def getDatitos():
    try:
        datitoz = datitos.query.all()
        toReturn = [datox.serialize() for datox in datitoz]
        solo_numeros = []
        fecha_y_hora = []
        extraccion = marcaciones.query.all()
        for dato in extraccion:
            fecha_y_hora.append({dato.numero : [dato.fecha, dato.hora]})
            # for dict in fecha_y_hora:
            #     for iterador in dict:
            #         print(iterador)
        for i in range(3):
            for i in datitoz:
                solo_numeros.append(i.numero)
        return jsonify({ "fecha_y_hora": fecha_y_hora})
    except Exception:
        exception("[SERVER]: Error->")
        return jsonify({"msg": "Ha ocurrido un error"}),500

#Aca en teoria va a ir lo que la funcion de arriba de aca me va a devolver. O sea, usar la API que está acá, convertirlo en Pandas, crear un xlsx y luego crear un link desde el cual se puedan descargar los registros seleccionados. Yokc como, capaz tenga que usar dos inputs type date.

@app.route("/descargar", methods=["POST", "GET"])
def descargar():
    path = "camioncito.png"
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True,port=4000)
