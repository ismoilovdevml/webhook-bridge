# Quick Start Guide

## Ishga tushirish

### 1. Docker bilan (Tavsiya etiladi)

```bash
# .env faylni yarating
cp .env.example .env

# Build va ishga tushirish
docker-compose build
docker-compose up -d

# Natijani ko'rish
docker-compose ps
docker-compose logs -f
```

**Servislar:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. To'xtatish

```bash
docker-compose down
```

### 3. Log'larni ko'rish

```bash
# Barcha loglar
docker-compose logs -f

# Faqat backend
docker-compose logs -f backend

# Faqat frontend
docker-compose logs -f frontend
```

## Provider qo'shish

1. http://localhost:3000 ochish
2. "Providers" sahifasiga o'tish
3. "+ Add Provider" tugmasini bosish

### Telegram misol:

```json
{
  "name": "Main Telegram",
  "type": "telegram",
  "config": {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  },
  "active": true
}
```

## Webhook sozlash

GitLab/GitHub/Bitbucket'da:
1. Repository Settings → Webhooks
2. URL: `http://your-server:8000/api/webhook/git`
3. Events: Push, Merge Request, Pipeline
4. Save

## Muammo yuzaga kelsa

```bash
# Loglarni tekshirish
docker-compose logs -f

# Qayta ishga tushirish
docker-compose restart

# To'liq tozalash va qayta ishga tushirish
docker-compose down -v
docker-compose up -d --build
```

## Health Check

```bash
# Backend
curl http://localhost:8000/health

# Test webhook
curl http://localhost:8000/api/webhook/test
```
