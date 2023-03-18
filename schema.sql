

CREATE TABLE `financial_data` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `symbol` varchar(128) NOT NULL COMMENT 'Stock symbol',
  `date` timestamp NOT NULL COMMENT 'Date of price data',
  `open_price` int unsigned NOT NULL COMMENT 'Unit: cent',
  `close_price` int unsigned NOT NULL COMMENT 'Unit: cent',
  `volume` bigint unsigned NOT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unq_symbol_date` (`symbol`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;