"# Rec Room Theater Co. Discord Bot

A Discord bot that sets up your server with appropriate channels and categories.

## Prerequisites

1. **Create a Discord Bot:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" and create a bot user
   - Copy the bot token

2. **Invite the Bot to Your Server:**
   - Go to "OAuth2" > "URL Generator"
   - Select scopes: `bot`, `application.commands`
   - Select permissions: `Manage Channels`, `Manage Server`, `Send Messages`, `Manage Roles` (optional)
   - Use the generated URL to invite the bot

## Installation

```bash
cd blockybot
pip install -r requirements.txt
```

## Running the Bot

1. Set the bot token:
   ```bash
   export DISCORD_BOT_TOKEN='your-bot-token-here'
   ```

2. Run the bot:
   ```bash
   python bot.py
   ```

## Using the Setup Command

1. Make sure the bot is in your Discord server
2. Run the `/setup` command
3. Only user ID `480751189366013973` can run this command

The bot will:
- Delete all existing channels
- Create the following categories with channels:

### 📌 General
- #welcome
- #rules
- #general-chat
- #introduce-yourself

### 🎭 Theater
- #scripts-discussion
- #audition-notices
- #production-talk
- #behind-the-scenes

### 📅 Events
- #upcoming-shows
- #past-shows
- #event-discussion

### 📣 Announcements
- #main-announcements
- #casting-calls

### 😂 Fun
- #memes
- #off-topic

### 🔊 Voice Channels
- Rehearsal Room 1
- Rehearsal Room 2
- Green Room

## Bot Features

- **Slash Commands**: Uses modern Discord `/` commands
- **Authorization**: Only the specified user ID can run the setup command
- **Complete Reset**: Deletes ALL channels before creating new ones

## Notes

- The bot requires the `Manage Channels` permission
- The setup process may take a few seconds depending on how many channels exist" 
