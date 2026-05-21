CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ia INTEGER,
    id_microcontrolador INTEGER,
    nome_projeto TEXT,
    apelido TEXT,
    diretorio TEXT,
    key_ai_api TEXT,
    api_key_valid BOOLEAN NOT NULL,
    ver_codigo BOOLEAN NOT NULL,
    comentario_codigo BOOLEAN NOT NULL,
    FOREIGN KEY(id_ia) REFERENCES ia (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(id_microcontrolador) REFERENCES microcontrolador (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_ia TEXT,
    modelo_disponivel TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS microcontrolador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    fqbn TEXT
);

INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("Gemini", "gemini-2.5-flash");
INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("Gemini", "gemini-3.1-flash-lite-preview");

INSERT OR IGNORE INTO microcontrolador(nome, fqbn) VALUES ("ESP32S NodeMCU-32S", "esp32:esp32:nodemcu-32s");
INSERT OR IGNORE INTO microcontrolador(nome, fqbn) VALUES ("Arduino UNO R3", "arduino:avr:uno");