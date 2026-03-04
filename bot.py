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
import re
import discord
from discord import app_commands, Permissions
from discord.ext import commands

# Configuration
AUTHORIZED_USER_ID = 480751189366013973

# Basic server rules
SERVER_RULES = """# 📜 Rec Room Theater Co. Server Rules

Welcome to Rec Room Theater Co.! Please follow these rules to keep our community great.

## 1. Be Respectful
- Treat everyone with respect and kindness
- No harassment, hate speech, or bullying
- Be inclusive and welcoming to all

## 2. No Swearing or Profanity
- This is a family-friendly environment
- No swearing, curse words, or inappropriate language
- Avoid offensive jokes or content

## 3. Keep It Appropriate
- No NSFW or explicit content
- No spam or excessive advertising
- Stay on topic in designated channels

## 4. Listen to Staff
- Follow directions from Moderators and Admins
- Staff decisions are final
- If you have issues, DM a staff member

## 5. Have Fun!
- Participate in discussions and events
- Be creative and collaborative
- Help others enjoy the community

---

**By reacting with ✅ below, you agree to follow these rules and will receive the Member role!**"""

# Roles to create
ROLES_CONFIG = [
    {"name": "Admin", "color": discord.Color.red(), "permissions": Permissions.all(), "hoist": True},
    {"name": "Moderator", "color": discord.Color.orange(), "permissions": Permissions(moderate_members=True, manage_messages=True, manage_channels=True, kick_members=True, ban_members=True), "hoist": True},
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
            "Member": Permissions(read_messages=True, send_messages=True),
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
        "role_permissions": {
            "Member": Permissions(read_messages=True, send_messages=True),
            "Guest": Permissions(read_messages=True, send_messages=False),
        },
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
            "Member": Permissions(read_messages=True, send_messages=False),
            "Guest": Permissions(read_messages=True, send_messages=False),
        },
    },
    {
        "name": "😂 Fun",
        "channels": [
            {"name": "memes", "type": discord.ChannelType.text, "topic": "Theater memes and humor"},
            {"name": "off-topic", "type": discord.ChannelType.text, "topic": "Talk about anything!"},
        ],
        "default_permissions": Permissions(read_messages=True, send_messages=True),
        "role_permissions": {
            "Member": Permissions(read_messages=True, send_messages=True),
            "Guest": Permissions(read_messages=True, send_messages=True),
        },
    },
    {
        "name": "🔊 Voice Channels",
        "channels": [
            {"name": "Rehearsal Room 1", "type": discord.ChannelType.voice, "topic": "Voice rehearsal space"},
            {"name": "Rehearsal Room 2", "type": discord.ChannelType.voice, "topic": "Voice rehearsal space"},
            {"name": "Green Room", "type": discord.ChannelType.voice, "topic": "Chill and wait for your cue"},
        ],
        "default_permissions": Permissions(connect=True, speak=True),
    },
]

# Swear words to filter (common profanity)
SWEAR_WORDS = [
    "fuck", "shit", "damn", "ass", "bitch", "bastard", "crap", "piss",
    "dick", "cock", "cunt", "whore", "slut", "retard", "faggot", "nigger",
    "chink", "gook", "spic", "kike", "wetback", "fucker", "shitty", "bullshit",
    "goddamn", "jesus christ", "hell", "dammit", "dumbass"
]


class SetupBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.role_message_id = None
        self.role_channel_id = None

    async def setup_hook(self):
        # Setup command
        @self.tree.command(name="setup", description="Set up the Discord server (authorized users only)")
        async def setup_command(interaction: discord.Interaction):
            if interaction.user.id != AUTHORIZED_USER_ID:
                await interaction.response.send_message(
                    "❌ You are not authorized to run this command.", 
                    ephemeral=True
                )
                return
            
            await interaction.response.send_message("🔄 Starting server setup...", ephemeral=True)
            
            try:
                await setup_server(interaction.guild, interaction.user, self)
                await interaction.edit_original_response(content="✅ Server setup complete!")
            except Exception as e:
                await interaction.edit_original_response(content=f"❌ Setup failed: {str(e)}")
        
        # Kick command (moderation)
        @self.tree.command(name="kick", description="Kick a user from the server")
        @app_commands.describe(user="User to kick", reason="Reason for kicking")
        async def kick_command(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message("❌ You don't have permission to kick members.", ephemeral=True)
                return
            
            try:
                await user.kick(reason=reason)
                await interaction.response.send_message(f"✅ Kicked {user.name}#{user.discriminator}")
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to kick: {str(e)}", ephemeral=True)
        
        # Ban command (moderation)
        @self.tree.command(name="ban", description="Ban a user from the server")
        @app_commands.describe(user="User to ban", reason="Reason for banning")
        async def ban_command(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
                return
            
            try:
                await user.ban(reason=reason)
                await interaction.response.send_message(f"✅ Banned {user.name}#{user.discriminator}")
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to ban: {str(e)}", ephemeral=True)
        
        # Unban command (moderation)
        @self.tree.command(name="unban", description="Unban a user from the server")
        @app_commands.describe(user="Username to unban (e.g., user#1234)")
        async def unban_command(interaction: discord.Interaction, user: str):
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("❌ You don't have permission to unban members.", ephemeral=True)
                return
            
            try:
                # Try to parse username#discriminator
                parts = user.split('#')
                if len(parts) == 2:
                    banned_users = await interaction.guild.bans()
                    for ban_entry in banned_users:
                        b_user = ban_entry.user
                        if b_user.name == parts[0] and b_user.discriminator == parts[1]:
                            await interaction.guild.unban(b_user)
                            await interaction.response.send_message(f"✅ Unbanned {user}")
                            return
                await interaction.response.send_message(f"❌ User {user} not found in ban list", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to unban: {str(e)}", ephemeral=True)
        
        # Clear messages command (moderation)
        @self.tree.command(name="clear", description="Delete a number of messages")
        @app_commands.describe(amount="Number of messages to delete (max 100)")
        async def clear_command(interaction: discord.Interaction, amount: int = 5):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("❌ You don't have permission to manage messages.", ephemeral=True)
                return
            
            if amount > 100:
                amount = 100
            if amount < 1:
                amount = 1
            
            try:
                await interaction.channel.purge(limit=amount)
                await interaction.response.send_message(f"✅ Deleted {amount} messages", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to clear messages: {str(e)}", ephemeral=True)
        
        # Warn command (moderation)
        @self.tree.command(name="warn", description="Warn a user")
        @app_commands.describe(user="User to warn", reason="Reason for warning")
        async def warn_command(interaction: discord.Interaction, user: discord.Member, reason: str):
            if not interaction.user.guild_permissions.moderate_members:
                await interaction.response.send_message("❌ You don't have permission to warn members.", ephemeral=True)
                return
            
            try:
                await user.send(f"⚠️ You have been warned in Rec Room Theater Co.: {reason}")
                await interaction.response.send_message(f"✅ Warned {user.name}#{user.discriminator}")
            except:
                await interaction.response.send_message(f"✅ Warned {user.name}#{user.discriminator} (could not DM)")
        
        # Mute command (moderation)
        @self.tree.command(name="mute", description="Mute a user in text channels")
        @app_commands.describe(user="User to mute", reason="Reason for muting")
        async def mute_command(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
            if not interaction.user.guild_permissions.moderate_members:
                await interaction.response.send_message("❌ You don't have permission to mute members.", ephemeral=True)
                return
            
            try:
                # Check if Member role exists
                member_role = discord.utils.get(interaction.guild.roles, name="Member")
                if member_role:
                    await user.remove_roles(member_role)
                await user.timeout(discord.utils.utcnow(), reason=reason)
                await interaction.response.send_message(f"✅ Muted {user.name}#{user.discriminator}")
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to mute: {str(e)}", ephemeral=True)
        
        # Add role commands
        @self.tree.command(name="addrole", description="Give yourself a role")
        @app_commands.describe(role="Role to add")
        async def addrole_command(interaction: discord.Interaction, role: str):
            valid_roles = ["Actor", "Crew Member", "Guest"]
            role_obj = discord.utils.get(interaction.guild.roles, name=role)
            
            if role not in valid_roles or not role_obj:
                await interaction.response.send_message(
                    f"❌ Invalid role. Available: {', '.join(valid_roles)}", 
                    ephemeral=True
                )
                return
            
            try:
                await interaction.user.add_roles(role_obj)
                await interaction.response.send_message(f"✅ Added {role} role!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed: {str(e)}", ephemeral=True)
        
        # Sync commands
        await self.tree.sync(guild=None)
        print("Bot is ready!")

    async def on_raw_reaction_add(self, payload):
        """Handle reaction to get roles"""
        if payload.message_id == self.role_message_id and payload.user_id != self.user.id:
            guild = self.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            
            if str(payload.emoji) == "✅":
                member_role = discord.utils.get(guild.roles, name="Member")
                guest_role = discord.utils.get(guild.roles, name="Guest")
                
                if member_role:
                    await user.add_roles(member_role)
                if guest_role:
                    await user.add_roles(guest_role)
    
    async def on_message(self, message):
        """Filter swear words"""
        if message.guild and not message.author.bot:
            content_lower = message.content.lower()
            for word in SWEAR_WORDS:
                if re.search(r'\b' + re.escape(word) + r'\b', content_lower):
                    await message.delete()
                    try:
                        await message.author.send("⚠️ Please avoid using inappropriate language!")
                    except:
                        pass
                    break
        
        await self.process_commands(message)


async def setup_server(guild: discord.Guild, user: discord.Member, bot: SetupBot):
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
                
                # If this is the rules channel, post the rules with reaction
                if channel_config["name"] == "rules":
                    rules_message = await channel.send(SERVER_RULES)
                    await rules_message.add_reaction("✅")
                    bot.role_message_id = rules_message.id
                    print(f"  Posted rules with reaction in #{channel_config['name']}")
                    
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
