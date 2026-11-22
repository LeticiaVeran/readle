"""Screen for the GRUPO_LEITURA table: the book clubs.

Rules applied here:
- RN05: a group can only be created from a book marked 'Quero Ler' on the creator's shelf
- RN06: the organizer is also an active member of the group
- RN07: the status stays 'Aguardando membros' while there are fewer than 2 active members
- RN09: every group has at least one stage

That is why, when a group is created, the program saves three things at once:
the group, the organizer's participation and the first stage.

When the administration is transferred or the group is closed, the members
receive a notification.
"""
from datetime import date
from datetime import timedelta

import psycopg2
import streamlit as st

import alerts
import database
import rules
import ui

PRIVACY_OPTIONS = ["Público", "Privado"]

LIST_SQL = "SELECT id_grupo, nome FROM GRUPO_LEITURA ORDER BY nome"


def show():
    ui.page_title("Grupos de leitura", "GRUPO_LEITURA")
    action = ui.choose_action("groups")
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
        """SELECT g.id_grupo AS "Id", g.nome AS "Grupo", l.titulo AS "Livro",
                  u.nome AS "Organizador", g.privacidade AS "Privacidade", g.situacao AS "Situação",
                  g.data_criacao AS "Criação",
                  (SELECT COUNT(*) FROM MEMBRO_GRUPO m
                    WHERE m.FK_GRUPO_LEITURA_id_grupo = g.id_grupo
                      AND m.status_participacao = 'Ativo') AS "Membros ativos",
                  (SELECT COUNT(*) FROM ETAPA_LEITURA e
                    WHERE e.FK_GRUPO_LEITURA_id_grupo = g.id_grupo) AS "Etapas",
                  g.descricao AS "Descrição"
           FROM GRUPO_LEITURA g
           JOIN LIVRO l ON l.id_livro = g.FK_LIVRO_id_livro
           JOIN USUARIO u ON u.id_usuario = g.FK_USUARIO_id_usuario
           ORDER BY g.nome"""
    )
    ui.show_table(table)


def insert():
    # Ready example: the first user who has a book marked 'Quero Ler' (RN05)
    suggested_organizer = database.fetch_value(
        """SELECT u.id_usuario
           FROM USUARIO u JOIN ITEM_ESTANTE i ON i.FK_USUARIO_id_usuario = u.id_usuario
           WHERE i.status_leitura = 'Quero Ler'
           ORDER BY u.nome
           LIMIT 1"""
    )
    organizer_id = ui.choose_record(
        "Organizador (quem está criando o grupo)", "SELECT id_usuario, nome FROM USUARIO ORDER BY nome",
        key="groups_insert_organizer", default_id=suggested_organizer,
    )
    if organizer_id is None:
        return
    # RN05: only books marked 'Quero Ler' on the organizer's shelf
    book_id = ui.choose_record(
        "Livro (somente livros 'Quero Ler' na estante do organizador)",
        """SELECT l.id_livro, l.titulo
           FROM ITEM_ESTANTE i JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
           WHERE i.FK_USUARIO_id_usuario = %s AND i.status_leitura = 'Quero Ler'
           ORDER BY l.titulo""",
        (organizer_id,),
        key="groups_insert_book",
    )
    if book_id is None:
        st.caption("Este usuário não tem livros marcados como Quero Ler.")
        return
    name = st.text_input("Nome do grupo", value="Círculo de Leitura", key="groups_insert_name")
    description = st.text_area("Descrição (opcional)", value="Uma etapa a cada duas semanas, conversa no fim de cada uma.",
                               key="groups_insert_description")
    privacy = st.selectbox("Privacidade", PRIVACY_OPTIONS, key="groups_insert_privacy")

    st.subheader("Primeira etapa do cronograma")
    stage_title = st.text_input("Título da etapa", value="Capítulos 1 a 10", key="groups_insert_stage_title")
    stage_description = st.text_input("Descrição da etapa (opcional)", key="groups_insert_stage_description")
    deadline = st.date_input("Data-limite da etapa", value=date.today() + timedelta(days=14), format="DD/MM/YYYY",
                             key="groups_insert_stage_deadline")

    if st.button("Criar grupo", key="groups_insert_save", type="primary"):
        if ui.is_blank(name):
            st.error("Informe o nome do grupo.")
            return
        if ui.is_blank(stage_title) or deadline is None:
            st.error("Informe o título e a data-limite da primeira etapa.")
            return
        if ui.is_blank(description):
            description = None
        if ui.is_blank(stage_description):
            stage_description = None

        # Saves everything in a single transaction: the three rows, or none of them.
        connection = database.connect()
        cursor = connection.cursor()
        try:
            # 1) The group starts as 'Aguardando membros', because it only has the organizer (RN07)
            cursor.execute(
                """INSERT INTO GRUPO_LEITURA (nome, descricao, privacidade, situacao,
                                              FK_LIVRO_id_livro, FK_USUARIO_id_usuario)
                   VALUES (%s, %s, %s, 'Aguardando membros', %s, %s)
                   RETURNING id_grupo""",
                (name.strip(), description, privacy, book_id, organizer_id),
            )
            new_group_id = cursor.fetchone()[0]
            # 2) The organizer joins as an active moderator (RN06)
            cursor.execute(
                """INSERT INTO MEMBRO_GRUPO (funcao, status_participacao,
                                             FK_USUARIO_id_usuario, FK_GRUPO_LEITURA_id_grupo)
                   VALUES ('Moderador', 'Ativo', %s, %s)""",
                (organizer_id, new_group_id),
            )
            # 3) The first stage of the schedule (RN09)
            cursor.execute(
                """INSERT INTO ETAPA_LEITURA (titulo, ordem, descricao, data_limite, FK_GRUPO_LEITURA_id_grupo)
                   VALUES (%s, 1, %s, %s, %s)""",
                (stage_title.strip(), stage_description, deadline, new_group_id),
            )
            connection.commit()
            error = None
        except psycopg2.Error as db_error:
            connection.rollback()
            error = database.translate_error(db_error)
        connection.close()
        ui.finish(error, "Grupo criado, com o organizador como membro e a primeira etapa.")


def update():
    group_id = ui.choose_record("Grupo", LIST_SQL, key="groups_update_choice")
    if group_id is None:
        return
    current = database.fetch_one(
        """SELECT nome, descricao, privacidade, situacao, FK_USUARIO_id_usuario
           FROM GRUPO_LEITURA WHERE id_grupo = %s""",
        (group_id,),
    )
    current_description = current[1]
    if current_description is None:
        current_description = ""
    old_status = current[3]
    old_organizer = current[4]
    suffix = "_" + str(group_id)
    name = st.text_input("Nome do grupo", value=current[0], key="groups_update_name" + suffix)
    description = st.text_area("Descrição", value=current_description, key="groups_update_description" + suffix)
    privacy = ui.choose_value("Privacidade", PRIVACY_OPTIONS, current[2], "groups_update_privacy" + suffix)
    # Transferring the administration: the new organizer must be an active member (RN06)
    new_organizer = ui.choose_record(
        "Organizador (para transferir a administração, escolha outro membro ativo)",
        """SELECT u.id_usuario, u.nome
           FROM MEMBRO_GRUPO m JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
           WHERE m.FK_GRUPO_LEITURA_id_grupo = %s AND m.status_participacao = 'Ativo'
           ORDER BY u.nome""",
        (group_id,),
        key="groups_update_organizer" + suffix,
        default_id=old_organizer,
    )
    closed = st.checkbox("Grupo encerrado", value=(old_status == "Encerrado"), key="groups_update_closed" + suffix)

    if st.button("Salvar alterações", key="groups_update_save", type="primary"):
        if ui.is_blank(name):
            st.error("Informe o nome do grupo.")
            return
        if ui.is_blank(description):
            description = None
        if closed:
            new_status = "Encerrado"
        else:
            new_status = rules.status_from_members(group_id)
        error = database.execute(
            """UPDATE GRUPO_LEITURA
               SET nome = %s, descricao = %s, privacidade = %s, situacao = %s, FK_USUARIO_id_usuario = %s
               WHERE id_grupo = %s""",
            (name.strip(), description, privacy, new_status, new_organizer, group_id),
        )
        if error is None:
            # Tells the members about important changes in the group
            if new_organizer != old_organizer:
                new_organizer_name = database.fetch_value("SELECT nome FROM USUARIO WHERE id_usuario = %s",
                                                          (new_organizer,))
                alerts.notify_group_members(group_id, "Grupo", "A administração do grupo " + name.strip()
                                            + " foi transferida para " + new_organizer_name + ".")
            if new_status == "Encerrado" and old_status != "Encerrado":
                alerts.notify_group_members(group_id, "Grupo", "O grupo " + name.strip()
                                            + " foi encerrado. Obrigado por participar!")
        ui.finish(error, "Grupo alterado.")


def delete():
    # Ready example: the most recently created group
    suggested_id = database.fetch_value(
        "SELECT id_grupo FROM GRUPO_LEITURA ORDER BY data_criacao DESC, id_grupo DESC LIMIT 1"
    )
    group_id = ui.choose_record("Grupo", LIST_SQL, key="groups_delete_choice", default_id=suggested_id)
    if group_id is None:
        return
    st.warning("Também apaga as participações, as etapas, o progresso e as mensagens do grupo.")
    if ui.delete_button("groups_delete", group_id):
        error = database.execute("DELETE FROM GRUPO_LEITURA WHERE id_grupo = %s", (group_id,))
        ui.finish(error, "Grupo excluído.")
