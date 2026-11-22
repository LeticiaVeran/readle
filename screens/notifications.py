"""Screen for the NOTIFICACAO table: notices sent to users.

Besides the notifications registered here, the system creates notices by itself
(see alerts.py). The deadline notices are created by the "Gerar avisos de prazo"
button, in the Consultar option.
"""
import streamlit as st

import alerts
import database
import ui

TYPES = ["Convite", "Mensagem", "Grupo", "Prazo"]

LIST_SQL = """SELECT n.id_notificacao, u.nome || ', ' || n.tipo || ': ' || LEFT(n.texto, 40)
              FROM NOTIFICACAO n
              JOIN USUARIO u ON u.id_usuario = n.FK_USUARIO_id_usuario
              ORDER BY n.data_hora DESC"""


def show():
    ui.page_title("Notificações", "NOTIFICACAO")
    action = ui.choose_action("notifications")
    if action == "Consultar":
        list_records()
    elif action == "Inserir":
        insert()
    elif action == "Alterar":
        update()
    elif action == "Excluir":
        delete()


def list_records():
    if st.button("Gerar avisos de prazo", key="notifications_deadlines", type="primary"):
        created = alerts.create_deadline_alerts()
        if created == 0:
            ui.finish(None, "Nenhum aviso novo de prazo.")
        else:
            ui.finish(None, ui.count_text(created, "aviso de prazo criado.", "avisos de prazo criados."))
    table = database.fetch_table(
        """SELECT n.id_notificacao AS "Id", u.nome AS "Destinatário", n.tipo AS "Tipo",
                  n.texto AS "Texto", n.data_hora AS "Data e hora", n.lida AS "Lida"
           FROM NOTIFICACAO n
           JOIN USUARIO u ON u.id_usuario = n.FK_USUARIO_id_usuario
           ORDER BY n.data_hora DESC"""
    )
    ui.show_table(table)


def insert():
    user_id = ui.choose_record("Destinatário", "SELECT id_usuario, nome FROM USUARIO ORDER BY nome",
                               key="notifications_insert_user")
    if user_id is None:
        return
    notification_type = st.selectbox("Tipo", TYPES, index=2, key="notifications_insert_type")
    text = st.text_input("Texto", value="Lembrete: confira as novidades dos seus grupos de leitura.",
                         key="notifications_insert_text")

    if st.button("Enviar notificação", key="notifications_insert_save", type="primary"):
        if ui.is_blank(text):
            st.error("Escreva o texto da notificação.")
            return
        error = database.execute(
            "INSERT INTO NOTIFICACAO (tipo, texto, FK_USUARIO_id_usuario) VALUES (%s, %s, %s)",
            (notification_type, text.strip(), user_id),
        )
        ui.finish(error, "Notificação enviada.")


def update():
    notification_id = ui.choose_record("Notificação", LIST_SQL, key="notifications_update_choice")
    if notification_id is None:
        return
    current = database.fetch_one("SELECT tipo, texto, lida FROM NOTIFICACAO WHERE id_notificacao = %s",
                                 (notification_id,))
    suffix = "_" + str(notification_id)
    notification_type = ui.choose_value("Tipo", TYPES, current[0], "notifications_update_type" + suffix)
    text = st.text_input("Texto", value=current[1], key="notifications_update_text" + suffix)
    read = st.checkbox("Lida", value=current[2], key="notifications_update_read" + suffix)

    if st.button("Salvar alterações", key="notifications_update_save", type="primary"):
        if ui.is_blank(text):
            st.error("Escreva o texto da notificação.")
            return
        error = database.execute(
            "UPDATE NOTIFICACAO SET tipo = %s, texto = %s, lida = %s WHERE id_notificacao = %s",
            (notification_type, text.strip(), read, notification_id),
        )
        ui.finish(error, "Notificação alterada.")


def delete():
    notification_id = ui.choose_record("Notificação", LIST_SQL, key="notifications_delete_choice")
    if notification_id is None:
        return
    if ui.delete_button("notifications_delete", notification_id):
        error = database.execute("DELETE FROM NOTIFICACAO WHERE id_notificacao = %s", (notification_id,))
        ui.finish(error, "Notificação excluída.")
