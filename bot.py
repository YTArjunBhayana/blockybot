"""
Discord Bot for Rec Room Theater Co.
Sets up the server with appropriate channels and categories.

Usage:
    Set the DISCORD_BOT_TOKEN environment variable and run:
    python bot.py
    
The bot responds to the 'setup' command only from user ID 480751189366013973.
"""

import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# Configuration
AUTHORIZED_USER_ID = 480751189366013973

# Server setup configuration
CATEGORIES_CONFIG = [
    {
        "name": "📌 General",
        "channels": [
            {"name": "welcome", "type": discord.ChannelType.text, "topic": "Welcome to Rec Room Theater Co.!"},
            {"name": "rules", "type": discord.ChannelType.text, "topic": "Server rules and guidelines"},
            {"name": "general-chat", "type": discord.ChannelType.text, "topic": "General discussion"},
            {"name": "introduce-yourself", "type": discord.ChannelType.text, "topic": "Tell us about yourself!"},
        ]
    },
    {
        "name": "🎭 Theater",
        "channels": [
            {"name": "scripts-discussion", "type": discord.ChannelType.text, "topic": "Discuss scripts and plays"},
            {"name": "audition-notices", "type": discord.ChannelType.text, "topic": "Audition announcements and info"},
            {"name": "production-talk", "type": discord.ChannelType.text, "topic": "Current production discussions"},
            {"name": "behind-the-scenes", "type": discord.ChannelType.text, "topic": "BTS content and updates"},
        ]
    },
    {
        "name": "📅 Events",
        "channels": [
            {"name": "upcoming-shows", "type": discord.ChannelType.text, "topic": "Upcoming show schedules"},
            {"name": "past-shows", "type": discord.ChannelType.text, "topic": "Recaps and reviews of past shows"},
            {"name": "event-discussion", "type": discord.ChannelType.text, "topic": "Event planning and discussion"},
        ]
    },
    {
        "name": "📣 Announcements",
        "channels": [
            {"name": "main-announcements", "type": discord.ChannelType.text, "topic": "Important server announcements"},
            {"name": "casting-calls", "type": discord.ChannelType.text, "topic": "Casting opportunities"},
        ]
    },
    {
        "name": "😂 Fun",
        "channels": [
            {"name": "memes", "type": discord.ChannelType.text, "topic": "Theater memes and humor"},
            {"name": "off-topic", "type": discord.ChannelType.text, "topic": "Talk about anything!"},
        ]
    },
    {
        "name": "🔊 Voice Channels",
        "channels": [
            {"name": "Rehearsal Room 1", "type": discord.ChannelType.voice, "topic": "Voice rehearsal space"},
            {"name": "Rehearsal Room 2", "type": discord.ChannelType.voice, "topic": "Voice rehearsal space"},
            {"name": "Green Room", "type": discord.ChannelType.voice, "topic": "Chill and wait for your cue"},
        ]
    },
]


class SetupBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Create the setup command
        @self.tree.command(name="setup", description="Set up the Discord server (authorized users only)")
        async def setup_command(interaction: discord.Interaction):
            # Check if the user is authorized
            if interaction.user.id != AUTHORIZED_USER_ID:
                await interaction.response.send_message(
                    "❌ You are not authorized to run this command.", 
                    ephemeral=True
                )
                return
            
            await interaction.response.send_message("🔄 Starting server setup...", ephemeral=True)
            
            try:
                await setup_server(interaction.guild, interaction.user)
                await interaction.edit_original_response(content="✅ Server setup complete!")
            except Exception as e:
                await interaction.edit_original_response(content=f"❌ Setup failed: {str(e)}")
        
        await self.tree.sync(guild=None)  # Global command
        print("Bot is ready!")


async def setup_server(guild: discord.Guild, user: discord.Member):
    """Delete all channels and recreate them according to the config."""
    
    # Delete all existing channels
    print(f"Deleting all channels in {guild.name}...")
    for channel in guild.channels:
        try:
            await channel.delete()
            print(f"Deleted: {channel.name}")
        except Exception as e:
            print(f"Failed to delete {channel.name}: {e}")
    
    # Small delay to ensure channels are fully deleted
    await asyncio.sleep(1)
    
    # Create categories and channels
    print("Creating new channels and categories...")
    
    for cat_config in CATEGORIES_CONFIG:
        # Create category
        category = await guild.create_category(
            name=cat_config["name"],
            reason=f"Setup requested by {user.name}"
        )
        print(f"Created category: {cat_config['name']}")
        
        # Create channels in this category
        for channel_config in cat_config["channels"]:
            if channel_config["type"] == discord.ChannelType.text:
                channel = await guild.create_text_channel(
                    name=channel_config["name"],
                    category=category,
                    topic=channel_config.get("topic", ""),
                    reason=f"Setup requested by {user.name}"
                )
            elif channel_config["type"] == discord.ChannelType.voice:
                channel = await guild.create_voice_channel(
                    name=channel_config["name"],
                    category=category,
                    reason=f"Setup requested by {user.name}"
                )
            print(f"  Created channel: {channel_config['name']}")


async def main():
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
        print("Please set it and try again:")
        print("  export DISCORD_BOT_TOKEN='your-bot-token'")
        return
    
    bot = SetupBot()
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
