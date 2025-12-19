import { createClient } from '@supabase/supabase-js';

// Credenciales directas para evitar bloqueo de secrets
const SUPABASE_URL = 'https://imuhtilqwbqjuuvztfjp.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltdWh0aWxxd2JxanV1dnp0ZmpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzI5MzEsImV4cCI6MjA4MTY0ODkzMX0.aXHKbUUnzOXuiCbx3OalgHPXEQ2rbiw0eDG56y_MBU4';

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export type Ficha = {
  id: string;
  titulo: string;
  institucion: string;
  canal_recomendado: string;
  prioridad: 'alta' | 'media' | 'baja';
  email: string | null;
  username: string | null;
  telefono: string | null;
  url: string;
  propuesta_comunicativa: string;
  estado: 'pendiente' | 'contactado' | 'descartado';
  timing_razon: string | null;
  created_at: string;
};
