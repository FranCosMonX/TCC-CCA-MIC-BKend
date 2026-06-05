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
    fqbn TEXT,
    package_id TEXT,
    ambiente_configurado BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entidade TEXT,
    mensagem TEXT
);

INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("Gemini", "gemini-2.5-flash");
INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("Gemini", "gemini-3.1-flash-lite-preview");
INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("Gemini", "gemini-3.1-flash-lite");
INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("Gemini", "gemini-3.5-flash");
INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ('ChatGPT', "gpt-4o");
INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ('ChatGPT', "gpt-4o-mini");
-- INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("ChatGPT", "gpt-3.5-turbo");
-- INSERT OR IGNORE INTO ia(nome_ia, modelo_disponivel) VALUES ("ChatGPT", "gpt-4-turbo");

INSERT OR IGNORE INTO microcontrolador(nome, fqbn, package_id, ambiente_configurado) VALUES ("ESP32S NodeMCU-32S", "esp32:esp32:nodemcu-32s", "esp32:esp32", 0);
INSERT OR IGNORE INTO microcontrolador(nome, fqbn, package_id, ambiente_configurado) VALUES ("Arduino UNO R3", "arduino:avr:uno", "arduino:avr", 0);