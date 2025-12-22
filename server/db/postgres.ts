/**
 * Módulo de conexión a PostgreSQL de Render
 */

import { Pool } from 'pg';

// URL de conexión a PostgreSQL de Render
const RENDER_DATABASE_URL = "postgresql://dashboard_captacion_db_user:zCQusHpUln7PINbsqKY3uedDk1tOjcBi@dpg-d54jlsdactks73agf7b0-a.frankfurt-postgres.render.com/dashboard_captacion_db";

// Pool de conexiones
const pool = new Pool({
  connectionString: RENDER_DATABASE_URL,
  ssl: {
    rejectUnauthorized: false // Render requiere SSL
  }
});

// Verificar conexión al iniciar
pool.on('connect', () => {
  console.log('✅ Conectado a PostgreSQL de Render');
});

pool.on('error', (err) => {
  console.error('❌ Error en pool de PostgreSQL:', err);
});

export default pool;

// Tipos para las fichas
export interface Ficha {
  id: string;
  tipo: string | null;
  keyword: string | null;
  url: string;
  titulo: string | null;
  snippet: string | null;
  dominio: string | null;
  institucion: string | null;
  email: string | null;
  telefono: string | null;
  tiene_formulario: boolean | null;
  plataforma_social: string | null;
  username: string | null;
  subreddit: string | null;
  grupo_facebook: string | null;
  fecha_detectada: Date | null;
  prioridad: string | null;
  propuesta_comunicativa: string | null;
  canal_recomendado: string | null;
  estado: string;
  procesada: string;
  fecha_contacto: Date | null;
  fecha_creacion: Date;
  ultima_actualizacion: Date;
}
