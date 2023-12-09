SELECT id_internal, group_name
FROM internal_user
WHERE login = "$login" AND password = "$password"