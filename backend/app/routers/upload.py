from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import pandas as pd
from io import BytesIO
from uuid import uuid4
from datetime import datetime
from app.database import supabase

router = APIRouter()


@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...),
    data_type: str = Form(default="sales", description="Тип данных: sales, customers, products")
):
    """
    Загрузка данных из Excel/CSV файла.
    
    Поддерживаемые типы:
    - sales: продажи (колонки: customer_name, product_name, quantity, price, date, agent_name)
    - customers: клиенты (колонки: name, email, phone, company)
    - products: товары (колонки: name, sku, price, category)
    """
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, "Поддерживаются только Excel (.xlsx, .xls) и CSV файлы")
    
    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(BytesIO(content))
        
        if data_type == "customers":
            return await _import_customers(df)
        elif data_type == "products":
            return await _import_products(df)
        else:
            return await _import_sales(df)
            
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки файла: {str(e)}")


async def _import_customers(df: pd.DataFrame) -> dict:
    """Импорт клиентов"""
    required = ['name']
    if not all(col in df.columns for col in required):
        raise HTTPException(400, f"Необходимые колонки: {required}")
    
    records = df.fillna('').to_dict('records')
    imported = 0
    
    for record in records:
        try:
            supabase.table("customers").insert({
                "name": str(record.get('name', '')),
                "email": str(record.get('email', '')) or None,
                "phone": str(record.get('phone', '')) or None,
                "company": str(record.get('company', '')) or None,
            }).execute()
            imported += 1
        except Exception:
            continue
    
    return {"type": "customers", "imported": imported, "total": len(records)}


async def _import_products(df: pd.DataFrame) -> dict:
    """Импорт товаров"""
    required = ['name', 'price']
    if not all(col in df.columns for col in required):
        raise HTTPException(400, f"Необходимые колонки: {required}")
    
    records = df.fillna('').to_dict('records')
    imported = 0
    
    for record in records:
        try:
            supabase.table("products").insert({
                "name": str(record.get('name', '')),
                "sku": str(record.get('sku', '')) or None,
                "price": float(record.get('price', 0)),
                "category": str(record.get('category', '')) or None,
            }).execute()
            imported += 1
        except Exception:
            continue
    
    return {"type": "products", "imported": imported, "total": len(records)}


async def _import_sales(df: pd.DataFrame) -> dict:
    """Импорт продаж"""
    required = ['customer_name', 'date', 'total']
    has_items = 'product_name' in df.columns and 'quantity' in df.columns
    
    # Если нет всех колонок продаж, проверяем минимальные
    if 'total' not in df.columns and 'quantity' in df.columns and 'price' in df.columns:
        df['total'] = df['quantity'] * df['price']
    
    records = df.fillna('').to_dict('records')
    imported = 0
    
    for record in records:
        try:
            # Находим или создаём клиента
            customer_name = str(record.get('customer_name', 'Неизвестный'))
            customer_result = supabase.table("customers").select("id").eq("name", customer_name).execute()
            
            if customer_result.data:
                customer_id = customer_result.data[0]["id"]
            else:
                new_customer = supabase.table("customers").insert({"name": customer_name}).execute()
                customer_id = new_customer.data[0]["id"]
            
            # Находим агента (если указан)
            agent_id = None
            agent_name = str(record.get('agent_name', ''))
            if agent_name:
                agent_result = supabase.table("agents").select("id").eq("name", agent_name).execute()
                if agent_result.data:
                    agent_id = agent_result.data[0]["id"]
            
            # Создаём продажу
            sale_date = record.get('date', datetime.now().date())
            if isinstance(sale_date, str):
                sale_date = pd.to_datetime(sale_date).date().isoformat()
            elif hasattr(sale_date, 'isoformat'):
                sale_date = sale_date.isoformat()
            
            total = float(record.get('total', 0))
            
            sale = supabase.table("sales").insert({
                "customer_id": customer_id,
                "agent_id": agent_id,
                "sale_date": sale_date,
                "total_amount": total,
            }).execute()
            
            # Если есть товары, добавляем позиции
            if has_items and record.get('product_name'):
                product_name = str(record.get('product_name'))
                product_result = supabase.table("products").select("id").eq("name", product_name).execute()
                
                if product_result.data:
                    product_id = product_result.data[0]["id"]
                else:
                    new_product = supabase.table("products").insert({
                        "name": product_name,
                        "price": float(record.get('price', 0))
                    }).execute()
                    product_id = new_product.data[0]["id"]
                
                quantity = int(record.get('quantity', 1))
                unit_price = float(record.get('price', total / quantity if quantity > 0 else 0))
                
                supabase.table("sale_items").insert({
                    "sale_id": sale.data[0]["id"],
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "amount": quantity * unit_price
                }).execute()
            
            imported += 1
        except Exception as e:
            print(f"Error importing sale: {e}")
            continue
    
    return {"type": "sales", "imported": imported, "total": len(records)}


@router.get("/template/{data_type}")
async def get_template(data_type: str):
    """Получить шаблон CSV для загрузки"""
    templates = {
        "sales": "customer_name,product_name,quantity,price,date,agent_name\nООО Клиент,Товар А,10,1500,2024-01-15,Иванов Иван",
        "customers": "name,email,phone,company\nИванов Иван,ivan@email.com,+79991234567,ООО Компания",
        "products": "name,sku,price,category\nТовар А,SKU001,1500,Категория 1"
    }
    
    if data_type not in templates:
        raise HTTPException(400, f"Неизвестный тип: {data_type}. Доступные: {list(templates.keys())}")
    
    return {"template": templates[data_type], "type": data_type}
