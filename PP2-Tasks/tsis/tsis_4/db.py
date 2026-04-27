import os

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False


DB_URL = os.environ.get(
    "SNAKE_DB",
    "postgresql://postgres:postgres@localhost/snakedb"   
)

_conn = None


def _get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(DB_URL)
    return _conn


def db_available() -> bool:

    if not _PSYCOPG2_AVAILABLE:
        return False
    try:
        _get_conn()
        return True
    except Exception:
        return False


def init_db():

    if not db_available():
        return
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id       SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id            SERIAL PRIMARY KEY,
                    player_id     INTEGER REFERENCES players(id),
                    score         INTEGER   NOT NULL,
                    level_reached INTEGER   NOT NULL,
                    played_at     TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()


# helpers 
def get_or_create_player(username: str) -> int:

    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) "
                "ON CONFLICT (username) DO NOTHING",
                (username,)
            )
            conn.commit()
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            return cur.fetchone()[0]


def save_session(username: str, score: int, level_reached: int):

    if not db_available():
        return
    try:
        pid = get_or_create_player(username)
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (pid, score, level_reached)
                )
            conn.commit()
    except Exception as e:
        print(f"[DB] save_session error: {e}")


def get_top10():
    if not db_available():
        return []
    try:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT p.username,
                           gs.score,
                           gs.level_reached,
                           gs.played_at
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    ORDER BY gs.score DESC, gs.played_at DESC
                    LIMIT 10
                """)
                rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB] get_top10 error: {e}")
        return []


def get_personal_best(username: str) -> int:

    if not db_available():
        return 0
    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COALESCE(MAX(gs.score), 0)
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    WHERE p.username = %s
                """, (username,))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0
