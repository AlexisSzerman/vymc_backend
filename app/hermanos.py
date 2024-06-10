# /tu_proyecto/app/hermanos.py
from flask import Blueprint, jsonify, request
import sqlite3

hermanos_bp = Blueprint('hermanos', __name__)

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

responsabilidades_mapping = {
    'Anciano': 1,
    'Siervo Ministerial': 2,
    'Precursor': 3,
    'Publicador Bautizado': 4,
    'Publicador no Bautizado': 5
}

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

@hermanos_bp.route('/hermanos', methods=['GET', 'POST'])
def gestionar_hermanos():
    if request.method == 'GET':
        conn = sqlite3.connect('db/vymc.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id_hermano, nombre_hermano, apellido_hermano, activo, comentarios FROM hermanos ORDER BY apellido_hermano')
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

        responsabilidades_seleccionadas = data.get('responsabilidades', [])
        responsabilidades_ids = [responsabilidades_mapping[responsabilidad] for responsabilidad in responsabilidades_seleccionadas]

        asignaciones_seleccionadas = data.get('asignaciones', [])
        asignaciones_ids = [asignaciones_mapping[asignacion] for asignacion in asignaciones_seleccionadas]

        conn = sqlite3.connect('db/vymc.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO hermanos (nombre_hermano, apellido_hermano, genero, activo, comentarios) VALUES (?, ?, ?, ?, ?)', (nombre, apellido, genero, activo, comentarios))
        id_hermano = cursor.lastrowid

        for responsabilidad_id in responsabilidades_ids:
            cursor.execute('INSERT INTO responsabilidades_hermanos (id_hermano, id_resp) VALUES (?, ?)', (id_hermano, responsabilidad_id))

        for asignacion_id in asignaciones_ids:
            cursor.execute('INSERT INTO asignaciones_hermanos (id_hermano, id_asign) VALUES (?, ?)', (id_hermano, asignacion_id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Hermano creado correctamente'}), 201

@hermanos_bp.route('/hermanos/<int:id_hermano>', methods=['DELETE'])
def eliminar_hermano(id_hermano):
    conn = sqlite3.connect('db/vymc.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM hermanos WHERE id_hermano = ?', (id_hermano,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Hermano eliminado correctamente'}), 200

""" 
@hermanos_bp.route('/hermanos/<int:id_hermano>', methods=['GET'])
def obtener_hermano(id_hermano):
    conn = sqlite3.connect('db/vymc.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nombre_hermano, apellido_hermano, genero, activo, comentarios FROM hermanos WHERE id_hermano = ?', (id_hermano,))
    hermano = cursor.fetchone()
    if not hermano:
        conn.close()
        return jsonify({'error': 'Hermano no encontrado'}), 404

    responsabilidades = obtener_responsabilidades_hermano(id_hermano)
    asignaciones = obtener_asignaciones_hermano(id_hermano)

    hermano_con_datos = {
        'Nombre_hermano': hermano[0],
        'Apellido_hermano': hermano[1],
        'Genero': hermano[2],
        'Activo': hermano[3],
        'Comentarios': hermano[4],
        'responsabilidades': responsabilidades,
        'asignaciones': asignaciones
    }

    conn.close()
    return jsonify(hermano_con_datos)

@hermanos_bp.route('/hermanos/<int:id_hermano>', methods=['PUT'])
def actualizar_hermano(id_hermano):
    datos = request.get_json()
    conn = sqlite3.connect('db/vymc.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE hermanos
        SET nombre_hermano = ?, apellido_hermano = ?, genero = ?, activo = ?, comentarios = ?
        WHERE id_hermano = ?
    ''', (
        datos.get('nombre_hermano'),
        datos.get('apellido_hermano'),
        datos.get('genero'),
        datos.get('activo'),
        datos.get('comentarios'),
        id_hermano
    ))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Hermano no encontrado'}), 404

    cursor.execute('DELETE FROM responsabilidades WHERE id_hermano = ?', (id_hermano,))
    cursor.execute('DELETE FROM asignaciones WHERE id_hermano = ?', (id_hermano,))

    for responsabilidad in datos.get('responsabilidades', []):
        cursor.execute('INSERT INTO responsabilidades (id_hermano, nombre) VALUES (?, ?)', (id_hermano, responsabilidad))

    for asignacion in datos.get('asignaciones', []):
        cursor.execute('INSERT INTO asignaciones (id_hermano, nombre) VALUES (?, ?)', (id_hermano, asignacion))

    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Hermano actualizado correctamente'})
 """