"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import LiquidButton from "@/components/LiquidButton";
import GlassInput from "@/components/GlassInput";
import GlassSelect from "@/components/GlassSelect";
import { AlertCircle, CheckCircle2, Loader2, Mail } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// Helper components for layout
function SectionHeader({ title, description }: { title: string; description: string }) {
  return (
    <div className="mb-6">
      <h3 className="text-xl font-medium text-white tracking-wide">{title}</h3>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  );
}

function GlassPanel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`p-8 rounded-3xl border border-white/5 bg-white/[0.02] backdrop-blur-sm ${className}`}>
      {children}
    </div>
  );
}

export default function EmailSettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const { toast } = useToast();

  const [settings, setSettings] = useState({
    email_address: "",
    email_provider: "gmail",
    connection_type: "imap",
    password: "",
    imap_server: "",
    imap_port: 993,
    smtp_server: "",
    smtp_port: 587,
    use_ssl: true,
    auto_sync_enabled: true,
    sync_interval_minutes: 10
  });

  useEffect(() => {
    loadSettings();
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("oauth_success")) {
      toast({ title: "Успешно", description: "Аккаунт Google подключен" });
    } else if (urlParams.get("oauth_error")) {
      toast({ title: "Ошибка", description: urlParams.get("oauth_error") || "Ошибка авторизации", variant: "destructive" });
    }
  }, []);

  const loadSettings = async () => {
    try {
      const data = await api.getEmailSettings();
      if (data) {
        setSettings({ ...data, password: "" }); // Don't show encrypted password
      }
    } catch (error) {
      console.error("Failed to load settings", error);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = (provider: string) => {
    let defaults = {};
    if (provider === "gmail") {
      defaults = { imap_server: "imap.gmail.com", imap_port: 993, smtp_server: "smtp.gmail.com", smtp_port: 587 };
    } else if (provider === "outlook") {
      defaults = { imap_server: "outlook.office365.com", imap_port: 993, smtp_server: "smtp.office365.com", smtp_port: 587 };
    } else if (provider === "yandex") {
      defaults = { imap_server: "imap.yandex.com", imap_port: 993, smtp_server: "smtp.yandex.com", smtp_port: 465 };
    } else if (provider === "mail_ru") {
      defaults = { imap_server: "imap.mail.ru", imap_port: 993, smtp_server: "smtp.mail.ru", smtp_port: 465 };
    }

    setSettings({ ...settings, email_provider: provider, ...defaults });
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.testEmailConnection(settings);
      setTestResult(res);
    } catch (error) {
      setTestResult({ success: false, details: { error: "Failed to connect to server" } });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.saveEmailSettings(settings);
      toast({
        title: "Успешно",
        description: "Настройки почты сохранены",
      });
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось сохранить настройки",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div className="flex justify-center p-8">
      <Loader2 className="h-8 w-8 animate-spin text-white/50" />
    </div>
  );

  return (
    <div className="container mx-auto py-6 max-w-4xl space-y-8 animate-fade-in text-gray-100">
      <div>
        <h1 className="text-3xl font-light text-white tracking-tight">Подключение почты</h1>
        <p className="text-gray-400 mt-2">Настройте подключение к вашему почтовому ящику через IMAP/SMTP.</p>
      </div>

      <GlassPanel>
        <SectionHeader
          title="Провайдер"
          description="Выберите вашего почтового провайдера"
        />
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {["gmail", "outlook", "yandex", "mail_ru", "custom"].map((prov) => {
            const isSelected = settings.email_provider === prov;
            return (
              <div
                key={prov}
                onClick={() => handleProviderChange(prov)}
                className={`
                                    cursor-pointer rounded-2xl border p-4 flex flex-col items-center justify-center gap-2
                                    transition-all duration-300
                                    ${isSelected
                    ? "bg-white/10 border-white/40 shadow-[0_0_15px_rgba(255,255,255,0.1)]"
                    : "bg-white/5 border-transparent hover:bg-white/10"
                  }
                                `}
              >
                <Mail className={`h-6 w-6 ${isSelected ? 'text-white' : 'text-gray-400'}`} />
                <span className="capitalize text-xs tracking-wider">{prov.replace("_", ".")}</span>
              </div>
            );
          })}
        </div>
      </GlassPanel>

      <GlassPanel>
        <SectionHeader
          title="Настройки подключения"
          description="IMAP/SMTP (универсальный способ для всех провайдеров)"
        />

        <div className="space-y-6">
          <div className="grid gap-2">
            <label className="text-sm font-medium text-gray-300">Email адрес</label>
            <GlassInput
              value={settings.email_address}
              onChange={(e) => setSettings({ ...settings, email_address: e.target.value })}
              placeholder="user@example.com"
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-gray-300">Пароль приложения</label>
            <GlassInput
              type="password"
              value={settings.password}
              onChange={(e) => setSettings({ ...settings, password: e.target.value })}
              placeholder="••••••••"
            />
            <p className="text-xs text-gray-500">
              Для Gmail/Yandex/Mail.ru используйте "Пароль приложения" (App Password), не обычный пароль
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">IMAP Сервер</label>
              <GlassInput
                value={settings.imap_server}
                onChange={(e) => setSettings({ ...settings, imap_server: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Порт</label>
              <GlassInput
                type="number"
                value={settings.imap_port}
                onChange={(e) => setSettings({ ...settings, imap_port: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">SMTP Сервер</label>
              <GlassInput
                value={settings.smtp_server}
                onChange={(e) => setSettings({ ...settings, smtp_server: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Порт</label>
              <GlassInput
                type="number"
                value={settings.smtp_port}
                onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })}
              />
            </div>
          </div>

          {testResult && (
            <div className={`p-4 rounded-xl flex items-start gap-3 border ${testResult.success ? 'bg-green-500/10 border-green-500/20 text-green-200' : 'bg-red-500/10 border-red-500/20 text-red-200'}`}>
              {testResult.success ? <CheckCircle2 className="h-5 w-5 mt-0.5" /> : <AlertCircle className="h-5 w-5 mt-0.5" />}
              <div>
                <h4 className="font-medium mb-1">{testResult.success ? "Успешно" : "Ошибка"}</h4>
                <p className="text-sm opacity-90">
                  {testResult.success
                    ? "Подключение установлено (IMAP и SMTP работают)"
                    : `Не удалось подключиться: ${testResult.details?.error || "Неизвестная ошибка"}`
                  }
                </p>
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-white/5">
            <LiquidButton
              variant="secondary"
              onClick={handleTestConnection}
              disabled={testing || !settings.email_address}
            >
              {testing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Проверить подключение
            </LiquidButton>

            <LiquidButton
              variant="primary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Сохранить настройки
            </LiquidButton>
          </div>
        </div>
      </GlassPanel>

      <GlassPanel>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-medium text-white tracking-wide">Синхронизация</h3>
            <p className="text-sm text-gray-400 mt-1">Настройки автоматического обновления</p>
          </div>

          {/* Style the Switch as a glass toggle */}
          <button
            onClick={() => setSettings({ ...settings, auto_sync_enabled: !settings.auto_sync_enabled })}
            className={`
                            relative h-7 w-12 rounded-full transition-colors duration-300
                            ${settings.auto_sync_enabled ? 'bg-white/80' : 'bg-white/10'}
                        `}
          >
            <span className={`
                            absolute top-1 left-1 h-5 w-5 rounded-full bg-black shadow-lg transition-transform duration-300
                            ${settings.auto_sync_enabled ? 'translate-x-5' : 'translate-x-0'}
                        `} />
          </button>
        </div>

        <div className="space-y-2 max-w-xs">
          <label className="text-sm font-medium text-gray-300">Интервал проверки</label>
          <GlassSelect
            value={String(settings.sync_interval_minutes)}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSettings({ ...settings, sync_interval_minutes: parseInt(e.target.value) })}
          >
            <option value="5">Каждые 5 минут</option>
            <option value="10">Каждые 10 минут</option>
            <option value="15">Каждые 15 минут</option>
            <option value="30">Каждые 30 минут</option>
            <option value="60">Каждый час</option>
          </GlassSelect>
        </div>
      </GlassPanel>
    </div>
  );
}
