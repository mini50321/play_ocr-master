from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Text
from typing import List, Optional

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Theater(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    joomla_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class Show(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True)

class Person(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    disciplines: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    joomla_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class Production(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    theater_id: Mapped[int] = mapped_column(ForeignKey("theater.id"))
    show_id: Mapped[int] = mapped_column(ForeignKey("show.id"))
    year: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[Optional[str]] = mapped_column(String(20))
    end_date: Mapped[Optional[str]] = mapped_column(String(20))
    preview_image: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    theater: Mapped["Theater"] = relationship()
    show: Mapped["Show"] = relationship()
    credits: Mapped[List["Credit"]] = relationship(back_populates="production", cascade="all, delete-orphan")

class Credit(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    production_id: Mapped[int] = mapped_column(ForeignKey("production.id"))
    person_id: Mapped[int] = mapped_column(ForeignKey("person.id"))
    role: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    is_equity: Mapped[bool] = mapped_column(default=False)

    production: Mapped["Production"] = relationship(back_populates="credits")
    person: Mapped["Person"] = relationship()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

class AdminSettings(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, default='admin')
    password_hash: Mapped[str] = mapped_column(String(255))
    
    @staticmethod
    def get_or_create():
        settings = AdminSettings.query.first()
        if not settings:
            from werkzeug.security import generate_password_hash
            settings = AdminSettings(
                username='admin',
                password_hash=generate_password_hash('admin')
            )
            db.session.add(settings)
            db.session.commit()
        return settings
