"""Screen for the AUTOR table."""
import streamlit as st

import database
import ui

LIST_SQL = "SELECT id_autor, nome FROM AUTOR ORDER BY nome"


def show():
    ui.page_title("Autores", "AUTOR")
    action = ui.choose_action("authors")
    if action == "Consultar":
        list_records()
    elif action == "Inserir":
        insert()
    elif action == "Alterar":
        update()
    elif action == "Excluir":
        delete()


def list_records():
    # LEFT JOIN also shows the authors that have no books yet (count zero)
    table = database.fetch_table(
        """SELECT a.id_autor AS "Id", a.nome AS "Nome",
                  COUNT(e.FK_LIVRO_id_livro) AS "Livros no catálogo"
           FROM AUTOR a
           LEFT JOIN ESCREVE e ON e.FK_AUTOR_id_autor = a.id_autor
           GROUP BY a.id_autor, a.nome
           ORDER BY a.nome"""
    )
    ui.show_table(table)


def insert():
    name = st.text_input("Nome do autor", value="Lygia Fagundes Telles", key="authors_insert_name")
    if st.button("Cadastrar autor", key="authors_insert_save", type="primary"):
        if ui.is_blank(name):
            st.error("Informe o nome do autor.")
            return
        error = database.execute("INSERT INTO AUTOR (nome) VALUES (%s)", (name.strip(),))
        ui.finish(error, "Autor cadastrado.")


def update():
    author_id = ui.choose_record("Autor", LIST_SQL, key="authors_update_choice")
    if author_id is None:
        return
    current_name = database.fetch_value("SELECT nome FROM AUTOR WHERE id_autor = %s", (author_id,))
    name = st.text_input("Nome do autor", value=current_name, key="authors_update_name_" + str(author_id))
    if st.button("Salvar alterações", key="authors_update_save", type="primary"):
        if ui.is_blank(name):
            st.error("Informe o nome do autor.")
            return
        error = database.execute("UPDATE AUTOR SET nome = %s WHERE id_autor = %s", (name.strip(), author_id))
        ui.finish(error, "Autor alterado.")


def delete():
    # Ready example: an author with no books (so the deletion is allowed)
    suggested_id = database.fetch_value(
        """SELECT id_autor FROM AUTOR
           WHERE id_autor NOT IN (SELECT FK_AUTOR_id_autor FROM ESCREVE)
           ORDER BY nome
           LIMIT 1"""
    )
    author_id = ui.choose_record("Autor", LIST_SQL, key="authors_delete_choice", default_id=suggested_id)
    if author_id is None:
        return
    if ui.delete_button("authors_delete", author_id):
        error = database.execute("DELETE FROM AUTOR WHERE id_autor = %s", (author_id,))
        ui.finish(error, "Autor excluído.")
