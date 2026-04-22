-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.auth_group (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  name character varying NOT NULL UNIQUE,
  CONSTRAINT auth_group_pkey PRIMARY KEY (id)
);
CREATE TABLE public.auth_group_permissions (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  group_id integer NOT NULL,
  permission_id integer NOT NULL,
  CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id),
  CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id),
  CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id)
);
CREATE TABLE public.auth_permission (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  name character varying NOT NULL,
  content_type_id integer NOT NULL,
  codename character varying NOT NULL,
  CONSTRAINT auth_permission_pkey PRIMARY KEY (id),
  CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id)
);
CREATE TABLE public.django_admin_log (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  action_time timestamp with time zone NOT NULL,
  object_id text,
  object_repr character varying NOT NULL,
  action_flag smallint NOT NULL CHECK (action_flag >= 0),
  change_message text NOT NULL,
  content_type_id integer,
  user_id bigint NOT NULL,
  CONSTRAINT django_admin_log_pkey PRIMARY KEY (id),
  CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id),
  CONSTRAINT django_admin_log_user_id_c564eba6_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id)
);
CREATE TABLE public.django_content_type (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  app_label character varying NOT NULL,
  model character varying NOT NULL,
  CONSTRAINT django_content_type_pkey PRIMARY KEY (id)
);
CREATE TABLE public.django_migrations (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  app character varying NOT NULL,
  name character varying NOT NULL,
  applied timestamp with time zone NOT NULL,
  CONSTRAINT django_migrations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.django_session (
  session_key character varying NOT NULL,
  session_data text NOT NULL,
  expire_date timestamp with time zone NOT NULL,
  CONSTRAINT django_session_pkey PRIMARY KEY (session_key)
);
CREATE TABLE public.establishment_address (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  street character varying NOT NULL,
  number bigint NOT NULL,
  complement character varying,
  neighborhood character varying NOT NULL,
  city character varying NOT NULL,
  state character varying NOT NULL,
  zip_code character varying NOT NULL,
  establishment_id bigint NOT NULL UNIQUE,
  CONSTRAINT establishment_address_pkey PRIMARY KEY (id),
  CONSTRAINT establishment_addres_establishment_id_d916d374_fk_establish FOREIGN KEY (establishment_id) REFERENCES public.establishment_establishment(id)
);
CREATE TABLE public.establishment_establishment (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name character varying NOT NULL,
  uid character varying NOT NULL UNIQUE,
  cnpj character varying NOT NULL UNIQUE,
  phone character varying NOT NULL,
  description text,
  user_id bigint NOT NULL UNIQUE,
  CONSTRAINT establishment_establishment_pkey PRIMARY KEY (id),
  CONSTRAINT establishment_establishment_user_id_59527301_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id)
);
CREATE TABLE public.establishment_operatinghours (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  day_of_week integer NOT NULL,
  open_time time without time zone NOT NULL,
  close_time time without time zone NOT NULL,
  is_closed boolean NOT NULL,
  establishment_id bigint NOT NULL,
  CONSTRAINT establishment_operatinghours_pkey PRIMARY KEY (id),
  CONSTRAINT establishment_operat_establishment_id_8a12bd04_fk_establish FOREIGN KEY (establishment_id) REFERENCES public.establishment_establishment(id)
);
CREATE TABLE public.services_appointment (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  date date NOT NULL,
  time time without time zone NOT NULL,
  duration integer NOT NULL,
  client_name character varying NOT NULL,
  phone character varying NOT NULL,
  observation text,
  total numeric NOT NULL,
  created_at timestamp with time zone NOT NULL,
  user_id bigint NOT NULL,
  service_id bigint NOT NULL,
  CONSTRAINT services_appointment_pkey PRIMARY KEY (id),
  CONSTRAINT services_appointment_user_id_8091c0fb_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id),
  CONSTRAINT services_appointment_service_id_d8826a21_fk_services_service_id FOREIGN KEY (service_id) REFERENCES public.services_service(id)
);
CREATE TABLE public.services_diverses (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  interval_time integer NOT NULL,
  descricao text,
  user_id bigint NOT NULL,
  CONSTRAINT services_diverses_pkey PRIMARY KEY (id),
  CONSTRAINT services_diverses_user_id_71bbbe14_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id)
);
CREATE TABLE public.services_hoursunavailable (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  day integer NOT NULL,
  hour time without time zone NOT NULL,
  availability boolean NOT NULL,
  user_id bigint NOT NULL,
  month_id bigint NOT NULL,
  CONSTRAINT services_hoursunavailable_pkey PRIMARY KEY (id),
  CONSTRAINT services_hoursunavailable_user_id_4a0dc2c4_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id),
  CONSTRAINT services_hoursunavai_month_id_74ea5ae2_fk_services_ FOREIGN KEY (month_id) REFERENCES public.services_monthavailability(id)
);
CREATE TABLE public.services_monthavailability (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  year integer NOT NULL,
  month integer NOT NULL,
  availability boolean NOT NULL,
  user_id bigint NOT NULL,
  CONSTRAINT services_monthavailability_pkey PRIMARY KEY (id),
  CONSTRAINT services_monthavailability_user_id_c5e053df_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id)
);
CREATE TABLE public.services_service (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  name character varying NOT NULL,
  price numeric NOT NULL,
  time_duration integer NOT NULL,
  user_id bigint NOT NULL,
  CONSTRAINT services_service_pkey PRIMARY KEY (id),
  CONSTRAINT services_service_user_id_4bbc67ac_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id)
);
CREATE TABLE public.user_user (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  password character varying NOT NULL,
  last_login timestamp with time zone,
  is_superuser boolean NOT NULL,
  username character varying NOT NULL UNIQUE,
  first_name character varying NOT NULL,
  last_name character varying NOT NULL,
  email character varying NOT NULL,
  is_staff boolean NOT NULL,
  is_active boolean NOT NULL,
  date_joined timestamp with time zone NOT NULL,
  is_owner boolean NOT NULL,
  establishment_id bigint,
  CONSTRAINT user_user_pkey PRIMARY KEY (id),
  CONSTRAINT user_user_establishment_id_b298ce29_fk_establish FOREIGN KEY (establishment_id) REFERENCES public.establishment_establishment(id)
);
CREATE TABLE public.user_user_groups (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint NOT NULL,
  group_id integer NOT NULL,
  CONSTRAINT user_user_groups_pkey PRIMARY KEY (id),
  CONSTRAINT user_user_groups_user_id_13f9a20d_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id),
  CONSTRAINT user_user_groups_group_id_c57f13c0_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id)
);
CREATE TABLE public.user_user_user_permissions (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint NOT NULL,
  permission_id integer NOT NULL,
  CONSTRAINT user_user_user_permissions_pkey PRIMARY KEY (id),
  CONSTRAINT user_user_user_permissions_user_id_31782f58_fk_user_user_id FOREIGN KEY (user_id) REFERENCES public.user_user(id),
  CONSTRAINT user_user_user_permi_permission_id_ce49d4de_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id)
);