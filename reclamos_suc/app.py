from flask import Flask, render_template, request, send_file, url_for, abort
import qrcode
import io
import urllib.parse
import sqlite3

app = Flask(__name__)

# Simulación de una "base de datos" de sucursales
sucursales = {
  
    "sucursalL2": {
        "nombre": "Sucursal Lavalle II"
    },
    "sucursal11": {
        "nombre": "Sucursal Once"
    },
    "sucursalR1": {
        "nombre": "Sucursal Rivadavia I"
    },
    "sucursalR2": {
        "nombre": "Sucursal Rivadavia II"
    },
    "sucursalS": {
        "nombre": "Sucursal Solano"
    },
    "sucursalV1": {
        "nombre": "Sucursal Varela I"
    },
    "sucursalV2": {
        "nombre": "Sucursal Varela II"
    },
    "sucursalV3": {
        "nombre": "Sucursal Varela III"
    },
    "sucursalW": {
        "nombre": "Sucursal Wilde"
    }
    # Agrega más sucursales según sea necesario.
    
}

# Ruta principal: muestra la lista de sucursales (index.html)
@app.route('/')
def index():
    return render_template("index.html", sucursales=sucursales)

# Ruta para generar el código QR de cada sucursal
@app.route('/generar_qr/<sucursal_id>')
def generar_qr(sucursal_id):
    if sucursal_id not in sucursales:
        abort(404, description="Sucursal no encontrada")
    
    # Construimos la URL de la página de contacto para la sucursal
    url_contacto = url_for('contacto', sucursal_id=sucursal_id, _external=True)
    
    # Generamos el QR con la librería qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url_contacto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardamos la imagen en un buffer de memoria y la retornamos
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

# Ruta de contacto: se muestra la información de la sucursal y se prepara el enlace para WhatsApp
@app.route('/contacto/<sucursal_id>')
def contacto(sucursal_id):
    if sucursal_id not in sucursales:
        abort(404, description="Sucursal no encontrada")
    
    sucursal = sucursales[sucursal_id]
    
    # Se prepara el mensaje con la información de la sucursal
    mensaje = f"Hola, tengo una consulta. Sucursal: {sucursal['nombre']}"
    mensaje_codificado = urllib.parse.quote(mensaje)
    
    # Número de WhatsApp único (en formato internacional sin símbolos)
    whatsapp_number = "5491138627941"  # Actualiza este valor según corresponda
    whatsapp_link = f"https://wa.me/{whatsapp_number}?text={mensaje_codificado}"
    
    return render_template("contact.html", sucursal=sucursal, whatsapp_link=whatsapp_link)

# Ruta para la mini encuesta (GET muestra el formulario, POST procesa y guarda los datos)
@app.route('/mini_encuesta', methods=['GET', 'POST'])
def mini_encuesta():
    if request.method == 'POST':
        # Recoger respuestas del formulario
        comfortable = request.form.get('comfortable')
        recommendation = request.form.get('recommendation')
        email = request.form.get('email')
        
        # Conectamos a la base de datos SQLite (se creará el archivo si no existe)
        conn = sqlite3.connect('encuesta_md.db')
        cursor = conn.cursor()
        
        # Creamos la tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encuensta_md (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comfortable TEXT,
                recommendation TEXT,
                email TEXT
            )
        ''')
        
        # Insertamos los datos en la tabla
        cursor.execute('''
            INSERT INTO encuensta_md (comfortable, recommendation, email)
            VALUES (?, ?, ?)
        ''', (comfortable, recommendation, email))
        
        conn.commit()
        conn.close()
        
        # Retornamos una plantilla de agradecimiento
        return render_template('encuesta_thanks.html')
    else:
        return render_template('mini_encuesta.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
