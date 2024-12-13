def get_user_by_username(conn, username):
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, username, public_key FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    return user
