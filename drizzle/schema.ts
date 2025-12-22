import { boolean, int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Tabla de fichas de estudiantes captados mediante búsqueda automatizada.
 * Contiene información de contacto, propuestas comunicativas y estado de seguimiento.
 */
export const fichas = mysqlTable("fichas", {
  /** ID único generado: formato SIG-YYYYMMDD-xxxxxxxx */
  id: varchar("id", { length: 64 }).primaryKey(),
  /** Tipo de señal de búsqueda */
  tipo: text("tipo"),
  /** Palabra clave de búsqueda original */
  keyword: text("keyword"),
  /** URL del resultado (única) */
  url: text("url").notNull(),
  /** Título del resultado */
  titulo: text("titulo"),
  /** Snippet de Google */
  snippet: text("snippet"),
  /** Dominio limpio */
  dominio: text("dominio"),
  /** Nombre de institución (llenado por ChatGPT) */
  institucion: text("institucion"),
  /** Email de contacto (llenado por ChatGPT) */
  email: text("email"),
  /** Teléfono de contacto (llenado por ChatGPT) */
  telefono: text("telefono"),
  /** Tiene formulario de contacto (llenado por ChatGPT) */
  tiene_formulario: boolean("tiene_formulario"),
  /** Plataforma social: Reddit/Facebook/LinkedIn/Web */
  plataforma_social: text("plataforma_social"),
  /** Username extraído */
  username: text("username"),
  /** Nombre del subreddit */
  subreddit: text("subreddit"),
  /** Nombre del grupo de Facebook */
  grupo_facebook: text("grupo_facebook"),
  /** Fecha de detección */
  fecha_detectada: timestamp("fecha_detectada"),
  /** Prioridad: Alta/Media/Baja */
  prioridad: text("prioridad"),
  /** Propuesta comunicativa personalizada (generada por ChatGPT) */
  propuesta_comunicativa: text("propuesta_comunicativa"),
  /** Canal recomendado (llenado por ChatGPT) */
  canal_recomendado: text("canal_recomendado"),
  /** Estado: pendiente/contactado/descartado */
  estado: varchar("estado", { length: 32 }).default("pendiente"),
  /** Procesada por ChatGPT: SI/NO */
  procesada: varchar("procesada", { length: 8 }).default("NO"),
  /** Fecha de contacto */
  fecha_contacto: timestamp("fecha_contacto"),
  /** Fecha de creación */
  fecha_creacion: timestamp("fecha_creacion").defaultNow().notNull(),
  /** Última actualización */
  ultima_actualizacion: timestamp("ultima_actualizacion").defaultNow().notNull(),
});

export type Ficha = typeof fichas.$inferSelect;
export type InsertFicha = typeof fichas.$inferInsert;