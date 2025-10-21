CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apelido TEXT,
    diretorio TEXT,
    microcontrolador TEXT,
    id_microcontrolador TEXT,
    ia TEXT,
    key_ai_api TEXT,
    api_key_valid BOOLEAN NOT NULL,
    ver_codigo BOOLEAN NOT NULL,
    comentario_codigo BOOLEAN NOT NULL
);