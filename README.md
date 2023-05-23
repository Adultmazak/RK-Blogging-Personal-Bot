<div class="flex flex-grow flex-col gap-3">
<div class="min-h-[20px] flex flex-col items-start gap-4 whitespace-pre-wrap flex flex-row gap-2 text-red-500">
   <div class="text-red-500 markdown prose w-full break-words dark:prose-invert dark">
      <h1>Blogger Manager Bot</h1>
      <p>A simple and easy-to-use Telegram bot that makes it easy to manage your Blogger sites. With this bot, you can easily post new articles to your site with just a few clicks.</p>
      <h2>Features</h2>
      <ul>
         <li>Set a default site to post to</li>
         <li>Add tags to post to specific sites</li>
         <li>Turn on or off the instant posting feature</li>
         <li>Turn on or off the auto title feature</li>
         <li>Write or ask the bot to write a post for you</li>
         <li>Attach images to your posts</li>
         <li>Add YouTube videos to your posts</li>
      </ul>
      <h2>Getting Started</h2>
      <p>To start using this bot, you'll need to set the following environment variables:</p>
      <ul>
         <li><code>BOT_USERNAME</code>: Your bot's username</li>
      </ul>
   </div>
</div>
<div class="min-h-[20px] flex flex-col items-start gap-4 whitespace-pre-wrap">
<div class="markdown prose w-full break-words dark:prose-invert dark">
<ul>
   <li><code>API_ID</code>: Your bot's API ID</li>
   <li><code>API_HASH</code>: Your bot's API hash</li>
   <li><code>BOT_TOKEN</code>: Your bot's access token</li>
   <li><code>ADMINS</code>: A comma-separated list of admin IDs</li>
   <li><code>DATABASE_NAME</code>: The name of the database (defaults to <code>BOT_USERNAME</code>)</li>
   <li><code>DATABASE_URL</code>: The URL of the database (defaults to <code>None</code>)</li>
   <li><code>OWNER_ID</code>: The ID of the bot owner</li>
   <li><code>LOG_CHANNEL</code>: The ID of the log channel (defaults to <code>0</code>)</li>
   <li><code>UPDATE_CHANNEL</code>: The ID of the update channel (defaults to <code>0</code>)</li>
   <li><code>BROADCAST_AS_COPY</code>: Whether to broadcast as copy (defaults to <code>False</code>)</li>
   <li><code>OWNER_USERNAME</code>: The username of the bot owner (defaults to <code>None</code>)</li>
   <li><code>WEB_SERVER</code>: Whether to run a web server (defaults to <code>False</code>)</li>
   <li><code>BLOG_ID</code>: The ID of your Blogger site</li>
   <li><code>BLOGGER_EMAIL</code>: Your Blogger account email address</li>
   <li><code>VALIDITY</code>: A comma-separated list of validity periods</li>
   <li><code>QUOTA</code>: The number of posts you can make per day (defaults to <code>50</code>)</li>
   <li><code>PREMIUM_TEXT</code>: The text to be displayed in the premium version (defaults to <code>This is a test message</code>)</li>
</ul>
<p>Once you have set these environment variables, you're ready to start using the bot!</p>
<h2>Premium Version</h2>
<p>In addition to the features mentioned above, the premium version of this bot also allows you to post unlimited posts and add multiples blogs.</p>

<h2>Run Command</h2>
<p>python3 -m bot</p>

# Getting Google API for Blogger

This guide will provide you with step by step instructions on how to get a Google API for Blogger, including adding required scopes and permissions and obtaining a refresh token.

## Prerequisites

* [A Google account](https://accounts.google.com/SignUp)

## Step 1: Create a Project

1. Go to [Google Developer Console](https://console.developers.google.com/).

2. Log in with your Google Account.

3. Click the **Select a project** dropdown.

4. Click **+ NEW PROJECT**.

5. Enter a project name and click **Create**.

## Step 2: Enable the Blogger API

1. From the left menu, select **APIs & Services > Library**.

2. Search for **Blogger**.

3. Click **Blogger API**.

4. Click **ENABLE**.

## Step 3: Create an OAuth Client ID

1. From the left menu, select **APIs & Services > Credentials**.

2. Click **Create credentials > OAuth client ID**.

3. Select **Web application**.

4. Enter a name for the OAuth Client ID.

5. Enter a **Authorized JavaScript origins** and **Authorized redirect URIs**.

6. Click **Create**.

## Step 4: Add Required Scopes

1. From the left menu, select **APIs & Services > Library**.

2. Search for **Blogger**.

3. Click **Blogger API**.

4. Click the **OAuth consent screen** tab.

5. Under **Scopes for Google APIs**, click **Add scope**.

6. Search for **blogger**.

7. Click **blogger.readonly**.

8. Click **Add**.

9. Click **Save**.

## Step 5: Get Refresh Token

1. Go to [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/).

2. Select **Blogger API v3** from the list of APIs.

3. Click **Authorize APIs**.

4. Sign in with your Google Account.

5. Select all the required scopes and click **Allow**.

6. Copy the refresh token from the page.</br></br>
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Conclusion

You have now successfully created a Google API for Blogger, added required scopes and permissions, and obtained a refresh token.
