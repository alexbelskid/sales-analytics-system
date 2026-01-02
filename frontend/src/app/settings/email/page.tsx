"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, Mail, CheckCircle2, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

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
    // Auto-fill defaults based on provider
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
      if (res.detected_settings && settings.email_provider === "custom") {
        // If custom and auto-detected something, suggest it?
        // For now just logged
      }
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

  const handleGoogleLogin = async () => {
    try {
      const { url } = await api.getAuthUrl();
      window.location.href = url;
    } catch (error: any) {
      toast({
        title: "Ошибка",
        description: error.message || "Не удалось получить ссылку для авторизации",
        variant: "destructive",
      });
    }
  };

  if (loading) return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>;

  return (
    <div className="container mx-auto py-6 max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Подключение почты</h1>
        <p className="text-muted-foreground">Настройте подключение к вашему почтовому ящику для синхронизации писем.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Провайдер</CardTitle>
          <CardDescription>Выберите вашего почтового провайдера</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {["gmail", "outlook", "yandex", "mail_ru", "yahoo", "custom"].map((prov) => (
              <div
                key={prov}
                onClick={() => handleProviderChange(prov)}
                className={`cursor-pointer rounded-lg border p-4 flex flex-col items-center justify-center gap-2 hover:bg-accent transition-colors ${settings.email_provider === prov ? "border-primary bg-accent/50" : ""}`}
              >
                <Mail className="h-6 w-6" />
                <span className="capitalize">{prov.replace("_", ".")}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Настройки подключения</CardTitle>
          <CardDescription>
            {settings.connection_type === "imap" ? "Настройки IMAP/SMTP" : "OAuth авторизация"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Tabs defaultValue="imap" value={settings.connection_type} onValueChange={(v) => setSettings({ ...settings, connection_type: v })}>
            <TabsList className="mb-4">
              <TabsTrigger value="imap">IMAP / Пароль</TabsTrigger>
              <TabsTrigger value="gmail_api" disabled={settings.email_provider !== "gmail"}>Gmail API</TabsTrigger>
              <TabsTrigger value="graph_api" disabled={settings.email_provider !== "outlook"}>Outlook API</TabsTrigger>
            </TabsList>

            <TabsContent value="imap" className="space-y-4">
              <div className="grid gap-2">
                <Label>Email адрес</Label>
                <Input
                  value={settings.email_address}
                  onChange={(e) => setSettings({ ...settings, email_address: e.target.value })}
                  placeholder="user@example.com"
                />
              </div>
              <div className="grid gap-2">
                <Label>Пароль приложения / Пароль</Label>
                <Input
                  type="password"
                  value={settings.password}
                  onChange={(e) => setSettings({ ...settings, password: e.target.value })}
                  placeholder="••••••••"
                />
                <p className="text-xs text-muted-foreground">Для Gmail/Yandex/Mail.ru лучше использовать "Пароль приложения"</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>IMAP Сервер</Label>
                  <Input value={settings.imap_server} onChange={(e) => setSettings({ ...settings, imap_server: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label>Порт</Label>
                  <Input value={settings.imap_port} onChange={(e) => setSettings({ ...settings, imap_port: parseInt(e.target.value) })} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>SMTP Сервер</Label>
                  <Input value={settings.smtp_server} onChange={(e) => setSettings({ ...settings, smtp_server: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label>Порт</Label>
                  <Input value={settings.smtp_port} onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })} />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="gmail_api">
              <div className="flex flex-col items-center justify-center p-8 border rounded-lg border-dashed">
                <p className="mb-4 text-center text-muted-foreground">Подключение через официальный API Gmail (OAuth2). <br />Более надежно и безопасно.</p>
                <Button variant="outline" onClick={handleGoogleLogin}>Войти через Google</Button>
              </div>
            </TabsContent>
          </Tabs>

          {testResult && (
            <Alert variant={testResult.success ? "default" : "destructive"}>
              {testResult.success ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
              <AlertTitle>{testResult.success ? "Успешно" : "Ошибка"}</AlertTitle>
              <AlertDescription>
                {testResult.success
                  ? "Подключение установлено (IMAP и SMTP работают)"
                  : `Не удалось подключиться: ${testResult.details?.error || "Неизвестная ошибка"}`
                }
              </AlertDescription>
            </Alert>
          )}

          <div className="flex justify-between items-center pt-4">
            <Button variant="outline" onClick={handleTestConnection} disabled={testing || !settings.email_address}>
              {testing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Проверить подключение
            </Button>

            <Button onClick={handleSave} disabled={saving}>
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Сохранить настройки
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Синхронизация</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Автоматическая синхронизация</Label>
              <p className="text-sm text-muted-foreground">Периодически проверять новые письма</p>
            </div>
            <Switch
              checked={settings.auto_sync_enabled}
              onCheckedChange={(c) => setSettings({ ...settings, auto_sync_enabled: c })}
            />
          </div>
          <div className="space-y-2">
            <Label>Интервал проверки</Label>
            <Select
              value={String(settings.sync_interval_minutes)}
              onValueChange={(v) => setSettings({ ...settings, sync_interval_minutes: parseInt(v) })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">Каждые 5 минут</SelectItem>
                <SelectItem value="10">Каждые 10 минут</SelectItem>
                <SelectItem value="15">Каждые 15 минут</SelectItem>
                <SelectItem value="30">Каждые 30 минут</SelectItem>
                <SelectItem value="60">Каждый час</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
