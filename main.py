import json
from flask import Flask, render_template, request, flash, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
# Se utiliza para usar flash(), debe ser cambiada en un entorno de producción
app.secret_key = 'clave_secreta'

if __name__ == "__main__":
    app.run(debug=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cliente')
def cliente():
    return render_template('cliente.html')


@app.route('/banco')
def banco():
    return render_template('banco.html')


@app.route('/procesar-dni', methods=['POST'])
def procesar_dni():
    dni_ingresado = request.form['dni']

    # Cargar los datos del archivo JSON
    with open('clientes.json', 'r') as file:
        clientes = json.load(file)

    # Buscar el DNI ingresado en el archivo JSON
    for cliente in clientes:
        if cliente.get('dni') == dni_ingresado:
            nombre = cliente.get('nombre')
            apellido = cliente.get('apellido')
            mensaje = f"Bienvenido {nombre} {apellido}"
            return render_template('cliente.html', mensaje=mensaje)

    # Si no se encuentra el DNI, mostrar un mensaje de error
    session['dni'] = dni_ingresado
    mensaje_error = "Cliente no encontrado"
    return render_template('cliente.html', mensaje_error=mensaje_error)


@app.route('/nuevo-cliente', methods=['POST'])
def nuevo_cliente():
    dni_ingresado = session.get('dni')  # Obtener el DNI de la sesión

    nombre_ingresado = request.form['nombre']
    apellido_ingresado = request.form['apellido']
    fecha_nacimiento = request.form['edad']
    fecha_nacimiento_dt = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    fecha_actual = datetime.now()
    edad = fecha_actual.year - fecha_nacimiento_dt.year - \
        ((fecha_actual.month, fecha_actual.day) <
         (fecha_nacimiento_dt.month, fecha_nacimiento_dt.day))

    # Crear un nuevo diccionario para el nuevo cliente
    nuevo_cliente = {
        "dni": dni_ingresado,
        "nombre": nombre_ingresado,
        "apellido": apellido_ingresado,
        "edad": edad
    }

    # Abrir el archivo JSON y agregar el nuevo cliente
    with open('clientes.json', 'r+') as file:
        clientes = json.load(file)
        clientes.append(nuevo_cliente)
        file.seek(0)  # Colocar el puntero al inicio del archivo
        # Escribir los clientes actualizados en el archivo JSON
        json.dump(clientes, file, indent=4)

    # Mostrar el mensaje de confirmación
    mensaje = f"Felicidades {nombre_ingresado} {
        apellido_ingresado}, ya eres cliente del banco"
    return render_template('cliente.html', mensaje=mensaje)
