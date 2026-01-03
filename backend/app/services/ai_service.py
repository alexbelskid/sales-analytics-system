from openai import OpenAI
from app.config import settings
from app.database import supabase
from typing import List, Dict

# Initialize OpenAI client
client = None
if settings.openai_api_key:
    try:
        client = OpenAI(api_key=settings.openai_api_key)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        client = None


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


async def generate_manual_response(subject: str, body: str, sender: str, tone: str = "professional") -> str:
    """
    Manual generation of email response with specific tone.
    """
    if not client:
        return _generate_tone_template(subject, sender, tone)

    system_prompt = f"""You are an expert sales assistant. Write a reply to the email below.
    
Tone: {tone}
Language: Russian
    
Rules:
1. Be polite and professional (unless tone is 'creative')
2. Use the provided Subject as context
3. Address the sender if known
4. { 'Keep it under 50 words' if tone == 'brief' else 'Provide detailed information' if tone == 'detailed' else 'Standard length' }
    """

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"From: {sender}\nSubject: {subject}\n\nBody:\n{body}"}
            ],
            temperature=0.7 if tone != "creative" else 1.0,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return _generate_tone_template(subject, sender, tone)


def _generate_tone_template(subject: str, sender: str, tone: str) -> str:
    """Fallback templates based on tone"""
    
    # Extract name from sender if possible
    name = sender.split('@')[0] if '@' in sender else "Client"
    
    templates = {
        "professional": f"""Здравствуйте, {name}!

Спасибо за ваше письмо по теме "{subject}".

Мы получили ваш запрос и внимательно его изучили. Мы свяжемся с вами в течение рабочего дня для обсуждения деталей.

С уважением,
Команда Sales AI""",

        "friendly": f"""Привет, {name}! 👋

Спасибо, что написали нам насчет "{subject}".

Всё получили! Я сейчас всё проверю и вернусь с ответом как можно скорее.

Хорошего дня!
Команда Sales AI""",

        "formal": f"""Уважаемый(ая) {name}!

Настоящим подтверждаем получение вашего письма касательно "{subject}".

Ваш запрос принят в обработку. Ответ будет предоставлен в установленные регламентом сроки.

С уважением,
Sales Analytics System""",

        "brief": f"""Здравствуйте, {name}.

Получили ваш запрос по теме "{subject}". Ответим в ближайшее время.

Спасибо.""",

        "detailed": f"""Здравствуйте, {name}!

Большое спасибо за ваше подробное письмо относительно "{subject}".

Мы очень ценим ваш интерес и внимание к деталям. Мы получили вашу информацию и передали её профильным специалистам для глубокого анализа.
Мы подготовим развернутый ответ, учитывающий все описанные вами нюансы, и свяжемся с вами, как только он будет готов.

Если у вас есть дополнительные вопросы или материалы, пожалуйста, присылайте их в ответном письме.

С наилучшими пожеланиями,
Команда Sales AI""",

        "creative": f"""Здравствуйте, {name}! 🚀

Ваше письмо по теме "{subject}" только что приземлилось в нашем инбоксе!

Мы уже работаем над магическим решением для вас. Ожидайте вестей от наших почтовых сов в ближайшее время! 🦉

Искренне ваши,
Волшебники Sales AI"""
    }
    
    return templates.get(tone, templates["professional"])


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
