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
import random
import json
from datetime import datetime, timedelta
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
            {"name": "games", "type": discord.ChannelType.text, "topic": "Play games and earn Thespian Coins!"},
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

# Thespian currency system
CURRENCY_FILE = "thespian_coins.json"
CURRENCY_NAME = "Thespian Coins"

# Coin economy settings
COINS_DAILY = 100  # Daily reward
COINS_GUESS_WIN = 50
COINS_GUESS_LOSE = 10
COINS_TRIVIA_WIN = 75
COINS_TRIVIA_LOSE = 15
COINS_8BALL_COST = 25

# Games category channel
GAMES_CATEGORY = "🎮 Fun & Games"


def load_coins():
    """Load coins from file"""
    if os.path.exists(CURRENCY_FILE):
        try:
            with open(CURRENCY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_coins(coins):
    """Save coins to file"""
    with open(CURRENCY_FILE, 'w') as f:
        json.dump(coins, f, indent=2)

def get_balance(user_id):
    """Get user's coin balance"""
    coins = load_coins()
    return coins.get(str(user_id), 0)

def add_coins(user_id, amount):
    """Add coins to user"""
    coins = load_coins()
    user_id = str(user_id)
    if user_id not in coins:
        coins[user_id] = 0
    coins[user_id] += amount
    save_coins(coins)
    return coins[user_id]

def remove_coins(user_id, amount):
    """Remove coins from user (returns True if successful)"""
    coins = load_coins()
    user_id = str(user_id)
    if coins.get(user_id, 0) >= amount:
        coins[user_id] -= amount
        save_coins(coins)
        return True
    return False

def set_coins(user_id, amount):
    """Set user's coin balance"""
    coins = load_coins()
    coins[str(user_id)] = amount
    save_coins(coins)

# Trivia questions (theater themed)
TRIVIA_QUESTIONS = [
    {"q": "Who wrote 'Romeo and Juliet'?", "a": "Shakespeare", "options": ["Shakespeare", "Marlowe", "Webster", "Kyd"]},
    {"q": "What is the term for the backstage area called?", "a": "Wings", "options": ["Wings", "Stage", "Booth", "Set"]},
    {"q": "Who wrote 'The Phantom of the Opera'?", "a": "Andrew Lloyd Webber", "options": ["Andrew Lloyd Webber", "Cole Porter", "Stephen Sondheim", "Leonard Bernstein"]},
    {"q": "What is a soliloquy?", "a": "A speech alone on stage", "options": ["A speech alone on stage", "A song in a play", "A fight scene", "An intermission"]},
    {"q": "What does 'break a leg' mean in theater?", "a": "Good luck", "options": ["Good luck", "Get injured", "End the show", "Take a bow"]},
    {"q": "Who is the Greek god of theater?", "a": "Dionysus", "options": ["Dionysus", "Apollo", "Athena", "Zeus"]},
    {"q": "What is a 'matinee'?", "a": "Afternoon performance", "options": ["Afternoon performance", "Opening night", "Dress rehearsal", "Final show"]},
    {"q": "Who wrote 'Hamlet'?", "a": "Shakespeare", "options": ["Shakespeare", "Molière", "Chekhov", "Ibsen"]},
    {"q": "What is 'blocking' in theater?", "a": "Planning actor movements", "options": ["Planning actor movements", "Ending a scene", "Setting lights", "Writing dialogue"]},
    {"q": "What color is used for ghost lighting?", "a": "Blue", "options": ["Blue", "Red", "Green", "White"]},
]

# 8ball responses
EIGHT_BALL_RESPONSES = [
    "Yes, definitely!", "Without a doubt!", "Most definitely!", "Yes!", "Absolutely!",
    "No way!", "I don't think so!", "Definitely not!", "No!", "Probably not.",
    "I'm not sure...", "Ask again later!", "I can't predict that!", "Maybe...",
    "Signs point to yes!", "Reply hazy, try again!", "Better not tell you now.",
]

# Word bank for guess the word game
WORD_LIST = ["THESPACTOR", "PRODUCTION", "AUDITION", "SCRIPTS", "CURTAIN", 
             "ORCHESTRA", "SCENERY", "COSTUME", "REHEARSAL", "DIRECTOR",
             "STAGEHAND", "LIGHTING", "SOUNDEFFECT", "MAKEUP", "PROPS",
             "BACKSTAGE", "GREENROOM", "DRESSREHEARSAL", "OPENINGNIGHT", "FINALE"]


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
        
        # Add role to user command (moderation)
        @self.tree.command(name="addrole", description="Add a role to a user (staff only)")
        @app_commands.describe(user="User to give role to", role="Role to give")
        async def addrole_command(interaction: discord.Interaction, user: discord.Member, role: str):
            # Check if user has moderation permissions
            mod_roles = ["Admin", "Moderator", "Director", "Stage Manager"]
            user_roles = [r.name for r in interaction.user.roles]
            has_mod = any(mod_role in user_roles for mod_role in mod_roles)
            
            if not has_mod:
                # Regular users can still self-assign certain roles
                valid_self_roles = ["Actor", "Crew Member", "Guest"]
                if user.id != interaction.user.id:
                    await interaction.response.send_message("❌ You can only add roles to yourself.", ephemeral=True)
                    return
                role_obj = discord.utils.get(interaction.guild.roles, name=role)
                if role not in valid_self_roles or not role_obj:
                    await interaction.response.send_message(
                        f"❌ Invalid role. Available: {', '.join(valid_self_roles)}", 
                        ephemeral=True
                    )
                    return
            else:
                role_obj = discord.utils.get(interaction.guild.roles, name=role)
                if not role_obj:
                    await interaction.response.send_message(f"❌ Role '{role}' not found.", ephemeral=True)
                    return
            
            try:
                await user.add_roles(role_obj)
                await interaction.response.send_message(f"✅ Added {role} role to {user.name}!")
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed: {str(e)}", ephemeral=True)
        
        # ======== GAMES & CURRENCY COMMANDS ========
        
        # Balance command
        @self.tree.command(name="balance", description="Check your Thespian Coins balance")
        @app_commands.describe(user="User to check (optional)")
        async def balance_command(interaction: discord.Interaction, user: discord.Member = None):
            target_user = user or interaction.user
            balance = get_balance(target_user.id)
            await interaction.response.send_message(f"💰 {target_user.name} has **{balance}** Thespian Coins!")
        
        # Daily reward command
        @self.tree.command(name="daily", description="Claim your daily Thespian Coins reward")
        async def daily_command(interaction: discord.Interaction):
            user_id = str(interaction.user.id)
            coins = load_coins()
            
            # Check if already claimed today
            last_claim = coins.get(f"{user_id}_daily")
            today = datetime.now().strftime("%Y-%m-%d")
            
            if last_claim == today:
                await interaction.response.send_message("❌ You already claimed your daily reward today! Come back tomorrow.", ephemeral=True)
                return
            
            # Add daily coins
            new_balance = add_coins(interaction.user.id, COINS_DAILY)
            coins = load_coins()
            coins[f"{user_id}_daily"] = today
            save_coins(coins)
            
            await interaction.response.send_message(f"✅ You claimed **{COINS_DAILY}** Thespian Coins! Your balance: **{new_balance}**")
        
        # Guess the word game
        @self.tree.command(name="guess", description="Play a word guessing game (costs 20 coins)")
        @app_commands.describe(guess="Your guess")
        async def guess_command(interaction: discord.Interaction, guess: str):
            if not remove_coins(interaction.user.id, 20):
                await interaction.response.send_message("❌ You need 20 Thespian Coins to play!", ephemeral=True)
                return
            
            target_word = random.choice(WORD_LIST)
            guess_upper = guess.upper()
            
            if guess_upper == target_word:
                new_balance = add_coins(interaction.user.id, COINS_GUESS_WIN)
                await interaction.response.send_message(f"🎉 **CORRECT!** The word was **{target_word}**! You won **{COINS_GUESS_WIN}** coins! Balance: **{new_balance}**")
            else:
                # Show hint
                hint = ""
                for i, char in enumerate(target_word):
                    if i < len(guess_upper) and char == guess_upper[i]:
                        hint += char
                    else:
                        hint += "_"
                new_balance = add_coins(interaction.user.id, COINS_GUESS_LOSE)
                await interaction.response.send_message(f"❌ Wrong! The word was not **{guess_upper}**. Hint: `{' '.join(list(target_word))}`\nYou got **{COINS_GUESS_LOSE}** coins for trying. Balance: **{new_balance}**")
        
        # Trivia command
        @self.tree.command(name="trivia", description="Answer a theater trivia question")
        @app_commands.describe(answer="Your answer (just the number 1-4)")
        async def trivia_command(interaction: discord.Interaction, answer: int):
            if answer < 1 or answer > 4:
                await interaction.response.send_message("❌ Please choose a number 1-4!", ephemeral=True)
                return
            
            if not remove_coins(interaction.user.id, 25):
                await interaction.response.send_message("❌ You need 25 Thespian Coins to play!", ephemeral=True)
                return
            
            question = random.choice(TRIVIA_QUESTIONS)
            correct_idx = question["options"].index(question["a"]) + 1
            
            options_text = "\n".join([f"{i}. {opt}" for i, opt in enumerate(question["options"], 1)])
            
            if answer == correct_idx:
                new_balance = add_coins(interaction.user.id, COINS_TRIVIA_WIN)
                await interaction.response.send_message(f"🎉 **CORRECT!** The answer was **{question['a']}**!\nYou won **{COINS_TRIVIA_WIN}** coins! Balance: **{new_balance}**")
            else:
                new_balance = add_coins(interaction.user.id, COINS_TRIVIA_LOSE)
                await interaction.response.send_message(f"❌ Wrong! The correct answer was **{question['a']}**.\n{options_text}\nYou got **{COINS_TRIVIA_LOSE}** coins for trying. Balance: **{new_balance}**")
        
        # 8ball command
        @self.tree.command(name="8ball", description="Ask the magic 8ball a question")
        @app_commands.describe(question="Your question")
        async def eightball_command(interaction: discord.Interaction, question: str):
            if not remove_coins(interaction.user.id, COINS_8BALL_COST):
                await interaction.response.send_message(f"❌ You need {COINS_8BALL_COST} Thespian Coins to ask the 8ball!", ephemeral=True)
                return
            
            response = random.choice(EIGHT_BALL_RESPONSES)
            new_balance = add_coins(interaction.user.id, 5)  # Get 5 coins back
            
            embed = discord.Embed(title="🎱 Magic 8ball", color=discord.Color.purple())
            embed.add_field(name="Question", value=question, inline=False)
            embed.add_field(name="Answer", value=response, inline=False)
            embed.set_footer(text=f"Cost: {COINS_8BALL_COST} coins | You got 5 back | Balance: {new_balance}")
            
            await interaction.response.send_message(embed=embed)
        
        # Leaderboard command
        @self.tree.command(name="leaderboard", description="Show top Thespian Coin holders")
        async def leaderboard_command(interaction: discord.Interaction):
            coins = load_coins()
            
            # Filter out daily claim keys
            balances = {k: v for k, v in coins.items() if not k.endswith("_daily")}
            
            if not balances:
                await interaction.response.send_message("No one has any coins yet!", ephemeral=True)
                return
            
            sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:10]
            
            leaderboard_text = "🏆 **Top Thespian Coin Holders**\n\n"
            for i, (user_id, balance) in enumerate(sorted_balances, 1):
                user = self.get_user(int(user_id))
                name = user.name if user else f"User {user_id}"
                leaderboard_text += f"{i}. {name}: **{balance}** coins\n"
            
            await interaction.response.send_message(leaderboard_text)
        
        # Give coins command
        @self.tree.command(name="give", description="Give coins to another user")
        @app_commands.describe(user="User to give coins to", amount="Amount of coins")
        async def give_command(interaction: discord.Interaction, user: discord.Member, amount: int):
            if amount < 1:
                await interaction.response.send_message("❌ Amount must be at least 1!", ephemeral=True)
                return
            
            if not remove_coins(interaction.user.id, amount):
                await interaction.response.send_message(f"❌ You don't have enough coins! Balance: {get_balance(interaction.user.id)}", ephemeral=True)
                return
            
            add_coins(user.id, amount)
            await interaction.response.send_message(f"✅ You gave **{amount}** Thespian Coins to {user.name}!")
        
        # Add coins (mod only)
        @self.tree.command(name="addcoins", description="Add coins to a user (staff only)")
        @app_commands.describe(user="User to give coins", amount="Amount of coins")
        async def addcoins_command(interaction: discord.Interaction, user: discord.Member, amount: int):
            mod_roles = ["Admin", "Moderator", "Director", "Stage Manager"]
            user_roles = [r.name for r in interaction.user.roles]
            has_mod = any(mod_role in user_roles for mod_role in mod_roles)
            
            if not has_mod:
                await interaction.response.send_message("❌ Only staff can use this command!", ephemeral=True)
                return
            
            if amount < 1:
                await interaction.response.send_message("❌ Amount must be at least 1!", ephemeral=True)
                return
            
            new_balance = add_coins(user.id, amount)
            await interaction.response.send_message(f"✅ Added **{amount}** coins to {user.name}. New balance: **{new_balance}**")
        
        # Remove coins (mod only)
        @self.tree.command(name="removecoins", description="Remove coins from a user (staff only)")
        @app_commands.describe(user="User to remove coins from", amount="Amount of coins")
        async def removecoins_command(interaction: discord.Interaction, user: discord.Member, amount: int):
            mod_roles = ["Admin", "Moderator", "Director", "Stage Manager"]
            user_roles = [r.name for r in interaction.user.roles]
            has_mod = any(mod_role in user_roles for mod_role in mod_roles)
            
            if not has_mod:
                await interaction.response.send_message("❌ Only staff can use this command!", ephemeral=True)
                return
            
            if amount < 1:
                await interaction.response.send_message("❌ Amount must be at least 1!", ephemeral=True)
                return
            
            if not remove_coins(user.id, amount):
                await interaction.response.send_message(f"❌ User doesn't have enough coins!", ephemeral=True)
                return
            
            await interaction.response.send_message(f"✅ Removed **{amount}** coins from {user.name}. New balance: **{get_balance(user.id)}**")
        
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
