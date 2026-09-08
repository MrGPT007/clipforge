import { sqliteTable, text, integer, index } from 'drizzle-orm/sqlite-core';
export const records = sqliteTable('records', {
  id: text('id').primaryKey(), owner: text('owner').notNull(), kind: text('kind').notNull(),
  body: text('body').notNull(), revision: integer('revision').notNull().default(1), updated: text('updated').notNull(),
}, t => [index('idx_records_owner_kind').on(t.owner,t.kind)]);
export const files = sqliteTable('files', {
  id: text('id').primaryKey(), owner: text('owner').notNull(), name: text('name').notNull(),
  mime: text('mime').notNull(), size: integer('size').notNull(), created: text('created').notNull(),
}, t => [index('idx_files_owner').on(t.owner)]);
