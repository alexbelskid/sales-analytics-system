-- Таблица для хранения сессий чата
create table if not exists public.chat_sessions (
    id uuid default gen_random_uuid() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    title text,
    user_id uuid references auth.users(id)
);

-- Таблица для хранения сообщений
create table if not exists public.chat_messages (
    id uuid default gen_random_uuid() primary key,
    session_id uuid references public.chat_sessions(id) on delete cascade not null,
    role text not null check (role in ('user', 'assistant', 'system')),
    content text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    metadata jsonb default '{}'::jsonb
);

-- Индексы для ускорения поиска
create index if not exists chat_messages_session_id_idx on public.chat_messages(session_id);
create index if not exists chat_sessions_user_id_idx on public.chat_sessions(user_id);

-- Политики безопасности (RLS) - Опционально, если нужен доступ с клиента
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;

create policy "Users can view their own sessions"
    on public.chat_sessions for select
    using (auth.uid() = user_id);

create policy "Users can insert their own sessions"
    on public.chat_sessions for insert
    with check (auth.uid() = user_id);

create policy "Users can view messages of their sessions"
    on public.chat_messages for select
    using (exists (
        select 1 from public.chat_sessions
        where id = chat_messages.session_id
        and user_id = auth.uid()
    ));

create policy "Users can insert messages into their sessions"
    on public.chat_messages for insert
    with check (exists (
        select 1 from public.chat_sessions
        where id = chat_messages.session_id
        and user_id = auth.uid()
    ));
