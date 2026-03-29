from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import time

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_super_segura' # Necesario para usar sesiones

def obtener_pregunta_aleatoria():
    conn = sqlite3.connect('banco_preguntas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, enunciado, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta FROM preguntas")
    todas = cursor.fetchall()
    conn.close()
    return random.choice(todas) if todas else None

@app.route('/')
def inicio():
    session['aciertos'] = 0
    session['total'] = 0
    session['modo_examen'] = False
    
    # === ¡Mágica Lista de Frases de Ánimo de Rapunzel! ===
    frases_rapunzel = [
        "¡Sal de tu zona de confort, el examen está afuera!",
        "✨ ¡Haz brillar tu conocimiento hoy! ✨",
        "🎨 ¡Pinta tu futuro con cada respuesta correcta!",
        "🍳 ¡Sartenazo a las dudas! ¡Tú puedes!",
        "🌸 ¡Tu sueño está cada vez más cerca!",
        "¡Ventura te aguarda en este cuestionario!",
        "🕯️ ¡Ilumina tu camino al éxito!",
        "¡Hoy es el día en que tu nota empieza!",
        "¡Con cada pregunta, tu luz se enciende!",
        "💖 ¡Rapunzel y yo creemos en ti!"
    ]
    mensaje_animado = random.choice(frases_rapunzel)
    
    # Enviamos el mensaje aleatorio a la plantilla
    return render_template('index.html', mensaje_rapunzel=mensaje_animado)

@app.route('/iniciar_examen')
def iniciar_examen():
    session['aciertos'] = 0
    session['total'] = 0
    session['modo_examen'] = True
    session['tiempo_inicio'] = time.time() 
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'aciertos' not in session:
        session['aciertos'] = 0
        session['total'] = 0

    mensaje = ""
    es_correcta = None
    quedan_segundos = 1200 # 20 minutos por defecto

    # Si es modo examen, calculamos el tiempo restante
    if session.get('modo_examen'):
        tiempo_transcurrido = time.time() - session.get('tiempo_inicio', time.time())
        quedan_segundos = int(1200 - tiempo_transcurrido)
        
        # Si se acabó el tiempo o ya respondieron 30 preguntas, ¡al resultado!
        if quedan_segundos <= 0 or session['total'] >= 30:
            return redirect(url_for('resultado'))

    if request.method == 'POST':
        opcion_elegida = request.form.get('respuesta')
        correcta_bd = request.form.get('correcta')
        
        session['total'] += 1
        
        if opcion_elegida == correcta_bd:
            session['aciertos'] += 1
            mensaje = "¡Correcto! Sigue así. 👏"
            es_correcta = True
        else:
            mensaje = f"❌ Incorrecto. La respuesta correcta era la opción '{correcta_bd}'."
            es_correcta = False

    pregunta = obtener_pregunta_aleatoria()
    if not pregunta:
        return "No hay preguntas cargadas en la base de datos."

    id_preg, enunciado, a, b, c, d, correcta = pregunta

    return render_template('quiz.html', 
                           enunciado=enunciado, 
                           a=a, b=b, c=c, d=d, 
                           correcta=correcta,
                           mensaje=mensaje,
                           es_correcta=es_correcta,
                           aciertos=session['aciertos'],
                           total=session['total'],
                           modo_examen=session.get('modo_examen'),
                           tiempo_restante=quedan_segundos)

@app.route('/resultado')
def resultado():
    return render_template('resultado.html', 
                           aciertos=session.get('aciertos', 0), 
                           total=session.get('total', 0))

@app.route('/reset')
def reset():
    session['aciertos'] = 0
    session['total'] = 0
    session['modo_examen'] = False
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)