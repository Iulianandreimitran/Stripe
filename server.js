const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

const appId = '1291328168557869'; // Your App ID
const appSecret = 'a5ba95bf812779d0d43c946dd18dad13'; // Your App Secret
const redirectUri = 'https://3834-89-238-211-222.ngrok-free.app/redirect'; // Your redirect URI

// Serve static files (HTML)
app.use(express.static(path.join(__dirname, 'public')));

// Step 1: Redirect user to Facebook OAuth dialog
app.get('/login', (req, res) => {
  const facebookAuthUrl = `https://www.facebook.com/v21.0/dialog/oauth?client_id=${appId}&redirect_uri=${encodeURIComponent(redirectUri)}&state=12345`;
  res.redirect(facebookAuthUrl);
});

// Step 2: Handle the redirect and exchange code for access token
app.get('/redirect', async (req, res) => {
  const { code } = req.query;

  if (!code) {
    return res.status(400).send('No code found in query.');
  }

  try {
    const response = await axios.get('https://graph.facebook.com/v21.0/oauth/access_token', {
      params: {
        client_id: appId,
        client_secret: appSecret,
        redirect_uri: redirectUri,
        code: code,
      },
    });

    if (response.data && response.data.access_token) {
      const accessToken = response.data.access_token;
      // Redirect to success page with the access token
      return res.redirect(`/success.html?access_token=${accessToken}`);
    } else {
      console.error('No access token found in response');
      return res.status(500).send('Access token not found.');
    }
  } catch (error) {
    console.error('Error exchanging code for token:', error);
    return res.status(500).send('Failed to exchange code for access token');
  }
});

app.listen(5500, () => {
  console.log('Server is running on port 5500');
});

