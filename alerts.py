"""
Automatic notifications that the system itself sends to users.

According to item 2 of the report, notifications tell users about group
invitations, new messages, relevant changes in a group and deadlines that are
getting close. The screens call these functions when those things happen:

- invitation to a group                   -> screens/members.py (Inserir)
- participation approved or removed       -> screens/members.py (Alterar)
- new message in a discussion             -> screens/messages.py (Inserir)
- administration transferred / closed     -> screens/groups.py (Alterar)
- stage deadline getting close            -> screens/notifications.py ("Gerar avisos de prazo" button)

The notification texts are data saved in the database, so they are in Portuguese.
"""
from datetime import date
from datetime import timedelta

import database

DAYS_AHEAD = 7


def notify_user(user_id, notification_type, text):
    """Saves one notification for one user."""
    database.execute(
        "INSERT INTO NOTIFICACAO (tipo, texto, FK_USUARIO_id_usuario) VALUES (%s, %s, %s)",
        (notification_type, text, user_id),
    )


def notify_group_members(group_id, notification_type, text, except_user=None):
    """Saves the same notification for every active member of the group.
    The user given in except_user (for example, who wrote the message) is skipped."""
    rows = database.fetch_all(
        """SELECT FK_USUARIO_id_usuario FROM MEMBRO_GRUPO
           WHERE FK_GRUPO_LEITURA_id_grupo = %s AND status_participacao = 'Ativo'""",
        (group_id,),
    )
    for row in rows:
        user_id = row[0]
        if user_id != except_user:
            notify_user(user_id, notification_type, text)


def create_deadline_alerts():
    """Warns the active members who have not finished a stage whose deadline is in
    the next DAYS_AHEAD days. A notice that was already sent is not repeated.
    Returns how many new notices were created."""
    today = date.today()
    last_day = today + timedelta(days=DAYS_AHEAD)
    rows = database.fetch_all(
        """SELECT m.FK_USUARIO_id_usuario, e.titulo, g.nome, e.data_limite
           FROM ETAPA_LEITURA e
           JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
           JOIN MEMBRO_GRUPO m ON m.FK_GRUPO_LEITURA_id_grupo = g.id_grupo
           WHERE g.situacao <> 'Encerrado'
             AND m.status_participacao = 'Ativo'
             AND e.data_limite BETWEEN %s AND %s
             AND NOT EXISTS (SELECT 1 FROM PROGRESSO_ETAPA p
                             WHERE p.FK_ETAPA_LEITURA_id_etapa = e.id_etapa
                               AND p.FK_MEMBRO_GRUPO_id_membro = m.id_membro
                               AND p.concluida = TRUE)""",
        (today, last_day),
    )
    created = 0
    for row in rows:
        user_id = row[0]
        text = ("A etapa " + row[1] + " do grupo " + row[2] + " termina em "
                + row[3].strftime("%d/%m") + ".")
        already_sent = database.fetch_value(
            "SELECT COUNT(*) FROM NOTIFICACAO WHERE FK_USUARIO_id_usuario = %s AND tipo = 'Prazo' AND texto = %s",
            (user_id, text),
        )
        if already_sent == 0:
            notify_user(user_id, "Prazo", text)
            created = created + 1
    return created
