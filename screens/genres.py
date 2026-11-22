"""Screen for the GENERO table (literary genres)."""
import streamlit as st

import database
import ui

LIST_SQL = "SELECT id_genero, nome FROM GENERO ORDER BY nome"


def show():
    ui.page_title("Gêneros", "GENERO")
    action = ui.choose_action("genres")
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
        """SELECT g.id_genero AS "Id", g.nome AS "Nome",
                  COUNT(c.FK_LIVRO_id_livro) AS "Livros no catálogo"
           FROM GENERO g
           LEFT JOIN CLASSIFICA c ON c.FK_GENERO_id_genero = g.id_genero
           GROUP BY g.id_genero, g.nome
           ORDER BY g.nome"""
    )
    ui.show_table(table)


def insert():
    name = st.text_input("Nome do gênero", value="Contos", key="genres_insert_name")
    if st.button("Cadastrar gênero", key="genres_insert_save", type="primary"):
        if ui.is_blank(name):
            st.error("Informe o nome do gênero.")
            return
        error = database.execute("INSERT INTO GENERO (nome) VALUES (%s)", (name.strip(),))
        ui.finish(error, "Gênero cadastrado.")


def update():
    genre_id = ui.choose_record("Gênero", LIST_SQL, key="genres_update_choice")
    if genre_id is None:
        return
    current_name = database.fetch_value("SELECT nome FROM GENERO WHERE id_genero = %s", (genre_id,))
    name = st.text_input("Nome do gênero", value=current_name, key="genres_update_name_" + str(genre_id))
    if st.button("Salvar alterações", key="genres_update_save", type="primary"):
        if ui.is_blank(name):
            st.error("Informe o nome do gênero.")
            return
        error = database.execute("UPDATE GENERO SET nome = %s WHERE id_genero = %s", (name.strip(), genre_id))
        ui.finish(error, "Gênero alterado.")


def delete():
    # Ready example: a genre with no books (so the deletion is allowed)
    suggested_id = database.fetch_value(
        """SELECT id_genero FROM GENERO
           WHERE id_genero NOT IN (SELECT FK_GENERO_id_genero FROM CLASSIFICA)
           ORDER BY nome
           LIMIT 1"""
    )
    genre_id = ui.choose_record("Gênero", LIST_SQL, key="genres_delete_choice", default_id=suggested_id)
    if genre_id is None:
        return
    if ui.delete_button("genres_delete", genre_id):
        error = database.execute("DELETE FROM GENERO WHERE id_genero = %s", (genre_id,))
        ui.finish(error, "Gênero excluído.")
