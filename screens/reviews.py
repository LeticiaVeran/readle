"""Screen for the AVALIACAO_RESENHA table: readers' ratings and reviews.

RN04: a user can only review books marked 'Lido' on their shelf, and each book only once.
"""
import streamlit as st

import database
import ui

LIST_SQL = """SELECT a.id_avaliacao, u.nome || ', ' || l.titulo || ' (nota ' || a.nota || ')'
              FROM AVALIACAO_RESENHA a
              JOIN USUARIO u ON u.id_usuario = a.FK_USUARIO_id_usuario
              JOIN LIVRO l ON l.id_livro = a.FK_LIVRO_id_livro
              ORDER BY u.nome, l.titulo"""


def show():
    ui.page_title("Avaliações", "AVALIACAO_RESENHA")
    action = ui.choose_action("reviews")
    if action == "Consultar":
        list_records()
    elif action == "Inserir":
        insert()
    elif action == "Alterar":
        update()
    elif action == "Excluir":
        delete()


def list_records():
    table = database.fetch_table(
        """SELECT a.id_avaliacao AS "Id", u.nome AS "Usuário", l.titulo AS "Livro",
                  a.nota AS "Nota", a.texto_resenha AS "Resenha", a.data_publicacao AS "Publicação"
           FROM AVALIACAO_RESENHA a
           JOIN USUARIO u ON u.id_usuario = a.FK_USUARIO_id_usuario
           JOIN LIVRO l ON l.id_livro = a.FK_LIVRO_id_livro
           ORDER BY a.data_publicacao DESC"""
    )
    ui.show_table(table)


def insert():
    # Ready example: the first user who has a book marked 'Lido' that was not reviewed yet
    suggested_user = database.fetch_value(
        """SELECT u.id_usuario
           FROM USUARIO u
           JOIN ITEM_ESTANTE i ON i.FK_USUARIO_id_usuario = u.id_usuario
           WHERE i.status_leitura = 'Lido'
             AND NOT EXISTS (SELECT 1 FROM AVALIACAO_RESENHA a
                             WHERE a.FK_USUARIO_id_usuario = i.FK_USUARIO_id_usuario
                               AND a.FK_LIVRO_id_livro = i.FK_LIVRO_id_livro)
           ORDER BY u.nome
           LIMIT 1"""
    )
    user_id = ui.choose_record("Usuário", "SELECT id_usuario, nome FROM USUARIO ORDER BY nome",
                               key="reviews_insert_user", default_id=suggested_user)
    if user_id is None:
        return
    # RN04: the list only shows books 'Lido' on this user's shelf that this user did not review yet
    book_id = ui.choose_record(
        "Livro (somente livros com status Lido e ainda sem avaliação)",
        """SELECT l.id_livro, l.titulo
           FROM ITEM_ESTANTE i
           JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
           WHERE i.FK_USUARIO_id_usuario = %s
             AND i.status_leitura = 'Lido'
             AND NOT EXISTS (SELECT 1 FROM AVALIACAO_RESENHA a
                             WHERE a.FK_USUARIO_id_usuario = i.FK_USUARIO_id_usuario
                               AND a.FK_LIVRO_id_livro = i.FK_LIVRO_id_livro)
           ORDER BY l.titulo""",
        (user_id,),
        key="reviews_insert_book",
    )
    if book_id is None:
        return
    rating = st.slider("Nota", min_value=1, max_value=5, value=4, key="reviews_insert_rating")
    text = st.text_area("Resenha (opcional)", value="Demorei a engrenar, mas o final valeu a leitura.",
                        key="reviews_insert_text")

    if st.button("Publicar avaliação", key="reviews_insert_save", type="primary"):
        if ui.is_blank(text):
            text = None
        error = database.execute(
            """INSERT INTO AVALIACAO_RESENHA (nota, texto_resenha, FK_LIVRO_id_livro, FK_USUARIO_id_usuario)
               VALUES (%s, %s, %s, %s)""",
            (rating, text, book_id, user_id),
        )
        ui.finish(error, "Avaliação publicada.")


def update():
    review_id = ui.choose_record("Avaliação", LIST_SQL, key="reviews_update_choice")
    if review_id is None:
        return
    current = database.fetch_one("SELECT nota, texto_resenha FROM AVALIACAO_RESENHA WHERE id_avaliacao = %s",
                                 (review_id,))
    current_text = current[1]
    if current_text is None:
        current_text = ""
    suffix = "_" + str(review_id)
    rating = st.slider("Nota", min_value=1, max_value=5, value=current[0], key="reviews_update_rating" + suffix)
    text = st.text_area("Resenha", value=current_text, key="reviews_update_text" + suffix)

    if st.button("Salvar alterações", key="reviews_update_save", type="primary"):
        if ui.is_blank(text):
            text = None
        error = database.execute(
            "UPDATE AVALIACAO_RESENHA SET nota = %s, texto_resenha = %s WHERE id_avaliacao = %s",
            (rating, text, review_id),
        )
        ui.finish(error, "Avaliação alterada.")


def delete():
    review_id = ui.choose_record("Avaliação", LIST_SQL, key="reviews_delete_choice")
    if review_id is None:
        return
    if ui.delete_button("reviews_delete", review_id):
        error = database.execute("DELETE FROM AVALIACAO_RESENHA WHERE id_avaliacao = %s", (review_id,))
        ui.finish(error, "Avaliação excluída.")
