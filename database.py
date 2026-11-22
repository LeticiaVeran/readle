"""
Database access (item 7a).

Every screen reads and writes data through the functions in this file:
- connect():         opens a connection to PostgreSQL
- fetch_all():       runs a SELECT and returns all rows
- fetch_one():       runs a SELECT and returns only the first row
- fetch_value():     runs a SELECT and returns a single value (for example, a COUNT)
- fetch_table():     runs a SELECT and returns a table (pandas DataFrame) ready to show on screen
- execute():         runs an INSERT, UPDATE or DELETE
- run_sql_files():   runs the scripts in the sql folder (create, load and drop the tables)

The connection settings (host, user, password...) come from the .env file.
Table and column names are in Portuguese because they come from the data
model described in the report.
"""
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Folder where this file is, so the program works no matter where it is started from
APP_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Reads the .env file and loads its values as environment variables
load_dotenv(os.path.join(APP_FOLDER, ".env"))

# Folder with the .sql scripts
SQL_FOLDER = os.path.join(APP_FOLDER, "sql")

# The 14 tables of the logical model
TABLES = [
    "usuario", "autor", "genero", "livro", "escreve", "classifica", "item_estante",
    "avaliacao_resenha", "grupo_leitura", "membro_grupo", "etapa_leitura",
    "progresso_etapa", "mensagem", "notificacao",
]

# Friendly messages (shown to the user, in Portuguese) for each database constraint.
# The names come from sql/schema.sql. When the database refuses an operation it
# reports the name of the constraint that was violated, and we use that name to
# show an explanation instead of the technical error.
ERROR_MESSAGES = {
    # Uniqueness (UNIQUE and composite primary keys)
    "uq_usuario_nome_usuario": "Já existe um usuário com esse nome de usuário (RN01).",
    "uq_usuario_email": "Já existe um usuário com esse e-mail (RN01).",
    "uq_livro_isbn": "Já existe um livro com esse ISBN (RN01).",
    "uq_item_estante_usuario_livro": "Esse livro já está na estante desse usuário (RN02).",
    "uq_avaliacao_usuario_livro": "Esse usuário já avaliou esse livro (RN04).",
    "uq_membro_usuario_grupo": "Esse usuário já participa desse grupo (RN08).",
    "uq_etapa_grupo_ordem": "Já existe uma etapa com essa ordem nesse grupo (RN09).",
    "uq_progresso_membro_etapa": "Já existe um registro de progresso desse membro nessa etapa (RN10).",
    "pk_escreve": "Esse autor já está associado a esse livro.",
    "pk_classifica": "Esse gênero já está associado a esse livro.",
    # Allowed values (CHECK)
    "ck_livro_isbn": "O ISBN precisa ter 10 ou 13 caracteres.",
    "ck_livro_paginas": "O número de páginas precisa ser maior que zero.",
    "ck_avaliacao_nota": "A nota precisa ser um número inteiro de 1 a 5.",
    "ck_item_estante_status": "Status de leitura inválido.",
    "ck_item_estante_datas": "A data de conclusão não pode ser anterior à data de início.",
    "ck_etapa_ordem": "A ordem da etapa precisa ser maior que zero.",
    "ck_progresso_confirmacao": "Etapa concluída precisa de data de confirmação, e etapa não concluída não pode ter data.",
    "ck_mensagem_edicao": "A data de edição não pode ser anterior à publicação.",
    # Blocked deletions (foreign keys with ON DELETE RESTRICT, report Quadro 2)
    "fk_grupo_livro": "Esse livro é discutido em um grupo de leitura e não pode ser excluído.",
    "fk_grupo_organizador": "Esse usuário organiza um grupo. Transfira a administração ou exclua o grupo antes.",
    "fk_avaliacao_livro": "Esse livro possui avaliações e não pode ser excluído.",
    "fk_item_estante_livro": "Esse livro está na estante de algum usuário e não pode ser excluído.",
    "fk_escreve_autor": "Esse autor está associado a livros e não pode ser excluído.",
    "fk_classifica_genero": "Esse gênero está associado a livros e não pode ser excluído.",
}


def connect():
    """Opens and returns a connection to the database, using the values of the .env file."""
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "readle"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    # Makes sure accented letters are sent and received correctly
    connection.set_client_encoding("UTF8")
    return connection


def test_connection():
    """Tries to connect. Returns None if it worked, or the text of the problem."""
    try:
        connection = connect()
        connection.close()
        return None
    except Exception as error:
        return str(error)


def fetch_all(sql, params=None):
    """Runs a SELECT and returns a list of rows. Each row is a tuple.

    The values go in 'params', never glued into the SQL text: psycopg2 replaces
    each %s safely, which prevents SQL injection."""
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    connection.close()
    return rows


def fetch_one(sql, params=None):
    """Runs a SELECT and returns only the first row (or None when nothing comes back)."""
    rows = fetch_all(sql, params)
    if len(rows) == 0:
        return None
    return rows[0]


def fetch_value(sql, params=None):
    """Runs a SELECT that returns a single value (a COUNT, a name, an id...)
    and returns that value. Returns None when nothing comes back."""
    row = fetch_one(sql, params)
    if row is None:
        return None
    return row[0]


def fetch_table(sql, params=None):
    """Runs a SELECT and returns the result as a pandas table (DataFrame),
    which Streamlit knows how to show on screen and turn into a chart."""
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    column_names = []
    for column in cursor.description:
        column_names.append(column[0])
    connection.close()
    table = pd.DataFrame(rows, columns=column_names)
    return table


def translate_error(error):
    """Turns a PostgreSQL error into a message in Portuguese for the user."""
    constraint_name = error.diag.constraint_name
    if constraint_name in ERROR_MESSAGES:
        return ERROR_MESSAGES[constraint_name]
    # Code 23502 = a required column (NOT NULL) was left empty
    if error.pgcode == "23502":
        return "Preencha o campo obrigatório: " + str(error.diag.column_name)
    return "O banco de dados recusou a operação: " + str(error.diag.message_primary)


def execute(sql, params=None):
    """Runs an INSERT, UPDATE or DELETE.
    Returns None if it worked, or an error message in Portuguese."""
    connection = connect()
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        connection.commit()
        error_message = None
    except psycopg2.Error as error:
        connection.rollback()
        error_message = translate_error(error)
    connection.close()
    return error_message


def run_sql_files(file_names):
    """Runs the given scripts of the sql folder, one after the other.
    If any command fails, nothing is saved (everything is undone with rollback).
    Returns None if it worked, or an error message."""
    connection = connect()
    cursor = connection.cursor()
    try:
        for file_name in file_names:
            path = os.path.join(SQL_FOLDER, file_name)
            sql_file = open(path, encoding="utf-8")
            content = sql_file.read()
            sql_file.close()
            cursor.execute(content)
        connection.commit()
        error_message = None
    except psycopg2.Error as error:
        connection.rollback()
        error_message = translate_error(error)
    connection.close()
    return error_message


def existing_tables():
    """Returns the list of Readle tables that already exist in the database."""
    rows = fetch_all(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    )
    found = []
    for row in rows:
        if row[0] in TABLES:
            found.append(row[0])
    return found


def tables_created():
    """Returns True when all 14 Readle tables exist in the database."""
    return len(existing_tables()) == len(TABLES)
