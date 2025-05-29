# Guida al Deployment su Render.com

## File necessari per la produzione

Assicurati di avere questi file nel tuo repository:

### File essenziali:
- `fixed_bot.py` - Bot principale
- `scheduler_bot.py` - Scheduler automatico
- `rai_scraper.py` - Scraper dati lottery
- `utils.py` - Funzioni di utilità
- `config.py` - Configurazioni
- `render.yaml` - Configurazione Render

## Passaggi per il deployment

### 1. Preparazione Repository
```bash
# Crea un nuovo repository Git
git init
git add fixed_bot.py scheduler_bot.py rai_scraper.py utils.py config.py render.yaml
git commit -m "Initial commit - Lottery Bot"
git push origin main
```

### 2. Configurazione su Render.com

1. Vai su [render.com](https://render.com)
2. Crea un account o accedi
3. Clicca "New +" e seleziona "Blueprint"
4. Connetti il tuo repository GitHub/GitLab
5. Render rileverà automaticamente il file `render.yaml`

### 3. Configurazione Variabili d'Ambiente

Durante il setup, configura:
- `TELEGRAM_BOT_TOKEN`: Il token del tuo bot Telegram

### 4. Servizi Creati

Il deployment creerà automaticamente:

**lottery-bot (Web Service)**
- Gestisce i comandi degli utenti
- Endpoint: `/start`, `/help`, `/ultima`
- Sempre attivo per rispondere agli utenti

**lottery-scheduler (Background Worker)**
- Controlli automatici alle 20:15
- Pubblica risultati su @estrazionilotto
- Gestisce messaggi fissati

### 5. Monitoraggio

Dopo il deployment:
- Vai nella dashboard Render
- Controlla i logs di entrambi i servizi
- Verifica che non ci siano errori di startup

### 6. Test del Sistema

Una volta online:
1. Invia `/start` al bot su Telegram
2. Testa `/ultima` per i risultati
3. Verifica il canale @estrazionilotto

## Vantaggi del Piano Gratuito Render

- 750 ore/mese di runtime (sufficienti per uso continuativo)
- Deploy automatico ad ogni push
- Logs integrati
- HTTPS automatico
- Riavvio automatico in caso di crash

## Struttura del Progetto in Produzione

```
lottery-bot/
├── fixed_bot.py          # Bot principale
├── scheduler_bot.py      # Scheduler automatico  
├── rai_scraper.py        # Scraper RAI Televideo
├── utils.py              # Utilità di formattazione
├── config.py             # Configurazioni
├── render.yaml           # Config deployment
└── README.md             # Documentazione
```

## Note Importanti

- Il bot principale resta sempre attivo per rispondere agli utenti
- Lo scheduler si attiva automaticamente alle 20:15 ogni sera
- I messaggi vengono automaticamente fissati nel canale
- Non serve database - tutto funziona via API Telegram e scraping

## Troubleshooting

Se i servizi non si avviano:
1. Controlla i logs nella dashboard Render
2. Verifica che `TELEGRAM_BOT_TOKEN` sia configurato
3. Assicurati che il bot abbia i permessi sul canale @estrazionilotto