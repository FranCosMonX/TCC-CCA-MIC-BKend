CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ia INTEGER,
    nome_projeto TEXT,
    apelido TEXT,
    diretorio TEXT,
    microcontrolador TEXT,
    id_microcontrolador TEXT,
    key_ai_api TEXT,
    api_key_valid BOOLEAN NOT NULL,
    ver_codigo BOOLEAN NOT NULL,
    comentario_codigo BOOLEAN NOT NULL,
    FOREIGN KEY(id_ia) REFERENCES ia (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_ia TEXT,
    modelo_disponivel TEXT UNIQUE
);