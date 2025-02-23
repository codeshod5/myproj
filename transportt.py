from typing import Optional,Annotated,List

from sqlmodel import SQLModel, Field,create_engine,Session,select
from fastapi import FastAPI,Depends,HTTPException,Header,Query
from sqlalchemy.dialects.postgresql import JSON
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()


class Buses(SQLModel, table=True):
    bus_id: int = Field(primary_key=True)
    bus_no: int = Field(index=True)
    driver_id: int = Field(index=True)

class Driver(SQLModel, table=True):
    driver_id: int = Field(primary_key=True)
    driver_no: int = Field(index=True)


class Routes(SQLModel):
    routes_no: int = Field(index=True)
    areas: str= Field(index=True) 


class Routespublic(Routes, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Busroutes(Routes, table=True):
    id: int = Field(primary_key=True)
    bus_id: Optional[int] = Field(default=None, index=True)  


class View_on_map(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  
    routes_no: int = Field(index=True)
    bus_no: int = Field(index=True)
    url_of_mp: str = Field(index=True)

class Form_update(BaseModel):
    routes_no :int|None = None
    bus_no :int|None = None
    url_of_mp:str|None = None
    
class Routesupdate(BaseModel):
    routes_no:int|None=None
    areas:str|None=None

    
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine
engine = create_engine(DATABASE_URL)



# def cretertable():
#     SQLModel.metadata.create_all(engine)
# cretertable()
    

app = FastAPI()
origins =[
    "http://localhost:8080",
    "http://127.0.0.1:5500"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_ssion():
    with Session(engine) as session:
        yield session
sess = Annotated[Session,Depends(get_ssion)]



@app.get('/readd',response_model=list[Routespublic])
def read_routes(session:sess):
    route_data = session.exec(select(Routespublic)).all()
    if not route_data:
        raise HTTPException(status_code=404,detail="not have any data")
    return route_data

@app.post('/routes',response_model=Routes)
def create_routes(routes:Routes,session:sess):
    rout_db = Routespublic(**routes.model_dump()) #first convert dict than unpack dict into pydantic name="skflsd" like that 
    session.add(rout_db)
    session.commit()
    session.refresh(rout_db)
    return rout_db

@app.post('/search')
def get_search_items(session:sess,route_item:Annotated[int|None,Query(description="search by routes")]=None,area_item:Annotated[str|None,Query(description="search byarea")]=None):
    query = select(Routespublic)
    if area_item:
        query = query.where(Routespublic.areas.contains(area_item))
    if route_item:
        query = query.where(Routespublic.routes_no==route_item)
    results = session.exec(query).all()
    return results






    


     




# @app.get('/readd/{rout_no}',response_model=Routes)
# def get_by_routeno(rout_no:int,session:sess):
#     route_data = session.get(Routespublic,rout_no)
#     return route_data

#this method will work for primary keys 

@app.get('/readd/{route_no}',response_model=Routes)
def get_by_id(route_no:int,session:sess):
    route_data = session.exec(select(Routespublic).where(Routespublic.routes_no==route_no)).first()
    if not route_no:
        raise HTTPException(status_code=404,detail="not there")
    return route_data

@app.patch('/upda/{route_id}',response_model=Routespublic)
def update_route_id(route_id:int,session:sess,route:Routesupdate):
    data = session.get(Routespublic,route_id)
    route_db = route.model_dump(exclude_unset=True)
    data.sqlmodel_update(route_db)
    session.add(data)
    session.commit()
    session.refresh(data)
    return data

# def sqlmodel_update(self, update_dict):
#     for key, value in update_dict.items():
#         setattr(self, key, value



#for patch you need to keep your fields optional 

@app.post('/create_bus')
def cretebus(mapp:View_on_map,session:sess):
    bus_db = View_on_map.model_validate(mapp)
    session.add(bus_db)
    session.commit()
    session.refresh(bus_db)
    return bus_db

@app.patch('/updat/{route_no}',response_model=View_on_map)
def update_mp(route_no:int,mapp:Form_update,session:sess):
    route_data = session.exec(select(View_on_map).where(View_on_map.routes_no==route_no)).first()
    updat_data = mapp.model_dump(exclude_unset=True)
    route_data.sqlmodel_update(updat_data)
    session.add(route_data)
    session.commit()
    session.refresh(route_data)
    return route_data










    





        



    






