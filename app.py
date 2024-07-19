from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
from datetime import datetime
import calendar

app = Flask(__name__)

db = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='bancoweb',
    cursorclass=pymysql.cursors.DictCursor
)

# Database Factory Method
class Database:
    @staticmethod
    def get_cursor():
        return db.cursor()

# Template Method for rendering pages with session check
class PageRenderer:
    def render(self, template_name, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        user_name = session['user_name']
        return render_template(template_name, user_name=user_name, **kwargs)

page_renderer = PageRenderer()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']
        cursor = Database.get_cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and user['password'] == password:
            session['loggedin'] = True
            session['username'] = user['usuario']
            session['user_name'] = f"{user['nombre']} {user['apellido']}"
            session['tipo'] = user['tipo']

            return redirect(url_for(f"operaciones_{user['tipo']}"))
        else:
            return 'Login fallido. Por favor, verifica tu usuario y contraseña.'
    return render_template('login.html')

@app.route('/operaciones/<tipo>.html')
def operaciones(tipo):
    if 'loggedin' in session and session.get('tipo') == tipo:
        return page_renderer.render(f'operaciones{tipo.capitalize()}.html')
    return redirect(url_for('login'))

@app.route('/realizarRetiros.html')
def realizar_retiros():
    return page_renderer.render('realizarRetiros.html')

@app.route('/realizarDeposito.html')
def realizar_depositos():
    return page_renderer.render('realizarDeposito.html')

@app.route('/realizarTransferencias.html')
def realizar_tr():
    cursor = Database.get_cursor()
    cursor.execute("SELECT numcuenta FROM cuentas WHERE cedula = (SELECT cedula FROM usuarios WHERE usuario = %s)", (session['username'],))
    cuentas = cursor.fetchall()
    cursor.close()
    return page_renderer.render('realizarTransferencias.html', cuentas=cuentas)

@app.route('/analisis.html')
def realizar_analisis():
    return page_renderer.render('analisis.html')

@app.route('/analisis2.html')
def realizar_analisis2():
    return page_renderer.render('analisis2.html')

@app.route('/obtener_cuentas', methods=['POST'])
def obtener_cuentas():
    cedula = request.form['cedula']
    cursor = Database.get_cursor()
    cursor.execute("SELECT numcuenta FROM cuentas WHERE cedula = %s", (cedula,))
    cuentas = cursor.fetchall()
    cursor.close()
    return jsonify(cuentas)

@app.route('/procesar_retiro', methods=['POST'])
def procesar_retiro():
    if 'loggedin' in session:
        cedula = request.form['cedula']
        numcuenta = request.form['numcuenta']
        monto = float(request.form['monto'])
        fecha = request.form['fecha']

        cursor = Database.get_cursor()
        cursor.execute("SELECT saldo FROM cuentas WHERE cedula = %s AND numcuenta = %s", (cedula, numcuenta))
        cuenta = cursor.fetchone()

        if not cuenta or cuenta['saldo'] < monto:
            cursor.close()
            return jsonify({'status': 'error', 'message': 'Fondos insuficientes o cuenta no encontrada.'}), 400

        nuevo_saldo = cuenta['saldo'] - monto
        cursor.execute("UPDATE cuentas SET saldo = %s WHERE cedula = %s AND numcuenta = %s", (nuevo_saldo, cedula, numcuenta))
        cursor.execute("INSERT INTO reriros (usuario, cuenta, monto, fecha) VALUES (%s, %s, %s, %s)", (cedula, numcuenta, monto, fecha))
        db.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': f'Retiro exitoso. Saldo actual: {nuevo_saldo}'}), 200

    return jsonify({'status': 'error', 'message': 'Usuario no logeado.'}), 401

@app.route('/procesar_deposito', methods=['POST'])
def procesar_deposito():
    if 'loggedin' in session:
        cedula_beneficiario = request.form['cedula_beneficiario']
        numcuenta = request.form['numcuenta']
        monto = float(request.form['monto'])
        fecha = request.form['fecha']

        cursor = Database.get_cursor()
        cursor.execute("SELECT saldo FROM cuentas WHERE cedula = %s AND numcuenta = %s", (cedula_beneficiario, numcuenta))
        cuenta = cursor.fetchone()

        if not cuenta:
            cursor.close()
            return jsonify({'status': 'error', 'message': 'Cuenta no encontrada.'}), 400

        nuevo_saldo = cuenta['saldo'] + monto
        cursor.execute("UPDATE cuentas SET saldo = %s WHERE cedula = %s AND numcuenta = %s", (nuevo_saldo, cedula_beneficiario, numcuenta))
        cursor.execute("INSERT INTO depositos (usuario, cuenta, monto, fecha) VALUES (%s, %s, %s, %s)", (cedula_beneficiario, numcuenta, monto, fecha))
        db.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': f'Depósito realizado con éxito. Saldo actual: {nuevo_saldo}'}), 200

    return jsonify({'status': 'error', 'message': 'Usuario no logeado.'}), 401

@app.route('/verificar_cedula', methods=['POST'])
def verificar_cedula():
    cedula = request.form['cedula']
    cursor = Database.get_cursor()
    cursor.execute("SELECT 1 FROM cuentas WHERE cedula = %s", (cedula,))
    existe = cursor.fetchone() is not None
    cursor.close()
    return jsonify({'exists': existe})

@app.route('/verificar_cuenta', methods=['POST'])
def verificar_cuenta():
    cedula = request.form['cedula']
    numero_cuenta = request.form['numero_cuenta']
    cursor = Database.get_cursor()
    cursor.execute("SELECT 1 FROM cuentas WHERE cedula = %s AND numcuenta = %s", (cedula, numero_cuenta))
    valida = cursor.fetchone() is not None
    cursor.close()
    return jsonify({'valid': valida})

@app.route('/procesar_transferencia', methods=['POST'])
def procesar_transferencia():
    if 'loggedin' in session:
        cedula_beneficiario = request.form['cedula']
        numero_cuenta_beneficiario = request.form['numero_cuenta']
        cuenta_origen = request.form['numcuenta']
        monto = float(request.form['monto'])
        fecha = request.form['fecha']

        cursor = Database.get_cursor()
        cursor.execute("SELECT saldo FROM cuentas WHERE numcuenta = %s", (cuenta_origen,))
        cuenta_origen_data = cursor.fetchone()
        if not cuenta_origen_data or cuenta_origen_data['saldo'] < monto:
            cursor.close()
            return jsonify({'status': 'error', 'message': 'Fondos insuficientes o cuenta de origen no encontrada.'}), 400
        
        cursor.execute("SELECT saldo FROM cuentas WHERE cedula = %s AND numcuenta = %s", (cedula_beneficiario, numero_cuenta_beneficiario))
        cuenta_beneficiario_data = cursor.fetchone()
        if not cuenta_beneficiario_data:
            cursor.close()
            return jsonify({'status': 'error', 'message': 'Cuenta del beneficiario no encontrada.'}), 400
        
        cursor.execute("INSERT INTO transferencias (cuentaOrigen, cuentaDestino, monto, fecha) VALUES (%s, %s, %s, %s)", 
                       (cuenta_origen, numero_cuenta_beneficiario, monto, fecha))
        cursor.execute("UPDATE cuentas SET saldo = %s WHERE numcuenta = %s", (cuenta_origen_data['saldo'] - monto, cuenta_origen))
        cursor.execute("UPDATE cuentas SET saldo = %s WHERE numcuenta = %s", (cuenta_beneficiario_data['saldo'] + monto, numero_cuenta_beneficiario))
        db.commit()
        cursor.close()

        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'error', 'message': 'Usuario no logeado.'}), 401

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.secret_key = 'supersecretkey'
    app.run(port=8000, debug=True)