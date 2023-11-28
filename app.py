import json
from flask import Flask, render_template, request, url_for, flash, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
# Se utiliza para usar flash(), debe ser cambiada en un entorno de producción
app.secret_key = 'clave_secreta'

if __name__ == "__app__":
    app.run(debug=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cliente')
def cliente():
    return render_template('cliente.html')


@app.route('/nuevoCliente')
def nuevoCliente():
    return render_template('nuevoCliente.html')


@app.route('/banco')
def banco():
    return render_template('banco.html')


@app.route('/procesar-dni', methods=['POST'])
def procesar_dni():
    dni_ingresado = request.form['dni']
    session['dni'] = dni_ingresado
    # Cargar los datos del archivo JSON
    with open('clientes.json', 'r') as file:
        clientes = json.load(file)

    # Buscar el DNI ingresado en el archivo JSON
    cliente_encontrado = None
    for cliente in clientes:
        if cliente.get('dni') == dni_ingresado:
            cliente_encontrado = cliente
            break

    if cliente_encontrado:
        nombre = cliente_encontrado.get('nombre')
        apellido = cliente_encontrado.get('apellido')
        mensaje = f"Bienvenido {nombre} {apellido}"
        return render_template('turnos.html', mensaje=mensaje, dni=dni_ingresado)
    else:
        return render_template('nuevoCliente.html', dni=dni_ingresado)


@app.route('/nuevo-cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    dni_ingresado = session.get('dni')
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
    return render_template('turnos.html', mensaje=mensaje, dni=dni_ingresado)


@app.route('/crear-turno', methods=['POST'])
def crear_turno():
    eleccion = request.form.get('elegir')
    dni_ingresado = session.get('dni')

    # Cargar los datos del archivo JSON 'clientes.json'
    with open('clientes.json', 'r') as file:
        clientes = json.load(file)

    nombre = ""
    apellido = ""

    # Buscar el cliente por su DNI en 'clientes.json'
    for clientes in clientes:
        if str(clientes.get('dni')) == dni_ingresado:
            nombre = clientes.get('nombre')
            apellido = clientes.get('apellido')
            break

    numero_turno = generar_numero_turno(eleccion)

    nuevo_turno = {
        "Numero": numero_turno,
        "Nombre": nombre,
        "Apellido": apellido,
    }

    try:
        with open('turnos.json', 'r') as file:
            turnos = json.load(file)
    except FileNotFoundError:
        turnos = {}

    if eleccion not in turnos:
        turnos[eleccion] = []

    turnos[eleccion].append(nuevo_turno)

    with open('turnos.json', 'w') as file:
        json.dump(turnos, file, indent=4)

    turnoAgregado = f"Nuevo turno agregado correctamente, su turno es {
        numero_turno}"
    return render_template('index.html', mensaje=turnoAgregado)

    session.pop('dni', None)


def generar_numero_turno(servicio):
    with open('turnos.json', 'r') as file:
        data = json.load(file)

        # Verificar si el servicio existe en los datos
        if servicio in data:
            # Obtener la lista de turnos para el servicio dado
            turnos_servicio = data[servicio]

            # Verificar si hay turnos para ese servicio
            if turnos_servicio:
                # Obtener el número más alto de turno para el servicio dado
                numeros_turno = [int(turno['Numero'][1:])
                                 for turno in turnos_servicio]
                ultimo_numero = max(numeros_turno)

                # Generar el nuevo número de turno sumando 1 al número más alto
                nuevo_numero = f"{servicio[0]}{ultimo_numero + 1:03}"
                return nuevo_numero
            else:
                # Si no hay turnos para ese servicio, empezar desde 1
                return f"{servicio[0]}001"
        else:
            # Si el servicio no está en los datos
            return "Servicio no encontrado en los turnos existentes"
