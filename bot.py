"""
Discord Bot for Rec Room Theater Co.
Sets up the server with appropriate channels, roles, and permissions.

Usage:
    Set the DISCORD_BOT_TOKEN environment variable and run:
    python bot.py
    
The bot responds to the 'setup' command only from user ID 480751189366013973.
"""

import os
import asyncio
import discord
from discord import app_commands, Permissions
from discord.ext import commands

# Configuration
AUTHORIZED_USER_ID = 480751189366013973

# Roles to create
ROLES_CONFIG = [
    {"name": "Admin", "color": discord.Color.red(), "permissions": Permissions.all(), "hoist": True},
    {"name": "Moderator", "color": discord.Color.orange(), "permissions": Permissions(moderate_members=True, manage_messages=True, manage_channels=True, kick_members=True), "hoist": True},
    {"name": "Director", "color": discord.Color.purple(), "permissions": Permissions(manage_guild=True, manage_roles=True, manage_channels=True), "hoist": True},
    {"name": "Stage Manager", "color": discord.Color.blue(), "permissions": Permissions(manage_channels=True, manage_messages=True), "hoist": True},
    {"name": "Actor", "color": discord.Color.green(), "permissions": Permissions(send_messages=True, connect=True, speak=True, use_application_commands=True), "hoist": False},
    {"name": "Crew Member", "color": discord.Color.teal(), "permissions": Permissions(send_messages=True, connect=True, speak=True, use_application_commands=True), "hoist": False},
    {"name": "Member", "color": discord.Color.default(), "permissions": Permissions(send_messages=True, connect=True, speak=True, read_message_history=True), "hoist": False},
    {"name": "Guest", "color": discord.Color.light_gray(), "permissions": Permissions(read_messages=True, connect=True, speak=False), "hoist": False},
]

# Server setup configuration - now includes permission overwrites
CATEGORIES_CONFIG = [
    {
        "name": "📌 General",
        "channels": [
            {"name": "welcome", "type": discord.ChannelType.text, "topic": "Welcome to Rec Room Theater Co.!"},
            {"name": "rules", "type": discord.ChannelType.text, "topic": "Server rules and guidelines"},
            {"name": "general-chat", "type": discord.ChannelType.text, "topic": "General discussion"},
            {"name": "introduce-yourself", "type": discord.ChannelType.text, "topic": "Tell us about yourself!"},
        ],
        "default_permissions": Permissions(read_messages=True, send_messages=True, read_message_history=True),
    },
    {
        "name": "🎭 Theater",
        "channels": [
            {"name": "scripts-discussion", "type": discord.ChannelType.text, "topic": "Discuss scripts and plays"},
            {"name": "audition-notices", "type": discord.ChannelType.text, "topic": "Audition announcements and info"},
            {"name": "production-talk", "type": discord.ChannelType.text, "topic": "Current production discussions"},
            {"name": "behind-the-scenes", "type": discord.ChannelType.text, "topic": "BTS content and updates"},
        ],
        "default_permissions": Permissions(read_messages=True, send_messages=True),
        "role_permissions": {
            "Director": Permissions(read_messages=True, send_messages=True, manage_messages=True),
            "Stage Manager": Permissions(read_messages=True, send_messages=True, manage_messages=True),
            "Actor": Permissions(read_messages=True, send_messages=True),
            "Crew Member": Permissions(read_messages=True, send_messages=True),
            "Guest": Permissions(read_messages=True, send_messages=False),
        },
    },
    {
        "name": "📅 Events",
        "channels": [
            {"name": "upcoming-shows", "type": discord.ChannelType.text, "topic": "Upcoming show schedules"},
            {"name": "past-shows", "type": discord.ChannelType.text, "topic": "Recaps and reviews of past shows"},
            {"name": "event-discussion", "type": discord.ChannelType.text, "topic": "Event planning and discussion"},
        ],
        "default_permissions": Permissions(read_messages=True, send_messages=True),
    },
    {
        "name": "📣 Announcements",
        "channels": [
            {"name": "main-announcements", "type": discord.ChannelType.text, "topic": "Important server announcements"},
            {"name": "casting-calls", "type": discord.ChannelType.text, "topic": "Casting opportunities"},
        ],
        "default_permissions": Permissions(read_messages=True, send_messages=False),
        "role_permissions": {
            "Admin": Permissions(read_messages=True, send_messages=True, mention_everyone=True),
            "Moderator": Permissions(read_messages=True, send_messages=True),
            "Director": Permissions(read_messages=True, send_messages=True, mention_everyone=True),
            "Stage Manager": Permissions(read_messages=True, send_messages=True),
        },
    },
    {
        "name": "😂 Fun",
        "channels": [
            {"name": "memes", "type": discord.ChannelType.text, "topic": "Theater memes and humor"},
            {"name": "off-topic", "type": discord.ChannelType.text, "topic": "Talk about anything!"},
        ],
        "default_permissions": Permissions(read_messages=True, send_messages=True),
    },
    {
        "name": "🔊 Voice Channels",
        "channels": [
            {"name": "Rehearsal Room 1", "type": discord.ChannelType.voice, "topic": "Voice rehearsal space"},
            {"name": "Rehearsal Room 2", "type": discord.ChannelType.voice, "topic": "Voice rehearsal space"},
            {"name": "Green Room", "type": discord.ChannelType.voice, "topic": "Chill and wait for your cue"},
        ],
        "default_permissions": Permissions(connect=True, speak=True, use_video=True),
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
    
    # Delete all existing roles (except @everyone)
    print(f"Deleting all custom roles in {guild.name}...")
    for role in guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
                print(f"Deleted role: {role.name}")
            except Exception as e:
                print(f"Failed to delete role {role.name}: {e}")
    
    # Small delay to ensure deletions are complete
    await asyncio.sleep(1)
    
    # Create roles
    print("Creating roles...")
    role_map = {}  # Maps role name to role object
    for role_config in ROLES_CONFIG:
        role = await guild.create_role(
            name=role_config["name"],
            color=role_config["color"],
            permissions=role_config["permissions"],
            hoist=role_config["hoist"],
            reason=f"Setup requested by {user.name}"
        )
        role_map[role_config["name"]] = role
        print(f"Created role: {role_config['name']}")
    
    # Get @everyone role
    everyone_role = guild.default_role
    
    # Create categories and channels with permissions
    print("Creating new channels and categories...")
    
    for cat_config in CATEGORIES_CONFIG:
        # Create category
        category = await guild.create_category(
            name=cat_config["name"],
            reason=f"Setup requested by {user.name}"
        )
        print(f"Created category: {cat_config['name']}")
        
        # Set category permissions
        default_perms = cat_config.get("default_permissions", Permissions(read_messages=True, send_messages=True))
        await category.set_permissions(everyone_role, overwrite=discord.PermissionOverwrite.from_pair(default_perms, default_perms))
        
        # Apply role-specific permissions to category
        role_perms = cat_config.get("role_permissions", {})
        for role_name, perms in role_perms.items():
            if role_name in role_map:
                await category.set_permissions(
                    role_map[role_name], 
                    overwrite=discord.PermissionOverwrite.from_pair(perms, perms)
                )
        
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
