import os
import uuid
from typing import List, Union

from fastapi import (Depends, FastAPI, HTTPException, Path, Query, Request,
                     Response)

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from typing_extensions import Required

'''
Models / Schema
'''

Base = declarative_base()

class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True, index=True)
    description = Column(String(255))
    active = Column(Boolean)

class ResourceSchema(BaseModel):
    id: str
    description: str
    active: bool

    class Config:
        orm_mode = True

class Widget(Base):
    __tablename__ = "widgets"

    id = Column(String, primary_key=True, index=True)
    resource_id = Column(String, index=True)
    description = Column(String(255))
    active = Column(Boolean)

class WidgetSchema(BaseModel):
    id: str
    resource_id: str
    description: str
    active: bool

    class Config:
        orm_mode = True

'''
Database setup
'''

def create_sql_engine():
    db_uri = os.getenv("DATABASE_URI")

    # Create an in-memory sqlite database if a database URI is not
    # specified
    if not db_uri:
        print("Running with in-memory sqlite database...")
        return create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
    print(f"Running with database {db_uri}")
    return create_engine(db_uri)


engine = create_sql_engine()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()

'''
FastAPI initialization
'''

app = FastAPI()

# In dev & testing only, include the stacktrace in the response on internal
# server errors
if os.getenv("FASTAPI_ENV") in ["dev", "test"]:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!                           WARNING                            !!")
    print("!! Running in debug mode. This is not recommended in Production !!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    @app.exception_handler(Exception)
    async def debug_exception_handler(request: Request, exc: Exception):
        import traceback

        return Response(
            status_code=500,
            content="".join(
                traceback.format_exception(
                    etype=type(exc), value=exc, tb=exc.__traceback__
                )
            )
        )

'''
Helper methods
'''

class NewResource(BaseModel):
    description: str

def create_new_resource(new_resource: NewResource, db: Session) -> Resource:
    resource = Resource()
    resource.id = str(uuid.uuid4())
    resource.description = new_resource.description
    resource.active = True

    db.add(resource)
    return resource
class NewWidget(BaseModel):
    description: str

def create_new_widget(
    resource: Resource,
    new_widget: NewWidget,
    db: Session
) -> Resource:
    if not resource.active:
         raise HTTPException(status_code=400, detail=f"Resource {resource.id} is not active")

    # Now create the widget
    widget = Widget()
    widget.id = str(uuid.uuid4())
    widget.resource_id = resource.id
    widget.description = new_widget.description
    widget.active = True

    db.add(widget)
    return widget

'''
REST API Endpoints
'''

@app.get("/resources/", response_model=Page[ResourceSchema])
def get_resources(
    db: Session = Depends(get_db),
    params: Params = Depends()
):
    records = paginate(db.query(Resource), params)
    return records

@app.get("/resources/{resource_id}/widgets/", response_model=Page[WidgetSchema])
def get_all_resource_widgets(
    resource_id: str = Path(title= "Resource to get widgets for"),
    db: Session = Depends(get_db),
    params: Params = Depends()
):
    return paginate(db.query(Widget).filter(Widget.resource_id == resource_id), params)

@app.post("/resources/", response_model=ResourceSchema)
def post_resource(
    new_resource: NewResource,
    db: Session = Depends(get_db)
):
    return create_new_resource(new_resource, db)

@app.post("/resources/{resource_id}/widgets/", response_model=WidgetSchema)
def post_resource_widget(
        resource_id: str,
        new_widget: NewWidget,
        db: Session = Depends(get_db)
):
    resource = db.get(Resource, resource_id)
    if resource:
        return create_new_widget(resource, new_widget, db)
    else:
        raise HTTPException(status_code=404, detail=f"No resource found for id:{resource_id}")


@app.delete("/resources/{resource_id}/widgets/{widget_id}/", response_model=WidgetSchema)
def deactivate_resource_widget(
        resource_id: str,
        widget_id: str,
        db: Session = Depends(get_db)
):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail=f"No resource found for id:{resource_id}")

    widget = db.get(Widget, widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail=f"No widget found for id:{widget_id}")

    widget.active = False
    return widget

@app.post("/resources/{source_resource_id}/transfer_inactive_widgets/")
def transfer_inactive_widgets(
    source_resource_id: str,
    target_resource_id: Union[str, None] = Query(),
    db: Session = Depends(get_db)
):
    source_resource = db.get(Resource, source_resource_id)
    if not source_resource:
        raise HTTPException(status_code=404, detail=f"No resource found for id:{source_resource_id}")

    for widget in db.query(Widget).filter(Widget.resource_id == source_resource_id).all():
        db.execute(f"UPDATE widgets SET resource_id='{target_resource_id}' \
                WHERE id = '{widget.id}' AND active = false")
    return f"records transferred"

# @app.post("/resources/{source_resource_id}/transfer_all_widgets/")
# def unsafe_transfer_all_widgets(
#     source_resource_id: str,
#     target_resource_id: Union[str, None] = Query(),
#     db: Session = Depends(get_db)
# ):
#     db.execute(f"UPDATE widgets SET resource_id='{target_resource_id}' \
#                  WHERE id = '{source_resource_id}'")
#     return "Some widgets transferred"
