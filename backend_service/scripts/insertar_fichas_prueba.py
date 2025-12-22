#!/usr/bin/env python3
"""
Script para insertar fichas de prueba con diferentes canales en PostgreSQL de Render
"""

import psycopg2
from datetime import datetime
import hashlib

# URL de conexión a PostgreSQL de Render
DATABASE_URL = "postgresql://dashboard_captacion_db_user:zCQusHpUln7PINbsqKY3uedDk1tOjcBi@dpg-d54jlsdactks73agf7b0-a.frankfurt-postgres.render.com/dashboard_captacion_db"

# Fichas de prueba con diferentes canales
fichas_prueba = [
    {
        'tipo': 'reddit',
        'keyword': 'student accommodation Barcelona',
        'url': 'https://reddit.com/r/Barcelona/comments/abc123/looking_for_roommate',
        'titulo': 'Looking for roommate in Barcelona for 2026',
        'snippet': 'Hey! I\'m a 22yo student from USA starting at UB in Feb 2026. Looking for someone to share a flat near campus. Budget 400-500€/month.',
        'dominio': 'reddit.com',
        'institucion': 'Universitat de Barcelona',
        'email': None,
        'telefono': None,
        'tiene_formulario': False,
        'plataforma_social': 'reddit',
        'username': 'student_bcn_2026',
        'subreddit': 'Barcelona',
        'grupo_facebook': None,
        'prioridad': 'Alta',
        'propuesta_comunicativa': '¡Hola! Vi tu post sobre buscar compañero de piso en Barcelona. Yo también empiezo en la UB en febrero 2026. ¿Te gustaría hablar sobre compartir un apartamento cerca del campus?',
        'canal_recomendado': 'reddit',
        'estado': 'pendiente',
        'procesada': 'SI'
    },
    {
        'tipo': 'email',
        'keyword': 'housing Valencia students 2026',
        'url': 'https://www.uv.es/international/housing',
        'titulo': 'International Students Housing - University of Valencia',
        'snippet': 'The University of Valencia offers housing assistance for international students. Contact our housing office for more information about available accommodations.',
        'dominio': 'www.uv.es',
        'institucion': 'Universidad de Valencia',
        'email': 'housing@uv.es',
        'telefono': '+34 963 864 100',
        'tiene_formulario': True,
        'plataforma_social': None,
        'username': None,
        'subreddit': None,
        'grupo_facebook': None,
        'prioridad': 'Media',
        'propuesta_comunicativa': 'Buenos días, soy un estudiante internacional que comenzará en la Universidad de Valencia en septiembre de 2026. Me gustaría recibir información sobre las opciones de alojamiento disponibles para estudiantes extranjeros.',
        'canal_recomendado': 'email',
        'estado': 'pendiente',
        'procesada': 'SI'
    },
    {
        'tipo': 'facebook',
        'keyword': 'student groups Madrid',
        'url': 'https://facebook.com/groups/madrid.students.2026',
        'titulo': 'Madrid International Students 2026',
        'snippet': 'Group for international students coming to Madrid in 2026. Share housing tips, meet roommates, and connect with fellow students!',
        'dominio': 'facebook.com',
        'institucion': None,
        'email': None,
        'telefono': None,
        'tiene_formulario': False,
        'plataforma_social': 'facebook',
        'username': None,
        'subreddit': None,
        'grupo_facebook': 'Madrid International Students 2026',
        'prioridad': 'Media',
        'propuesta_comunicativa': '¡Hola a todos! Soy un estudiante que llegará a Madrid en 2026. ¿Alguien está buscando compañero de piso o tiene recomendaciones de zonas para vivir cerca de las universidades?',
        'canal_recomendado': 'facebook',
        'estado': 'pendiente',
        'procesada': 'SI'
    },
    {
        'tipo': 'reddit',
        'keyword': 'erasmus housing Spain',
        'url': 'https://reddit.com/r/Erasmus/comments/xyz789/housing_tips_spain',
        'titulo': 'Housing tips for Erasmus students in Spain 2026',
        'snippet': 'Starting my Erasmus in Seville next year. Any tips on finding affordable housing? What neighborhoods are best for students?',
        'dominio': 'reddit.com',
        'institucion': 'Universidad de Sevilla',
        'email': None,
        'telefono': None,
        'tiene_formulario': False,
        'plataforma_social': 'reddit',
        'username': 'erasmus_seville_26',
        'subreddit': 'Erasmus',
        'grupo_facebook': None,
        'prioridad': 'Alta',
        'propuesta_comunicativa': '¡Hola! También voy a Sevilla para Erasmus en 2026. He encontrado algunas opciones de pisos compartidos en Triana y Los Remedios. ¿Quieres que compartamos información y tal vez busquemos juntos?',
        'canal_recomendado': 'reddit',
        'estado': 'pendiente',
        'procesada': 'SI'
    },
    {
        'tipo': 'web',
        'keyword': 'student residences Barcelona',
        'url': 'https://www.resa.es/en/student-residences/barcelona',
        'titulo': 'Student Residences in Barcelona | RESA',
        'snippet': 'Modern student residences in Barcelona with all services included. Rooms available for 2026 academic year. Book now!',
        'dominio': 'www.resa.es',
        'institucion': None,
        'email': 'info@resa.es',
        'telefono': '+34 900 123 456',
        'tiene_formulario': True,
        'plataforma_social': None,
        'username': None,
        'subreddit': None,
        'grupo_facebook': None,
        'prioridad': 'Baja',
        'propuesta_comunicativa': 'Buenos días, estoy interesado en reservar una habitación en una de sus residencias de estudiantes en Barcelona para el curso académico 2026. ¿Podrían enviarme información sobre precios, disponibilidad y servicios incluidos?',
        'canal_recomendado': 'email',
        'estado': 'pendiente',
        'procesada': 'SI'
    }
]

def generar_id_ficha(url):
    """Genera un ID único para una ficha"""
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_url = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"TEST-{timestamp}-{hash_url}"

def insertar_fichas():
    """Inserta las fichas de prueba en PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("📝 INSERTANDO FICHAS DE PRUEBA")
        print("=" * 70)
        print()
        
        insertadas = 0
        
        for i, ficha in enumerate(fichas_prueba, 1):
            # Generar ID único
            ficha_id = generar_id_ficha(ficha['url'])
            
            # Verificar si ya existe
            cursor.execute("SELECT id FROM fichas WHERE url = %s", (ficha['url'],))
            if cursor.fetchone():
                print(f"[{i}/5] ⏭️  Ya existe: {ficha['titulo'][:50]}...")
                continue
            
            # Insertar ficha
            cursor.execute("""
                INSERT INTO fichas (
                    id, tipo, keyword, url, titulo, snippet, dominio,
                    institucion, email, telefono, tiene_formulario,
                    plataforma_social, username, subreddit, grupo_facebook,
                    prioridad, propuesta_comunicativa, canal_recomendado,
                    estado, procesada
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                ficha_id,
                ficha['tipo'],
                ficha['keyword'],
                ficha['url'],
                ficha['titulo'],
                ficha['snippet'],
                ficha['dominio'],
                ficha['institucion'],
                ficha['email'],
                ficha['telefono'],
                ficha['tiene_formulario'],
                ficha['plataforma_social'],
                ficha['username'],
                ficha['subreddit'],
                ficha['grupo_facebook'],
                ficha['prioridad'],
                ficha['propuesta_comunicativa'],
                ficha['canal_recomendado'],
                ficha['estado'],
                ficha['procesada']
            ))
            
            conn.commit()
            
            print(f"[{i}/5] ✅ Insertada: {ficha['titulo'][:50]}...")
            print(f"      Canal: {ficha['canal_recomendado']}")
            if ficha['email']:
                print(f"      Email: {ficha['email']}")
            if ficha['username']:
                print(f"      Username: @{ficha['username']}")
            if ficha['subreddit']:
                print(f"      Subreddit: r/{ficha['subreddit']}")
            if ficha['grupo_facebook']:
                print(f"      Grupo: {ficha['grupo_facebook']}")
            print()
            
            insertadas += 1
        
        cursor.close()
        conn.close()
        
        print("=" * 70)
        print(f"✅ PROCESO COMPLETADO")
        print(f"   Fichas insertadas: {insertadas}")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    insertar_fichas()
