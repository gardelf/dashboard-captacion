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
}

export default function Home() {
  const [fichas, setFichas] = useState<Ficha[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, pendientes: 0, contactados: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarFichas();
  }, []);

  async function cargarFichas() {
    try {
      const response = await fetch('/api/fichas');
      if (!response.ok) {
        throw new Error('Error al cargar fichas');
      }
      const data = await response.json();
      setFichas(data.fichas || []);
      setStats(data.stats || { total: 0, pendientes: 0, contactados: 0 });
    } catch (error) {
      console.error('Error:', error);
      toast.error(`Error al cargar fichas: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setLoading(false);
    }
  }

  async function marcarContactada(id: string) {
    try {
      const response = await fetch(`/api/fichas/${id}/contactar`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Error al marcar como contactada');
      }
      
      toast.success('Ficha marcada como contactada');
      cargarFichas();
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error al actualizar el estado');
    }
  }

  async function descartarFicha(id: string) {
    try {
      const response = await fetch(`/api/fichas/${id}/descartar`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Error al descartar ficha');
      }
      
      toast.success('Ficha descartada');
      cargarFichas();
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error al descartar ficha');
    }
  }

  async function descartarTodasBajas() {
    const fichasBajas = fichas.filter(f => 
      f.prioridad?.toLowerCase() === 'baja' && f.estado === 'pendiente'
    );
    
    if (fichasBajas.length === 0) {
      toast.info('No hay fichas de prioridad baja pendientes');
      return;
    }
    
    const confirmacion = confirm(`¿Descartar ${fichasBajas.length} ficha(s) de prioridad baja?`);
    if (!confirmacion) return;
    
    toast.info(`Descartando ${fichasBajas.length} fichas...`);
    
    let exitosas = 0;
    let fallidas = 0;
    
    for (const ficha of fichasBajas) {
      try {
        const response = await fetch(`/api/fichas/${ficha.id}/descartar`, {
          method: 'POST',
        });
        
        if (response.ok) {
          exitosas++;
        } else {
          fallidas++;
        }
      } catch (error) {
        fallidas++;
      }
    }
    
    toast.success(`✅ ${exitosas} fichas descartadas${fallidas > 0 ? ` (❌ ${fallidas} errores)` : ''}`);
    cargarFichas();
  }

  function copiarTexto(texto: string, tipo: string) {
    navigator.clipboard.writeText(texto);
    toast.success(`${tipo} copiado al portapapeles`);
  }

  function abrirURL(url: string) {
    window.open(url, '_blank');
  }

  function formatearFecha(fecha: string | null): string {
    if (!fecha) return 'N/A';
    try {
      return new Date(fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return fecha;
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header & Stats */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
              Dashboard Captación Estudiantes
            </h1>
            <p className="text-slate-500 dark:text-slate-400">
              Fichas pendientes de contactar
            </p>
          </div>
          <div className="flex flex-col md:flex-row gap-2">
            <div className="flex gap-2">
              <Card className="p-4 py-2 bg-white dark:bg-slate-800">
                <div className="text-xs text-slate-500 uppercase font-bold">Total</div>
                <div className="text-2xl font-bold text-slate-900 dark:text-white">{stats.total}</div>
              </Card>
              <Card className="p-4 py-2 bg-white dark:bg-slate-800">
                <div className="text-xs text-slate-500 uppercase font-bold">Pendientes</div>
                <div className="text-2xl font-bold text-amber-600">{stats.pendientes}</div>
              </Card>
              <Card className="p-4 py-2 bg-white dark:bg-slate-800">
                <div className="text-xs text-slate-500 uppercase font-bold">Contactados</div>
                <div className="text-2xl font-bold text-green-600">{stats.contactados}</div>
              </Card>
            </div>
            
            {/* Botón descarte masivo prioridad baja */}
            {fichas.filter(f => f.prioridad?.toLowerCase() === 'baja' && f.estado === 'pendiente').length > 0 && (
              <Button
                variant="outline"
                className="border-orange-300 bg-orange-50 hover:bg-orange-100 dark:bg-orange-950 dark:border-orange-800 dark:hover:bg-orange-900 text-orange-700 dark:text-orange-300"
                onClick={descartarTodasBajas}
              >
                <span className="mr-2">🗑️</span>
                Descartar todas las bajas ({fichas.filter(f => f.prioridad?.toLowerCase() === 'baja' && f.estado === 'pendiente').length})
              </Button>
            )}
          </div>
        </div>

        {/* Fichas */}
        {fichas.length === 0 ? (
          <Card className="p-12 text-center">
            <div className="text-slate-400 dark:text-slate-500">
              <CheckCircle className="h-16 w-16 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">¡Todo al día!</h3>
              <p>No hay fichas pendientes de contactar</p>
            </div>
          </Card>
        ) : (
          <div className="grid gap-4">
            {fichas.map((ficha) => (
              <Card key={ficha.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                
                {/* HEADER con badges y metadata principal */}
                <CardHeader className="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-slate-800 dark:to-slate-850 pb-4">
                  <div className="flex flex-wrap justify-between items-start gap-3">
                    
                    {/* Título */}
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg mb-3 break-words">
                        {ficha.titulo || 'Sin título'}
                      </CardTitle>
                      
                      {/* Badges principales */}
                      <div className="flex flex-wrap gap-2">
                        {ficha.prioridad && (
                          <Badge 
                            variant={
                              ficha.prioridad.toLowerCase() === 'alta' ? 'destructive' : 
                              ficha.prioridad.toLowerCase() === 'media' ? 'default' : 
                              'outline'
                            }
                            className="uppercase"
                          >
                            {ficha.prioridad}
                          </Badge>
                        )}
                        
                        {ficha.canal_recomendado && (
                          <Badge variant="secondary" className="capitalize">
                            📢 {ficha.canal_recomendado}
                          </Badge>
                        )}
                        
                        {ficha.institucion && (
                          <Badge variant="outline" className="capitalize">
                            <Building2 className="h-3 w-3 mr-1" />
                            {ficha.institucion}
                          </Badge>
                        )}
                        
                        <Badge variant="outline" className="capitalize">
                          <Globe className="h-3 w-3 mr-1" />
                          {ficha.plataforma_social}
                        </Badge>
                      </div>
                    </div>
                    
                    {/* Metadata derecha */}
                    <div className="flex flex-col gap-1 text-xs text-slate-500 dark:text-slate-400 text-right">
                      <div className="flex items-center gap-1">
                        <Hash className="h-3 w-3" />
                        <span className="font-mono">{ficha.id.substring(0, 20)}...</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{formatearFecha(ficha.fecha_creacion)}</span>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-4 space-y-4">
                  
                  {/* Grid de información de contacto */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    
                    {/* Email */}
                    {ficha.email && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <Mail className="h-4 w-4 text-slate-500 flex-shrink-0" />
                        <span className="text-sm font-mono flex-1 truncate">{ficha.email}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copiarTexto(ficha.email!, 'Email')}
                          className="h-6 w-6 p-0 flex-shrink-0"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    )}

                    {/* Username */}
                    {ficha.username && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <User className="h-4 w-4 text-slate-500 flex-shrink-0" />
                        <span className="text-sm font-mono flex-1 truncate">@{ficha.username}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copiarTexto(ficha.username!, 'Username')}
                          className="h-6 w-6 p-0 flex-shrink-0"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                    
                    {/* Tipo */}
                    <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                      <span className="text-xs text-slate-500 uppercase font-bold">Tipo:</span>
                      <span className="text-sm capitalize">{ficha.tipo}</span>
                    </div>
                    
                    {/* Dominio */}
                    <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                      <span className="text-xs text-slate-500 uppercase font-bold">Dominio:</span>
                      <span className="text-sm font-mono truncate">{ficha.dominio}</span>
                    </div>
                    
                    {/* Subreddit */}
                    {ficha.subreddit && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <span className="text-xs text-slate-500 uppercase font-bold">Subreddit:</span>
                        <span className="text-sm">r/{ficha.subreddit}</span>
                      </div>
                    )}
                    
                    {/* Grupo Facebook */}
                    {ficha.grupo_facebook && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <span className="text-xs text-slate-500 uppercase font-bold">Grupo FB:</span>
                        <span className="text-sm truncate">{ficha.grupo_facebook}</span>
                      </div>
                    )}
                  </div>

                  {/* Snippet - Contexto */}
                  {ficha.snippet && (
                    <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                      <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-2 text-sm uppercase tracking-wide">
                        📋 Contexto / Descripción
                      </h4>
                      <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                        {ficha.snippet}
                      </p>
                    </div>
                  )}

                  {/* Propuesta Comunicativa */}
                  {ficha.propuesta_comunicativa && (
                    <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                      <div className="flex justify-between items-start gap-2 mb-2">
                        <h4 className="font-semibold text-blue-900 dark:text-blue-100 flex items-center gap-2">
                          <MessageCircle className="h-4 w-4" />
                          Propuesta Comunicativa
                        </h4>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copiarTexto(ficha.propuesta_comunicativa!, 'Propuesta')}
                          className="h-8"
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          Copiar
                        </Button>
                      </div>
                      <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                        {ficha.propuesta_comunicativa}
                      </p>
                    </div>
                  )}

                  {/* Botones de acción */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => abrirURL(ficha.url)}
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Abrir URL
                    </Button>
                    <Button
                      variant="default"
                      className="flex-1 bg-green-600 hover:bg-green-700"
                      onClick={() => marcarContactada(ficha.id)}
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Contactada
                    </Button>
                    <Button
                      variant="destructive"
                      className="flex-1"
                      onClick={() => descartarFicha(ficha.id)}
                    >
                      <span className="mr-2">❌</span>
                      Descartar
                    </Button>
                  </div>
                  
                  {/* Botón rápido de descarte para prioridad baja */}
                  {ficha.prioridad?.toLowerCase() === 'baja' && ficha.estado === 'pendiente' && (
                    <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                      <Button
                        variant="outline"
                        className="w-full border-orange-300 bg-orange-50 hover:bg-orange-100 dark:bg-orange-950 dark:border-orange-800 dark:hover:bg-orange-900 text-orange-700 dark:text-orange-300"
                        onClick={() => descartarFicha(ficha.id)}
                      >
                        <span className="mr-2">🗑️</span>
                        Descarte rápido (Prioridad Baja)
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
