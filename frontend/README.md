# ORU Transcript Formatter - Frontend

Modern React frontend for the ORU Transcript Formatter application.

## Features

- **Upload Transcript**: Drag & drop or select .txt files
- **Real-time Feedback**: Loading states and success/error messages
- **Professional UI**: Clean, modern design with TailwindCSS
- **Auto-Download**: Formatted Word document downloads automatically

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **TailwindCSS** - Styling
- **FastAPI** - Backend API integration

## Deployment

The frontend is configured for deployment on Render. The build process will:
1. Build the React application with `npm run build`
2. Serve static files via the backend API

## API Integration

- Development: Connects to `http://localhost:8000`
- Production: Uses `/api` proxy to backend

## Environment Variables

- `VITE_API_URL` - Backend API URL (optional, defaults to localhost for dev)