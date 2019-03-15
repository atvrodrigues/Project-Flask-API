
-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS aluno;

CREATE TABLE aluno(
  usuario TEXT NOT NULL,
  uidNumber TEXT NOT NULL,
  nome TEXT NOT NULL,
  matricula TEXT,
  home TEXT,
  grupoBase TEXT,
  email TEXT,
  grupoSecundario TEXT,
  Senha TEXT
);


