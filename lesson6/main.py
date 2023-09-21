from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field
from fastapi import FastAPI, Path
from typing import List
import sqlalchemy
import databases
import random

DATABASE_URL = "sqlite:///order_product_user.db"
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata = sqlalchemy.MetaData()

# Таблица пользователей
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(50)),
    sqlalchemy.Column("surname", sqlalchemy.String(50)),
    sqlalchemy.Column("email", sqlalchemy.String(50)),
    sqlalchemy.Column("password", sqlalchemy.String(120)),
)

# Таблица товаров
products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(50)),
    sqlalchemy.Column("description", sqlalchemy.String(200)),
    sqlalchemy.Column("price", sqlalchemy.Float)
)

# Таблица заказов
orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("product_id", sqlalchemy.ForeignKey("products.id"), nullable=False),
    sqlalchemy.Column("order_date", sqlalchemy.DATE),
    sqlalchemy.Column('status', sqlalchemy.String(20))
)

metadata.create_all(engine)


# Определение моделей данных с новыми именами
class User(BaseModel):
    id: int = Field(default=None)
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=4, max_length=50)
    password: str = Field(min_length=5, max_length=120)


class UserIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=5, max_length=120)


class Product(BaseModel):
    id: int = Field(default=None)
    name: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=200)
    price: float = Field(..., ge=0.1, le=100000)


class ProductIn(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=200)
    price: float = Field(..., ge=0.1, le=100000)


class Order(BaseModel):
    id: int = Field(default=None)
    order_date: date = Field(default=datetime.now())
    status: str = Field(default='in_progress')
    user_id: int
    product_id: int


class OrderIn(BaseModel):
    order_date: date = Field(default=datetime.now())
    status: str = Field(default='in_progress')
    user_id: int
    product_id: int


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/')
async def root():
    return {"message": "Online shop"}


@app.get('/fake_users/{count}')
async def create_users(count: int):
    for i in range(count):
        query = users.insert().values(name=f'user{i}',
                                      surname=f'user{i}',
                                      email=f'email{i}@mail.ru',
                                      password=f'qwerty{i}')
        await database.execute(query)
    return {'message': f'{count} fake users were created and inserted into db'}


@app.get('/fake_products/{count}')
async def create_products(count: int):
    for i in range(count):
        query = products.insert().values(
            name=f'Product_name {i}',
            description='Some description',
            price=f'{random.randint(1, 100000):.2f}'
        )
        await database.execute(query)
    return {'message': f'{count} fake products were created and inserted into db'}


@app.get('/fake_orders/{count}')
async def create_orders(count: int):
    for i in range(count):
        query = orders.insert().values(
            order_date=datetime.strptime("2010-03-13", "%Y-%m-%d").date() + timedelta(days=i ** 2),
            status=random.choice(['in_progress', 'done', 'cancelled']),
            user_id=random.randint(1, 10),
            product_id=random.randint(1, 10)
        )
        await database.execute(query)
    return {'message': f'{count} fake orders were created and inserted into db'}


@app.get('/users/', response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{user_id}', response_model=User)
async def read_user(user_id: int = Path(..., ge=1)):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.post('/users/', response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(
        name=user.name,
        surname=user.surname,
        email=user.email,
        password=user.password
    )
    actual_id = await database.execute(query)
    return {**user.dict(), 'id': actual_id}


@app.put('/users/', response_model=User)
async def update_user(new_user: UserIn, user_id: int = Path(..., ge=1)):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), 'id': user_id}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int = Path(..., ge=1)):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': f'User with id {user_id} was deleted'}


@app.get('/products/', response_model=List[Product])
async def get_all_products():
    query = products.select()
    return await database.fetch_all(query)


@app.get('/products/{product_id}', response_model=Product)
async def get_product(product_id: int = Path(..., ge=1)):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)


@app.post('/products/', response_model=Product)
async def create_product(product: ProductIn):
    query = products.insert().values(
        name=product.name,
        description=product.description,
        price=product.price
    )
    actual_id = await database.execute(query)
    return {**product.dict(), 'id': actual_id}


@app.put('/products/{product_id}', response_model=Product)
async def update_product(new_product: ProductIn, product_id: int = Path(..., ge=1)):
    query = products.update().where(products.c.id == product_id).values(**new_product.dict())
    await database.execute(query)
    return {**new_product.dict(), 'id': product_id}


@app.delete('/products/{product_id}')
async def delete_product(product_id: int = Path(..., ge=1)):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {'message': f'Product with id {product_id} was deleted'}


@app.get('/orders/', response_model=List[Order])
async def get_all_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get('/orders/{order_id}', response_model=Order)
async def get_order(order_id: int = Path(..., ge=1)):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.post('/orders/', response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(
        order_date=order.order_date,
        status=order.status,
        user_id=order.user_id,
        product_id=order.product_id
    )
    actual_id = await database.execute(query)
    return {**order.dict(), 'id': actual_id}


@app.put('/orders/{order_id}', response_model=Order)
async def update_order(new_order: OrderIn, order_id: int = Path(..., ge=1)):
    query = orders.update().where(orders.c.id == order_id).values(**new_order.dict())
    await database.execute(query)
    return {**new_order.dict(), 'id': order_id}


@app.delete('/orders/{order_id}')
async def delete_order(order_id: int = Path(..., ge=1)):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': f'Order with id {order_id} was deleted'}


