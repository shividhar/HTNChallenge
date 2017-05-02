drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name text not null,
  picture text not null,
  company text not null,
  email text not null,
  phone text not null,
  country text default null,
  latitude real not null,
  longitude real not null
);

drop table if exists skills;
create table skills (
  id integer key,
  name text not null,
  rating real not null
);