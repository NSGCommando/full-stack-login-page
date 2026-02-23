from backend.database_connect import UserBase
from sqlalchemy.orm import Mapped,mapped_column

class UserData(UserBase):
    __tablename__ = "user_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)