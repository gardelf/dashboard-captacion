import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  ExternalLink, 
  Copy, 
  CheckCircle, 
  Loader2,
  Mail,
  User,
  Calendar,
  Building2,
  MessageCircle,
  Hash,
  Globe
} from 'lucide-react';
import { toast } from 'sonner';

interface Ficha {
  id: string;
  tipo: string;
  keyword: string;
  url: string;
  titulo: string;
  snippet: string;
  dominio: string;
  institucion: string | null;
  email: string | null;
  telefono: string | null;
  tiene_formulario: boolean | null;
  plataforma_social: string;
  username: string | null;
  subreddit: string | null;
  grupo_facebook: string | null;
  fecha_detectada: string | null;
  prioridad: string | null;
  propuesta_comunicativa: string | null;
  canal_recomendado: string | null;
  estado: string;
  procesada: string;
  fecha_contacto: string | null;
  fecha_creacion: string;
  ultima_actualizacion: string;
}

interface Stats {
  total: number;
  pendientes: number;
  contactados: number;
  descartados: number;
  procesadas: number;
}

export default function Home() {
  const [fichas, setFichas] = useState<Ficha[]>([]);
  const [stats, setStats] = useState<Stats>({
    total: 0,
    pendientes: 0,
    contactados: 0,
    descartados: 0,
    procesadas: 0
  });
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState('todos');
  const [vista, setVista] = useState<'tarjetas' | 'tabla'>('tarjetas');

  // Cargar datos desde JSON estático
  useEffect(() => {
    const cargarFichas = async () => {
      try {
        const response = await fetch('/fichas.json');
        if (!response.ok) throw new Error('Error cargando fichas');
        
        const data = await response.json();
        setFichas(data.fichas || []);
        setStats(data.estadisticas || {});
        toast.success('Fichas cargadas correctamente');
      } catch (error) {
        console.error('Error cargando fichas:', error);
        toast.error('Error al cargar fichas');
      } finally {
        setLoading(false);
      }
    };

    cargarFichas();
  }, []);

  const fichasFiltradas = fichas.filter(f => {
    if (filtro === 'todos') return true;
    if (filtro === 'pendientes') return f.estado === 'pendiente';
    if (filtro === 'contactados') return f.estado === 'contactado';
    if (filtro === 'descartados') return f.estado === 'descartado';
    if (filtro === 'procesadas') return f.procesada === 'SÍ';
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Dashboard de Captación</h1>
          <p className="text-slate-400">Gestión de leads de estudiantes internacionales</p>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">{stats.total}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Pendientes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-400">{stats.pendientes}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Contactados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">{stats.contactados}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Descartados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-400">{stats.descartados}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Procesadas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400">{stats.procesadas}</div>
            </CardContent>
          </Card>
        </div>

        {/* Controles */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex gap-2">
            {['todos', 'pendientes', 'contactados', 'descartados', 'procesadas'].map(f => (
              <Button
                key={f}
                onClick={() => setFiltro(f)}
                variant={filtro === f ? 'default' : 'outline'}
                className="capitalize"
              >
                {f}
              </Button>
            ))}
          </div>

          <div className="flex gap-2 ml-auto">
            <Button
              onClick={() => setVista('tarjetas')}
              variant={vista === 'tarjetas' ? 'default' : 'outline'}
            >
              Tarjetas
            </Button>
            <Button
              onClick={() => setVista('tabla')}
              variant={vista === 'tabla' ? 'default' : 'outline'}
            >
              Tabla
            </Button>
          </div>
        </div>

        {/* Fichas */}
        {vista === 'tarjetas' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {fichasFiltradas.map(ficha => (
              <Card key={ficha.id} className="bg-slate-800 border-slate-700 hover:border-slate-600 transition">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg text-white line-clamp-2">{ficha.titulo}</CardTitle>
                      <p className="text-xs text-slate-400 mt-1">{ficha.dominio}</p>
                    </div>
                    <Badge className="ml-2">{ficha.estado}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-slate-300 line-clamp-2">{ficha.snippet}</p>

                  <div className="space-y-2">
                    {ficha.email && (
                      <div className="flex items-center gap-2 text-sm text-slate-300">
                        <Mail className="w-4 h-4" />
                        <span className="truncate">{ficha.email}</span>
                      </div>
                    )}
                    {ficha.telefono && (
                      <div className="flex items-center gap-2 text-sm text-slate-300">
                        <MessageCircle className="w-4 h-4" />
                        <span>{ficha.telefono}</span>
                      </div>
                    )}
                    {ficha.institucion && (
                      <div className="flex items-center gap-2 text-sm text-slate-300">
                        <Building2 className="w-4 h-4" />
                        <span className="truncate">{ficha.institucion}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => window.open(ficha.url, '_blank')}
                    >
                      <ExternalLink className="w-4 h-4 mr-1" />
                      Ver
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        navigator.clipboard.writeText(ficha.url);
                        toast.success('URL copiada');
                      }}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-slate-300">
              <thead className="bg-slate-700 text-slate-200">
                <tr>
                  <th className="px-4 py-2 text-left">ID</th>
                  <th className="px-4 py-2 text-left">Título</th>
                  <th className="px-4 py-2 text-left">Dominio</th>
                  <th className="px-4 py-2 text-left">Email</th>
                  <th className="px-4 py-2 text-left">Estado</th>
                  <th className="px-4 py-2 text-left">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {fichasFiltradas.map(ficha => (
                  <tr key={ficha.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                    <td className="px-4 py-2">{ficha.id}</td>
                    <td className="px-4 py-2 truncate max-w-xs">{ficha.titulo}</td>
                    <td className="px-4 py-2">{ficha.dominio}</td>
                    <td className="px-4 py-2">{ficha.email || '-'}</td>
                    <td className="px-4 py-2">
                      <Badge>{ficha.estado}</Badge>
                    </td>
                    <td className="px-4 py-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(ficha.url, '_blank')}
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {fichasFiltradas.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-400">No hay fichas que mostrar</p>
          </div>
        )}
      </div>
    </div>
  );
}
