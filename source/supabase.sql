-- Hinoki SPA — схема базы Supabase (уже применена к проекту hinoki-spa)
create table public.bookings (
  id text primary key default ('b' || replace(gen_random_uuid()::text,'-','')),
  date date not null, start int not null, dur int not null, svc text not null,
  guests int not null default 1, pref text not null default 'any', intensity text not null default 'medium',
  comment text not null default '', name text not null, phone text not null,
  status text not null default 'wait', price int not null default 0, source text not null default '',
  segs jsonb not null default '[]', seed boolean not null default false, fresh boolean not null default true,
  created_at timestamptz not null default now()
);
create table public.clients (phone text primary key, name text not null, notes text not null default '', history jsonb not null default '[]', created_at timestamptz not null default now());
create table public.admins (user_id uuid primary key references auth.users(id) on delete cascade);

alter table public.bookings enable row level security;
alter table public.clients enable row level security;
alter table public.admins enable row level security;

create function public.is_admin() returns boolean language sql stable security definer set search_path = public
as $$ select exists(select 1 from public.admins where user_id = auth.uid()); $$;

create policy "admin all bookings" on public.bookings for all to authenticated using (public.is_admin()) with check (public.is_admin());
create policy "admin all clients" on public.clients for all to authenticated using (public.is_admin()) with check (public.is_admin());
create policy "admin read self" on public.admins for select to authenticated using (user_id = auth.uid());

-- public.get_busy(date)        — занятые интервалы без персональных данных (доступно всем)
-- public.create_booking(jsonb) — создание брони с проверкой накладок, цены и лимита (доступно всем)
-- полный текст функций — в миграции hinoki_init в Supabase (Database → Migrations)

alter publication supabase_realtime add table public.bookings, public.clients;

-- Добавить нового администратора: создать пользователя в Authentication → Users, затем
-- insert into public.admins(user_id) select id from auth.users where email = 'почта@пример.kz';
