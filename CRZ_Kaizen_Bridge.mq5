//+------------------------------------------------------------------+
//|                                       CRZ_Kaizen_Bridge.mq5     |
//|                              CRZ Kaizen Journal - Bridge EA      |
//|  Sube datos de tu cuenta MT5 a GitHub en tiempo real.            |
//|  No necesitas Python ni terminal.                                 |
//|                                                                   |
//|  INSTALACION:                                                     |
//|  1. Copia este archivo en: MT5 > File > Open Data Folder >       |
//|     MQL5 > Experts                                               |
//|  2. En MT5: Herramientas > Opciones > Asesores Expertos >        |
//|     Activar "Permitir WebRequest" y añadir:                      |
//|     https://api.github.com                                        |
//|  3. Arrastra el EA a cualquier grafico                           |
//|  4. Pon tu GITHUB_TOKEN en los parametros y acepta               |
//+------------------------------------------------------------------+
#property copyright "CRZ Kaizen Journal"
#property version   "1.00"
#property description "Bridge EA: sube datos MT5 a GitHub sin Python."

//── Parametros del usuario ─────────────────────────────────────────
input string GITHUB_TOKEN  = "";                         // GitHub Token (ghp_...)
input string GITHUB_USER   = "cristianzafra924-source"; // Usuario GitHub
input string GITHUB_REPO   = "crz-kaizen-journal";      // Repositorio GitHub
input string GITHUB_BRANCH = "main";                    // Rama
input int    UPDATE_SECS   = 10;                        // Segundos entre actualizaciones
input int    HISTORY_DAYS  = 365;                       // Dias de historial

//── Variables globales ─────────────────────────────────────────────
string   g_account_id = "";
string   g_api_url    = "";
datetime g_last_push  = 0;
string   g_cached_sha = "";

//+------------------------------------------------------------------+
int OnInit()
{
    if(GITHUB_TOKEN == "")
    {
        Alert("CRZ Bridge: configura tu GITHUB_TOKEN en los parametros del EA.");
        return INIT_FAILED;
    }
    g_account_id = IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN));
    g_api_url    = "https://api.github.com/repos/" + GITHUB_USER + "/" + GITHUB_REPO
                 + "/contents/data/" + g_account_id + ".json";

    Print("=== CRZ Kaizen Bridge iniciado ===");
    Print("Cuenta : #" + g_account_id + " - " + AccountInfoString(ACCOUNT_NAME));
    Print("Destino: data/" + g_account_id + ".json");
    Print("Intervalo: " + IntegerToString(UPDATE_SECS) + "s");

    EventSetTimer(UPDATE_SECS);
    PushToGitHub();
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { EventKillTimer(); Print("CRZ Bridge detenido."); }
void OnTimer()                  { PushToGitHub(); }
void OnTick()
{
    if(TimeCurrent() - g_last_push >= UPDATE_SECS)
        PushToGitHub();
}

//+------------------------------------------------------------------+
//| Formatea datetime a "YYYY-MM-DD HH:MM:SS"                        |
//+------------------------------------------------------------------+
string FmtDT(datetime dt)
{
    string s = TimeToString(dt, TIME_DATE | TIME_MINUTES | TIME_SECONDS);
    StringReplace(s, ".", "-");
    return s;
}

//+------------------------------------------------------------------+
//| Escapa caracteres especiales para JSON                            |
//+------------------------------------------------------------------+
string EscJ(string s)
{
    StringReplace(s, "\\", "\\\\");
    StringReplace(s, "\"", "\\\"");
    return s;
}

//+------------------------------------------------------------------+
//| JSON de posiciones abiertas                                       |
//+------------------------------------------------------------------+
string BuildPositions()
{
    string arr = "[";
    int total = PositionsTotal();
    for(int i = 0; i < total; i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(ticket == 0) continue;
        double prof = PositionGetDouble(POSITION_PROFIT);
        double swap = PositionGetDouble(POSITION_SWAP);
        if(i > 0) arr += ",";
        arr += StringFormat(
            "{\"ticket\":%I64u,\"symbol\":\"%s\",\"type\":\"%s\","
            "\"volume\":%.2f,\"price_open\":%.5f,\"price_current\":%.5f,"
            "\"sl\":%.5f,\"tp\":%.5f,\"profit\":%.2f,\"swap\":%.2f,"
            "\"pnl_net\":%.2f,\"time_open\":\"%s\"}",
            ticket,
            EscJ(PositionGetString(POSITION_SYMBOL)),
            PositionGetInteger(POSITION_TYPE) == 0 ? "buy" : "sell",
            PositionGetDouble(POSITION_VOLUME),
            PositionGetDouble(POSITION_PRICE_OPEN),
            PositionGetDouble(POSITION_PRICE_CURRENT),
            PositionGetDouble(POSITION_SL),
            PositionGetDouble(POSITION_TP),
            prof, swap, prof + swap,
            FmtDT((datetime)PositionGetInteger(POSITION_TIME))
        );
    }
    return arr + "]";
}

//+------------------------------------------------------------------+
//| JSON de deals (hoy o historial)                                  |
//+------------------------------------------------------------------+
string BuildDeals(datetime from, datetime to, double &pnl_out, bool is_today)
{
    HistorySelect(from, to);
    string arr  = "[";
    pnl_out     = 0.0;
    int count   = 0;
    int total   = HistoryDealsTotal();

    for(int i = 0; i < total; i++)
    {
        ulong ticket = HistoryDealGetTicket(i);
        if(ticket == 0) continue;
        ENUM_DEAL_TYPE dtype = (ENUM_DEAL_TYPE)HistoryDealGetInteger(ticket, DEAL_TYPE);
        if(dtype != DEAL_TYPE_BUY && dtype != DEAL_TYPE_SELL) continue;

        double prof = HistoryDealGetDouble(ticket, DEAL_PROFIT);
        double comm = HistoryDealGetDouble(ticket, DEAL_COMMISSION);
        double swap = HistoryDealGetDouble(ticket, DEAL_SWAP);
        double pnl  = prof + comm + swap;
        datetime dt = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
        pnl_out += pnl;

        string time_str;
        if(is_today)
            time_str = TimeToString(dt, TIME_MINUTES | TIME_SECONDS); // HH:MM:SS
        else
            time_str = FmtDT(dt); // YYYY-MM-DD HH:MM:SS

        if(count > 0) arr += ",";
        if(is_today)
        {
            arr += StringFormat(
                "{\"ticket\":%I64u,\"symbol\":\"%s\",\"type\":\"%s\","
                "\"volume\":%.2f,\"price\":%.5f,\"profit\":%.2f,"
                "\"commission\":%.2f,\"swap\":%.2f,\"pnl_net\":%.2f,\"time\":\"%s\"}",
                ticket,
                EscJ(HistoryDealGetString(ticket, DEAL_SYMBOL)),
                dtype == DEAL_TYPE_BUY ? "buy" : "sell",
                HistoryDealGetDouble(ticket, DEAL_VOLUME),
                HistoryDealGetDouble(ticket, DEAL_PRICE),
                prof, comm, swap, pnl, time_str
            );
        }
        else
        {
            arr += StringFormat(
                "{\"ticket\":%I64u,\"symbol\":\"%s\",\"type\":\"%s\","
                "\"volume\":%.2f,\"price\":%.5f,\"profit\":%.2f,"
                "\"commission\":%.2f,\"swap\":%.2f,\"pnl_net\":%.2f,"
                "\"win\":%s,\"time\":\"%s\"}",
                ticket,
                EscJ(HistoryDealGetString(ticket, DEAL_SYMBOL)),
                dtype == DEAL_TYPE_BUY ? "buy" : "sell",
                HistoryDealGetDouble(ticket, DEAL_VOLUME),
                HistoryDealGetDouble(ticket, DEAL_PRICE),
                prof, comm, swap, pnl,
                prof > 0 ? "true" : "false",
                time_str
            );
        }
        count++;
    }
    return arr + "]";
}

//+------------------------------------------------------------------+
//| Equity series acumulada del historial                             |
//+------------------------------------------------------------------+
string BuildEquitySeries(datetime from, datetime to)
{
    HistorySelect(from, to);
    string arr = "[";
    double acum = 0.0;
    int count = 0;
    int total = HistoryDealsTotal();
    for(int i = 0; i < total; i++)
    {
        ulong ticket = HistoryDealGetTicket(i);
        if(ticket == 0) continue;
        ENUM_DEAL_TYPE dtype = (ENUM_DEAL_TYPE)HistoryDealGetInteger(ticket, DEAL_TYPE);
        if(dtype != DEAL_TYPE_BUY && dtype != DEAL_TYPE_SELL) continue;
        acum += HistoryDealGetDouble(ticket, DEAL_PROFIT)
              + HistoryDealGetDouble(ticket, DEAL_COMMISSION)
              + HistoryDealGetDouble(ticket, DEAL_SWAP);
        if(count > 0) arr += ",";
        arr += DoubleToString(NormalizeDouble(acum, 2), 2);
        count++;
    }
    return arr + "]";
}

//+------------------------------------------------------------------+
//| JSON completo de la cuenta                                        |
//+------------------------------------------------------------------+
string BuildFullJSON()
{
    datetime now         = TimeCurrent();
    datetime today_start = (datetime)(now - now % 86400);
    datetime hist_from   = now - (datetime)(HISTORY_DAYS * 86400LL);

    double pnl_dia  = 0.0;
    double pnl_hist = 0.0;

    string positions   = BuildPositions();
    string deals_hoy   = BuildDeals(today_start, now + 86400, pnl_dia, true);
    string historial   = BuildDeals(hist_from,   now + 86400, pnl_hist, false);
    string eq_series   = BuildEquitySeries(hist_from, now + 86400);

    // Contar trades en historial
    HistorySelect(hist_from, now + 86400);
    int n_trades = 0;
    for(int i = 0; i < HistoryDealsTotal(); i++)
    {
        ulong t = HistoryDealGetTicket(i);
        if(t == 0) continue;
        ENUM_DEAL_TYPE dt = (ENUM_DEAL_TYPE)HistoryDealGetInteger(t, DEAL_TYPE);
        if(dt == DEAL_TYPE_BUY || dt == DEAL_TYPE_SELL) n_trades++;
    }

    string json = StringFormat(
        "{\"timestamp\":\"%s\",\"estado\":\"conectado\","
        "\"cuenta\":{"
        "\"login\":%I64d,\"nombre\":\"%s\",\"empresa\":\"%s\",\"servidor\":\"%s\","
        "\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f,\"margin_libre\":%.2f,"
        "\"margin_nivel\":%.2f,\"profit_abierto\":%.2f,\"divisa\":\"%s\","
        "\"apalancamiento\":%I64d},"
        "\"posiciones_abiertas\":%s,"
        "\"deals_hoy\":%s,"
        "\"pnl_dia\":%.2f,"
        "\"historial\":%s,"
        "\"equity_series\":%s,"
        "\"n_trades\":%d}",
        FmtDT(now),
        AccountInfoInteger(ACCOUNT_LOGIN),
        EscJ(AccountInfoString(ACCOUNT_NAME)),
        EscJ(AccountInfoString(ACCOUNT_COMPANY)),
        EscJ(AccountInfoString(ACCOUNT_SERVER)),
        AccountInfoDouble(ACCOUNT_BALANCE),
        AccountInfoDouble(ACCOUNT_EQUITY),
        AccountInfoDouble(ACCOUNT_MARGIN),
        AccountInfoDouble(ACCOUNT_FREEMARGIN),
        AccountInfoDouble(ACCOUNT_MARGIN_LEVEL),
        AccountInfoDouble(ACCOUNT_PROFIT),
        EscJ(AccountInfoString(ACCOUNT_CURRENCY)),
        AccountInfoInteger(ACCOUNT_LEVERAGE),
        positions, deals_hoy, pnl_dia,
        historial, eq_series, n_trades
    );
    return json;
}

//+------------------------------------------------------------------+
//| Obtiene el SHA actual del archivo en GitHub                       |
//+------------------------------------------------------------------+
string GetSHA()
{
    string req_headers = "Authorization: token " + GITHUB_TOKEN + "\r\n"
                       + "Accept: application/vnd.github.v3+json\r\n";
    char   result[];
    string res_headers;
    int code = WebRequest("GET", g_api_url + "?ref=" + GITHUB_BRANCH,
                          req_headers, 10000, NULL, result, res_headers);
    if(code == 200)
    {
        string body = CharArrayToString(result);
        int pos = StringFind(body, "\"sha\":");
        if(pos >= 0)
        {
            int s = StringFind(body, "\"", pos + 6) + 1;
            int e = StringFind(body, "\"", s);
            if(s > 0 && e > s)
                return StringSubstr(body, s, e - s);
        }
    }
    return "";
}

//+------------------------------------------------------------------+
//| Sube el JSON a GitHub                                             |
//+------------------------------------------------------------------+
void PushToGitHub()
{
    string json = BuildFullJSON();

    // Base64 encode
    uchar src[], dst[], key[];
    StringToCharArray(json, src, 0, StringLen(json));
    CryptEncode(CRYPT_BASE64, src, key, dst);
    string b64 = CharArrayToString(dst);
    StringReplace(b64, "\n", "");
    StringReplace(b64, "\r", "");

    // SHA (necesario para actualizar archivo existente)
    string sha = GetSHA();

    // Payload
    string now_str = FmtDT(TimeCurrent());
    string payload = "{\"message\":\"live " + now_str + "\","
                   + "\"content\":\"" + b64 + "\","
                   + "\"branch\":\"" + GITHUB_BRANCH + "\"";
    if(sha != "") payload += ",\"sha\":\"" + sha + "\"";
    payload += "}";

    // PUT request
    string req_headers = "Authorization: token " + GITHUB_TOKEN + "\r\n"
                       + "Accept: application/vnd.github.v3+json\r\n"
                       + "Content-Type: application/json\r\n";
    char   post[], result[];
    string res_headers;
    StringToCharArray(payload, post, 0, StringLen(payload));

    int code = WebRequest("PUT", g_api_url, req_headers, 20000, post, result, res_headers);

    g_last_push = TimeCurrent();
    string bal = DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2);
    string eq  = DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY),  2);

    if(code == 200 || code == 201)
        Print("[" + now_str + "] Balance: $" + bal + " | Equity: $" + eq + " | GitHub OK");
    else
        Print("[" + now_str + "] GitHub Error HTTP " + IntegerToString(code));
}
//+------------------------------------------------------------------+
