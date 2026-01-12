from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from typing import Optional
import pandas as pd
from io import BytesIO
from uuid import uuid4
from datetime import datetime
from app.database import supabase
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()

# Rate limiter for upload endpoints
limiter = Limiter(key_func=get_remote_address)


@router.post("/excel")
@limiter.limit("10/minute")
async def upload_excel(
    request: Request,
    file: UploadFile = File(...),
    data_type: str = Form(default="sales", description="Тип данных: sales, customers, products"),
    mode: str = Form(default="append", description="Режим: append (добавить) или replace (заменить)")
):
    """
    Загрузка данных из Excel/CSV файла.
    
    Режимы загрузки:
    - append: добавляет новые записи, пропускает дубликаты
    - replace: удаляет старые данные и загружает новые
    
    Поддерживаемые типы:
    - sales: продажи (колонки: customer_name, product_name, quantity, price, date, agent_name)
    - customers: клиенты (колонки: name, email, phone, company)
    - products: товары (колонки: name, sku, price, category)
    """
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, "Поддерживаются только Excel (.xlsx, .xls) и CSV файлы")
    
    if mode not in ("append", "replace"):
        raise HTTPException(400, "Режим должен быть 'append' или 'replace'")
    
    try:
        content = await file.read()
        
        # SECURITY: Limit file size to 10MB to prevent DoS
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(413, f"Файл слишком большой. Максимум: 10MB, получено: {len(content) / 1024 / 1024:.1f}MB")
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(BytesIO(content))
        
        if data_type == "customers":
            return await _import_customers(df, mode)
        elif data_type == "products":
            return await _import_products(df, mode)
        else:
            return await _import_sales(df, mode)
            
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки файла: {str(e)}")


async def _import_customers(df: pd.DataFrame, mode: str) -> dict:
    """Импорт клиентов с поддержкой append/replace"""
    required = ['name']
    if not all(col in df.columns for col in required):
        raise HTTPException(400, f"Необходимые колонки: {required}")
    
    # Replace mode: clear existing data
    if mode == "replace":
        try:
            # Delete all customers (cascade will handle related records)
            supabase.table("customers").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        except Exception as e:
            print(f"Warning: Could not clear customers: {e}")
    
    records = df.fillna('').to_dict('records')
    imported = 0
    skipped = 0
    
    for record in records:
        try:
            customer_name = str(record.get('name', ''))
            
            # Check for duplicates in append mode
            if mode == "append":
                existing = supabase.table("customers").select("id").eq("name", customer_name).execute()
                if existing.data:
                    skipped += 1
                    continue
            
            supabase.table("customers").insert({
                "name": customer_name,
                "email": str(record.get('email', '')) or None,
                "phone": str(record.get('phone', '')) or None,
                "company": str(record.get('company', '')) or None,
            }).execute()
            imported += 1
        except Exception:
            continue
    
    return {
        "type": "customers",
        "mode": mode,
        "imported": imported,
        "skipped": skipped,
        "total": len(records)
    }


async def _import_products(df: pd.DataFrame, mode: str) -> dict:
    """Импорт товаров с поддержкой append/replace"""
    required = ['name', 'price']
    if not all(col in df.columns for col in required):
        raise HTTPException(400, f"Необходимые колонки: {required}")
    
    # Replace mode: clear existing data
    if mode == "replace":
        try:
            supabase.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        except Exception as e:
            print(f"Warning: Could not clear products: {e}")
    
    records = df.fillna('').to_dict('records')
    imported = 0
    skipped = 0
    
    for record in records:
        try:
            product_name = str(record.get('name', ''))
            
            # Check for duplicates in append mode (by name or SKU)
            if mode == "append":
                sku = str(record.get('sku', ''))
                if sku:
                    existing = supabase.table("products").select("id").eq("sku", sku).execute()
                else:
                    existing = supabase.table("products").select("id").eq("name", product_name).execute()
                if existing.data:
                    skipped += 1
                    continue
            
            supabase.table("products").insert({
                "name": product_name,
                "sku": str(record.get('sku', '')) or None,
                "price": float(record.get('price', 0)),
                "category": str(record.get('category', '')) or None,
                "in_stock": int(record.get('in_stock', 0)) if record.get('in_stock') else 0,
            }).execute()
            imported += 1
        except Exception:
            continue
    
    return {
        "type": "products",
        "mode": mode,
        "imported": imported,
        "skipped": skipped,
        "total": len(records)
    }


async def _import_sales(df: pd.DataFrame, mode: str) -> dict:
    """Импорт продаж с поддержкой append/replace"""
    # Calculate total if not present
    if 'total' not in df.columns and 'quantity' in df.columns and 'price' in df.columns:
        df['total'] = df['quantity'] * df['price']
    
    # Replace mode: clear existing sales
    if mode == "replace":
        try:
            # Delete sale_items first (foreign key constraint)
            supabase.table("sale_items").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            supabase.table("sales").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        except Exception as e:
            print(f"Warning: Could not clear sales: {e}")
    
    records = df.fillna('').to_dict('records')
    has_items = 'product_name' in df.columns and 'quantity' in df.columns
    imported = 0
    skipped = 0
    
    for record in records:
        try:
            # Find or create customer
            customer_name = str(record.get('customer_name', 'Неизвестный'))
            customer_result = supabase.table("customers").select("id").eq("name", customer_name).execute()
            
            if customer_result.data:
                customer_id = customer_result.data[0]["id"]
            else:
                new_customer = supabase.table("customers").insert({"name": customer_name}).execute()
                customer_id = new_customer.data[0]["id"]
            
            # Find agent if specified
            agent_id = None
            agent_name = str(record.get('agent_name', ''))
            if agent_name:
                agent_result = supabase.table("agents").select("id").eq("name", agent_name).execute()
                if agent_result.data:
                    agent_id = agent_result.data[0]["id"]
            
            # Parse date
            sale_date = record.get('date', datetime.now().date())
            if isinstance(sale_date, str):
                sale_date = pd.to_datetime(sale_date).date().isoformat()
            elif hasattr(sale_date, 'isoformat'):
                sale_date = sale_date.isoformat()
            
            total = float(record.get('total', 0))
            
            # In append mode, check for duplicate sales (same customer, date, amount)
            if mode == "append" and total > 0:
                existing = supabase.table("sales").select("id").eq(
                    "customer_id", customer_id
                ).eq("sale_date", sale_date).eq("total_amount", total).execute()
                if existing.data:
                    skipped += 1
                    continue
            
            # Create sale
            sale = supabase.table("sales").insert({
                "customer_id": customer_id,
                "agent_id": agent_id,
                "sale_date": sale_date,
                "total_amount": total,
            }).execute()
            
            # Add items if present
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
    
    return {
        "type": "sales",
        "mode": mode,
        "imported": imported,
        "skipped": skipped,
        "total": len(records)
    }


@router.get("/stats")
async def get_upload_stats():
    """Получить статистику загруженных данных"""
    if supabase is None:
        return {
            "customers": 0,
            "products": 0,
            "sales": 0,
            "sale_items": 0
        }
    
    try:
        customers = supabase.table("customers").select("id", count="exact").execute()
        products = supabase.table("products").select("id", count="exact").execute()
        sales = supabase.table("sales").select("id", count="exact").execute()
        sale_items = supabase.table("sale_items").select("id", count="exact").execute()
        
        return {
            "customers": customers.count or 0,
            "products": products.count or 0,
            "sales": sales.count or 0,
            "sale_items": sale_items.count or 0
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/template/{data_type}")
async def get_template(data_type: str):
    """Получить шаблон CSV для загрузки"""
    templates = {
        "sales": "customer_name,product_name,quantity,price,date,agent_name\nООО Клиент,Товар А,10,1500,2024-01-15,Иванов Иван",
        "customers": "name,email,phone,company\nИванов Иван,ivan@email.com,+79991234567,ООО Компания",
        "products": "name,sku,price,category,in_stock\nТовар А,SKU001,1500,Категория 1,100"
    }
    
    if data_type not in templates:
        raise HTTPException(400, f"Неизвестный тип: {data_type}. Доступные: {list(templates.keys())}")
    
    return {"template": templates[data_type], "type": data_type}
