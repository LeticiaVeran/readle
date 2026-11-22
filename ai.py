"""
Generative AI integration (item 7f): book recommendations.

What happens when a reader asks for recommendations:
1. We read the reader's shelf from the database (books and statuses) and the ratings they gave.
2. We read the catalog books that are NOT on the reader's shelf yet.
3. We build a text (the "prompt") with this information and send it to a large
   language model (LLM) through Groq, a free service that runs open models
   such as GPT-OSS (an open model published by OpenAI) and Llama.
4. The model answers with up to 3 suggestions, each with a justification, in JSON.
5. We check that every suggested book really is in the list we sent, so the AI
   cannot invent books that are not in the catalog.

The access key lives in the .env file (GROQ_API_KEY) and never goes to GitHub.
The prompt is written in Portuguese because the answer is shown to Portuguese readers.
"""
import json
import os

import groq

import database

DEFAULT_MODEL = "openai/gpt-oss-120b"
MAX_SUGGESTIONS = 3


def get_shelf(user_id):
    """Returns the books on the reader's shelf: (title, authors, genres, status, rating)."""
    return database.fetch_all(
        """SELECT l.titulo,
                  (SELECT STRING_AGG(a.nome, ', ') FROM ESCREVE e JOIN AUTOR a ON a.id_autor = e.FK_AUTOR_id_autor
                    WHERE e.FK_LIVRO_id_livro = l.id_livro) AS autores,
                  (SELECT STRING_AGG(g.nome, ', ') FROM CLASSIFICA c JOIN GENERO g ON g.id_genero = c.FK_GENERO_id_genero
                    WHERE c.FK_LIVRO_id_livro = l.id_livro) AS generos,
                  i.status_leitura,
                  av.nota
           FROM ITEM_ESTANTE i
           JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
           LEFT JOIN AVALIACAO_RESENHA av ON av.FK_USUARIO_id_usuario = i.FK_USUARIO_id_usuario
                                         AND av.FK_LIVRO_id_livro = i.FK_LIVRO_id_livro
           WHERE i.FK_USUARIO_id_usuario = %s
           ORDER BY l.titulo""",
        (user_id,),
    )


def get_candidates(user_id):
    """Returns the catalog books that are not on the reader's shelf:
    (id, title, authors, genres, synopsis)."""
    return database.fetch_all(
        """SELECT l.id_livro, l.titulo,
                  (SELECT STRING_AGG(a.nome, ', ') FROM ESCREVE e JOIN AUTOR a ON a.id_autor = e.FK_AUTOR_id_autor
                    WHERE e.FK_LIVRO_id_livro = l.id_livro) AS autores,
                  (SELECT STRING_AGG(g.nome, ', ') FROM CLASSIFICA c JOIN GENERO g ON g.id_genero = c.FK_GENERO_id_genero
                    WHERE c.FK_LIVRO_id_livro = l.id_livro) AS generos,
                  l.sinopse
           FROM LIVRO l
           WHERE l.id_livro NOT IN (SELECT FK_LIVRO_id_livro FROM ITEM_ESTANTE
                                    WHERE FK_USUARIO_id_usuario = %s)
           ORDER BY l.titulo""",
        (user_id,),
    )


def build_prompt(reader_name, shelf, candidates):
    """Builds the text that is sent to the language model."""
    lines = []
    lines.append("Você é o assistente de recomendação literária da plataforma Readle.")
    lines.append("Leitor: " + reader_name)
    lines.append("")

    # Groups the shelf by status, so the AI understands the reader's taste
    for status in ["Lido", "Lendo", "Quero Ler", "Abandonado"]:
        lines.append("Livros com status '" + status + "' na estante:")
        count = 0
        for book in shelf:
            if book[3] == status:
                text = "- " + book[0] + " (" + str(book[1]) + "; gêneros: " + str(book[2]) + ")"
                if book[4] is not None:
                    text = text + " — nota dada pelo leitor: " + str(book[4]) + " de 5"
                lines.append(text)
                count = count + 1
        if count == 0:
            lines.append("- (nenhum)")
        lines.append("")

    lines.append("Livros disponíveis no catálogo que ainda NÃO estão na estante do leitor:")
    for book in candidates:
        synopsis = book[4]
        if synopsis is None:
            synopsis = "sem sinopse"
        lines.append("[id " + str(book[0]) + "] " + book[1] + " — " + str(book[2])
                     + " — gêneros: " + str(book[3]) + " — " + synopsis)
    lines.append("")

    lines.append("Tarefa: recomende até " + str(MAX_SUGGESTIONS) + " livros, escolhidos SOMENTE da lista "
                 "de livros disponíveis acima, que combinem com o gosto do leitor.")
    lines.append("Para cada livro, escreva em português uma justificativa curta (2 ou 3 frases) "
                 "que cite leituras e notas do leitor.")
    lines.append("Dê preferência a gêneros e autores que o leitor avaliou bem e evite o que ele avaliou mal ou abandonou.")
    lines.append("Responda apenas com JSON, exatamente neste formato:")
    lines.append('{"recomendacoes": [{"id_livro": 7, "justificativa": "texto"}]}')
    return "\n".join(lines)


def model_name():
    """Returns the name of the model that will be used (it can be changed in the .env file)."""
    return os.getenv("GROQ_MODELO", DEFAULT_MODEL)


def call_model(prompt):
    """Sends the prompt to Groq and returns the text of the answer."""
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY").strip())
    messages = [{"role": "user", "content": prompt}]
    try:
        # First asks for the answer in "JSON mode", which guarantees valid JSON
        answer = client.chat.completions.create(
            model=model_name(),
            messages=messages,
            response_format={"type": "json_object"},
        )
    except groq.BadRequestError:
        # Not every model accepts JSON mode. In that case we ask again without it:
        # the prompt itself already asks for a JSON answer.
        answer = client.chat.completions.create(
            model=model_name(),
            messages=messages,
        )
    return answer.choices[0].message.content


def parse_answer(text, candidates):
    """Reads the JSON returned by the AI and builds the list of recommendations.
    Books that are not in the candidate list are thrown away (the AI cannot invent books)."""
    if text is None:
        return []

    # Some models write something before or after the JSON (for example, a ```json block).
    # So we keep only the part between the first "{" and the last "}".
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return []
    clean_text = text[start:end + 1]

    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError:
        return []

    items = []
    if isinstance(data, dict) and "recomendacoes" in data:
        items = data["recomendacoes"]
    elif isinstance(data, list):
        items = data

    # Dictionary {book id: book data}, used to check the suggestions
    books_by_id = {}
    for book in candidates:
        books_by_id[book[0]] = book

    recommendations = []
    ids_already_added = []
    for item in items:
        if not isinstance(item, dict) or "id_livro" not in item:
            continue
        try:
            book_id = int(item["id_livro"])
        except (ValueError, TypeError):
            continue
        if book_id not in books_by_id or book_id in ids_already_added:
            continue
        book = books_by_id[book_id]
        justification = ""
        if "justificativa" in item:
            justification = str(item["justificativa"])
        recommendations.append({
            "book_id": book_id,
            "title": book[1],
            "authors": book[2],
            "genres": book[3],
            "justification": justification,
        })
        ids_already_added.append(book_id)
        if len(recommendations) == MAX_SUGGESTIONS:
            break
    return recommendations


def recommend(user_id, reader_name):
    """Runs the whole process and returns a dictionary with:
    - "recommendations": the list of suggested books
    - "prompt": the text sent to the AI
    - "error": None when everything worked, or a message explaining the problem
    - "model": the name of the AI model used
    """
    result = {"recommendations": [], "prompt": "", "error": None, "model": ""}

    shelf = get_shelf(user_id)
    candidates = get_candidates(user_id)
    if len(candidates) == 0:
        result["error"] = "Este leitor já tem todos os livros do catálogo na estante."
        return result

    prompt = build_prompt(reader_name, shelf, candidates)
    result["prompt"] = prompt

    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key.strip() == "":
        result["error"] = ("A chave da API do Groq não foi configurada. Coloque-a no arquivo .env, "
                           "na linha GROQ_API_KEY, e reinicie o programa.")
        return result
    result["model"] = model_name()

    try:
        answer_text = call_model(prompt)
    except Exception as error:
        result["error"] = "Não foi possível consultar a IA: " + str(error)
        return result

    recommendations = parse_answer(answer_text, candidates)
    if len(recommendations) == 0:
        result["error"] = "A IA respondeu, mas não foi possível aproveitar as sugestões. Tente de novo."
    result["recommendations"] = recommendations
    return result
