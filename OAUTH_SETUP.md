# Google OAuth Setup Instructions

## 1. Install New Dependencies

Run this command to install the OAuth packages:
```bash
cd backend
pip install authlib==1.3.0 itsdangerous==2.1.2
```

## 2. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Set application type to **Web application**
6. Add authorized redirect URIs:
   - `http://localhost:3000/auth/callback`
   - `http://localhost:8000/auth/callback`
7. Copy the **Client ID** and **Client Secret**

## 3. Update .env File

Replace the placeholder values in `backend/.env`:

```env
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
```

## 4. Restart the Server

Kill the current server (Ctrl+C) and restart:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 5. How It Works

### Login Flow:
1. User clicks "Sign In" button on homepage
2. Redirected to Google OAuth login page
3. After authentication, Google redirects back to your app
4. Backend creates/finds user in database
5. JWT token is created and stored in cookie
6. User is redirected to homepage (now authenticated)

### Logout Flow:
1. User clicks "Sign Out" button
2. Cookie is cleared
3. User is redirected to homepage

### Protected Pages:
- **Dashboard** now requires authentication
- Non-authenticated users are redirected to homepage
- Auth state is checked on page load

## 6. Testing

1. Go to `http://localhost:3000`
2. Click "Sign In" button
3. You should be redirected to Google login
4. After login, you'll be back on the homepage (authenticated)
5. Click "Get Started" or "Dashboard" to access protected pages
6. Click "Sign Out" to logout

## API Endpoints Added

- `GET /auth/login` - Initiate Google OAuth
- `GET /auth/callback` - Handle OAuth callback
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user
- `GET /auth/check` - Check authentication status
