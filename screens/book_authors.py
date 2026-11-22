"""Screen for the ESCREVE table: which authors wrote each book (many-to-many relationship).

This table has no id of its own: each row is identified by the pair
(author, book), which is its composite primary key.
"""
import streamlit as st

import database
import ui


def show():
    ui.page_title("Autoria", "ESCREVE")
    action = ui.choose_action("book_authors")
    if action == "Consultar":
        list_records()
    elif action == "Inserir":
        insert()
    elif action == "Alterar":
        update()
    elif action == "Excluir":
        delete()


def choose_link(key, default_pair=None):
    """Shows the list of book-author links and returns the chosen pair (author_id, book_id).
    default_pair is the link that starts selected."""
    rows = database.fetch_all(
        """SELECT e.FK_AUTOR_id_autor, e.FK_LIVRO_id_livro, a.nome, l.titulo
           FROM ESCREVE e
           JOIN AUTOR a ON a.id_autor = e.FK_AUTOR_id_autor
           JOIN LIVRO l ON l.id_livro = e.FK_LIVRO_id_livro
           ORDER BY l.titulo, a.nome"""
    )
    if len(rows) == 0:
        st.info("Não há vínculos cadastrados.")
        return None
    options = {}
    start_position = 0
    counter = 0
    for row in rows:
        text = row[3] + ", de " + row[2]
        options[text] = (row[0], row[1])
        if default_pair is not None and row[0] == default_pair[0] and row[1] == default_pair[1]:
            start_position = counter
        counter = counter + 1
    chosen_text = st.selectbox("Livro e autor", list(options.keys()), index=start_position, key=key)
    return options[chosen_text]


def list_records():
    table = database.fetch_table(
        """SELECT l.titulo AS "Livro", a.nome AS "Autor",
                  e.FK_LIVRO_id_livro AS "Id do livro", e.FK_AUTOR_id_autor AS "Id do autor"
           FROM ESCREVE e
           JOIN AUTOR a ON a.id_autor = e.FK_AUTOR_id_autor
           JOIN LIVRO l ON l.id_livro = e.FK_LIVRO_id_livro
           ORDER BY l.titulo, a.nome"""
    )
    ui.show_table(table)


def insert():
    book_id = ui.choose_record("Livro", "SELECT id_livro, titulo FROM LIVRO ORDER BY titulo",
                               key="book_authors_insert_book")
    if book_id is None:
        return
    # Only authors that are not linked to this book yet
    author_id = ui.choose_record(
        "Autor",
        """SELECT id_autor, nome FROM AUTOR
           WHERE id_autor NOT IN (SELECT FK_AUTOR_id_autor FROM ESCREVE WHERE FK_LIVRO_id_livro = %s)
           ORDER BY nome""",
        (book_id,),
        key="book_authors_insert_author",
    )
    if author_id is None:
        return
    if st.button("Ligar autor ao livro", key="book_authors_insert_save", type="primary"):
        error = database.execute(
            "INSERT INTO ESCREVE (FK_AUTOR_id_autor, FK_LIVRO_id_livro) VALUES (%s, %s)",
            (author_id, book_id),
        )
        ui.finish(error, "Autor ligado ao livro.")


def update():
    link = choose_link("book_authors_update_choice")
    if link is None:
        return
    current_author_id = link[0]
    book_id = link[1]
    st.write("Troque o autor deste vínculo:")
    new_author_id = ui.choose_record(
        "Novo autor", "SELECT id_autor, nome FROM AUTOR ORDER BY nome",
        key="book_authors_update_author_" + str(current_author_id) + "_" + str(book_id),
        default_id=current_author_id,
    )
    if st.button("Salvar alterações", key="book_authors_update_save", type="primary"):
        error = database.execute(
            """UPDATE ESCREVE SET FK_AUTOR_id_autor = %s
               WHERE FK_AUTOR_id_autor = %s AND FK_LIVRO_id_livro = %s""",
            (new_author_id, current_author_id, book_id),
        )
        ui.finish(error, "Vínculo alterado.")


def delete():
    # Ready example: a link of a book that has more than one author (so it can be removed)
    suggested_pair = database.fetch_one(
        """SELECT e.FK_AUTOR_id_autor, e.FK_LIVRO_id_livro
           FROM ESCREVE e
           WHERE (SELECT COUNT(*) FROM ESCREVE x WHERE x.FK_LIVRO_id_livro = e.FK_LIVRO_id_livro) > 1
           ORDER BY e.FK_LIVRO_id_livro, e.FK_AUTOR_id_autor
           LIMIT 1"""
    )
    link = choose_link("book_authors_delete_choice", suggested_pair)
    if link is None:
        return
    author_id = link[0]
    book_id = link[1]
    if ui.delete_button("book_authors_delete", str(author_id) + "_" + str(book_id)):
        count = database.fetch_value("SELECT COUNT(*) FROM ESCREVE WHERE FK_LIVRO_id_livro = %s", (book_id,))
        if count <= 1:
            st.error("Este é o único autor do livro. Cadastre outro autor antes de remover este.")
            return
        error = database.execute(
            "DELETE FROM ESCREVE WHERE FK_AUTOR_id_autor = %s AND FK_LIVRO_id_livro = %s",
            (author_id, book_id),
        )
        ui.finish(error, "Vínculo removido.")
