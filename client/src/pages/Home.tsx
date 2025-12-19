import { useEffect, useState } from "react";
import { supabase, type Ficha } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Mail, MessageCircle, ExternalLink, CheckCircle, XCircle, Copy, Search, Filter, LayoutGrid, List } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [pin, setPin] = useState("");
  const [fichas, setFichas] = useState<Ficha[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("pendiente");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    const savedAuth = localStorage.getItem("dashboard_auth");
    if (savedAuth === "true") {
      setIsAuthenticated(true);
      fetchFichas();
    }
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (pin === "MADRID2025") {
      setIsAuthenticated(true);
      localStorage.setItem("dashboard_auth", "true");
      fetchFichas();
      toast.success("Acceso concedido");
    } else {
      toast.error("PIN incorrecto");
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Acceso Restringido</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Input
                  type="password"
                  placeholder="Introduce el PIN de acceso"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  className="text-center text-lg tracking-widest"
                />
              </div>
              <Button type="submit" className="w-full">
                Entrar
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  async function fetchFichas() {
    setLoading(true);
    const { data, error } = await supabase
      .from('fichas')
      .select('*')
      .order('prioridad', { ascending: true }) // alta (1) -> baja (3) if mapped, but usually string. Let's check sort.
      .order('created_at', { ascending: false });

    if (error) {
      toast.error("Error al cargar fichas: " + error.message);
    } else {
      setFichas(data as Ficha[]);
    }
    setLoading(false);
  }

  async function updateStatus(id: string, newStatus: 'contactado' | 'descartado' | 'pendiente') {
    // Optimistic update
    setFichas(prev => prev.map(f => f.id === id ? { ...f, estado: newStatus } : f));
    
    const { error } = await supabase
      .from('fichas')
      .update({ estado: newStatus })
      .eq('id', id);

    if (error) {
      toast.error("Error al actualizar estado");
      // Revert
      fetchFichas();
    } else {
      toast.success(`Ficha marcada como ${newStatus}`);
    }
  }

  const filteredFichas = fichas.filter(ficha => {
    const matchesSearch = 
      ficha.titulo?.toLowerCase().includes(filter.toLowerCase()) ||
      ficha.institucion?.toLowerCase().includes(filter.toLowerCase()) ||
      ficha.canal_recomendado?.toLowerCase().includes(filter.toLowerCase());
    
    const matchesStatus = statusFilter === "all" || ficha.estado === statusFilter;
    const matchesPriority = priorityFilter === "all" || ficha.prioridad === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  const stats = {
    total: fichas.length,
    contactados: fichas.filter(f => f.estado === 'contactado').length,
    pendientes: fichas.filter(f => f.estado === 'pendiente').length,
    descartados: fichas.filter(f => f.estado === 'descartado').length
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header & Stats */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Dashboard Captación</h1>
            <p className="text-slate-500 dark:text-slate-400">Gestionando {stats.total} oportunidades de estudiantes</p>
          </div>
          <div className="flex gap-2">
            <Card className="p-4 py-2 bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <div className="text-xs text-slate-500 uppercase font-bold">Pendientes</div>
              <div className="text-2xl font-bold text-amber-600">{stats.pendientes}</div>
            </Card>
            <Card className="p-4 py-2 bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <div className="text-xs text-slate-500 uppercase font-bold">Contactados</div>
              <div className="text-2xl font-bold text-green-600">{stats.contactados}</div>
            </Card>
          </div>
        </div>

        {/* Filters */}
        <Card className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-500" />
              <Input 
                placeholder="Buscar por título, institución..." 
                className="pl-8"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="pendiente">Pendientes</SelectItem>
                <SelectItem value="contactado">Contactados</SelectItem>
                <SelectItem value="descartado">Descartados</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Prioridad" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las prioridades</SelectItem>
                <SelectItem value="alta">Alta</SelectItem>
                <SelectItem value="media">Media</SelectItem>
                <SelectItem value="baja">Baja</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
              <Button 
                variant={viewMode === 'grid' ? 'default' : 'ghost'} 
                size="icon" 
                className="h-8 w-8"
                onClick={() => setViewMode('grid')}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button 
                variant={viewMode === 'list' ? 'default' : 'ghost'} 
                size="icon" 
                className="h-8 w-8"
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Table */}
        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
          </div>
        ) : (
          <>
            {viewMode === 'grid' ? (
              <div className="grid gap-4">
                {filteredFichas.map((ficha) => (
                  <FichaCard key={ficha.id} ficha={ficha} onUpdateStatus={updateStatus} />
                ))}
              </div>
            ) : (
              <FichaList fichas={filteredFichas} onUpdateStatus={updateStatus} />
            )}
            
            {filteredFichas.length === 0 && (
              <div className="text-center py-20 text-slate-500">
                No se encontraron fichas con estos filtros
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function FichaList({ fichas, onUpdateStatus }: { fichas: Ficha[], onUpdateStatus: (id: string, status: any) => void }) {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copiado al portapapeles");
  };

  const openAction = (ficha: Ficha) => {
    if (ficha.canal_recomendado === 'email' && ficha.email) {
      const subject = encodeURIComponent("Alojamiento para estudiantes internacionales en Madrid");
      const body = encodeURIComponent(ficha.propuesta_comunicativa);
      window.open(`https://mail.google.com/mail/?view=cm&fs=1&to=${ficha.email}&su=${subject}&body=${body}`, '_blank');
    } else if (ficha.canal_recomendado === 'reddit' && ficha.url) {
      copyToClipboard(ficha.propuesta_comunicativa);
      window.open(ficha.url, '_blank');
      toast.info("Propuesta copiada. Pegala en Reddit.");
    } else if (ficha.canal_recomendado === 'whatsapp' && ficha.telefono) {
      const text = encodeURIComponent(ficha.propuesta_comunicativa);
      window.open(`https://wa.me/${ficha.telefono}?text=${text}`, '_blank');
    } else {
      copyToClipboard(ficha.propuesta_comunicativa);
      window.open(ficha.url, '_blank');
      toast.info("Propuesta copiada. Pegala en el formulario.");
    }
  };

  const getPriorityColor = (p: string) => {
    switch(p) {
      case 'alta': return 'bg-red-100 text-red-800 border-red-200';
      case 'media': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getChannelIcon = (c: string) => {
    if (c?.includes('email')) return <Mail className="h-4 w-4" />;
    if (c?.includes('reddit') || c?.includes('facebook')) return <MessageCircle className="h-4 w-4" />;
    return <ExternalLink className="h-4 w-4" />;
  };

  return (
    <Card className="overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">Prioridad</TableHead>
            <TableHead className="w-[120px]">Canal</TableHead>
            <TableHead>Título / Institución</TableHead>
            <TableHead className="w-[300px]">Propuesta (Preview)</TableHead>
            <TableHead className="text-right">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {fichas.map((ficha) => (
            <TableRow key={ficha.id} className={ficha.estado === 'contactado' ? 'opacity-60 bg-slate-50' : ''}>
              <TableCell>
                <Badge variant="outline" className={getPriorityColor(ficha.prioridad)}>
                  {ficha.prioridad.toUpperCase()}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  {getChannelIcon(ficha.canal_recomendado)}
                  <span className="capitalize">{ficha.canal_recomendado}</span>
                </div>
              </TableCell>
              <TableCell>
                <div className="font-medium text-slate-900">{ficha.titulo}</div>
                <div className="text-sm text-slate-500">{ficha.institucion}</div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2 group">
                  <div className="truncate max-w-[250px] text-sm text-slate-500 font-mono">
                    {ficha.propuesta_comunicativa}
                  </div>
                  <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100" onClick={() => copyToClipboard(ficha.propuesta_comunicativa)}>
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex justify-end gap-2">
                  <Button size="sm" variant="outline" onClick={() => openAction(ficha)}>
                    Contactar
                  </Button>
                  <Button 
                    size="icon" 
                    variant={ficha.estado === 'contactado' ? "default" : "ghost"}
                    className={`h-8 w-8 ${ficha.estado === 'contactado' ? 'bg-green-600 hover:bg-green-700' : 'text-green-600 hover:bg-green-50'}`}
                    onClick={() => onUpdateStatus(ficha.id, 'contactado')}
                  >
                    <CheckCircle className="h-4 w-4" />
                  </Button>
                  <Button 
                    size="icon" 
                    variant={ficha.estado === 'descartado' ? "default" : "ghost"}
                    className={`h-8 w-8 ${ficha.estado === 'descartado' ? 'bg-slate-600' : 'text-slate-400 hover:bg-slate-50'}`}
                    onClick={() => onUpdateStatus(ficha.id, 'descartado')}
                  >
                    <XCircle className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}

function FichaCard({ ficha, onUpdateStatus }: { ficha: Ficha, onUpdateStatus: (id: string, status: any) => void }) {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copiado al portapapeles");
  };

  const openAction = () => {
    if (ficha.canal_recomendado === 'email' && ficha.email) {
      const subject = encodeURIComponent("Alojamiento para estudiantes internacionales en Madrid");
      const body = encodeURIComponent(ficha.propuesta_comunicativa);
      window.open(`https://mail.google.com/mail/?view=cm&fs=1&to=${ficha.email}&su=${subject}&body=${body}`, '_blank');
    } else if (ficha.canal_recomendado === 'reddit' && ficha.url) {
      copyToClipboard(ficha.propuesta_comunicativa);
      window.open(ficha.url, '_blank');
      toast.info("Propuesta copiada. Pegala en Reddit.");
    } else if (ficha.canal_recomendado === 'whatsapp' && ficha.telefono) {
      const text = encodeURIComponent(ficha.propuesta_comunicativa);
      window.open(`https://wa.me/${ficha.telefono}?text=${text}`, '_blank');
    } else {
      // Default fallback (forms, etc)
      copyToClipboard(ficha.propuesta_comunicativa);
      window.open(ficha.url, '_blank');
      toast.info("Propuesta copiada. Pegala en el formulario.");
    }
  };

  const getPriorityColor = (p: string) => {
    switch(p) {
      case 'alta': return 'bg-red-100 text-red-800 border-red-200';
      case 'media': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getChannelIcon = (c: string) => {
    if (c?.includes('email')) return <Mail className="h-4 w-4" />;
    if (c?.includes('reddit') || c?.includes('facebook')) return <MessageCircle className="h-4 w-4" />;
    return <ExternalLink className="h-4 w-4" />;
  };

  return (
    <Card className={`transition-all hover:shadow-md ${ficha.estado === 'contactado' ? 'opacity-60 bg-slate-50' : 'bg-white'}`}>
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row gap-6">
          
          {/* Left: Info */}
          <div className="flex-1 space-y-3">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={getPriorityColor(ficha.prioridad)}>
                {ficha.prioridad.toUpperCase()}
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                {getChannelIcon(ficha.canal_recomendado)}
                {ficha.canal_recomendado}
              </Badge>
              <span className="text-xs text-slate-400 font-mono">{ficha.id.split('-').pop()}</span>
            </div>
            
            <h3 className="text-lg font-semibold text-slate-900 leading-tight">
              {ficha.titulo}
            </h3>
            <p className="text-sm text-slate-600 font-medium">
              {ficha.institucion}
            </p>
            
            {ficha.timing_razon && (
              <div className="text-xs bg-blue-50 text-blue-700 p-2 rounded border border-blue-100">
                💡 {ficha.timing_razon}
              </div>
            )}
          </div>

          {/* Middle: Proposal */}
          <div className="flex-1 bg-slate-50 p-3 rounded border border-slate-100 text-sm text-slate-600 relative group">
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => copyToClipboard(ficha.propuesta_comunicativa)}>
                <Copy className="h-3 w-3" />
              </Button>
            </div>
            <p className="whitespace-pre-wrap line-clamp-4 hover:line-clamp-none transition-all">
              {ficha.propuesta_comunicativa}
            </p>
          </div>

          {/* Right: Actions */}
          <div className="flex flex-row md:flex-col gap-2 justify-center min-w-[140px]">
            <Button 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white shadow-sm" 
              onClick={openAction}
            >
              {getChannelIcon(ficha.canal_recomendado)}
              <span className="ml-2">Contactar</span>
            </Button>
            
            <div className="flex gap-2">
              <Button 
                variant={ficha.estado === 'contactado' ? "default" : "outline"}
                className={`flex-1 ${ficha.estado === 'contactado' ? 'bg-green-600 hover:bg-green-700' : 'text-green-600 border-green-200 hover:bg-green-50'}`}
                onClick={() => onUpdateStatus(ficha.id, 'contactado')}
              >
                <CheckCircle className="h-4 w-4" />
              </Button>
              <Button 
                variant={ficha.estado === 'descartado' ? "default" : "outline"}
                className={`flex-1 ${ficha.estado === 'descartado' ? 'bg-slate-600' : 'text-slate-400 border-slate-200 hover:bg-slate-50'}`}
                onClick={() => onUpdateStatus(ficha.id, 'descartado')}
              >
                <XCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>

        </div>
      </CardContent>
    </Card>
  );
}
