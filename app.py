import requests 
from flask import Flask
from flask import render_template,request,redirect,url_for,flash
from flaskext.mysql import MySQL 


app= Flask(__name__)
app.secret_key="Develoteca"

#Instrucciones para usar MySQL y el localhost
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
#Conexion con los datos
mysql.init_app(app)

#Cuando el usuario escriba / se retorna la url que dirije a index.html
@app.route('/')
def index():
    return render_template('usuarios/index.html')

@app.route('/admin')
def indexAdmin():
    sql="SELECT * from `usuarios`;"
    #Conexion a la base de datos
    conn= mysql.connect()
    cursor= conn.cursor()
    cursor.execute(sql)
    usuarios=cursor.fetchall()

    conn.commit()
    return render_template('usuarios/indexAdmin.html', usuarios=usuarios)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn= mysql.connect()
    cursor= conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id=%s",(id))
    conn.commit()
    return redirect('/admin')

@app.route('/edit/<int:id>')
def edit(id):

    conn= mysql.connect()
    cursor= conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=%s",(id))
    usuarios=cursor.fetchall()
    conn.commit()

    return render_template('usuarios/edit.html', usuarios=usuarios)

@app.route('/update', methods=['POST'])
def update():

    _dni=request.form['intDNI']
    _nombre=request.form['txtNombre']
    _apellido=request.form['txtApellido']
    _genero=request.form['txtGenero']
    _correo=request.form['txtCorreo']
    _monto=request.form['decimalMonto']
    id=request.form['txtID']

    sql="UPDATE usuarios SET dni=%s,nombre=%s, apellido=%s, genero=%s, email=%s, monto=%s WHERE id=%s ;"
    
    datos=(_dni,_nombre,_apellido,_genero,_correo,_monto,id)

    conn= mysql.connect()
    cursor= conn.cursor()

    cursor.execute(sql, datos)

    conn.commit()

    return redirect ('/admin')

@app.route('/prestamo')
def prestamo():
    return render_template('usuarios/prestamo.html')


@app.route('/store', methods=['POST'])
def storage():
    
    _dni=request.form['intDNI']
    _nombre=request.form['txtNombre']
    _apellido=request.form['txtApellido']
    _genero=request.form['txtGenero']
    _correo=request.form['txtCorreo']
    _monto=request.form['decimalMonto']

    if _dni == '' or _nombre == '' or _apellido =='' or _genero == '' or _correo == '' or _monto == '':
        flash('Recuerda llenar los datos de los campos','danger')
        return redirect(url_for('prestamo'))

    urlMoni = 'https://api.moni.com.ar/api/v4/scoring/pre-score/' + _dni
    
    r = requests.get(urlMoni, headers={ 'credential': 'ZGpzOTAzaWZuc2Zpb25kZnNubm5u'})

    r.raise_for_status()  
    if r.status_code != 500:
        if r.text.__contains__('true'):
            flash('El campo DNI debe tener 8 caracteres y solo números', 'danger')
            return redirect(url_for('prestamo'))

        elif r.text.__contains__('approve'):
            #%s Se orden como yo se los paso
            sql="INSERT INTO `usuarios` (`id`,`dni`, `nombre`, `apellido`, `genero`, `email`, `monto`) VALUES (NULL, %s, %s ,%s, %s, %s, %s);"
    
            datos=(_dni,_nombre,_apellido,_genero,_correo,_monto)

            conn= mysql.connect()
            cursor= conn.cursor()
            cursor.execute(sql, datos)
            conn.commit()

            flash('Se aprobó su préstamo con exito')
            return redirect(url_for('prestamo'))

        else:
            
            flash('Se rechazó su préstamo', 'danger')
            return redirect(url_for('prestamo'))

    return ('/')

#Activo el dbug, pauta de lo que sucede
if __name__ == '__main__':
    app.run(debug=True)