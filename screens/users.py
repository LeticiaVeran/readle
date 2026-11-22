"""Screen for the USUARIO table: the readers' accounts."""
import hashlib

import streamlit as st

import database
import ui

LIST_SQL = "SELECT id_usuario, nome FROM USUARIO ORDER BY nome"


def hash_password(password):
    """Turns the password into a code (SHA-256 hash). The original password is never stored."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def show():
    ui.page_title("Usuários", "USUARIO")
    action = ui.choose_action("users")
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
        """SELECT id_usuario AS "Id", nome AS "Nome", nome_usuario AS "Nome de usuário",
                  email AS "E-mail", data_cadastro AS "Cadastro"
           FROM USUARIO
           ORDER BY nome"""
    )
    ui.show_table(table)


def validate(name, username, email):
    """Checks the fields before saving. Returns an error message or None."""
    if ui.is_blank(name):
        return "Informe o nome."
    if ui.is_blank(username):
        return "Informe o nome de usuário."
    if ui.is_blank(email) or "@" not in email:
        return "Informe um e-mail válido."
    return None


def insert():
    name = st.text_input("Nome completo", value="Paula Freitas", key="users_insert_name")
    username = st.text_input("Nome de usuário", value="paula.freitas", key="users_insert_username")
    email = st.text_input("E-mail", value="paula.freitas@exemplo.com", key="users_insert_email")
    password = st.text_input("Senha", value="readle123", type="password", key="users_insert_password")

    if st.button("Cadastrar usuário", key="users_insert_save", type="primary"):
        problem = validate(name, username, email)
        if problem is None and len(password) < 6:
            problem = "A senha precisa ter pelo menos 6 caracteres."
        if problem is not None:
            st.error(problem)
            return
        error = database.execute(
            """INSERT INTO USUARIO (nome, nome_usuario, email, senha_hash)
               VALUES (%s, %s, %s, %s)""",
            (name.strip(), username.strip(), email.strip(), hash_password(password)),
        )
        ui.finish(error, "Usuário cadastrado.")


def update():
    user_id = ui.choose_record("Usuário", LIST_SQL, key="users_update_choice")
    if user_id is None:
        return
    current = database.fetch_one(
        "SELECT nome, nome_usuario, email, data_cadastro FROM USUARIO WHERE id_usuario = %s",
        (user_id,),
    )
    suffix = "_" + str(user_id)
    name = st.text_input("Nome completo", value=current[0], key="users_update_name" + suffix)
    username = st.text_input("Nome de usuário", value=current[1], key="users_update_username" + suffix)
    email = st.text_input("E-mail", value=current[2], key="users_update_email" + suffix)
    signup_date = st.date_input("Data de cadastro", value=current[3], format="DD/MM/YYYY",
                                key="users_update_date" + suffix)
    new_password = st.text_input("Nova senha (deixe em branco para manter a atual)", type="password",
                                 key="users_update_password" + suffix)

    if st.button("Salvar alterações", key="users_update_save", type="primary"):
        problem = validate(name, username, email)
        if problem is not None:
            st.error(problem)
            return
        if new_password == "":
            error = database.execute(
                """UPDATE USUARIO SET nome = %s, nome_usuario = %s, email = %s, data_cadastro = %s
                   WHERE id_usuario = %s""",
                (name.strip(), username.strip(), email.strip(), signup_date, user_id),
            )
        else:
            error = database.execute(
                """UPDATE USUARIO SET nome = %s, nome_usuario = %s, email = %s, data_cadastro = %s,
                          senha_hash = %s
                   WHERE id_usuario = %s""",
                (name.strip(), username.strip(), email.strip(), signup_date,
                 hash_password(new_password), user_id),
            )
        ui.finish(error, "Usuário alterado.")


def delete():
    # Ready example: the newest user who does not organize any group (so the deletion is allowed)
    suggested_id = database.fetch_value(
        """SELECT id_usuario FROM USUARIO
           WHERE id_usuario NOT IN (SELECT FK_USUARIO_id_usuario FROM GRUPO_LEITURA)
           ORDER BY data_cadastro DESC, id_usuario DESC
           LIMIT 1"""
    )
    user_id = ui.choose_record("Usuário", LIST_SQL, key="users_delete_choice", default_id=suggested_id)
    if user_id is None:
        return
    st.warning("Também apaga a estante, as avaliações, as notificações e as participações do usuário.")
    if ui.delete_button("users_delete", user_id):
        error = database.execute("DELETE FROM USUARIO WHERE id_usuario = %s", (user_id,))
        ui.finish(error, "Usuário excluído.")
