from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, SalesRecord

DB_PATH = Path(__file__).resolve().parent.parent / "dashboard.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session():
    return SessionLocal()


def init_db():
    Base.metadata.create_all(bind=engine)
    seed_sample_data()


def seed_sample_data():
    from sqlalchemy import select

    with SessionLocal() as session:
        existing = session.execute(select(SalesRecord).limit(1)).scalar_one_or_none()
        if existing:
            return

        months = [
            ("2024-01-01", "East", "Enterprise", 120000, 2100),
            ("2024-02-01", "East", "Enterprise", 132000, 2250),
            ("2024-03-01", "East", "SMB", 98000, 1720),
            ("2024-04-01", "West", "Enterprise", 151000, 2440),
            ("2024-05-01", "West", "SMB", 143000, 2300),
            ("2024-06-01", "Central", "Enterprise", 127000, 2050),
            ("2024-07-01", "Central", "SMB", 119000, 1950),
            ("2024-08-01", "East", "Enterprise", 164000, 2640),
            ("2024-09-01", "West", "Enterprise", 172000, 2790),
            ("2024-10-01", "Central", "SMB", 134000, 2125),
            ("2024-11-01", "East", "SMB", 149000, 2310),
            ("2024-12-01", "West", "Enterprise", 186000, 2910),
        ]

        for date_value, region, category, revenue, customers in months:
            session.add(
                SalesRecord(
                    date=date_value,
                    region=region,
                    product_category=category,
                    revenue=revenue,
                    customers=customers,
                )
            )

        session.commit()
