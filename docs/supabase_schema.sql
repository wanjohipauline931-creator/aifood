-- Run in Supabase SQL Editor
create table if not exists prices (
  id bigint generated always as identity primary key,
  date date not null,
  item text not null,
  market text not null,
  price_kes numeric not null,
  unit text not null,
  created_at timestamptz default now()
);
create table if not exists predictions (
  id bigint generated always as identity primary key,
  item text not null,
  ds date not null,
  yhat numeric not null,
  yhat_lower numeric,
  yhat_upper numeric,
  created_at timestamptz default now()
);
alter table prices enable row level security;
alter table predictions enable row level security;
drop policy if exists "public read prices" on prices;
drop policy if exists "public read predictions" on predictions;
create policy "public read prices" on prices for select using (true);
create policy "public read predictions" on predictions for select using (true);
