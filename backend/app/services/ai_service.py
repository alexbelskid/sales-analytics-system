from openai import OpenAI
from app.config import settings
from app.database import supabase
from typing import List, Dict

# Initialize OpenAI client
client = None
if settings.openai_api_key:
    client = OpenAI(api_key=settings.openai_api_key)


async def generate_email_reply(email_content: str, email_type: str = "general") -> str:
    """
    Генерация ответа на письмо с помощью LLM.
    
    Args:
        email_content: Содержимое письма
        email_type: Тип письма (price, availability, complaint, general)
    
    Returns:
        Сгенерированный ответ
    """
    if not client:
        return _generate_template_reply(email_type)
    
    # Получаем релевантную информацию из базы знаний
    try:
        knowledge = supabase.table("knowledge_base")\
            .select("question, answer")\
            .eq("category", email_type)\
            .eq("is_active", True)\
            .limit(5)\
            .execute()
        
        context = "\n".join([
            f"Q: {k['question']}\nA: {k['answer']}" 
            for k in knowledge.data
        ]) if knowledge.data else ""
    except Exception:
        context = ""
    
    system_prompt = f"""Ты — вежливый и профессиональный помощник менеджера по продажам.
Твоя задача — составить ответ на входящее письмо клиента.

Правила:
1. Отвечай на русском языке
2. Будь вежливым и профессиональным
3. Если нужна информация которой нет — предложи связаться с менеджером
4. Не выдумывай цены или условия если их нет в контексте

{"Используй эту информацию для ответа:" + chr(10) + context if context else ""}"""

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Напиши ответ на это письмо:\n\n{email_content}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return _generate_template_reply(email_type)


async def generate_proposal_text(customer: str, products: List[Dict], conditions: str) -> str:
    """
    Генерация текста коммерческого предложения с помощью AI.
    
    Args:
        customer: Имя/компания клиента
        products: Список товаров [{"name": str, "quantity": int, "price": float}]
        conditions: Условия поставки
    
    Returns:
        Текст КП
    """
    if not client:
        return _generate_simple_proposal(customer, products, conditions)
    
    products_text = "\n".join([
        f"- {p['name']}: {p['quantity']} шт. по {p['price']:,.0f} ₽"
        for p in products
    ])
    
    total = sum(p['quantity'] * p['price'] for p in products)
    
    prompt = f"""Составь профессиональный текст коммерческого предложения:

Клиент: {customer}

Товары:
{products_text}

Общая сумма: {total:,.0f} ₽

Условия: {conditions}

Требования к тексту:
1. Профессиональный деловой стиль
2. Краткое вступление
3. Выгоды для клиента
4. Призыв к действию
5. Не более 200 слов"""

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Ты составляешь коммерческие предложения. Пиши профессионально и убедительно на русском языке."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return _generate_simple_proposal(customer, products, conditions)


def _generate_template_reply(email_type: str) -> str:
    """Шаблонный ответ без AI"""
    templates = {
        "price": """Здравствуйте!

Благодарим за интерес к нашей продукции. 
Для получения актуального прайс-листа, пожалуйста, свяжитесь с вашим персональным менеджером.

С уважением,
Отдел продаж""",
        
        "availability": """Здравствуйте!

Благодарим за обращение. 
Для уточнения наличия товара на складе, пожалуйста, свяжитесь с менеджером по телефону или email.

С уважением,
Отдел продаж""",
        
        "complaint": """Здравствуйте!

Благодарим за обратную связь. Мы сожалеем о возникшей ситуации.
Ваше обращение зарегистрировано. Менеджер свяжется с вами в ближайшее время для решения вопроса.

С уважением,
Отдел контроля качества""",
        
        "general": """Здравствуйте!

Благодарим за обращение. 
Менеджер ознакомится с вашим запросом и свяжется с вами в ближайшее время.

С уважением,
Отдел продаж"""
    }
    
    return templates.get(email_type, templates["general"])


def _generate_simple_proposal(customer: str, products: List[Dict], conditions: str) -> str:
    """Простой шаблон КП без AI"""
    products_text = "\n".join([
        f"• {p['name']} — {p['quantity']} шт. × {p['price']:,.0f} ₽ = {p['quantity'] * p['price']:,.0f} ₽"
        for p in products
    ])
    
    total = sum(p['quantity'] * p['price'] for p in products)
    
    return f"""Уважаемый(ая) {customer}!

Благодарим за проявленный интерес к нашей продукции.
Рады предложить вам следующие позиции:

{products_text}

ИТОГО: {total:,.0f} ₽

Условия: {conditions}

Данное предложение действительно в течение 30 дней.
Для оформления заказа свяжитесь с вашим персональным менеджером.

С уважением,
Отдел продаж"""
