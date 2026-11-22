"""
READLE - Application of the final project of Banco de Dados I (DEC7129)

This is the main module (item 7d): it builds the side menu and calls the
chosen screen. To run it, open a terminal in this folder and type:

    python -m streamlit run app.py

The screens are in the "screens" folder; the text the user sees is in Portuguese.
Colors and fonts are set in .streamlit/config.toml.
"""
import os
import sys

import streamlit as st
from streamlit import runtime
from streamlit.web import cli as streamlit_cli

# If the file was started with "python app.py" (for example, with the Run button
# of VS Code), Streamlit is not running yet. In that case we restart the program
# the right way, as if "streamlit run app.py" had been typed.
if __name__ == "__main__" and not runtime.exists():
    sys.argv = ["streamlit", "run", sys.argv[0]]
    sys.exit(streamlit_cli.main())

import database
import ui
from screens import authors
from screens import book_authors
from screens import book_genres
from screens import books
from screens import bookshelf
from screens import database_setup
from screens import genres
from screens import groups
from screens import home
from screens import members
from screens import messages
from screens import notifications
from screens import profile
from screens import progress
from screens import queries
from screens import recommendation
from screens import reviews
from screens import stages
from screens import users

# Images of the "static" folder: the icon of the browser tab and the logo
ICON_FILE = os.path.join(database.APP_FOLDER, "static", "readle_icon.png")
LOGO_FILE = os.path.join(database.APP_FOLDER, "static", "readle_logo.png")

# layout="wide" lets the content use the whole width of the window
st.set_page_config(page_title="Readle", page_icon=ICON_FILE, layout="wide")

# ---------------------------------------------------------------- Side menu
# The logo at the top of the side menu (the word Readle, an image in the static folder).
# When the menu is closed (for example, on a phone) the small green icon appears instead.
st.logo(LOGO_FILE, size="large", icon_image=ICON_FILE)

# Each page of the menu: the function that draws it (show), the name in the menu
# and the address shown in the browser (url_path). The dictionary keys are the
# section titles of the menu.
MENU = {
    "": [
        st.Page(home.show, title="Início", default=True),
        st.Page(profile.show, title="Perfil do leitor", url_path="perfil"),
        st.Page(recommendation.show, title="Recomendação com IA", url_path="recomendacao"),
        st.Page(queries.show, title="Consultas do relatório", url_path="consultas"),
    ],
    "Tabelas": [
        st.Page(users.show, title="Usuários", url_path="usuarios"),
        st.Page(books.show, title="Livros", url_path="livros"),
        st.Page(authors.show, title="Autores", url_path="autores"),
        st.Page(genres.show, title="Gêneros", url_path="generos"),
        st.Page(book_authors.show, title="Autoria", url_path="autoria"),
        st.Page(book_genres.show, title="Classificação", url_path="classificacao"),
        st.Page(bookshelf.show, title="Estante", url_path="estante"),
        st.Page(reviews.show, title="Avaliações", url_path="avaliacoes"),
        st.Page(groups.show, title="Grupos de leitura", url_path="grupos"),
        st.Page(members.show, title="Membros dos grupos", url_path="membros"),
        st.Page(stages.show, title="Etapas de leitura", url_path="etapas"),
        st.Page(progress.show, title="Progresso nas etapas", url_path="progresso"),
        st.Page(messages.show, title="Mensagens", url_path="mensagens"),
        st.Page(notifications.show, title="Notificações", url_path="notificacoes"),
    ],
    "Banco de dados": [
        st.Page(database_setup.show, title="Criar ou apagar o banco", url_path="banco"),
    ],
}
page = st.navigation(MENU, expanded=True)

st.sidebar.caption("Trabalho final de Banco de Dados I, UFSC, 2026.2. "
                   "Leticia Veran e Valentina Ragnini.")

# ---------------------------------------------------------------- Connection (item 7a)
problem = database.test_connection()
if problem is not None:
    st.title("Sem conexão com o banco")
    st.write("Confira os dados do arquivo **.env** (servidor, porta, nome do banco, usuário e senha) "
             "e se o PostgreSQL está ligado. Depois, recarregue a página.")
    st.code(problem)
    st.stop()

# Success message of the last operation (for example, "Autor cadastrado.")
ui.show_saved_notice()

# Only the home page and the database page work before the tables exist
if page.title != "Início" and page.title != "Criar ou apagar o banco":
    if not database.tables_created():
        st.title(page.title)
        st.warning("As tabelas ainda não existem. Crie em **Criar ou apagar o banco**.")
        st.stop()

# ---------------------------------------------------------------- Chosen screen
page.run()
