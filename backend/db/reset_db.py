from sqlalchemy import text
from db.session import engine
from db.init_db import init_db, seed_admin, seed_forestry, seed_land_types, seed_municipalities,seed_selsovets,seed_fire_participants,seed_tech_types, seed_reasons


def reset_database():
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        conn.commit()

    # пересоздаем таблицы
    init_db()
    seed_admin()
    seed_forestry()
    seed_land_types()
    seed_municipalities()
    seed_selsovets()
    seed_tech_types()
    seed_fire_participants()
    seed_reasons()