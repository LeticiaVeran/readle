"""Screen for the PROGRESSO_ETAPA table: which stages each member has finished.

RN10: at most one progress row per member and stage (enforced by the database;
      the screen only offers the stages the member has no progress row for yet).
RN11: the member and the stage must belong to the same group. To guarantee that,
      the screen asks for the group first and then only shows its members and stages.
"""
from datetime import date

import streamlit as st

import database
import rules
import ui

LIST_SQL = """SELECT p.id_progresso,
                     g.nome || ', ' || u.nome || ', etapa ' || e.ordem
                     || CASE WHEN p.concluida THEN ' (concluída)' ELSE ' (não concluída)' END
              FROM PROGRESSO_ETAPA p
              JOIN MEMBRO_GRUPO m ON m.id_membro = p.FK_MEMBRO_GRUPO_id_membro
              JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
              JOIN ETAPA_LEITURA e ON e.id_etapa = p.FK_ETAPA_LEITURA_id_etapa
              JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
              ORDER BY g.nome, u.nome, e.ordem"""

# Active members that still have a stage of their group without a progress row
MISSING_PROGRESS_SQL = """
    SELECT m.FK_GRUPO_LEITURA_id_grupo, m.id_membro
    FROM MEMBRO_GRUPO m
    JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
    JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
    JOIN ETAPA_LEITURA e ON e.FK_GRUPO_LEITURA_id_grupo = m.FK_GRUPO_LEITURA_id_grupo
    WHERE m.status_participacao = 'Ativo'
      AND NOT EXISTS (SELECT 1 FROM PROGRESSO_ETAPA p
                      WHERE p.FK_MEMBRO_GRUPO_id_membro = m.id_membro
                        AND p.FK_ETAPA_LEITURA_id_etapa = e.id_etapa)"""


def show():
    ui.page_title("Progresso nas etapas", "PROGRESSO_ETAPA")
    action = ui.choose_action("progress")
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
        """SELECT p.id_progresso AS "Id", g.nome AS "Grupo", u.nome AS "Membro",
                  e.ordem AS "Etapa", e.titulo AS "Título da etapa",
                  p.concluida AS "Concluída", p.data_confirmacao AS "Confirmação"
           FROM PROGRESSO_ETAPA p
           JOIN MEMBRO_GRUPO m ON m.id_membro = p.FK_MEMBRO_GRUPO_id_membro
           JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
           JOIN ETAPA_LEITURA e ON e.id_etapa = p.FK_ETAPA_LEITURA_id_etapa
           JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
           ORDER BY g.nome, u.nome, e.ordem"""
    )
    ui.show_table(table)


def insert():
    # Ready example: a group (and a member of it) that still has a stage without progress
    suggested_group = database.fetch_value(MISSING_PROGRESS_SQL + " ORDER BY g.nome, u.nome LIMIT 1")
    group_id = ui.choose_record("Grupo", "SELECT id_grupo, nome FROM GRUPO_LEITURA ORDER BY nome",
                                key="progress_insert_group", default_id=suggested_group)
    if group_id is None:
        return
    suggested_member = database.fetch_one(
        MISSING_PROGRESS_SQL + " AND m.FK_GRUPO_LEITURA_id_grupo = %s ORDER BY u.nome LIMIT 1", (group_id,)
    )
    suggested_member_id = None
    if suggested_member is not None:
        suggested_member_id = suggested_member[1]
    member_id = ui.choose_record(
        "Membro (membros ativos deste grupo)",
        """SELECT m.id_membro, u.nome
           FROM MEMBRO_GRUPO m JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
           WHERE m.FK_GRUPO_LEITURA_id_grupo = %s AND m.status_participacao = 'Ativo'
           ORDER BY u.nome""",
        (group_id,),
        key="progress_insert_member",
        default_id=suggested_member_id,
    )
    if member_id is None:
        return
    # Only the stages of this group that have no progress row for this member yet (RN10)
    stage_id = ui.choose_record(
        "Etapa (etapas deste grupo ainda sem registro para este membro)",
        """SELECT e.id_etapa, 'Etapa ' || e.ordem || ': ' || e.titulo
           FROM ETAPA_LEITURA e
           WHERE e.FK_GRUPO_LEITURA_id_grupo = %s
             AND NOT EXISTS (SELECT 1 FROM PROGRESSO_ETAPA p
                             WHERE p.FK_MEMBRO_GRUPO_id_membro = %s
                               AND p.FK_ETAPA_LEITURA_id_etapa = e.id_etapa)
           ORDER BY e.ordem""",
        (group_id, member_id),
        key="progress_insert_stage",
    )
    if stage_id is None:
        return
    finished = st.checkbox("Etapa concluída", key="progress_insert_finished")
    confirmation_date = None
    if finished:
        confirmation_date = st.date_input("Data da confirmação", value=date.today(), format="DD/MM/YYYY",
                                          key="progress_insert_date")

    if st.button("Registrar progresso", key="progress_insert_save", type="primary"):
        if not rules.same_group(member_id, stage_id):
            st.error("O membro e a etapa precisam ser do mesmo grupo (RN11).")
            return
        error = database.execute(
            """INSERT INTO PROGRESSO_ETAPA (concluida, data_confirmacao, FK_ETAPA_LEITURA_id_etapa, FK_MEMBRO_GRUPO_id_membro)
               VALUES (%s, %s, %s, %s)""",
            (finished, confirmation_date, stage_id, member_id),
        )
        ui.finish(error, "Progresso registrado.")


def update():
    progress_id = ui.choose_record("Registro de progresso", LIST_SQL, key="progress_update_choice")
    if progress_id is None:
        return
    current = database.fetch_one("SELECT concluida, data_confirmacao FROM PROGRESSO_ETAPA WHERE id_progresso = %s",
                                 (progress_id,))
    suffix = "_" + str(progress_id)
    finished = st.checkbox("Etapa concluída", value=current[0], key="progress_update_finished" + suffix)
    confirmation_date = None
    if finished:
        current_date = current[1]
        if current_date is None:
            current_date = date.today()
        confirmation_date = st.date_input("Data da confirmação", value=current_date, format="DD/MM/YYYY",
                                          key="progress_update_date" + suffix)

    if st.button("Salvar alterações", key="progress_update_save", type="primary"):
        error = database.execute(
            "UPDATE PROGRESSO_ETAPA SET concluida = %s, data_confirmacao = %s WHERE id_progresso = %s",
            (finished, confirmation_date, progress_id),
        )
        ui.finish(error, "Progresso alterado.")


def delete():
    progress_id = ui.choose_record("Registro de progresso", LIST_SQL, key="progress_delete_choice")
    if progress_id is None:
        return
    if ui.delete_button("progress_delete", progress_id):
        error = database.execute("DELETE FROM PROGRESSO_ETAPA WHERE id_progresso = %s", (progress_id,))
        ui.finish(error, "Registro de progresso excluído.")
