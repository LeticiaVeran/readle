# Readle

Reading organizer and book club platform — final project of **Banco de Dados I
(DEC7129, 2026.2)** at UFSC Araranguá, taught by Prof. Alexandre Leopoldo Gonçalves.

Team: Leticia Veran and Valentina Ragnini.

Readle is a **Python + Streamlit** application connected to a **PostgreSQL** database.
It opens in the browser and lets you create, read, update and delete the rows of all
14 tables, run the three summary queries of the report (as a table and as a chart) and
ask a generative AI model for book recommendations based on the reader's shelf.

- **Report (in Portuguese):** [`docs/Relatorio_Readle.pdf`](docs/Relatorio_Readle.pdf)
  (editable version: [`docs/Relatorio_Readle.docx`](docs/Relatorio_Readle.docx))
- **Data models (brModelo):** [`docs/models/`](docs/models)

> The user interface and the sample data are in Portuguese, like the report and the
> presentation. Table and column names are also in Portuguese because they come from the
> data model described in the report. Code, comments and documentation are in English.

---

## Requirements

- Python 3.10 or newer
- PostgreSQL 14 or newer (pgAdmin is optional, but handy)
- A free [Groq](https://console.groq.com) API key, for the AI recommendation (item 7f)

## Getting started (Windows)

1. **Install Python** from <https://www.python.org/downloads/>. On the first screen of the
   installer, tick **"Add python.exe to PATH"**.
2. **Create an empty database.** In pgAdmin: right-click **Databases → Create → Database...**,
   name it `readle` and save. The application creates the tables itself.
3. **Open a terminal in the project folder** (in VS Code: *Terminal → New Terminal*).
4. **Install the libraries** (the first time, and again whenever `requirements.txt` changes):
   ```
   python -m pip install -r requirements.txt
   ```
   The look of the app needs Streamlit 1.66 or newer; this command updates it.
5. **Create the `.env` file** from the example and fill it in:
   ```
   Copy-Item .env.example .env
   ```
   - `DB_PASSWORD`: the password of the `postgres` user (the one you use in pgAdmin);
   - `DB_NAME`: the database created in step 2;
   - `GROQ_API_KEY`: the AI key (see below). Without it everything else works; only the
     recommendation screen shows a warning.
6. **Run the application:**
   ```
   python -m streamlit run app.py
   ```
   The browser opens at <http://localhost:8501>. Opening `app.py` in VS Code and pressing
   the Run button (▶) also works. Press `Ctrl + C` in the terminal to stop it.
7. **Create the tables:** in the side menu, open **Criar ou apagar o banco** and click
   **Criar tabelas e carregar dados**.

### Groq API key (item 7f)

1. Sign in at <https://console.groq.com> (a Google or GitHub account works).
2. Open **API Keys → Create API Key**, give it a name (e.g. `readle`) and copy it. It starts
   with `gsk_` and is shown only once.
3. Paste it on the `GROQ_API_KEY=` line of `.env` and restart the application.

The model is set on the `GROQ_MODELO` line (default: `openai/gpt-oss-120b`, an open model
published by OpenAI and served for free by Groq). If you get a "model not found" or a rate
limit error, try `openai/gpt-oss-20b`.

**Never commit the `.env` file or paste your keys anywhere.** It is already in `.gitignore`.

---

## Where each requirement (item 7) is

| Requirement | Where |
|---|---|
| 7a — Connect to PostgreSQL | `database.py` (`connect`) |
| 7b — Insert, update, delete and read in every table | `screens/` — one module per table |
| 7c — The 3 queries of item 6 as a table and a chart | `screens/queries.py` + `sql/queries.sql` |
| 7d — Main menu | `app.py` |
| 7e — Create tables + load data / drop all tables | `screens/database_setup.py` + `sql/` |
| 7f — Generative AI integration | `ai.py` + `screens/recommendation.py` |

## Project structure

```
readle/
├── app.py              main module: side menu that calls the chosen screen
├── database.py         connection and functions to read and write data
├── ui.py               screen pieces shared by all screens (lists, buttons, messages)
├── rules.py            business rules that span several tables (RN06, RN07, RN11, RN12)
├── alerts.py           automatic notifications (invitations, messages, group changes, deadlines)
├── ai.py               book recommendation with a language model (Groq)
├── screens/            one screen per table, plus home, database setup, profile, queries and AI
├── .streamlit/
│   └── config.toml     theme: colors, fonts and toolbar
├── static/             font files, logo and browser tab icon used by the theme
├── sql/
│   ├── schema.sql      DDL: the 14 tables, constraints and foreign keys
│   ├── seed.sql        sample data (dates relative to the day it runs)
│   ├── drop.sql        drops every table
│   └── queries.sql     the 3 queries of item 6
├── docs/               report (Portuguese), figures and brModelo files
├── requirements.txt    Python libraries
└── .env.example        template of the settings file
```

Every table screen follows the same pattern: `show()` draws the
**Consultar / Inserir / Alterar / Excluir** choice and calls `list_records()`, `insert()`,
`update()` or `delete()`. Once you understand one screen (e.g. `screens/authors.py`) you
understand them all.

Every button works the first time it is pressed: forms come filled with a valid example,
and delete screens start on a record that can be deleted.

## Look and feel

The theme lives in `.streamlit/config.toml`, so the visual identity needs no extra Python code:

- the side menu is dark green, like the cloth cover of a library book, and the main area
  is a plain white page that uses the whole width of the window;
- all text uses **Libre Franklin** (a free revival of Franklin Gothic, under the SIL Open Font
  License), served from `static/fonts`, so it works offline;
- `st.navigation` builds the menu with sections and gives every screen its own address
  (for example `http://localhost:8501/livros`);
- `ui.page_title()`, `ui.choose_action()` and `ui.show_table()` give every screen the same
  title, action bar and table format (dates as dd/mm/yyyy, blank cells instead of None).

## Business rules

The database enforces uniqueness, allowed values and delete behaviour (see the header
of `sql/schema.sql`). The application enforces the rest:

- **RN04** — only books marked *Lido* can be reviewed (the book list is already filtered);
- **RN05** — a group is created only from a *Quero Ler* book on the organizer's shelf;
- **RN06** — the organizer joins as an active member and cannot be removed;
- **RN07** — at most 20 active members, and the group status is recalculated automatically;
- **RN09** — a group is created together with its first stage, and its last stage cannot be deleted;
- **RN11** — progress and messages only link a member and a stage of the same group;
- **RN12** — messages of a stage stay locked until its deadline or until the member finishes it
  (see **Mensagens → Consultar → Ver como membro**);
- every book has at least one author and one genre.

## Other features described in the report

- **Reader profile** (*Perfil do leitor*): shelf, reading history, reviews, groups and
  notifications of a reader, plus the other readers who want to read the same books.
- **Catalog search** by title, author or ISBN (*Tabelas → Livros → Consultar*).
- **Automatic notifications** (`alerts.py`): group invitation, participation approved or
  removed, new message, administration transferred, group closed and upcoming deadline
  (**Gerar avisos de prazo** button in *Tabelas → Notificações → Consultar*).
- **Moderation**: messages can be hidden (*Tabelas → Mensagens → Alterar*).

The application works as an administration panel to demonstrate the database operations:
there is no login, and any operation can be done for any user.

## Sample data

`sql/seed.sql` loads 12 users, 30 books, 27 authors, 9 genres, 84 shelf items,
38 reviews, 5 reading groups, 15 stages and 47 messages. All dates are written relative
to the day the script runs (`CURRENT_DATE - n`), so deadlines, locked stages and deadline
notices always make sense. **Recreate the database right before a demo** to start from
the original data. Every sample user's password is `readle123`.

## Troubleshooting

- **"Não foi possível conectar ao banco de dados" / "no password supplied"**: the `.env`
  file is missing or has no password. Check that it is named exactly `.env` (not
  `.env.txt`), that it is in the same folder as `app.py`, and that the password, port
  and database name are right.
- **"python is not recognized"**: reinstall Python ticking "Add python.exe to PATH", or use
  `py` instead of `python`.
- **"No module named ..."**: run `python -m pip install -r requirements.txt` again.
- **AI rate limit**: wait a minute and try again.

