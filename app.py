import os
import random
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'clave_secreta_rapunzel'

# Base de datos
DATABASE = 'banco_preguntas.db'

def obtener_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Frases para los personajes
frases_rapunzel = [
    "¡Sé que puedes lograrlo! Sigue adelante. ☀️",
    "¡El conocimiento es la llave para salir de la torre! 🔑",
    "¡No te rindas! Cada pregunta te acerca más a tu sueño. 🌸",
    "¿Sabías que el cabello de Rapunzel mide 21 metros? ¡Como tu inteligencia! ✨"
]

curiosidades_flynn = [
    "Flynn Rider en realidad se llama Eugene Fitzherbert. 🤫",
    "¡Cuidado con la nariz en los carteles! 👃",
    "A veces un sartenazo es la mejor defensa. 🍳",
    "Maximus el caballo es más detective que los guardias reales. 🐴"
]

@app.route('/')
def inicio():
    # Reiniciamos sesión para un juego nuevo
    session['total'] = 0
    session['aciertos'] = 0
    session['modo'] = 'normal'
    
    aparece_rapunzel = random.choice([True, False])
    
    if aparece_rapunzel:
        personaje = "rapunzel"
        imagen = "rapunzel_colgada.png"
        mensaje = random.choice(frases_rapunzel)
    else:
        personaje = "flynn"
        imagen = "flynn.png"
        mensaje = random.choice(curiosidades_flynn)
        
    session['personaje_actual'] = personaje
    session['imagen_personaje'] = imagen
    session['mensaje_actual'] = mensaje
    
    return render_template('index.html', 
                           personaje_actual=personaje, 
                           imagen_personaje=imagen, 
                           mensaje_actual=mensaje)

@app.route('/iniciar_examen')
def iniciar_examen():
    session['total'] = 0
    session['aciertos'] = 0
    session['modo'] = 'torre'
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'total' not in session:
        session['total'] = 0
        session['aciertos'] = 0
        session['modo'] = 'normal'

    mensaje_feedback = None
    es_correcta = False
    motivacion_pascal = None

    if request.method == 'POST':
        respuesta_usuario = request.form.get('respuesta')
        respuesta_correcta = request.form.get('correcta')
        
        session['total'] += 1
        
        if respuesta_usuario == respuesta_correcta:
            session['aciertos'] += 1
            mensaje_feedback = "¡Correcto! Sigue así. 👏"
            es_correcta = True
        else:
            mensaje_feedback = f"❌ Incorrecto. La respuesta correcta era la opción que contenía: {respuesta_correcta}"
            es_correcta = False

        # Si es modo Torre y llegó a 30, va a resultados
        if session.get('modo') == 'torre' and session['total'] >= 30:
            return redirect(url_for('resultado'))

    # Traer una pregunta aleatoria de la base de datos
    db = obtener_db()
    pregunta = db.execute('SELECT * FROM preguntas ORDER BY RANDOM() LIMIT 1').fetchone()
    db.close()

    if not pregunta:
        return "No hay preguntas en la base de datos.", 500

    enunciado = pregunta['enunciado']
    
    # 🎲 EL TRUCO PARA REVOLVER LAS OPCIONES:
    # Creamos una lista con las opciones y su letra original
    opciones = [
        {'texto': pregunta['opcion_a'], 'id': 'a'},
        {'texto': pregunta['opcion_b'], 'id': 'b'},
        {'texto': pregunta['opcion_c'], 'id': 'c'},
        {'texto': pregunta['opcion_d'], 'id': 'd'}
    ]
    
    # Las mezclamos al azar
    random.shuffle(opciones)
    
    # Buscamos cuál de las mezcladas es la correcta de verdad
    letra_correcta_original = pregunta['respuesta_correcta'].lower().strip()
    valor_correcto_real = ""
    for op in opciones:
        if op['id'] == letra_correcta_original:
            valor_correcto_real = op['texto']

    # Aparece Pascal cada 10 preguntas
    if session['total'] > 0 and session['total'] % 10 == 0:
        motivacion_pascal = "¡Pascal dice que te concentres! 🦎💚"

    return render_template('quiz.html',
                           enunciado=enunciado,
                           # Pasamos las opciones ya revueltas
                           a=opciones[0]['texto'],
                           b=opciones[1]['texto'],
                           c=opciones[2]['texto'],
                           d=opciones[3]['texto'],
                           # La respuesta correcta ahora se evalúa por el TEXTO y no por la letra 'a'
                           correcta=valor_correcto_real,
                           mensaje=mensaje_feedback,
                           es_correcta=es_correcta,
                           motivacion_pascal=motivacion_pascal,
                           total=session['total'],
                           aciertos=session['aciertos'])

@app.route('/resultado')
def resultado():
    total = session.get('total', 0)
    aciertos = session.get('aciertos', 0)
    modo = session.get('modo', 'normal')
    return render_template('resultado.html', total=total, aciertos=aciertos, modo=modo)

@app.route('/reset')
def reset():
    session['total'] = 0
    session['aciertos'] = 0
    session['modo'] = 'normal'
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)
