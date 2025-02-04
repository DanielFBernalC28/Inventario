from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 


def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  
        database='inventario'
    )
    return conn

# URL página principal (Inventario)
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # trae todos los datos de la tabla productos
    cursor.execute('SELECT * FROM productos')
    column_names = [col[0] for col in cursor.description]
    productos = [dict(zip(column_names, producto)) for producto in cursor.fetchall()]
    conn.close()

    return render_template('index.html', productos=productos)

# URL para agregar un producto
@app.route('/agregar', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        try:
            # Trae los datos del inventario
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = float(request.form['precio']) 
            cantidad = int(request.form['cantidad'])  
        except ValueError:
            flash('Precio o cantidad no son válidos.')
            return redirect(url_for('agregar_producto'))

        # Conexion a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Agrega el nuevo producto a la base de datos.
        cursor.execute('INSERT INTO productos (nombre, descripcion, precio, cantidad) VALUES (%s, %s, %s, %s)',
                       (nombre, descripcion, precio, cantidad))
        conn.commit()
        conn.close()

        flash('Producto agregado con éxito!')
        return redirect(url_for('index'))

    return render_template('agregar.html')

# URL para editar producto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = float(request.form['precio']) 
            cantidad = int(request.form['cantidad']) 
        except ValueError:
            flash('Precio o cantidad no son válidos.')
            return redirect(url_for('editar_producto', id=id))  

        #   Actualiza los datos en la base de datos
        cursor.execute('UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s WHERE id = %s',
                       (nombre, descripcion, precio, cantidad, id))
        conn.commit()

        flash('Producto actualizado con éxito!')
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
    producto = cursor.fetchone()
    conn.close()

    # utilizamos esta validacion en caso de que no encuentre el producto y lo redirecciona al inventario
    if producto is None:
        flash('Producto no encontrado.')
        return redirect(url_for('index'))


    column_names = [col[0] for col in cursor.description]
    producto = dict(zip(column_names, producto))

  
    return render_template('editar.html', producto=producto)

# URL para eliminar producto
@app.route('/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Aqui validamos si el producto existe o no
    cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
    producto = cursor.fetchone()

    if producto is None:
        flash('Producto no encontrado para eliminar.')
        return redirect(url_for('index'))

    # Qui eliminamos el dato de la base de datos
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    conn.commit()
    conn.close()

    flash('Producto eliminado con éxito!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
