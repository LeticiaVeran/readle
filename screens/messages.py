"""Screen for the MENSAGEM table: the discussions of each stage.

RN11: the member and the stage must belong to the same group (the screen asks for the group first).
RN12: a member only reads and posts messages of a stage after its deadline or after
confirming that they finished the stage. This is what prevents spoilers.
The "Ver como membro" option shows the discussion the way a member sees it.
When a message is posted, the other active members of the group get a notification.
"""
import streamlit as st

import alerts
import database
import rules
import ui

VISIBILITY_OPTIONS = ["Visível", "Oculta"]

LIST_SQL = """SELECT x.id_mensagem,
                     g.nome || ', etapa ' || e.ordem || ', ' || u.nome || ': ' || LEFT(x.conteudo, 40)
              FROM MENSAGEM x
              JOIN MEMBRO_GRUPO m ON m.id_membro = x.FK_MEMBRO_GRUPO_id_membro
              JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
              JOIN ETAPA_LEITURA e ON e.id_etapa = x.FK_ETAPA_LEITURA_id_etapa
              JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
              ORDER BY g.nome, e.ordem, x.data_hora_publicacao"""

GROUP_LIST_SQL = "SELECT id_grupo, nome FROM GRUPO_LEITURA ORDER BY nome"


def show():
    ui.page_title("Mensagens", "MENSAGEM")
    action = ui.choose_action("messages")
    if action == "Consultar":
        list_records()
    elif action == "Inserir":
        insert()
    elif action == "Alterar":
        update()
    elif action == "Excluir":
        delete()


def list_records():
    mode = st.radio("Como mostrar", ["Todas as mensagens (visão da moderação)", "Ver como membro (sem spoilers)"],
                    key="messages_list_mode", horizontal=True)
    if mode == "Todas as mensagens (visão da moderação)":
        table = database.fetch_table(
            """SELECT x.id_mensagem AS "Id", g.nome AS "Grupo", e.ordem AS "Etapa", u.nome AS "Autor",
                      x.conteudo AS "Mensagem", x.data_hora_publicacao AS "Publicação",
                      x.data_hora_edicao AS "Edição", x.situacao AS "Situação"
               FROM MENSAGEM x
               JOIN MEMBRO_GRUPO m ON m.id_membro = x.FK_MEMBRO_GRUPO_id_membro
               JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
               JOIN ETAPA_LEITURA e ON e.id_etapa = x.FK_ETAPA_LEITURA_id_etapa
               JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
               ORDER BY g.nome, e.ordem, x.data_hora_publicacao"""
        )
        ui.show_table(table)
    else:
        show_as_member()


def show_as_member():
    """Shows a group's discussion from the point of view of one member, following RN12."""
    # Ready example: the first group that still has a stage whose deadline has not arrived
    suggested_group = database.fetch_value(
        """SELECT g.id_grupo FROM GRUPO_LEITURA g
           WHERE EXISTS (SELECT 1 FROM ETAPA_LEITURA e
                         WHERE e.FK_GRUPO_LEITURA_id_grupo = g.id_grupo AND e.data_limite > CURRENT_DATE)
           ORDER BY g.nome
           LIMIT 1"""
    )
    group_id = ui.choose_record("Grupo", GROUP_LIST_SQL, key="messages_view_group", default_id=suggested_group)
    if group_id is None:
        return
    member_id = ui.choose_record(
        "Ver como o membro",
        """SELECT m.id_membro, u.nome
           FROM MEMBRO_GRUPO m JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
           WHERE m.FK_GRUPO_LEITURA_id_grupo = %s
           ORDER BY u.nome""",
        (group_id,),
        key="messages_view_member",
    )
    if member_id is None:
        return
    stages = database.fetch_all(
        "SELECT id_etapa, ordem, titulo, data_limite FROM ETAPA_LEITURA WHERE FK_GRUPO_LEITURA_id_grupo = %s ORDER BY ordem",
        (group_id,),
    )
    for stage in stages:
        stage_id = stage[0]
        st.subheader("Etapa " + str(stage[1]) + ": " + stage[2])
        if not rules.stage_unlocked(member_id, stage_id):
            st.info("Bloqueada para este membro até " + ui.format_date(stage[3])
                    + ", ou até ele marcar a etapa como concluída.")
            continue
        stage_messages = database.fetch_all(
            """SELECT u.nome, x.data_hora_publicacao, x.conteudo
               FROM MENSAGEM x
               JOIN MEMBRO_GRUPO m ON m.id_membro = x.FK_MEMBRO_GRUPO_id_membro
               JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
               WHERE x.FK_ETAPA_LEITURA_id_etapa = %s AND x.situacao = 'Visível'
               ORDER BY x.data_hora_publicacao""",
            (stage_id,),
        )
        if len(stage_messages) == 0:
            st.caption("Nenhuma mensagem nesta etapa.")
        for message in stage_messages:
            posted_at = message[1].strftime("%d/%m/%Y às %H:%M")
            # Two spaces + \n break the line; :gray[...] writes in gray
            st.markdown("**" + message[0] + "**  \n:gray[" + posted_at + "]")
            st.write(message[2])


def first_unlocked_stage(member_id, group_id):
    """Returns the id of the first stage of the group that is unlocked for the member (RN12), or None."""
    stages = database.fetch_all(
        "SELECT id_etapa FROM ETAPA_LEITURA WHERE FK_GRUPO_LEITURA_id_grupo = %s ORDER BY ordem", (group_id,)
    )
    for stage in stages:
        if rules.stage_unlocked(member_id, stage[0]):
            return stage[0]
    return None


def insert():
    # Ready example: the first active group (its first member and the first stage unlocked for them)
    suggested_group = database.fetch_value(
        "SELECT id_grupo FROM GRUPO_LEITURA WHERE situacao = 'Ativo' ORDER BY nome LIMIT 1"
    )
    group_id = ui.choose_record("Grupo", GROUP_LIST_SQL, key="messages_insert_group", default_id=suggested_group)
    if group_id is None:
        return
    member_id = ui.choose_record(
        "Autor da mensagem (membros ativos deste grupo)",
        """SELECT m.id_membro, u.nome
           FROM MEMBRO_GRUPO m JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
           WHERE m.FK_GRUPO_LEITURA_id_grupo = %s AND m.status_participacao = 'Ativo'
           ORDER BY u.nome""",
        (group_id,),
        key="messages_insert_member",
    )
    if member_id is None:
        return
    stage_id = ui.choose_record(
        "Etapa",
        """SELECT id_etapa, 'Etapa ' || ordem || ': ' || titulo
           FROM ETAPA_LEITURA WHERE FK_GRUPO_LEITURA_id_grupo = %s ORDER BY ordem""",
        (group_id,),
        key="messages_insert_stage",
        default_id=first_unlocked_stage(member_id, group_id),
    )
    if stage_id is None:
        return
    content = st.text_area("Mensagem", value="Alguém mais achou esta parte mais lenta que a anterior?",
                           key="messages_insert_content")

    if st.button("Publicar mensagem", key="messages_insert_save", type="primary"):
        if ui.is_blank(content):
            st.error("Escreva a mensagem.")
            return
        if not rules.same_group(member_id, stage_id):
            st.error("O membro e a etapa precisam ser do mesmo grupo (RN11).")
            return
        if not rules.stage_unlocked(member_id, stage_id):
            st.error("Esta etapa ainda está bloqueada para este membro: a data-limite não chegou e ele "
                     "ainda não confirmou a conclusão (RN12).")
            return
        error = database.execute(
            """INSERT INTO MENSAGEM (conteudo, FK_ETAPA_LEITURA_id_etapa, FK_MEMBRO_GRUPO_id_membro)
               VALUES (%s, %s, %s)""",
            (content.strip(), stage_id, member_id),
        )
        if error is None:
            # Warns the other active members (the notice does not show the content, to avoid spoilers)
            author = database.fetch_one(
                """SELECT u.id_usuario, u.nome, g.nome
                   FROM MEMBRO_GRUPO m
                   JOIN USUARIO u ON u.id_usuario = m.FK_USUARIO_id_usuario
                   JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
                   WHERE m.id_membro = %s""",
                (member_id,),
            )
            alerts.notify_group_members(group_id, "Mensagem",
                                        "Nova mensagem de " + author[1] + " em " + author[2] + ".",
                                        except_user=author[0])
        ui.finish(error, "Mensagem publicada.")


def update():
    message_id = ui.choose_record("Mensagem", LIST_SQL, key="messages_update_choice")
    if message_id is None:
        return
    current = database.fetch_one("SELECT conteudo, situacao FROM MENSAGEM WHERE id_mensagem = %s", (message_id,))
    current_content = current[0]
    suffix = "_" + str(message_id)
    content = st.text_area("Mensagem", value=current_content, key="messages_update_content" + suffix)
    visibility = ui.choose_value("Situação (a moderação pode ocultar mensagens inadequadas)",
                                 VISIBILITY_OPTIONS, current[1], "messages_update_visibility" + suffix)

    if st.button("Salvar alterações", key="messages_update_save", type="primary"):
        if ui.is_blank(content):
            st.error("A mensagem não pode ficar vazia.")
            return
        if content.strip() != current_content:
            # The text changed: saves the date and time of the edit
            error = database.execute(
                "UPDATE MENSAGEM SET conteudo = %s, situacao = %s, data_hora_edicao = NOW() WHERE id_mensagem = %s",
                (content.strip(), visibility, message_id),
            )
        else:
            error = database.execute(
                "UPDATE MENSAGEM SET situacao = %s WHERE id_mensagem = %s",
                (visibility, message_id),
            )
        ui.finish(error, "Mensagem alterada.")


def delete():
    message_id = ui.choose_record("Mensagem", LIST_SQL, key="messages_delete_choice")
    if message_id is None:
        return
    if ui.delete_button("messages_delete", message_id):
        error = database.execute("DELETE FROM MENSAGEM WHERE id_mensagem = %s", (message_id,))
        ui.finish(error, "Mensagem excluída.")
