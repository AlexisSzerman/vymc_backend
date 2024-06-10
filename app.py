from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


def obtener_responsabilidades_hermano(id_hermano):
    conn = sqlite3.connect('db/vymc.db')
    cursor = conn.cursor()
    cursor.execute('SELECT responsabilidades.nombre_resp FROM responsabilidades INNER JOIN responsabilidades_hermanos ON responsabilidades.id_resp = responsabilidades_hermanos.id_resp WHERE responsabilidades_hermanos.id_hermano = ?', (id_hermano,))
    responsabilidades = cursor.fetchall()
    conn.close()
    return [responsabilidad[0] for responsabilidad in responsabilidades]

def obtener_asignaciones_hermano(id_hermano):
    conn = sqlite3.connect('db/vymc.db')
    cursor = conn.cursor()
    cursor.execute('SELECT asignaciones.nombre_asign FROM asignaciones INNER JOIN asignaciones_hermanos ON asignaciones.id_asign = asignaciones_hermanos.id_asign WHERE asignaciones_hermanos.id_hermano = ?', (id_hermano,))
    asignaciones = cursor.fetchall()
    conn.close()
    return [asignacion[0] for asignacion in asignaciones]

# Mapeo de nombres de responsabilidades a IDs
responsabilidades_mapping = {
    'Anciano': 1,
    'Siervo Ministerial': 2,
    'Precursor': 3,
    'Publicador Bautizado': 4,
    'Publicador no Bautizado': 5
}

# Mapeo de nombres de asignaciones a IDs
asignaciones_mapping = {
    'Presidencia': 1,
    'Oración': 2,
    'Tesoros de la Biblia': 3,
    'Perlas Escondidas': 4,
    'Lectura de la Biblia': 5,
    'Empiece Conversaciones': 6,
    'Haga Revisitas': 7,
    'Haga Discípulos': 8,
    'Explique Creencias': 9,
    'Amo/a de casa': 10,
    'Discurso': 11,
    'Análisis Seamos Mejores Maestros': 12,
    'Nuestra Vida Cristiana': 13,
    'Estudio Bíblico de congregación': 14,
    'Lectura libro': 15,
    'Necesidades de la congregación': 16
}

@app.route('/hermanos', methods=['GET', 'POST'])
def gestionar_hermanos():
    if request.method == 'GET':
        conn = sqlite3.connect('db/vymc.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id_hermano,nombre_hermano, apellido_hermano, activo, comentarios FROM hermanos ORDER BY apellido_hermano')
        hermanos = cursor.fetchall()

        hermanos_con_responsabilidades = []
        for hermano in hermanos:
            id_hermano = hermano[0]
            responsabilidades = obtener_responsabilidades_hermano(id_hermano)
            asignaciones = obtener_asignaciones_hermano(id_hermano)
            hermano_con_responsabilidades = {
                'id_hermano': hermano[0],
                'nombre_hermano': hermano[1],
                'apellido_hermano': hermano[2],
                'activo': hermano[3],
                'comentarios': hermano[4],
                'responsabilidades': responsabilidades,
                'asignaciones': asignaciones
            }
            hermanos_con_responsabilidades.append(hermano_con_responsabilidades)

        conn.close()
        return jsonify(hermanos_con_responsabilidades)
    elif request.method == 'POST':
        data = request.json
        nombre = data.get('nombre_hermano')
        apellido = data.get('apellido_hermano')
        genero = data.get('genero')
        activo = data.get('activo')
        comentarios = data.get('comentarios')

        # Obtener las responsabilidades seleccionadas y mapearlas a sus respectivos IDs
        responsabilidades_seleccionadas = data.get('responsabilidades', [])
        responsabilidades_ids = [responsabilidades_mapping[responsabilidad] for responsabilidad in responsabilidades_seleccionadas]

        # Obtener las asignaciones seleccionadas y mapearlas a sus respectivos IDs
        asignaciones_seleccionadas = data.get('asignaciones', [])
        asignaciones_ids = [asignaciones_mapping[asignacion] for asignacion in asignaciones_seleccionadas]

        # Guardar los datos del hermano en la tabla Hermanos
        conn = sqlite3.connect('db/vymc.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO hermanos (nombre_hermano, apellido_hermano, genero, activo, comentarios) VALUES (?, ?, ?, ?, ?)', (nombre, apellido, genero, activo, comentarios))
        id_hermano = cursor.lastrowid

        # Insertar los registros en las tablas de relaciones
        for responsabilidad_id in responsabilidades_ids:
            cursor.execute('INSERT INTO responsabilidades_hermanos (id_hermano, id_resp) VALUES (?, ?)', (id_hermano, responsabilidad_id))

        for asignacion_id in asignaciones_ids:
            cursor.execute('INSERT INTO asignaciones_hermanos (id_hermano, id_asign) VALUES (?, ?)', (id_hermano, asignacion_id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Hermano creado correctamente'}), 201

@app.route('/hermanos/<int:id_hermano>', methods=['DELETE'])
def eliminar_hermano(id_hermano):
    conn = sqlite3.connect('db/vymc.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM hermanos WHERE id_hermano = ?', (id_hermano,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Hermano eliminado correctamente'}), 200

@app.route('/reuniones', methods=['GET', 'POST'])
def gestionar_reuniones():
    if request.method == 'GET':
        conn = sqlite3.connect('db/vymc.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT reuniones.fecha, reuniones.sala, 
                   asignaciones.nombre_asign AS Asignacion, 
                   hermanos_titular.nombre_hermano || ' ' || hermanos_titular.apellido_hermano AS titular, 
                   CASE WHEN reuniones.ayudante IS NULL THEN ' ' ELSE hermanos_suplente.nombre_hermano || ' ' || hermanos_suplente.apellido_hermano END AS Ayudante 
            FROM reuniones 
            INNER JOIN asignaciones ON reuniones.id_asign = asignaciones.id_asign 
            INNER JOIN hermanos AS hermanos_titular ON reuniones.id_hermano = hermanos_titular.id_hermano 
            LEFT JOIN hermanos AS hermanos_suplente ON reuniones.ayudante = hermanos_suplente.id_hermano
        ''')
        reuniones = cursor.fetchall()
        conn.close()

        reuniones_info = []
        for reunion in reuniones:
            reunion_info = {
                'fecha': reunion[0],
                'sala': reunion[1],
                'asignacion': reunion[2],
                'titular': reunion[3],
                'ayudante': reunion[4]
            }
            reuniones_info.append(reunion_info)

        return jsonify(reuniones_info)

### New POST /reuniones endpoint ###
    elif request.method == 'POST':
        data = request.json
        reuniones = data.get('reuniones', [])

        conn = sqlite3.connect('db/vymc.db')
        cursor = conn.cursor()

        for reunion in reuniones:
            fecha = reunion.get('fecha')
            sala = reunion.get('sala')
            asignacion = reunion.get('asignacion')
            titular = reunion.get('titular')
            ayudante = reunion.get('ayudante')

            # Convert the assignment name into its corresponding ID
            id_asignacion = asignaciones_mapping.get(asignacion)

            # Fetch the ID of the titular hermano
            cursor.execute('SELECT id_hermano FROM hermanos WHERE nombre_hermano || " " || apellido_hermano = ?', (titular,))
            titular_result = cursor.fetchone()
            id_titular = titular_result[0] if titular_result else None

            # Fetch the ID of the ayudante hermano (if any)
            id_ayudante = None
            if ayudante:
                cursor.execute('SELECT id_hermano FROM hermanos WHERE nombre_hermano || " " || apellido_hermano = ?', (ayudante,))
                ayudante_result = cursor.fetchone()
                id_ayudante = ayudante_result[0] if ayudante_result else None

            # Insert the meeting data into the Reuniones table
            cursor.execute('''
                INSERT INTO reuniones (fecha, sala, id_asign, id_hermano, ayudante) 
                VALUES (?, ?, ?, ?, ?)
            ''', (fecha, sala, id_asignacion, id_titular, id_ayudante))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Reuniones guardadas correctamente'}), 201
    
@app.route('/hermano_apariciones/<nombre_hermano>', methods=['GET'])
def obtener_apariciones(nombre_hermano):
    conn = sqlite3.connect('db/vymc.db')
    cursor = conn.cursor()

    cursor.execute('''
         SELECT reuniones.fecha, reuniones.sala, 
           asignaciones.nombre_asign AS Asignacion, 
           hermanos_titular.nombre_hermano || ' ' || hermanos_titular.apellido_hermano AS Titular, 
           CASE WHEN reuniones.ayudante IS NULL THEN ' ' ELSE hermanos_suplente.nombre_hermano || ' ' || hermanos_suplente.apellido_hermano END AS Ayudante 
    FROM reuniones 
    INNER JOIN asignaciones ON reuniones.id_asign = asignaciones.id_asign 
    INNER JOIN hermanos AS hermanos_titular ON reuniones.id_hermano = hermanos_titular.id_hermano 
    LEFT JOIN hermanos AS hermanos_suplente ON reuniones.ayudante = hermanos_suplente.id_hermano
    WHERE (hermanos_titular.nombre_hermano || ' ' || hermanos_titular.apellido_hermano LIKE ?)
       OR (hermanos_suplente.nombre_hermano || ' ' || hermanos_suplente.apellido_hermano LIKE ?)
    ORDER BY reuniones.fecha DESC
    LIMIT 5
    ''', (f'%{nombre_hermano}%', f'%{nombre_hermano}%'))

    apariciones = cursor.fetchall()
    conn.close()

    apariciones_info = [
        {
            'fecha': aparicion[0],
            'sala': aparicion[1],
            'asignacion': aparicion[2],
            'titular': aparicion[3],
            'ayudante': aparicion[4]
        }
        for aparicion in apariciones
    ]

    return jsonify(apariciones_info)



if __name__ == '__main__':
    app.run(debug=True)


