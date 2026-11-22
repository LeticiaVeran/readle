"""
Business rules that the database alone does not guarantee (report, Quadro 1).

The database already enforces many rules with UNIQUE, CHECK and foreign keys.
The ones that depend on more than one table live here, and the screens call
these functions before writing:

- RN06: the organizer is also an active member of the group
- RN07: at most 20 active members; 'Aguardando membros' while there are fewer than 2
- RN11: progress and messages only link a member and a stage of the same group
- RN12: the messages of a stage unlock after its deadline or after the member
        confirms the stage is finished
"""
from datetime import date

import database

MAX_ACTIVE_MEMBERS = 20


def count_active_members(group_id):
    """Counts how many members with status 'Ativo' the group has."""
    return database.fetch_value(
        """SELECT COUNT(*) FROM MEMBRO_GRUPO
           WHERE FK_GRUPO_LEITURA_id_grupo = %s AND status_participacao = 'Ativo'""",
        (group_id,),
    )


def status_from_members(group_id):
    """RN07: returns 'Ativo' when the group has 2 or more active members,
    or 'Aguardando membros' when it has fewer than 2."""
    if count_active_members(group_id) >= 2:
        return "Ativo"
    return "Aguardando membros"


def refresh_group_status(group_id):
    """Recalculates the group status after a member joins, leaves or changes status.
    A closed group ('Encerrado') does not change by itself."""
    current_status = database.fetch_value("SELECT situacao FROM GRUPO_LEITURA WHERE id_grupo = %s", (group_id,))
    if current_status is None or current_status == "Encerrado":
        return
    database.execute(
        "UPDATE GRUPO_LEITURA SET situacao = %s WHERE id_grupo = %s",
        (status_from_members(group_id), group_id),
    )


def is_organizer(member_id):
    """RN06: returns True when this participation belongs to the group organizer."""
    count = database.fetch_value(
        """SELECT COUNT(*)
           FROM MEMBRO_GRUPO m
           JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
           WHERE m.id_membro = %s AND g.FK_USUARIO_id_usuario = m.FK_USUARIO_id_usuario""",
        (member_id,),
    )
    return count > 0


def same_group(member_id, stage_id):
    """RN11: returns True when the member and the stage belong to the same group."""
    count = database.fetch_value(
        """SELECT COUNT(*)
           FROM MEMBRO_GRUPO m, ETAPA_LEITURA e
           WHERE m.id_membro = %s AND e.id_etapa = %s
             AND m.FK_GRUPO_LEITURA_id_grupo = e.FK_GRUPO_LEITURA_id_grupo""",
        (member_id, stage_id),
    )
    return count > 0


def stage_unlocked(member_id, stage_id):
    """RN12: returns True when the member can read and post messages in the stage,
    that is, when the deadline has arrived or the member has finished the stage."""
    deadline = database.fetch_value("SELECT data_limite FROM ETAPA_LEITURA WHERE id_etapa = %s", (stage_id,))
    if deadline <= date.today():
        return True
    finished = database.fetch_value(
        """SELECT COUNT(*) FROM PROGRESSO_ETAPA
           WHERE FK_MEMBRO_GRUPO_id_membro = %s
             AND FK_ETAPA_LEITURA_id_etapa = %s
             AND concluida = TRUE""",
        (member_id, stage_id),
    )
    return finished > 0
