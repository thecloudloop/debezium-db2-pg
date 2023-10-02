create schema db2inst1 ;

CREATE TABLE db2inst1.customers (
	id int4 NOT NULL,
	first_name text NOT NULL,
	last_name text NOT NULL,
	email text NOT NULL,
	CONSTRAINT customers_pkey PRIMARY KEY (id)
);

CREATE TABLE db2inst1.orders (
	id int4 NOT NULL,
	order_date date NOT NULL,
	purchaser int4 NOT NULL,
	quantity int4 NOT NULL,
	product_id int4 NOT NULL,
	CONSTRAINT orders_pkey PRIMARY KEY (id)
);

CREATE TABLE db2inst1.products (
	id int4 NOT NULL,
	"name" text NOT NULL,
	description text NULL,
	weight float8 NULL,
	CONSTRAINT products_pkey PRIMARY KEY (id)
);

CREATE TABLE db2inst1.products_on_hand (
	product_id int4 NOT NULL,
	quantity int4 NOT NULL,
	CONSTRAINT products_on_hand_pkey PRIMARY KEY (product_id)
);

