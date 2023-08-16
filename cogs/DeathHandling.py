import settings


async def dead_person(role_id, specifics=None):
    dead_role_id = settings.dead_role_ID
    role_name = settings.dead_role_NAME

    if role_id == dead_role_id and specifics == "remove role":
        return True, role_name
    elif role_id != dead_role_id and specifics == "remove role":
        return False, role_name
