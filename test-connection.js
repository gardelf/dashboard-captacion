import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://imuhtilqwbqjuuvztfjp.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltdWh0aWxxd2JxanV1dnp0ZmpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzI5MzEsImV4cCI6MjA4MTY0ODkzMX0.aXHKbUUnzOXuiCbx3OalgHPXEQ2rbiw0eDG56y_MBU4';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function testConnection() {
  console.log('🔄 Probando conexión a Supabase...');
  
  const { data, error, count } = await supabase
    .from('fichas')
    .select('*', { count: 'exact', head: true });

  if (error) {
    console.error('❌ Error de conexión:', error.message);
    return;
  }

  console.log(`✅ Conexión exitosa! Se encontraron ${count} fichas.`);
  
  const { data: fichas } = await supabase
    .from('fichas')
    .select('id, titulo, canal_recomendado')
    .limit(3);
    
  console.log('📋 Primeras 3 fichas:', fichas);
}

testConnection();
