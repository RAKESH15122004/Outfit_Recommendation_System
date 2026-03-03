# Outfit Project — Frontend

A modern, interactive React frontend for the AI-powered outfit recommendation system.

## Features

- **Landing page** — Hero section with CTA
- **Auth** — Login, register, JWT with refresh token support
- **Dashboard** — Overview of wardrobe, outfits, saved items
- **Wardrobe** — Grid view, category filters, image upload, delete, favorite
- **Recommendations** — Generate AI outfits by occasion and location, accept/reject
- **Saved outfits** — View and remove saved looks
- **Profile** — Update name
- **Subscriptions** — View plans, upgrade via Stripe checkout

## Tech stack

- React 18 + TypeScript
- Vite
- Tailwind CSS
- Framer Motion (animations)
- Lucide React (icons)
- React Router v6

## Setup

```bash
cd frontend
npm install
```

## Development

Start the frontend (runs on port 3000):

```bash
npm run dev
```

Ensure the backend is running on port 8000. The Vite proxy forwards `/api` and `/uploads` to the backend.

## Production

```bash
npm run build
npm run preview
```

For production, set `VITE_API_BASE` to your backend URL if it differs from the frontend origin.

## Design

- **Fonts**: Playfair Display (headings), Outfit (body)
- **Colors**: Warm ink neutrals with copper accents
- **Animations**: Page transitions, card hovers, loading states
