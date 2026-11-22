"""Screen for the ITEM_ESTANTE table: the books on each user's shelf, with the reading status."""
import streamlit as st

import database
import ui

STATUSES = ["Quero Ler", "Lendo", "Lido", "Abandonado"]

LIST_SQL = """SELECT i.id_item, u.nome || ', ' || l.titulo || ' (' || i.status_leitura || ')'
              FROM ITEM_ESTANTE i
              JOIN USUARIO u ON u.id_usuario = i.FK_USUARIO_id_usuario
              JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
              ORDER BY u.nome, l.titulo"""


def show():
    ui.page_title("Estante", "ITEM_ESTANTE")
    action = ui.choose_action("shelf")
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
        """SELECT i.id_item AS "Id", u.nome AS "Usuário", l.titulo AS "Livro",
                  i.status_leitura AS "Status", i.data_inclusao AS "Inclusão",
                  i.data_inicio AS "Início", i.data_conclusao AS "Conclusão"
           FROM ITEM_ESTANTE i
           JOIN USUARIO u ON u.id_usuario = i.FK_USUARIO_id_usuario
           JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
           ORDER BY u.nome, i.status_leitura, l.titulo"""
    )
    ui.show_table(table)


def validate_dates(status, start_date, end_date):
    """Checks that the dates match the chosen status. Returns an error message or None."""
    if status == "Quero Ler":
        if start_date is not None or end_date is not None:
            return "Para 'Quero Ler', deixe as datas de início e conclusão em branco."
    if status == "Lendo" or status == "Abandonado":
        if start_date is None:
            return "Informe a data de início da leitura."
        if end_date is not None:
            return "Para '" + status + "', deixe a data de conclusão em branco."
    if status == "Lido":
        if start_date is None or end_date is None:
            return "Para 'Lido', informe as datas de início e de conclusão."
        if end_date < start_date:
            return "A data de conclusão não pode ser anterior à data de início."
    return None


def insert():
    user_id = ui.choose_record("Usuário", "SELECT id_usuario, nome FROM USUARIO ORDER BY nome",
                               key="shelf_insert_user")
    if user_id is None:
        return
    # Only books that are not on this user's shelf yet (RN02)
    book_id = ui.choose_record(
        "Livro",
        """SELECT id_livro, titulo FROM LIVRO
           WHERE id_livro NOT IN (SELECT FK_LIVRO_id_livro FROM ITEM_ESTANTE
                                  WHERE FK_USUARIO_id_usuario = %s)
           ORDER BY titulo""",
        (user_id,),
        key="shelf_insert_book",
    )
    if book_id is None:
        return
    status = st.selectbox("Status de leitura", STATUSES, key="shelf_insert_status")
    start_date = st.date_input("Data de início (se houver)", value=None, format="DD/MM/YYYY",
                               key="shelf_insert_start")
    end_date = st.date_input("Data de conclusão (se houver)", value=None, format="DD/MM/YYYY",
                             key="shelf_insert_end")

    if st.button("Incluir na estante", key="shelf_insert_save", type="primary"):
        problem = validate_dates(status, start_date, end_date)
        if problem is not None:
            st.error(problem)
            return
        error = database.execute(
            """INSERT INTO ITEM_ESTANTE
                   (status_leitura, data_inicio, data_conclusao, FK_LIVRO_id_livro, FK_USUARIO_id_usuario)
               VALUES (%s, %s, %s, %s, %s)""",
            (status, start_date, end_date, book_id, user_id),
        )
        ui.finish(error, "Livro incluído na estante.")


def update():
    item_id = ui.choose_record("Item da estante", LIST_SQL, key="shelf_update_choice")
    if item_id is None:
        return
    current = database.fetch_one(
        """SELECT status_leitura, data_inicio, data_conclusao, FK_LIVRO_id_livro, FK_USUARIO_id_usuario
           FROM ITEM_ESTANTE WHERE id_item = %s""",
        (item_id,),
    )
    current_status = current[0]
    book_id = current[3]
    user_id = current[4]
    suffix = "_" + str(item_id)
    status = ui.choose_value("Status de leitura", STATUSES, current_status, "shelf_update_status" + suffix)
    start_date = st.date_input("Data de início", value=current[1], format="DD/MM/YYYY",
                               key="shelf_update_start" + suffix)
    end_date = st.date_input("Data de conclusão", value=current[2], format="DD/MM/YYYY",
                             key="shelf_update_end" + suffix)

    if st.button("Salvar alterações", key="shelf_update_save", type="primary"):
        problem = validate_dates(status, start_date, end_date)
        if problem is not None:
            st.error(problem)
            return
        # RN04: only a book with status 'Lido' can have a review
        if current_status == "Lido" and status != "Lido":
            reviews = database.fetch_value(
                """SELECT COUNT(*) FROM AVALIACAO_RESENHA
                   WHERE FK_USUARIO_id_usuario = %s AND FK_LIVRO_id_livro = %s""",
                (user_id, book_id),
            )
            if reviews > 0:
                st.error("Este livro já foi avaliado pelo usuário. Exclua a avaliação antes "
                         "de mudar o status para algo diferente de 'Lido' (RN04).")
                return
        error = database.execute(
            """UPDATE ITEM_ESTANTE SET status_leitura = %s, data_inicio = %s, data_conclusao = %s
               WHERE id_item = %s""",
            (status, start_date, end_date, item_id),
        )
        ui.finish(error, "Item da estante alterado.")


def delete():
    # Ready example: a book the user gave up on ('Abandonado')
    suggested_id = database.fetch_value(
        "SELECT id_item FROM ITEM_ESTANTE WHERE status_leitura = 'Abandonado' ORDER BY id_item LIMIT 1"
    )
    item_id = ui.choose_record("Item da estante", LIST_SQL, key="shelf_delete_choice", default_id=suggested_id)
    if item_id is None:
        return
    if ui.delete_button("shelf_delete", item_id):
        error = database.execute("DELETE FROM ITEM_ESTANTE WHERE id_item = %s", (item_id,))
        ui.finish(error, "Livro removido da estante.")
