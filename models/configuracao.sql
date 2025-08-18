CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apelido TEXT,
    diretorio TEXT,
    microcontrolador TEXT,
    ai TEXT,
    key_ai_api TEXT,
    api_key_valid BOOLEAN,
    ver_codigo BOOLEAN NOT NULL,
    comentario_codigo BOOLEAN NOT NULL
);