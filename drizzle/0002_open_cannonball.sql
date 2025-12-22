ALTER TABLE `fichas` MODIFY COLUMN `estado` varchar(32) DEFAULT 'pendiente';--> statement-breakpoint
ALTER TABLE `fichas` MODIFY COLUMN `procesada` varchar(8) DEFAULT 'NO';