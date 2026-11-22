"""Screen for book recommendations with generative AI (item 7f).

The reader asks for recommendations, the AI suggests up to 3 catalog books with a
justification, and the reader can add any suggestion to the shelf as 'Quero Ler'.
The part that talks to the AI lives in ai.py.
"""
import streamlit as st

import ai
import database
import ui


def show():
    ui.page_title("Recomendação com IA")

    user_id = ui.choose_record("Leitor", "SELECT id_usuario, nome FROM USUARIO ORDER BY nome", key="ai_user")
    if user_id is None:
        return
    show_shelf_summary(user_id)

    if st.button("Pedir recomendações à IA", key="ai_ask", type="primary"):
        name = database.fetch_value("SELECT nome FROM USUARIO WHERE id_usuario = %s", (user_id,))
        with st.spinner("Consultando a IA..."):
            result = ai.recommend(user_id, name)
        result["user_id"] = user_id
        # Keeps the result in the session so it stays on screen after other clicks
        st.session_state["ai_result"] = result

    if "ai_result" in st.session_state:
        result = st.session_state["ai_result"]
        if result["user_id"] == user_id:
            show_result(result, user_id)


def show_shelf_summary(user_id):
    """Writes, in one sentence, how many books the reader has in each status
    (this is what the AI will read)."""
    rows = database.fetch_all(
        """SELECT status_leitura, COUNT(*) FROM ITEM_ESTANTE
           WHERE FK_USUARIO_id_usuario = %s GROUP BY status_leitura""",
        (user_id,),
    )
    counts = {"Lido": 0, "Lendo": 0, "Quero Ler": 0, "Abandonado": 0}
    for row in rows:
        counts[row[0]] = row[1]
    st.write("Na estante: " + ui.count_text(counts["Lido"], "lido", "lidos") + ", "
             + str(counts["Lendo"]) + " lendo, " + str(counts["Quero Ler"]) + " para ler e "
             + ui.count_text(counts["Abandonado"], "abandonado", "abandonados") + ".")


def book_on_shelf(user_id, book_id):
    count = database.fetch_value(
        "SELECT COUNT(*) FROM ITEM_ESTANTE WHERE FK_USUARIO_id_usuario = %s AND FK_LIVRO_id_livro = %s",
        (user_id, book_id),
    )
    return count > 0


def show_result(result, user_id):
    if result["error"] is not None:
        st.error(result["error"])

    if len(result["recommendations"]) > 0:
        st.caption("Recomendações geradas pelo modelo " + result["model"] + ".")

    for recommendation in result["recommendations"]:
        with st.container(border=True):
            st.subheader(recommendation["title"])
            st.caption("De " + str(recommendation["authors"]) + ". Gênero: " + str(recommendation["genres"]) + ".")
            st.write(recommendation["justification"])
            book_id = recommendation["book_id"]
            if book_on_shelf(user_id, book_id):
                st.success("Este livro já está na estante do leitor.")
            else:
                if st.button("Adicionar à estante como Quero Ler", key="ai_add_" + str(book_id)):
                    error = database.execute(
                        """INSERT INTO ITEM_ESTANTE (status_leitura, FK_LIVRO_id_livro, FK_USUARIO_id_usuario)
                           VALUES ('Quero Ler', %s, %s)""",
                        (book_id, user_id),
                    )
                    ui.finish(error, recommendation["title"] + " foi incluído na estante como Quero Ler.")

    if result["prompt"] != "":
        with st.expander("Ver o texto enviado à IA (prompt)"):
            st.text(result["prompt"])
