from flask import Blueprint, jsonify, request
import sqlite3

reuniones_bp = Blueprint('reuniones', __name__)

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

@reuniones_bp.route('/reuniones', methods=['GET', 'POST'])
def gestionar_reuniones():
    try:
        if request.method == 'GET':
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
            ''')
            reuniones = cursor.fetchall()
            conn.close()

            print("Datos obtenidos de la base de datos:", reuniones)  # Añadir mensaje de depuración

            reuniones_info = []
            for reunion in reuniones:
                reunion_info = {
                    'Fecha': reunion[0],
                    'Sala': reunion[1],
                    'Asignacion': reunion[2],
                    'Titular': reunion[3],
                    'Ayudante': reunion[4]
                }
                reuniones_info.append(reunion_info)

            return jsonify(reuniones_info)

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

                id_asignacion = asignaciones_mapping.get(asignacion)

                cursor.execute('SELECT id_hermano FROM hermanos WHERE nombre_hermano || " " || apellido_hermano = ?', (titular,))
                titular_result = cursor.fetchone()
                id_titular = titular_result[0] if titular_result else None

                id_ayudante = None
                if ayudante:
                    cursor.execute('SELECT id_hermano FROM hermanos WHERE nombre_hermano || " " || apellido_hermano = ?', (ayudante,))
                    ayudante_result = cursor.fetchone()
                    id_ayudante = ayudante_result[0] if ayudante_result else None

                cursor.execute('''
                    INSERT INTO reuniones (fecha, sala, id_asign, id_hermano, ayudante) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (fecha, sala, id_asignacion, id_titular, id_ayudante))

            conn.commit()
            conn.close()

            return jsonify({'message': 'Reuniones guardadas correctamente'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@reuniones_bp.route('/hermano_apariciones/<nombre_hermano>', methods=['GET'])
def obtener_apariciones(nombre_hermano):
    try:
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

        print("Datos de apariciones obtenidos de la base de datos:", apariciones)  # Añadir mensaje de depuración

        apariciones_info = [
            {
                'fecha': aparicion[0],
                'sala': aparicion[1],
                'asignacion': aparicion[2],
                'titular': aparicion[3],
                'ayudante': aparicion[4]
            }
        for aparicion in apariciones]

        return jsonify(apariciones_info)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
