/**
 * API endpoints para gestionar fichas
 */

import { Router } from 'express';
import pool, { type Ficha } from '../db/postgres';

const router = Router();

/**
 * GET /api/fichas/pendientes
 * Obtiene todas las fichas pendientes (no contactadas)
 */
router.get('/pendientes', async (req, res) => {
  try {
    const result = await pool.query<Ficha>(`
      SELECT * FROM fichas 
      WHERE estado = 'pendiente' 
      ORDER BY 
        CASE prioridad 
          WHEN 'Alta' THEN 1
          WHEN 'Media' THEN 2
          WHEN 'Baja' THEN 3
          ELSE 4
        END,
        fecha_creacion DESC
    `);
    
    res.json({
      success: true,
      data: result.rows,
      count: result.rows.length
    });
  } catch (error: any) {
    console.error('Error obteniendo fichas pendientes:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener fichas pendientes',
      message: error.message
    });
  }
});

/**
 * GET /api/fichas/:id
 * Obtiene una ficha específica por ID
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query<Ficha>(
      'SELECT * FROM fichas WHERE id = $1',
      [id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Ficha no encontrada'
      });
    }
    
    res.json({
      success: true,
      data: result.rows[0]
    });
  } catch (error: any) {
    console.error('Error obteniendo ficha:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener ficha',
      message: error.message
    });
  }
});

/**
 * PATCH /api/fichas/:id/contactar
 * Marca una ficha como contactada
 */
router.patch('/:id/contactar', async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query<Ficha>(
      `UPDATE fichas 
       SET estado = 'contactado', 
           fecha_contacto = CURRENT_TIMESTAMP,
           ultima_actualizacion = CURRENT_TIMESTAMP
       WHERE id = $1
       RETURNING *`,
      [id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Ficha no encontrada'
      });
    }
    
    res.json({
      success: true,
      data: result.rows[0],
      message: 'Ficha marcada como contactada'
    });
  } catch (error: any) {
    console.error('Error marcando ficha como contactada:', error);
    res.status(500).json({
      success: false,
      error: 'Error al marcar ficha como contactada',
      message: error.message
    });
  }
});

/**
 * PATCH /api/fichas/:id/descartar
 * Marca una ficha como descartada
 */
router.patch('/:id/descartar', async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query<Ficha>(
      `UPDATE fichas 
       SET estado = 'descartado',
           ultima_actualizacion = CURRENT_TIMESTAMP
       WHERE id = $1
       RETURNING *`,
      [id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'Ficha no encontrada'
      });
    }
    
    res.json({
      success: true,
      data: result.rows[0],
      message: 'Ficha descartada'
    });
  } catch (error: any) {
    console.error('Error descartando ficha:', error);
    res.status(500).json({
      success: false,
      error: 'Error al descartar ficha',
      message: error.message
    });
  }
});

/**
 * GET /api/fichas/stats
 * Obtiene estadísticas de las fichas
 */
router.get('/stats/summary', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE estado = 'pendiente') as pendientes,
        COUNT(*) FILTER (WHERE estado = 'contactado') as contactados,
        COUNT(*) FILTER (WHERE estado = 'descartado') as descartados,
        COUNT(*) FILTER (WHERE procesada = 'SI') as procesadas,
        COUNT(*) FILTER (WHERE procesada = 'NO') as sin_procesar
      FROM fichas
    `);
    
    res.json({
      success: true,
      data: result.rows[0]
    });
  } catch (error: any) {
    console.error('Error obteniendo estadísticas:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener estadísticas',
      message: error.message
    });
  }
});

export default router;
