-- Table: public.stock

-- DROP TABLE public.stock;

CREATE TABLE public.stock
(
    id bigint NOT NULL DEFAULT nextval('stock_id_seq'::regclass),
    product_name text COLLATE pg_catalog."default",
    product_unit text COLLATE pg_catalog."default",
    id_product integer NOT NULL,
    qty_purchase numeric,
    qty_sale numeric,
    date_ date,
    creation_date timestamp with time zone,
    id_si_detail integer,
    id_pi_detail integer,
    CONSTRAINT stock_id_pi_detail_fkey FOREIGN KEY (id_pi_detail)
        REFERENCES public.pi_detail (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT stock_id_product_fkey FOREIGN KEY (id_product)
        REFERENCES public.product (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT stock_id_si_detail_fkey FOREIGN KEY (id_si_detail)
        REFERENCES public.si_detail (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.stock
    OWNER to dba_tovak;
