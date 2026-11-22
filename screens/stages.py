"""Screen for the ETAPA_LEITURA table: the reading schedule of each group.

RN09: every group has at least one stage, and the stage order is unique inside
a group (this second part is enforced by the database).
"""
from datetime import date
from datetime import timedelta

import streamlit as st

import database
import ui

LIST_SQL = """SELECT e.id_etapa, g.nome || ', etapa ' || e.ordem || ': ' || e.titulo
              FROM ETAPA_LEITURA e
              JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
              ORDER BY g.nome, e.ordem"""


def show():
    ui.page_title("Etapas de leitura", "ETAPA_LEITURA")
    action = ui.choose_action("stages")
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
        """SELECT e.id_etapa AS "Id", g.nome AS "Grupo", e.ordem AS "Ordem", e.titulo AS "Título",
                  e.data_limite AS "Data-limite", e.descricao AS "Descrição"
           FROM ETAPA_LEITURA e
           JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
           ORDER BY g.nome, e.ordem"""
    )
    ui.show_table(table)


def insert():
    # Ready example: the first group that is not closed
    suggested_group = database.fetch_value(
        "SELECT id_grupo FROM GRUPO_LEITURA WHERE situacao <> 'Encerrado' ORDER BY nome LIMIT 1"
    )
    group_id = ui.choose_record("Grupo", "SELECT id_grupo, nome FROM GRUPO_LEITURA ORDER BY nome",
                                key="stages_insert_group", default_id=suggested_group)
    if group_id is None:
        return
    # Suggests the next free order (the highest order of the group + 1)
    highest_order = database.fetch_value(
        "SELECT COALESCE(MAX(ordem), 0) FROM ETAPA_LEITURA WHERE FK_GRUPO_LEITURA_id_grupo = %s", (group_id,)
    )
    suffix = "_" + str(group_id)
    title = st.text_input("Título", value="Conversa final sobre o livro", key="stages_insert_title")
    order = st.number_input("Ordem", min_value=1, max_value=100, value=highest_order + 1, step=1,
                            key="stages_insert_order" + suffix)
    description = st.text_input("Descrição (opcional)", key="stages_insert_description")
    deadline = st.date_input("Data-limite", value=date.today() + timedelta(days=30), format="DD/MM/YYYY",
                             key="stages_insert_deadline")

    if st.button("Cadastrar etapa", key="stages_insert_save", type="primary"):
        if ui.is_blank(title) or deadline is None:
            st.error("Informe o título e a data-limite.")
            return
        if ui.is_blank(description):
            description = None
        error = database.execute(
            """INSERT INTO ETAPA_LEITURA (titulo, ordem, descricao, data_limite, FK_GRUPO_LEITURA_id_grupo)
               VALUES (%s, %s, %s, %s, %s)""",
            (title.strip(), order, description, deadline, group_id),
        )
        ui.finish(error, "Etapa cadastrada.")


def update():
    stage_id = ui.choose_record("Etapa", LIST_SQL, key="stages_update_choice")
    if stage_id is None:
        return
    current = database.fetch_one("SELECT titulo, ordem, descricao, data_limite FROM ETAPA_LEITURA WHERE id_etapa = %s",
                                 (stage_id,))
    current_description = current[2]
    if current_description is None:
        current_description = ""
    suffix = "_" + str(stage_id)
    title = st.text_input("Título", value=current[0], key="stages_update_title" + suffix)
    order = st.number_input("Ordem", min_value=1, max_value=100, value=current[1], step=1,
                            key="stages_update_order" + suffix)
    description = st.text_input("Descrição", value=current_description, key="stages_update_description" + suffix)
    deadline = st.date_input("Data-limite", value=current[3], format="DD/MM/YYYY",
                             key="stages_update_deadline" + suffix)

    if st.button("Salvar alterações", key="stages_update_save", type="primary"):
        if ui.is_blank(title) or deadline is None:
            st.error("Informe o título e a data-limite.")
            return
        if ui.is_blank(description):
            description = None
        error = database.execute(
            "UPDATE ETAPA_LEITURA SET titulo = %s, ordem = %s, descricao = %s, data_limite = %s WHERE id_etapa = %s",
            (title.strip(), order, description, deadline, stage_id),
        )
        ui.finish(error, "Etapa alterada.")


def delete():
    # Ready example: the stage with the latest deadline among groups that have more than one stage
    suggested_id = database.fetch_value(
        """SELECT e.id_etapa FROM ETAPA_LEITURA e
           WHERE (SELECT COUNT(*) FROM ETAPA_LEITURA x
                  WHERE x.FK_GRUPO_LEITURA_id_grupo = e.FK_GRUPO_LEITURA_id_grupo) > 1
           ORDER BY e.data_limite DESC, e.id_etapa DESC
           LIMIT 1"""
    )
    stage_id = ui.choose_record("Etapa", LIST_SQL, key="stages_delete_choice", default_id=suggested_id)
    if stage_id is None:
        return
    st.warning("Também apaga o progresso e as mensagens desta etapa.")
    if ui.delete_button("stages_delete", stage_id):
        group_id = database.fetch_value("SELECT FK_GRUPO_LEITURA_id_grupo FROM ETAPA_LEITURA WHERE id_etapa = %s",
                                        (stage_id,))
        count = database.fetch_value("SELECT COUNT(*) FROM ETAPA_LEITURA WHERE FK_GRUPO_LEITURA_id_grupo = %s",
                                     (group_id,))
        if count <= 1:
            st.error("Esta é a única etapa do grupo, e todo grupo precisa de pelo menos uma (RN09).")
            return
        error = database.execute("DELETE FROM ETAPA_LEITURA WHERE id_etapa = %s", (stage_id,))
        ui.finish(error, "Etapa excluída.")
