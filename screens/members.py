"""Screen for the MEMBRO_GRUPO table: each user's participation in each group.

Rules applied here:
- RN06: the organizer's participation cannot be deleted or stop being 'Ativo'
- RN07: at most 20 active members per group; after any change the group
        status is recalculated
- RN08: a user joins each group at most once (enforced by the database)

It also sends automatic notifications: invitation, participation approved and removal.
"""
import streamlit as st

import alerts
import database
import rules
import ui

ROLES = ["Membro", "Moderador"]
STATUSES = ["Convidado", "Solicitado", "Ativo", "Removido"]

LIST_SQL = """SELECT m.id_membro, g.nome || ', ' || u.nome || ' (' || m.status_participacao || ')'
              FROM MEMBRO_GRUPO m
              JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
              JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
              ORDER BY g.nome, u.nome"""


def show():
    ui.page_title("Membros dos grupos", "MEMBRO_GRUPO")
    action = ui.choose_action("members")
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
        """SELECT m.id_membro AS "Id", g.nome AS "Grupo", u.nome AS "Usuário",
                  m.funcao AS "Função", m.status_participacao AS "Situação",
                  m.data_entrada AS "Entrada",
                  CASE WHEN g.FK_USUARIO_id_usuario = u.id_usuario THEN 'sim' ELSE '' END AS "Organizador"
           FROM MEMBRO_GRUPO m
           JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
           JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
           ORDER BY g.nome, u.nome"""
    )
    ui.show_table(table)


def insert():
    # Ready example: the first group that is not closed
    suggested_group = database.fetch_value(
        "SELECT id_grupo FROM GRUPO_LEITURA WHERE situacao <> 'Encerrado' ORDER BY nome LIMIT 1"
    )
    group_id = ui.choose_record("Grupo", "SELECT id_grupo, nome FROM GRUPO_LEITURA ORDER BY nome",
                                key="members_insert_group", default_id=suggested_group)
    if group_id is None:
        return
    # Only users who are not in this group yet (RN08)
    user_id = ui.choose_record(
        "Usuário",
        """SELECT id_usuario, nome FROM USUARIO
           WHERE id_usuario NOT IN (SELECT FK_USUARIO_id_usuario FROM MEMBRO_GRUPO
                                    WHERE FK_GRUPO_LEITURA_id_grupo = %s)
           ORDER BY nome""",
        (group_id,),
        key="members_insert_user",
    )
    if user_id is None:
        return
    role = st.selectbox("Função", ROLES, key="members_insert_role")
    status = st.selectbox("Situação da participação", ["Convidado", "Solicitado", "Ativo"],
                          key="members_insert_status")

    if st.button("Cadastrar participação", key="members_insert_save", type="primary"):
        if status == "Ativo":
            if rules.count_active_members(group_id) >= rules.MAX_ACTIVE_MEMBERS:
                st.error("O grupo já tem 20 membros ativos (RN07).")
                return
        error = database.execute(
            """INSERT INTO MEMBRO_GRUPO (funcao, status_participacao, FK_USUARIO_id_usuario, FK_GRUPO_LEITURA_id_grupo)
               VALUES (%s, %s, %s, %s)""",
            (role, status, user_id, group_id),
        )
        if error is None:
            rules.refresh_group_status(group_id)
            if status == "Convidado":
                group_name = database.fetch_value("SELECT nome FROM GRUPO_LEITURA WHERE id_grupo = %s", (group_id,))
                alerts.notify_user(user_id, "Convite", "Você foi convidado para o grupo " + group_name + ".")
        ui.finish(error, "Participação cadastrada.")


def update():
    member_id = ui.choose_record("Participação", LIST_SQL, key="members_update_choice")
    if member_id is None:
        return
    current = database.fetch_one(
        "SELECT funcao, status_participacao, FK_GRUPO_LEITURA_id_grupo FROM MEMBRO_GRUPO WHERE id_membro = %s",
        (member_id,),
    )
    current_status = current[1]
    group_id = current[2]
    suffix = "_" + str(member_id)
    role = ui.choose_value("Função", ROLES, current[0], "members_update_role" + suffix)
    status = ui.choose_value("Situação da participação", STATUSES, current_status, "members_update_status" + suffix)

    if st.button("Salvar alterações", key="members_update_save", type="primary"):
        if status != "Ativo" and rules.is_organizer(member_id):
            st.error("Esta é a participação do organizador, que precisa continuar 'Ativo' (RN06). "
                     "Transfira a administração na tela Grupos de leitura antes.")
            return
        if status == "Ativo" and current_status != "Ativo":
            if rules.count_active_members(group_id) >= rules.MAX_ACTIVE_MEMBERS:
                st.error("O grupo já tem 20 membros ativos (RN07).")
                return
        error = database.execute(
            "UPDATE MEMBRO_GRUPO SET funcao = %s, status_participacao = %s WHERE id_membro = %s",
            (role, status, member_id),
        )
        if error is None:
            rules.refresh_group_status(group_id)
            notify_status_change(member_id, current_status, status)
        ui.finish(error, "Participação alterada.")


def notify_status_change(member_id, old_status, new_status):
    """Notifies the member when the participation is approved or when they are removed."""
    if old_status == new_status:
        return
    data = database.fetch_one(
        """SELECT m.FK_USUARIO_id_usuario, g.nome
           FROM MEMBRO_GRUPO m JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
           WHERE m.id_membro = %s""",
        (member_id,),
    )
    user_id = data[0]
    group_name = data[1]
    if new_status == "Ativo" and (old_status == "Convidado" or old_status == "Solicitado"):
        alerts.notify_user(user_id, "Grupo", "Sua participação no grupo " + group_name + " foi confirmada.")
    if new_status == "Removido":
        alerts.notify_user(user_id, "Grupo", "Você foi removido do grupo " + group_name + ".")


def delete():
    # Ready example: a participation that is not the organizer's and is not active
    suggested_id = database.fetch_value(
        """SELECT m.id_membro
           FROM MEMBRO_GRUPO m JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
           WHERE m.FK_USUARIO_id_usuario <> g.FK_USUARIO_id_usuario
             AND m.status_participacao <> 'Ativo'
           ORDER BY m.id_membro
           LIMIT 1"""
    )
    member_id = ui.choose_record("Participação", LIST_SQL, key="members_delete_choice", default_id=suggested_id)
    if member_id is None:
        return
    st.warning("Também apaga o progresso e as mensagens deste membro.")
    if ui.delete_button("members_delete", member_id):
        if rules.is_organizer(member_id):
            st.error("A participação do organizador não pode ser excluída (RN06).")
            return
        group_id = database.fetch_value("SELECT FK_GRUPO_LEITURA_id_grupo FROM MEMBRO_GRUPO WHERE id_membro = %s",
                                        (member_id,))
        error = database.execute("DELETE FROM MEMBRO_GRUPO WHERE id_membro = %s", (member_id,))
        if error is None:
            rules.refresh_group_status(group_id)
        ui.finish(error, "Participação excluída.")
