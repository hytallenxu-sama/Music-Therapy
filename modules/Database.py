from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

# Database handler class
class Database:
    def __init__(self, database_url):
        """
        Initialize the database handler.

        Parameters:
            database_url (str): The database connection string (e.g., 'sqlite:///example.db').
        """
        # Configure the engine with connection pooling for concurrency
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_size=20,         # Maximum number of connections in the pool
            max_overflow=20,      # Maximum number of overflow connections
            pool_timeout=30,      # Timeout for obtaining a connection
            pool_recycle=1800     # Recycle connections every 30 minutes
        )
        # Use scoped_session for thread safety
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def insert_data(self, model, **kwargs):
        """
        Insert data into the database.

        Parameters:
            model: SQLAlchemy ORM model class.
            **kwargs: Data to insert, passed as keyword arguments.

        Returns:
            The inserted object or None if an error occurs.
        """
        session = self.Session()  # Create a new session for each operation
        try:
            obj = model(**kwargs)
            session.add(obj)
            session.commit()
            return obj
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error inserting data: {e}")
            return None
        finally:
            session.close()

    def query_data(self, model, **filters):
        """
        Query data from the database.

        Parameters:
            model: SQLAlchemy ORM model class.
            **filters: Filters to apply in the query (e.g., column=value).

        Returns:
            List of results or an empty list if no data is found or an error occurs.
        """
        session = self.Session()
        try:
            query = session.query(model)
            if filters:
                query = query.filter_by(**filters)
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error querying data: {e}")
            return []
        finally:
            session.close()

    def delete_data(self, model, **filters):
        """
        Delete data from the database.

        Parameters:
            model: SQLAlchemy ORM model class.
            **filters: Filters to apply in the query (e.g., column=value).

        Returns:
            Number of rows deleted.
        """
        session = self.Session()
        try:
            rows_deleted = session.query(model).filter_by(**filters).delete()
            session.commit()
            return rows_deleted
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting data: {e}")
            return 0
        finally:
            session.close()

    def update_data(self, model, filters, updates):
        """
        Update data in the database.

        Parameters:
            model: SQLAlchemy ORM model class.
            filters (dict): Filters to identify the records to update.
            updates (dict): Fields to update with their new values.

        Returns:
            Number of rows updated.
        """
        session = self.Session()
        try:
            rows_updated = session.query(model).filter_by(**filters).update(updates)
            session.commit()
            return rows_updated
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating data: {e}")
            return 0
        finally:
            session.close()
