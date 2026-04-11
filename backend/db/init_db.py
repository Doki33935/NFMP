from db.base import Base
from db.session import engine

import models  # 🔥 ВАЖНО: один импорт = всё загружено


def init_db():
    Base.metadata.create_all(bind=engine)