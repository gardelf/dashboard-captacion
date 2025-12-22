import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Mail, User, ExternalLink, CheckCircle, Copy, MessageCircle } from "lucide-react";
import { toast } from "sonner";

interface Ficha {
  id: string;
  titulo: string | null;
  snippet: string | null;
  url: string;
  institucion: string | null;
  email: string | null;
  username: string | null;
  subreddit: string | null;
  grupo_facebook: string | null;
  propuesta_comunicativa: string | null;
  canal_recomendado: string | null;
  prioridad: string | null;
  fecha_creacion: string;
}

export default function Home() {
  const [fichas, setFichas] = useState<Ficha[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, pendientes: 0, contactados: 0 });

  useEffect(() => {
    fetchFichas();
    fetchStats();
  }, []);

  async function fetchFichas() {
    setLoading(true);
    try {
      const response = await fetch('/api/fichas/pendientes');
      const data = await response.json();
      
      if (data.success) {
        setFichas(data.data);
      } else {
        toast.error('Error al cargar fichas');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  }

  async function fetchStats() {
    try {
      const response = await fetch('/api/fichas/stats/summary');
      const data = await response.json();
      
      if (data.success) {
        setStats({
          total: parseInt(data.data.total) || 0,
          pendientes: parseInt(data.data.pendientes) || 0,
          contactados: parseInt(data.data.contactados) || 0
        });
      }
    } catch (error) {
      console.error('Error obteniendo stats:', error);
    }
  }

  async function marcarContactada(id: string) {
    try {
      const response = await fetch(`/api/fichas/${id}/contactar`, {
        method: 'PATCH'
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('Ficha marcada como contactada');
        // Remover de la lista
        setFichas(prev => prev.filter(f => f.id !== id));
        // Actualizar stats
        setStats(prev => ({
          ...prev,
          pendientes: prev.pendientes - 1,
          contactados: prev.contactados + 1
        }));
      } else {
        toast.error('Error al marcar ficha');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error de conexión');
    }
  }

  function copiarTexto(texto: string, tipo: string) {
    navigator.clipboard.writeText(texto);
    toast.success(`${tipo} copiado al portapapeles`);
  }

  function abrirURL(url: string) {
    window.open(url, '_blank');
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
                <CardHeader className="bg-slate-100 dark:bg-slate-800 pb-3">
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">
                        {ficha.titulo || 'Sin título'}
                      </CardTitle>
                      {ficha.institucion && (
                        <Badge variant="secondary" className="mb-2">
                          {ficha.institucion}
                        </Badge>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {ficha.prioridad && (
                        <Badge 
                          variant={
                            ficha.prioridad === 'Alta' ? 'destructive' : 
                            ficha.prioridad === 'Media' ? 'default' : 
                            'outline'
                          }
                        >
                          {ficha.prioridad}
                        </Badge>
                      )}
                      {ficha.canal_recomendado && (
                        <Badge variant="outline" className="capitalize">
                          {ficha.canal_recomendado}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-4 space-y-4">
                  {/* Snippet */}
                  {ficha.snippet && (
                    <div className="text-sm text-slate-600 dark:text-slate-400">
                      {ficha.snippet}
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
                      <p className="text-sm text-blue-800 dark:text-blue-200">
                        {ficha.propuesta_comunicativa}
                      </p>
                    </div>
                  )}

                  {/* Información de contacto */}
                  <div className="flex flex-wrap gap-3">
                    {ficha.email && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <Mail className="h-4 w-4 text-slate-500" />
                        <span className="text-sm font-mono">{ficha.email}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copiarTexto(ficha.email!, 'Email')}
                          className="h-6 w-6 p-0"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    )}

                    {ficha.username && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <User className="h-4 w-4 text-slate-500" />
                        <span className="text-sm font-mono">@{ficha.username}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copiarTexto(ficha.username!, 'Username')}
                          className="h-6 w-6 p-0"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    )}

                    {ficha.subreddit && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <span className="text-sm">r/{ficha.subreddit}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copiarTexto(`r/${ficha.subreddit}`, 'Subreddit')}
                          className="h-6 w-6 p-0"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    )}

                    {ficha.grupo_facebook && (
                      <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <span className="text-sm">{ficha.grupo_facebook}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copiarTexto(ficha.grupo_facebook!, 'Grupo')}
                          className="h-6 w-6 p-0"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Acciones */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      onClick={() => abrirURL(ficha.url)}
                      className="flex-1"
                      variant="outline"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Abrir URL
                    </Button>
                    <Button
                      onClick={() => marcarContactada(ficha.id)}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Marcar como Contactada
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
