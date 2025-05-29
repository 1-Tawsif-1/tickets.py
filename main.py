import discord
from discord.ext import commands
from discord import Embed, SelectOption, ButtonStyle
from discord.ui import View, Button, Select, Modal, TextInput
import io
import json
import os
import time
import logging
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    """Configuration class to manage bot settings"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from config.json or environment variables"""
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                
            self.TOKEN = config.get('bot_token') or os.getenv('DISCORD_BOT_TOKEN')
            self.STAFF_ROLE_ID = config.get('staff_role_id')
            self.UNLIMITED_TICKETS_ROLE_ID = config.get('unlimited_tickets_role_id')
            self.TICKET_CHANNEL_ID = config.get('ticket_channel_id')
            self.TRANSCRIPTS_CHANNEL_ID = config.get('transcripts_channel_id')
            
            # Category IDs
            categories = config.get('categories', {})
            self.SUPPORT_CAT = categories.get('support')
            self.PARTNERSHIP_CAT = categories.get('partnership')
            self.TRANSFER_CATEGORY_ID = categories.get('transfer')
            
            # Bot settings
            settings = config.get('settings', {})
            self.RATE_LIMIT_SECONDS = settings.get('rate_limit_seconds', 10)
            self.MAX_TICKETS_PER_USER = settings.get('max_tickets_per_user', 1)
            
        else:
            # Fallback to environment variables
            self.TOKEN = os.getenv('DISCORD_BOT_TOKEN')
            self.STAFF_ROLE_ID = int(os.getenv('STAFF_ROLE_ID', 0))
            self.UNLIMITED_TICKETS_ROLE_ID = int(os.getenv('UNLIMITED_TICKETS_ROLE_ID', 0))
            self.TICKET_CHANNEL_ID = int(os.getenv('TICKET_CHANNEL_ID', 0))
            self.TRANSCRIPTS_CHANNEL_ID = int(os.getenv('TRANSCRIPTS_CHANNEL_ID', 0))
            self.SUPPORT_CAT = int(os.getenv('SUPPORT_CATEGORY_ID', 0))
            self.PARTNERSHIP_CAT = int(os.getenv('PARTNERSHIP_CATEGORY_ID', 0))
            self.TRANSFER_CATEGORY_ID = int(os.getenv('TRANSFER_CATEGORY_ID', 0))
            self.RATE_LIMIT_SECONDS = int(os.getenv('RATE_LIMIT_SECONDS', 10))
            self.MAX_TICKETS_PER_USER = int(os.getenv('MAX_TICKETS_PER_USER', 1))

# Initialize configuration
config = Config()

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Constants
TICKET_DATA_FILE = 'data/tickets.json'
TICKET_TYPES = {
    'support': {
        'label': 'Support',
        'description': 'Get help with technical issues or general questions',
        'emoji': '🛠️',
        'category_id': config.SUPPORT_CAT,
        'embed_title': 'Support Ticket',
        'embed_description': 'Thank you for creating a support ticket. Our team will assist you shortly.'
    },
    'partnership': {
        'label': 'Partnership',
        'description': 'Discuss partnership opportunities',
        'emoji': '🤝',
        'category_id': config.PARTNERSHIP_CAT,
        'embed_title': 'Partnership Inquiry',
        'embed_description': 'Thank you for your interest in partnering with us. Please provide all necessary details.'
    }
}

# Rate limiting
user_interaction_time = {}

class TicketManager:
    """Manages ticket data persistence"""
    
    @staticmethod
    def ensure_data_directory():
        """Ensure the data directory exists"""
        os.makedirs('data', exist_ok=True)
    
    @staticmethod
    def load_ticket_data():
        """Load ticket data from JSON file"""
        TicketManager.ensure_data_directory()
        if os.path.exists(TICKET_DATA_FILE):
            try:
                with open(TICKET_DATA_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("Could not load ticket data, starting fresh")
                return []
        return []
    
    @staticmethod
    def save_ticket_data(data):
        """Save ticket data to JSON file"""
        TicketManager.ensure_data_directory()
        try:
            with open(TICKET_DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save ticket data: {e}")
    
    @staticmethod
    def save_ticket(channel_id: int, user_id: int, category_id: int, ticket_type: str):
        """Save new ticket information"""
        tickets = TicketManager.load_ticket_data()
        ticket_data = {
            "channel_id": channel_id,
            "user_id": user_id,
            "category_id": category_id,
            "ticket_type": ticket_type,
            "created_at": datetime.now().isoformat(),
            "status": "open"
        }
        tickets.append(ticket_data)
        TicketManager.save_ticket_data(tickets)
        logger.info(f"Saved ticket: {channel_id} for user {user_id}")
    
    @staticmethod
    def update_ticket_category(channel_id: int, new_category_id: int):
        """Update ticket category in data"""
        tickets = TicketManager.load_ticket_data()
        for ticket in tickets:
            if ticket["channel_id"] == channel_id:
                ticket["category_id"] = new_category_id
                break
        TicketManager.save_ticket_data(tickets)
    
    @staticmethod
    def close_ticket(channel_id: int):
        """Mark ticket as closed in data"""
        tickets = TicketManager.load_ticket_data()
        for ticket in tickets:
            if ticket["channel_id"] == channel_id:
                ticket["status"] = "closed"
                ticket["closed_at"] = datetime.now().isoformat()
                break
        TicketManager.save_ticket_data(tickets)

class RateLimiter:
    """Handle rate limiting for user interactions"""
    
    @staticmethod
    def is_rate_limited(user_id: int) -> bool:
        """Check if user is rate limited"""
        if user_id in user_interaction_time:
            return time.time() - user_interaction_time[user_id] < config.RATE_LIMIT_SECONDS
        return False
    
    @staticmethod
    def update_last_interaction(user_id: int):
        """Update user's last interaction time"""
        user_interaction_time[user_id] = time.time()

class TicketSelect(Select):
    """Dropdown menu for selecting ticket type"""
    
    def __init__(self):
        options = [
            SelectOption(
                label=ticket_info['label'],
                description=ticket_info['description'],
                emoji=ticket_info['emoji'],
                value=ticket_type
            )
            for ticket_type, ticket_info in TICKET_TYPES.items()
        ]
        super().__init__(
            placeholder="Choose your ticket type...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        """Handle ticket type selection"""
        author = interaction.user
        guild = interaction.guild
        ticket_type = self.values[0]
        
        # Rate limiting check
        if RateLimiter.is_rate_limited(author.id):
            await interaction.response.send_message(
                "⏰ You're doing that too frequently. Please wait a moment.",
                ephemeral=True
            )
            return
        
        RateLimiter.update_last_interaction(author.id)
        
        # Check existing tickets (unless user has unlimited tickets role)
        if config.UNLIMITED_TICKETS_ROLE_ID not in [role.id for role in author.roles]:
            existing_tickets = 0
            for channel in guild.text_channels:
                if channel.topic == str(author.id):
                    existing_tickets += 1
            
            if existing_tickets >= config.MAX_TICKETS_PER_USER:
                await interaction.response.send_message(
                    f"❌ You already have {existing_tickets} open ticket(s)! Please close your existing ticket(s) before creating a new one.",
                    ephemeral=True
                )
                return
        
        # Get ticket configuration
        ticket_info = TICKET_TYPES[ticket_type]
        category = guild.get_channel(ticket_info['category_id'])
        
        if not category:
            await interaction.response.send_message(
                "❌ Ticket category not found. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        # Create ticket channel
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                author: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),
                guild.get_role(config.STAFF_ROLE_ID): discord.PermissionOverwrite(view_channel=True)
            }
            
            ticket_channel = await category.create_text_channel(
                name=f"ticket-{ticket_type}-{author.name}",
                topic=str(author.id),
                overwrites=overwrites
            )
            
            # Save ticket data
            TicketManager.save_ticket(ticket_channel.id, author.id, category.id, ticket_type)
            
            # Create ticket embed
            embed = Embed(
                title=ticket_info['embed_title'],
                description=ticket_info['embed_description'],
                color=discord.Color.blue()
            )
            embed.add_field(name="Created by", value=author.mention, inline=True)
            embed.add_field(name="Created at", value=f"<t:{int(time.time())}:F>", inline=True)
            embed.set_footer(text=f"Ticket ID: {ticket_channel.id}")
            
            ticket_view = TicketActionButtons()
            await ticket_channel.send(embed=embed, view=ticket_view)
            
            await interaction.response.send_message(
                f"✅ Your {ticket_info['label'].lower()} ticket has been created: {ticket_channel.mention}",
                ephemeral=True
            )
            
            logger.info(f"Created {ticket_type} ticket for {author} ({author.id})")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to create channels in that category.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while creating your ticket. Please try again.",
                ephemeral=True
            )

class TicketView(View):
    """Main ticket creation view"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketActionButtons(View):
    """Action buttons for ticket management"""
    
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        """Close ticket button"""
        if RateLimiter.is_rate_limited(interaction.user.id):
            await interaction.response.send_message(
                "⏰ You're doing that too frequently. Please wait a moment.",
                ephemeral=True
            )
            return
        
        # Check if user has permission to close ticket
        if not self._can_close_ticket(interaction):
            await interaction.response.send_message(
                "❌ You don't have permission to close this ticket.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            "⚠️ Are you sure you want to close this ticket? This action cannot be undone.",
            view=ConfirmCloseView(),
            ephemeral=True
        )

    @discord.ui.button(label="Close with Reason", style=ButtonStyle.secondary, emoji="📝")
    async def close_with_reason(self, interaction: discord.Interaction, button: Button):
        """Close ticket with reason button"""
        if RateLimiter.is_rate_limited(interaction.user.id):
            await interaction.response.send_message(
                "⏰ You're doing that too frequently. Please wait a moment.",
                ephemeral=True
            )
            return
        
        if not self._can_close_ticket(interaction):
            await interaction.response.send_message(
                "❌ You don't have permission to close this ticket.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_modal(CloseWithReasonModal())
    
    def _can_close_ticket(self, interaction: discord.Interaction) -> bool:
        """Check if user can close the ticket"""
        channel = interaction.channel
        # Channel owner or staff can close
        return (str(interaction.user.id) == channel.topic or 
                config.STAFF_ROLE_ID in [role.id for role in interaction.user.roles])

class ConfirmCloseView(View):
    """Confirmation view for closing tickets"""
    
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Confirm Close", style=ButtonStyle.danger, emoji="✅")
    async def confirm_close(self, interaction: discord.Interaction, button: Button):
        """Confirm ticket closure"""
        await self._close_ticket(interaction)

    async def _close_ticket(self, interaction: discord.Interaction, reason: str = "No reason specified"):
        """Close the ticket"""
        channel = interaction.channel
        user_id = channel.topic
        
        try:
            author = channel.guild.get_member(int(user_id))
        except (ValueError, TypeError):
            author = None
        
        # Generate transcript
        await TranscriptGenerator.generate_transcript(channel)
        
        # Create closure embed
        embed = Embed(
            title="🔒 Ticket Closed",
            description="This ticket has been closed.",
            color=discord.Color.red()
        )
        embed.add_field(name="Ticket ID", value=str(channel.id), inline=False)
        embed.add_field(name="Opened By", value=author.mention if author else "Unknown User", inline=True)
        embed.add_field(name="Closed By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Created", value=f"<t:{int(channel.created_at.timestamp())}:F>", inline=False)
        embed.add_field(name="Category", value=channel.category.name if channel.category else "Unknown", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        
        # Send closure notification to ticket owner
        if author:
            try:
                await author.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Could not send closure DM to {author}")
        
        # Update ticket data
        TicketManager.close_ticket(channel.id)
        
        await interaction.response.send_message("🔒 Ticket will be deleted in 5 seconds...", ephemeral=True)
        
        # Delete channel after delay
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        await channel.delete(reason=f"Ticket closed by {interaction.user}")
        
        logger.info(f"Closed ticket {channel.id} by {interaction.user}")

class CloseWithReasonModal(Modal, title="Close Ticket with Reason"):
    """Modal for closing ticket with custom reason"""
    
    reason = TextInput(
        label="Reason for closing",
        style=discord.TextStyle.paragraph,
        placeholder="Enter the reason for closing this ticket...",
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Handle reason submission"""
        view = ConfirmCloseView()
        await view._close_ticket(interaction, self.reason.value)

class TranscriptGenerator:
    """Handle transcript generation"""
    
    @staticmethod
    async def generate_transcript(channel):
        """Generate and save transcript"""
        transcript_channel = channel.guild.get_channel(config.TRANSCRIPTS_CHANNEL_ID)
        
        if not transcript_channel:
            logger.warning("Transcript channel not found")
            return
        
        try:
            transcript = io.StringIO()
            message_count = 0
            
            async for message in channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                content = message.content or "[No content]"
                
                # Handle embeds
                if message.embeds:
                    embed_info = " [Contains embeds]"
                else:
                    embed_info = ""
                
                # Handle attachments
                if message.attachments:
                    attachment_info = f" [Attachments: {', '.join(att.filename for att in message.attachments)}]"
                else:
                    attachment_info = ""
                
                transcript.write(f"[{timestamp}] {message.author}: {content}{embed_info}{attachment_info}\n")
                message_count += 1
            
            # Create transcript embed
            embed = Embed(
                title="📄 Ticket Transcript",
                description=f"Transcript for **{channel.name}**",
                color=discord.Color.blue()
            )
            embed.add_field(name="Messages", value=str(message_count), inline=True)
            embed.add_field(name="Channel ID", value=str(channel.id), inline=True)
            embed.add_field(name="Category", value=channel.category.name if channel.category else "Unknown", inline=True)
            embed.timestamp = datetime.now()
            
            # Create file
            transcript.seek(0)
            transcript_file = discord.File(
                fp=io.BytesIO(transcript.getvalue().encode('utf-8')),
                filename=f"transcript-{channel.name}-{int(time.time())}.txt"
            )
            
            await transcript_channel.send(embed=embed, file=transcript_file)
            logger.info(f"Generated transcript for {channel.name}")
            
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")

async def restore_tickets():
    """Restore ticket functionality after bot restart"""
    tickets = TicketManager.load_ticket_data()
    restored_count = 0
    
    for ticket in tickets:
        if ticket.get("status") != "open":
            continue
            
        channel_id = ticket['channel_id']
        user_id = ticket['user_id']
        category_id = ticket['category_id']
        
        for guild in bot.guilds:
            channel = guild.get_channel(channel_id)
            if not channel:
                continue
                
            author = guild.get_member(user_id)
            category = guild.get_channel(category_id)

            if not author or not category:
                continue

            # Restore permissions
            try:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    author: discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True
                    ),
                    guild.get_role(config.STAFF_ROLE_ID): discord.PermissionOverwrite(view_channel=True)
                }
                await channel.edit(overwrites=overwrites)

                # Restore action buttons
                async for message in channel.history(limit=50):
                    if (message.author == bot.user and 
                        message.embeds and 
                        any(keyword in message.embeds[0].title.lower() 
                            for keyword in ['ticket', 'support', 'partnership'])):
                        
                        ticket_view = TicketActionButtons()
                        await message.edit(view=ticket_view)
                        restored_count += 1
                        break

                logger.info(f"Restored ticket channel: {channel.name}")
                
            except Exception as e:
                logger.error(f"Error restoring ticket {channel_id}: {e}")
    
    if restored_count > 0:
        logger.info(f"Restored {restored_count} ticket channels")

@bot.event
async def on_ready():
    """Bot ready event"""
    logger.info(f'🤖 Bot is online as {bot.user}!')
    logger.info(f'📊 Connected to {len(bot.guilds)} guild(s)')
    
    # Restore tickets
    await restore_tickets()
    
    # Update ticket setup message
    await update_ticket_message()
    
    logger.info("✅ Bot initialization complete")

async def update_ticket_message():
    """Update existing ticket setup message"""
    channel = bot.get_channel(config.TICKET_CHANNEL_ID)
    if not channel:
        logger.warning("Ticket channel not found")
        return
    
    # Look for existing setup message
    async for message in channel.history(limit=50):
        if (message.author == bot.user and 
            message.embeds and 
            "ticket system" in message.embeds[0].title.lower()):
            
            ticket_view = TicketView()
            await message.edit(view=ticket_view)
            logger.info("✅ Restored ticket setup message")
            return
    
    logger.info("No existing ticket setup message found")

@bot.command(name='setup_tickets')
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    """Setup the ticket system embed"""
    embed = Embed(
        title="🎫 Ticket System",
        description="Use the dropdown menu below to create a ticket according to your needs.\n\n**Please note:** Abuse of the ticket system may result in warnings or restrictions.",
        color=discord.Color.green()
    )
    embed.add_field(
        name="📋 Available Ticket Types",
        value="\n".join([f"{info['emoji']} **{info['label']}** - {info['description']}" 
                        for info in TICKET_TYPES.values()]),
        inline=False
    )
    embed.set_footer(text="Select a ticket type from the dropdown below")
    
    await ctx.send(embed=embed, view=TicketView())
    logger.info(f"Ticket system setup by {ctx.author}")

@bot.command(name='add_user')
@commands.has_role(config.STAFF_ROLE_ID)
async def add_user(ctx, member: discord.Member):
    """Add a user to the current ticket"""
    # Check if in ticket channel
    valid_categories = [info['category_id'] for info in TICKET_TYPES.values()] + [config.TRANSFER_CATEGORY_ID]
    
    if not ctx.channel.category or ctx.channel.category.id not in valid_categories:
        await ctx.send("❌ This command can only be used in ticket channels.")
        return
    
    try:
        await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)
        
        embed = Embed(
            title="✅ User Added",
            description=f"{member.mention} has been added to this ticket.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        logger.info(f"{ctx.author} added {member} to ticket {ctx.channel.id}")
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to modify channel permissions.")

@bot.command(name='transfer_ticket')
@commands.has_role(config.STAFF_ROLE_ID)
async def transfer_ticket(ctx):
    """Transfer ticket to different category"""
    # Check if in ticket channel
    valid_categories = [info['category_id'] for info in TICKET_TYPES.values()]
    
    if not ctx.channel.category or ctx.channel.category.id not in valid_categories:
        await ctx.send("❌ This command can only be used in ticket channels.")
        return
    
    target_category = ctx.guild.get_channel(config.TRANSFER_CATEGORY_ID)
    if not target_category:
        await ctx.send("❌ Transfer category not found.")
        return
    
    old_category_name = ctx.channel.category.name
    
    try:
        await ctx.channel.edit(category=target_category)
        TicketManager.update_ticket_category(ctx.channel.id, config.TRANSFER_CATEGORY_ID)
        
        embed = Embed(
            title="📁 Ticket Transferred",
            description=f"Ticket moved from **{old_category_name}** to **{target_category.name}**",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        logger.info(f"Ticket {ctx.channel.id} transferred by {ctx.author}")
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to move this channel.")

@bot.command(name='ticket_stats')
@commands.has_role(config.STAFF_ROLE_ID)
async def ticket_stats(ctx):
    """Show ticket statistics"""
    tickets = TicketManager.load_ticket_data()
    
    total_tickets = len(tickets)
    open_tickets = len([t for t in tickets if t.get('status') == 'open'])
    closed_tickets = total_tickets - open_tickets
    
    # Count by type
    type_counts = {}
    for ticket in tickets:
        ticket_type = ticket.get('ticket_type', 'unknown')
        type_counts[ticket_type] = type_counts.get(ticket_type, 0) + 1
    
    embed = Embed(
        title="📊 Ticket Statistics",
        color=discord.Color.blue()
    )
    embed.add_field(name="Total Tickets", value=str(total_tickets), inline=True)
    embed.add_field(name="Open Tickets", value=str(open_tickets), inline=True)
    embed.add_field(name="Closed Tickets", value=str(closed_tickets), inline=True)
    
    if type_counts:
        type_breakdown = "\n".join([f"{ticket_type.title()}: {count}" 
                                   for ticket_type, count in type_counts.items()])
        embed.add_field(name="By Type", value=type_breakdown, inline=False)
    
    embed.timestamp = datetime.now()
    await ctx.send(embed=embed)

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler"""
    logger.error(f"Error in event {event}: {args}, {kwargs}")

@bot.event  
async def on_command_error(ctx, error):
    """Command error handler"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRole):
        await ctx.send("❌ You don't have the required role to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    else:
        logger.error(f"Command error in {ctx.command}: {error}")
        await ctx.send("❌ An error occurred while executing this command.")

if __name__ == "__main__":
    if not config.TOKEN:
        logger.error("❌ No bot token provided!")
        exit(1)
    
    try:
        bot.run(config.TOKEN)
    except discord.LoginFailure:
        logger.error("❌ Invalid bot token!")
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
