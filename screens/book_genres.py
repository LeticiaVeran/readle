"""Screen for the CLASSIFICA table: which genres each book belongs to (many-to-many relationship).

This table has no id of its own: each row is identified by the pair
(genre, book), which is its composite primary key.
"""
import streamlit as st

import database
import ui


def show():
    ui.page_title("Classificação", "CLASSIFICA")
    action = ui.choose_action("book_genres")
    if action == "Consultar":
        list_records()
    elif action == "Inserir":
        insert()
    elif action == "Alterar":
        update()
    elif action == "Excluir":
        delete()


def choose_link(key, default_pair=None):
    """Shows the list of book-genre links and returns the chosen pair (genre_id, book_id).
    default_pair is the link that starts selected."""
    rows = database.fetch_all(
        """SELECT c.FK_GENERO_id_genero, c.FK_LIVRO_id_livro, g.nome, l.titulo
           FROM CLASSIFICA c
           JOIN GENERO g ON g.id_genero = c.FK_GENERO_id_genero
           JOIN LIVRO l ON l.id_livro = c.FK_LIVRO_id_livro
           ORDER BY l.titulo, g.nome"""
    )
    if len(rows) == 0:
        st.info("Não há vínculos cadastrados.")
        return None
    options = {}
    start_position = 0
    counter = 0
    for row in rows:
        text = row[3] + " (" + row[2] + ")"
        options[text] = (row[0], row[1])
        if default_pair is not None and row[0] == default_pair[0] and row[1] == default_pair[1]:
            start_position = counter
        counter = counter + 1
    chosen_text = st.selectbox("Livro e gênero", list(options.keys()), index=start_position, key=key)
    return options[chosen_text]


def list_records():
    table = database.fetch_table(
        """SELECT l.titulo AS "Livro", g.nome AS "Gênero",
                  c.FK_LIVRO_id_livro AS "Id do livro", c.FK_GENERO_id_genero AS "Id do gênero"
           FROM CLASSIFICA c
           JOIN GENERO g ON g.id_genero = c.FK_GENERO_id_genero
           JOIN LIVRO l ON l.id_livro = c.FK_LIVRO_id_livro
           ORDER BY l.titulo, g.nome"""
    )
    ui.show_table(table)


def insert():
    book_id = ui.choose_record("Livro", "SELECT id_livro, titulo FROM LIVRO ORDER BY titulo",
                               key="book_genres_insert_book")
    if book_id is None:
        return
    # Only genres that are not linked to this book yet
    genre_id = ui.choose_record(
        "Gênero",
        """SELECT id_genero, nome FROM GENERO
           WHERE id_genero NOT IN (SELECT FK_GENERO_id_genero FROM CLASSIFICA WHERE FK_LIVRO_id_livro = %s)
           ORDER BY nome""",
        (book_id,),
        key="book_genres_insert_genre",
    )
    if genre_id is None:
        return
    if st.button("Ligar gênero ao livro", key="book_genres_insert_save", type="primary"):
        error = database.execute(
            "INSERT INTO CLASSIFICA (FK_GENERO_id_genero, FK_LIVRO_id_livro) VALUES (%s, %s)",
            (genre_id, book_id),
        )
        ui.finish(error, "Gênero ligado ao livro.")


def update():
    link = choose_link("book_genres_update_choice")
    if link is None:
        return
    current_genre_id = link[0]
    book_id = link[1]
    st.write("Troque o gênero deste vínculo:")
    new_genre_id = ui.choose_record(
        "Novo gênero", "SELECT id_genero, nome FROM GENERO ORDER BY nome",
        key="book_genres_update_genre_" + str(current_genre_id) + "_" + str(book_id),
        default_id=current_genre_id,
    )
    if st.button("Salvar alterações", key="book_genres_update_save", type="primary"):
        error = database.execute(
            """UPDATE CLASSIFICA SET FK_GENERO_id_genero = %s
               WHERE FK_GENERO_id_genero = %s AND FK_LIVRO_id_livro = %s""",
            (new_genre_id, current_genre_id, book_id),
        )
        ui.finish(error, "Vínculo alterado.")


def delete():
    # Ready example: a link of a book that has more than one genre (so it can be removed)
    suggested_pair = database.fetch_one(
        """SELECT c.FK_GENERO_id_genero, c.FK_LIVRO_id_livro
           FROM CLASSIFICA c
           WHERE (SELECT COUNT(*) FROM CLASSIFICA x WHERE x.FK_LIVRO_id_livro = c.FK_LIVRO_id_livro) > 1
           ORDER BY c.FK_LIVRO_id_livro, c.FK_GENERO_id_genero
           LIMIT 1"""
    )
    link = choose_link("book_genres_delete_choice", suggested_pair)
    if link is None:
        return
    genre_id = link[0]
    book_id = link[1]
    if ui.delete_button("book_genres_delete", str(genre_id) + "_" + str(book_id)):
        count = database.fetch_value("SELECT COUNT(*) FROM CLASSIFICA WHERE FK_LIVRO_id_livro = %s", (book_id,))
        if count <= 1:
            st.error("Este é o único gênero do livro. Cadastre outro gênero antes de remover este.")
            return
        error = database.execute(
            "DELETE FROM CLASSIFICA WHERE FK_GENERO_id_genero = %s AND FK_LIVRO_id_livro = %s",
            (genre_id, book_id),
        )
        ui.finish(error, "Vínculo removido.")
