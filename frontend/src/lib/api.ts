const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

interface FetchOptions extends RequestInit {
    params?: Record<string, string | number | boolean | undefined>;
}

async function fetchAPI<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { params, ...fetchOptions } = options;

    let url = `${API_BASE}${endpoint}`;

    if (params) {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined) {
                searchParams.append(key, String(value));
            }
        });
        const queryString = searchParams.toString();
        if (queryString) {
            url += `?${queryString}`;
        }
    }

    const response = await fetch(url, {
        ...fetchOptions,
        headers: {
            'Content-Type': 'application/json',
            ...fetchOptions.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Ошибка запроса' }));
        throw new Error(error.detail || 'Ошибка запроса');
    }

    return response.json();
}

// Analytics API
export const analyticsApi = {
    getDashboard: (params?: { start_date?: string; end_date?: string; customer_id?: string }) =>
        fetchAPI<{
            total_revenue: number;
            total_sales: number;
            average_check: number;
        }>('/api/analytics/dashboard', { params }),

    getTopCustomers: (limit = 10) =>
        fetchAPI<Array<{ customer_id: string; name: string; total: number }>>(
            '/api/analytics/top-customers',
            { params: { limit } }
        ),

    getTopProducts: (limit = 10) =>
        fetchAPI<Array<{ product_id: string; name: string; total_quantity: number; total_amount: number }>>(
            '/api/analytics/top-products',
            { params: { limit } }
        ),

    getSalesTrend: (period: 'day' | 'week' | 'month' = 'month') =>
        fetchAPI<Array<{ period: string; amount: number; count: number }>>(
            '/api/analytics/sales-trend',
            { params: { period } }
        ),

    getCustomers: () =>
        fetchAPI<Array<{ id: string; name: string; email: string }>>('/api/analytics/customers'),

    getProducts: () =>
        fetchAPI<Array<{ id: string; name: string; price: number }>>('/api/analytics/products'),
};

// Upload API
export const uploadApi = {
    uploadExcel: async (file: File, dataType: 'sales' | 'customers' | 'products') => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('data_type', dataType);

        const response = await fetch(`${API_BASE}/api/upload/excel`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки' }));
            throw new Error(error.detail);
        }

        return response.json();
    },

    getTemplate: (dataType: 'sales' | 'customers' | 'products') =>
        fetchAPI<{ template: string; type: string }>(`/api/upload/template/${dataType}`),
};

// Email API
export const emailApi = {
    generateReply: (email: { subject: string; body: string; sender: string; email_type?: string }) =>
        fetchAPI<{
            original_subject: string;
            generated_reply: string;
            status: string;
        }>('/api/email/generate-reply', {
            method: 'POST',
            body: JSON.stringify({ email, auto_send: false }),
        }),

    classifyEmail: (subject: string, body: string) =>
        fetchAPI<{ email_type: string; confidence: number }>('/api/email/classify', {
            method: 'POST',
            body: JSON.stringify({ subject, body }),
        }),
};

// Proposals API
export const proposalsApi = {
    generate: (data: {
        customer_name: string;
        customer_company?: string;
        items: Array<{ product_name: string; quantity: number; price: number; discount?: number }>;
        conditions?: string;
        use_ai?: boolean;
    }) =>
        fetchAPI<{
            id: string;
            customer_name: string;
            total_amount: number;
            generated_text?: string;
        }>('/api/proposals/generate', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    exportDocx: async (data: any) => {
        const response = await fetch(`${API_BASE}/api/proposals/export/docx`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return response.blob();
    },

    exportPdf: async (data: any) => {
        const response = await fetch(`${API_BASE}/api/proposals/export/pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return response.blob();
    },
};

// Forecast API
export const forecastApi = {
    predict: (monthsAhead = 3) =>
        fetchAPI<{
            forecast: Array<{
                date: string;
                predicted: number;
                lower_bound: number;
                upper_bound: number;
            }>;
        }>('/api/forecast/predict', { params: { months_ahead: monthsAhead } }),

    train: () =>
        fetchAPI<{ status: string; records_used: number }>('/api/forecast/train', {
            method: 'POST',
        }),

    getSeasonality: () =>
        fetchAPI<{
            monthly: Array<{ month: string; index: number }>;
            weekly: Array<{ day: string; index: number }>;
        }>('/api/forecast/seasonality'),
};

// Salary API
export const salaryApi = {
    calculate: (year: number, month: number, agentId?: string) =>
        fetchAPI<Array<{
            agent_id: string;
            agent_name: string;
            base_salary: number;
            sales_amount: number;
            commission_rate: number;
            commission: number;
            bonus: number;
            penalty: number;
            total_salary: number;
        }>>('/api/salary/calculate', { params: { year, month, agent_id: agentId } }),

    exportExcel: async (year: number, month: number) => {
        const response = await fetch(
            `${API_BASE}/api/salary/export?year=${year}&month=${month}`
        );
        return response.blob();
    },

    getAgents: () =>
        fetchAPI<Array<{
            id: string;
            name: string;
            base_salary: number;
            commission_rate: number;
        }>>('/api/salary/agents'),
};

// --- New Email System API ---

export const googleAuthApi = {
    getAuthUrl: () => fetchAPI<{ url: string }>('/api/google/auth-url'),
};

export const emailSettingsApi = {
    getEmailSettings: () =>
        fetchAPI<any>('/api/emails/settings/settings').catch(() => null),

    saveEmailSettings: (settings: any) =>
        fetchAPI<any>('/api/emails/settings/settings', {
            method: 'POST',
            body: JSON.stringify(settings),
        }),

    testEmailConnection: (settings: any) =>
        fetchAPI<any>('/api/emails/settings/test-connection', {
            method: 'POST',
            body: JSON.stringify(settings),
        }),

    deleteEmailSettings: () =>
        fetchAPI<any>('/api/emails/settings/settings', { method: 'DELETE' }),
};

export const inboxApi = {
    getInbox: (filter: string = 'new', category?: string, limit: number = 50, offset: number = 0) =>
        fetchAPI<Array<any>>('/api/emails/inbox', {
            params: { filter_status: filter, category, limit, offset },
        }),

    getEmailDetails: (id: string) => fetchAPI<any>(`/api/emails/${id}`),

    syncEmails: () => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000); // 20s timeout

        return fetchAPI<{ status: string; new_emails_count: number; sync_time?: number }>(
            '/api/emails/sync',
            {
                method: 'POST',
                signal: controller.signal
            }
        ).finally(() => clearTimeout(timeoutId));
    },

    sendReply: (emailId: string, draft: { draft_text: string; tone_id?: string }) =>
        fetchAPI<{ success: boolean }>((`/api/emails/${emailId}/send` as any), { // cast to any if string template fails TS check locally but it shouldn't
            method: 'POST',
            body: JSON.stringify(draft)
        }).catch(err => { throw err; }), // fix url construction

    generateResponse: (from: string, subject: string, body: string, tone: string) =>
        fetchAPI<{
            original_subject: string;
            generated_reply: string;
            status: string;
            tone_used: string;
        }>('/api/emails/generate-response', {
            method: 'POST',
            body: JSON.stringify({ from, subject, body, tone }),
        }),
};

// Fix for URL construction in sendReply above:
// actually fetchAPI takes endpoint string.
// `/api/emails/${emailId}/send` is correct.

export const toneSettingsApi = {
    getToneSettings: () => fetchAPI<Array<any>>('/api/tone-settings/'),

    createToneSetting: (tone: any) =>
        fetchAPI<any>('/api/tone-settings/', {
            method: 'POST',
            body: JSON.stringify(tone),
        }),

    updateToneSetting: (id: string, tone: any) =>
        fetchAPI<any>(`/api/tone-settings/${id}`, {
            method: 'PUT',
            body: JSON.stringify(tone),
        }),

    deleteToneSetting: (id: string) =>
        fetchAPI<any>(`/api/tone-settings/${id}`, { method: 'DELETE' }),
};

export const templatesApi = {
    getTemplates: () => fetchAPI<Array<any>>('/api/templates/'),

    createTemplate: (template: any) =>
        fetchAPI<any>('/api/templates/', {
            method: 'POST',
            body: JSON.stringify(template),
        }),

    updateTemplate: (id: string, template: any) =>
        fetchAPI<any>(`/api/templates/${id}`, {
            method: 'PUT',
            body: JSON.stringify(template),
        }),

    deleteTemplate: (id: string) =>
        fetchAPI<any>(`/api/templates/${id}`, { method: 'DELETE' }),
};

// Unified API Access
export const api = {
    ...analyticsApi,
    ...uploadApi,
    ...emailApi,
    ...proposalsApi,
    ...forecastApi,
    ...salaryApi,
    ...emailSettingsApi,
    ...inboxApi, // note: inboxApi has sendReply
    ...toneSettingsApi,
    ...templatesApi,
    ...googleAuthApi
};
