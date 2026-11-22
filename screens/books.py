"""Screen for the LIVRO table (the catalog).

Every book must have at least one author and one genre. So, when a book is
inserted, its authors and genres are chosen in the same form, and the program
saves everything at once: the book in LIVRO and the links in ESCREVE and CLASSIFICA.
"""
import psycopg2
import streamlit as st

import database
import ui

LIST_SQL = "SELECT id_livro, titulo FROM LIVRO ORDER BY titulo"


def show():
    ui.page_title("Livros", "LIVRO")
    action = ui.choose_action("books")
    if action == "Consultar":
        list_records()
    elif action == "Inserir":
        insert()
    elif action == "Alterar":
        update()
    elif action == "Excluir":
        delete()


def list_records():
    search = st.text_input("Buscar por título, autor ou ISBN (deixe vazio para ver todos)",
                           key="books_list_search")
    # The % symbols in ILIKE mean "any text before or after"; ILIKE ignores upper/lower case
    term = "%" + search.strip() + "%"
    table = database.fetch_table(
        """SELECT l.id_livro AS "Id",
                  l.titulo AS "Título",
                  (SELECT STRING_AGG(a.nome, ', ' ORDER BY a.nome)
                     FROM ESCREVE e JOIN AUTOR a ON a.id_autor = e.FK_AUTOR_id_autor
                    WHERE e.FK_LIVRO_id_livro = l.id_livro) AS "Autores",
                  (SELECT STRING_AGG(g.nome, ', ' ORDER BY g.nome)
                     FROM CLASSIFICA c JOIN GENERO g ON g.id_genero = c.FK_GENERO_id_genero
                    WHERE c.FK_LIVRO_id_livro = l.id_livro) AS "Gêneros",
                  l.isbn AS "ISBN",
                  l.ano_publicacao AS "Ano",
                  l.numero_paginas AS "Páginas",
                  l.sinopse AS "Sinopse"
           FROM LIVRO l
           WHERE l.titulo ILIKE %s
              OR l.isbn ILIKE %s
              OR l.id_livro IN (SELECT e.FK_LIVRO_id_livro
                                  FROM ESCREVE e JOIN AUTOR a ON a.id_autor = e.FK_AUTOR_id_autor
                                 WHERE a.nome ILIKE %s)
           ORDER BY l.titulo""",
        (term, term, term),
    )
    ui.show_table(table)


def validate(title, isbn):
    if ui.is_blank(title):
        return "Informe o título."
    if ui.is_blank(isbn):
        return "Informe o ISBN."
    if len(isbn.strip()) != 10 and len(isbn.strip()) != 13:
        return "O ISBN precisa ter 10 ou 13 caracteres."
    return None


def ids_by_name(table, id_column, names):
    """Returns the ids of the rows whose 'nome' is in the list (used for the ready example)."""
    ids = []
    for name in names:
        found_id = database.fetch_value("SELECT " + id_column + " FROM " + table + " WHERE nome = %s", (name,))
        if found_id is not None:
            ids.append(found_id)
    return ids


def insert():
    title = st.text_input("Título", value="Perto do Coração Selvagem", key="books_insert_title")
    isbn = st.text_input("ISBN (10 ou 13 caracteres)", value="9788532511010", key="books_insert_isbn")
    year = st.number_input("Ano de publicação", min_value=0, max_value=2100, value=1943, step=1,
                           key="books_insert_year")
    pages = st.number_input("Número de páginas", min_value=1, max_value=10000, value=224, step=1,
                            key="books_insert_pages")
    synopsis = st.text_area("Sinopse", value="Primeiro romance de Clarice Lispector, acompanha Joana "
                            "da infância à vida adulta.", key="books_insert_synopsis")
    cover_url = st.text_input("Endereço da imagem de capa (opcional)", key="books_insert_cover")
    author_ids = ui.choose_many("Autores (escolha pelo menos um)",
                                "SELECT id_autor, nome FROM AUTOR ORDER BY nome",
                                key="books_insert_authors",
                                default_ids=ids_by_name("AUTOR", "id_autor", ["Clarice Lispector"]))
    genre_ids = ui.choose_many("Gêneros (escolha pelo menos um)",
                               "SELECT id_genero, nome FROM GENERO ORDER BY nome",
                               key="books_insert_genres",
                               default_ids=ids_by_name("GENERO", "id_genero", ["Literatura brasileira", "Romance"]))

    if st.button("Cadastrar livro", key="books_insert_save", type="primary"):
        problem = validate(title, isbn)
        if problem is None and len(author_ids) == 0:
            problem = "Escolha pelo menos um autor."
        if problem is None and len(genre_ids) == 0:
            problem = "Escolha pelo menos um gênero."
        if problem is not None:
            st.error(problem)
            return

        # Empty optional fields are saved as NULL (None in Python)
        if ui.is_blank(synopsis):
            synopsis = None
        if ui.is_blank(cover_url):
            cover_url = None

        # Saves the book and its links in a single transaction:
        # either everything is saved, or nothing is (rollback).
        connection = database.connect()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """INSERT INTO LIVRO (titulo, isbn, ano_publicacao, numero_paginas, sinopse, url_capa)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   RETURNING id_livro""",
                (title.strip(), isbn.strip(), year, pages, synopsis, cover_url),
            )
            new_book_id = cursor.fetchone()[0]
            for author_id in author_ids:
                cursor.execute(
                    "INSERT INTO ESCREVE (FK_AUTOR_id_autor, FK_LIVRO_id_livro) VALUES (%s, %s)",
                    (author_id, new_book_id),
                )
            for genre_id in genre_ids:
                cursor.execute(
                    "INSERT INTO CLASSIFICA (FK_GENERO_id_genero, FK_LIVRO_id_livro) VALUES (%s, %s)",
                    (genre_id, new_book_id),
                )
            connection.commit()
            error = None
        except psycopg2.Error as db_error:
            connection.rollback()
            error = database.translate_error(db_error)
        connection.close()
        ui.finish(error, "Livro cadastrado com seus autores e gêneros.")


def update():
    book_id = ui.choose_record("Livro", LIST_SQL, key="books_update_choice")
    if book_id is None:
        return
    current = database.fetch_one(
        """SELECT titulo, isbn, ano_publicacao, numero_paginas, sinopse, url_capa
           FROM LIVRO WHERE id_livro = %s""",
        (book_id,),
    )
    current_synopsis = current[4]
    if current_synopsis is None:
        current_synopsis = ""
    current_cover = current[5]
    if current_cover is None:
        current_cover = ""
    suffix = "_" + str(book_id)
    title = st.text_input("Título", value=current[0], key="books_update_title" + suffix)
    isbn = st.text_input("ISBN", value=current[1], key="books_update_isbn" + suffix)
    year = st.number_input("Ano de publicação", min_value=0, max_value=2100, value=current[2], step=1,
                           key="books_update_year" + suffix)
    pages = st.number_input("Número de páginas", min_value=1, max_value=10000, value=current[3], step=1,
                            key="books_update_pages" + suffix)
    synopsis = st.text_area("Sinopse", value=current_synopsis, key="books_update_synopsis" + suffix)
    cover_url = st.text_input("Endereço da imagem de capa", value=current_cover, key="books_update_cover" + suffix)
    st.caption("Autores e gêneros são alterados em Autoria e Classificação.")

    if st.button("Salvar alterações", key="books_update_save", type="primary"):
        problem = validate(title, isbn)
        if problem is not None:
            st.error(problem)
            return
        if ui.is_blank(synopsis):
            synopsis = None
        if ui.is_blank(cover_url):
            cover_url = None
        error = database.execute(
            """UPDATE LIVRO
               SET titulo = %s, isbn = %s, ano_publicacao = %s, numero_paginas = %s,
                   sinopse = %s, url_capa = %s
               WHERE id_livro = %s""",
            (title.strip(), isbn.strip(), year, pages, synopsis, cover_url, book_id),
        )
        ui.finish(error, "Livro alterado.")


def delete():
    # Ready example: a book that is on no shelf, has no reviews and is in no group
    suggested_id = database.fetch_value(
        """SELECT l.id_livro FROM LIVRO l
           WHERE NOT EXISTS (SELECT 1 FROM ITEM_ESTANTE i WHERE i.FK_LIVRO_id_livro = l.id_livro)
             AND NOT EXISTS (SELECT 1 FROM AVALIACAO_RESENHA a WHERE a.FK_LIVRO_id_livro = l.id_livro)
             AND NOT EXISTS (SELECT 1 FROM GRUPO_LEITURA g WHERE g.FK_LIVRO_id_livro = l.id_livro)
           ORDER BY l.titulo
           LIMIT 1"""
    )
    book_id = ui.choose_record("Livro", LIST_SQL, key="books_delete_choice", default_id=suggested_id)
    if book_id is None:
        return
    if ui.delete_button("books_delete", book_id):
        error = database.execute("DELETE FROM LIVRO WHERE id_livro = %s", (book_id,))
        ui.finish(error, "Livro excluído.")
