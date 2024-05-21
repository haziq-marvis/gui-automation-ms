import psycopg2
import psycopg2.extras
import environ

environ.Env.read_env()
env = environ.Env()

conn = psycopg2.connect(
    database=env("db_name"),
    user=env("db_user"),
    password=env("db_password"),
    host=env("db_host"),
    port=5432
)


def get_all_workflows():
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM useractions_workflow ORDER BY created_at DESC")
        return cursor.fetchall()


def get_latest_workflow():
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM useractions_workflow ORDER BY created_at DESC LIMIT 1")
        return cursor.fetchone()


def get_workflow_actiongroups(workflow_id):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(
            'SELECT "useractions_actiongroup"."id", "useractions_actiongroup"."workflow_id", "useractions_actiongroup"."user_id", "useractions_actiongroup"."url", "useractions_actiongroup"."timestamp", "useractions_actiongroup"."sequence_number" FROM "useractions_actiongroup" WHERE "useractions_actiongroup"."workflow_id" = %s',
            (workflow_id,)
        )
        return cursor.fetchall()


def get_group_actions(actiongroup_id):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(
            'SELECT "useractions_useraction"."id", "useractions_useraction"."action_group_id", "useractions_useraction"."action_performed", "useractions_useraction"."action_details", "useractions_useraction"."object_path", "useractions_useraction"."action_time", "useractions_useraction"."tab_title", "useractions_useraction"."app_name", "useractions_useraction"."sequence_number", "useractions_useraction"."user_id" FROM "useractions_useraction" WHERE "useractions_useraction"."action_group_id" = %s',
            (actiongroup_id,)
        )
        return cursor.fetchall()


if __name__ == "__main__":
    wfs = get_latest_workflow()
    print(wfs)
