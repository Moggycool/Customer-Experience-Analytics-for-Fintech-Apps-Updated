--
-- PostgreSQL database dump
--

\restrict sVYabPRSlsOemJA9S97R9PvG7fgNGareDGfu9rkVAuhUtZUQGPMY7Icdeb7ZnLc

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: banks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.banks (
    bank_id integer NOT NULL,
    bank_name text NOT NULL,
    app_name text
);


ALTER TABLE public.banks OWNER TO postgres;

--
-- Name: banks_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.banks_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.banks_bank_id_seq OWNER TO postgres;

--
-- Name: banks_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.banks_bank_id_seq OWNED BY public.banks.bank_id;


--
-- Name: review_themes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.review_themes (
    review_id bigint NOT NULL,
    theme_id integer NOT NULL
);


ALTER TABLE public.review_themes OWNER TO postgres;

--
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    review_id bigint NOT NULL,
    bank_id integer NOT NULL,
    review_text text NOT NULL,
    rating integer,
    review_date date,
    source text,
    sentiment_label text,
    sentiment_score double precision,
    theme_primary text,
    review_hash text,
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5))),
    CONSTRAINT reviews_sentiment_label_check CHECK ((sentiment_label = ANY (ARRAY['POSITIVE'::text, 'NEGATIVE'::text, 'NEUTRAL'::text])))
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- Name: themes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.themes (
    theme_id integer NOT NULL,
    theme_name text NOT NULL
);


ALTER TABLE public.themes OWNER TO postgres;

--
-- Name: themes_theme_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.themes_theme_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.themes_theme_id_seq OWNER TO postgres;

--
-- Name: themes_theme_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.themes_theme_id_seq OWNED BY public.themes.theme_id;


--
-- Name: banks bank_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banks ALTER COLUMN bank_id SET DEFAULT nextval('public.banks_bank_id_seq'::regclass);


--
-- Name: themes theme_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.themes ALTER COLUMN theme_id SET DEFAULT nextval('public.themes_theme_id_seq'::regclass);


--
-- Name: banks banks_bank_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banks
    ADD CONSTRAINT banks_bank_name_key UNIQUE (bank_name);


--
-- Name: banks banks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banks
    ADD CONSTRAINT banks_pkey PRIMARY KEY (bank_id);


--
-- Name: review_themes review_themes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_themes
    ADD CONSTRAINT review_themes_pkey PRIMARY KEY (review_id, theme_id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (review_id);


--
-- Name: reviews reviews_review_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_review_hash_key UNIQUE (review_hash);


--
-- Name: themes themes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.themes
    ADD CONSTRAINT themes_pkey PRIMARY KEY (theme_id);


--
-- Name: themes themes_theme_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.themes
    ADD CONSTRAINT themes_theme_name_key UNIQUE (theme_name);


--
-- Name: idx_reviews_bank_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reviews_bank_id ON public.reviews USING btree (bank_id);


--
-- Name: idx_reviews_review_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reviews_review_date ON public.reviews USING btree (review_date);


--
-- Name: idx_reviews_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reviews_source ON public.reviews USING btree (source);


--
-- Name: idx_reviews_theme_primary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reviews_theme_primary ON public.reviews USING btree (theme_primary);


--
-- Name: review_themes review_themes_review_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_themes
    ADD CONSTRAINT review_themes_review_id_fkey FOREIGN KEY (review_id) REFERENCES public.reviews(review_id) ON DELETE CASCADE;


--
-- Name: review_themes review_themes_theme_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_themes
    ADD CONSTRAINT review_themes_theme_id_fkey FOREIGN KEY (theme_id) REFERENCES public.themes(theme_id) ON DELETE CASCADE;


--
-- Name: reviews reviews_bank_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES public.banks(bank_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict sVYabPRSlsOemJA9S97R9PvG7fgNGareDGfu9rkVAuhUtZUQGPMY7Icdeb7ZnLc

