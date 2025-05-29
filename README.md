# 🎫 Discord Ticket Bot

A professional Discord ticket system bot built with Python and discord.py. This bot provides a comprehensive ticket management solution for Discord servers with features like automatic transcripts, rate limiting, and flexible configuration.

## ✨ Features

### Core Functionality
- 🎫 **Multiple Ticket Types** - Support and Partnership tickets with customizable categories
- 🔒 **Smart Permissions** - Automatic channel permissions for ticket creators and staff
- 📄 **Automatic Transcripts** - Complete conversation logs saved when tickets are closed
- ⏰ **Rate Limiting** - Prevents spam and abuse with configurable cooldowns
- 🔄 **Persistent Storage** - Tickets survive bot restarts and maintain functionality
- 📊 **Statistics Dashboard** - Track ticket metrics and usage patterns

### Advanced Features
- 🚀 **Hot Reload** - Restores ticket functionality after bot restarts
- 🔧 **Flexible Configuration** - JSON config file or environment variables
- 📝 **Custom Close Reasons** - Staff can provide reasons when closing tickets
- 👥 **User Management** - Add users to existing tickets
- 📁 **Ticket Transfer** - Move tickets between categories
- 🛡️ **Permission Checks** - Role-based access control for all features

### User Experience
- 🎨 **Modern UI** - Clean embeds and intuitive button interactions
- ⚡ **Instant Feedback** - Real-time confirmations and error messages
- 🔔 **Smart Notifications** - DM notifications for ticket closures
- 📱 **Mobile Friendly** - Works seamlessly on all Discord clients

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- A Discord server with appropriate permissions

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/1-Tawsif-1/tickets.py.git
   cd tickets.py
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   
   Choose one of the following methods:

   **Method 1: Using config.json (Recommended)**
   ```bash
   cp config.json.template config.json
   # Edit config.json with your settings
   ```

   **Method 2: Using environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### config.json Structure
```json
{
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  "staff_role_id": 123456789012345678,
  "unlimited_tickets_role_id": 123456789012345678,
  "ticket_channel_id": 123456789012345678,
  "transcripts_channel_id": 123456789012345678,
  "categories": {
    "support": 123456789012345678,
    "partnership": 123456789012345678,
    "transfer": 123456789012345678
  },
  "settings": {
    "rate_limit_seconds": 10,
    "max_tickets_per_user": 1
  }
}
```

### Configuration Options

| Option | Description | Required |
|--------|-------------|----------|
| `bot_token` | Your Discord bot token | ✅ |
| `staff_role_id` | Role ID that can manage all tickets | ✅ |
| `unlimited_tickets_role_id` | Role ID that can create unlimited tickets | ✅ |
| `ticket_channel_id` | Channel where the ticket creation embed is posted | ✅ |
| `transcripts_channel_id` | Channel where ticket transcripts are saved | ✅ |
| `categories.support` | Category ID for support tickets | ✅ |
| `categories.partnership` | Category ID for partnership tickets | ✅ |
| `categories.transfer` | Category ID for transferred tickets | ✅ |
| `settings.rate_limit_seconds` | Cooldown between user interactions | ❌ |
| `settings.max_tickets_per_user` | Max open tickets per user | ❌ |

## 🎮 Commands

### Administrator Commands
- `!setup_tickets` - Create the ticket system embed in the current channel
  - **Permission Required:** Administrator

### Staff Commands  
- `!add_user <@user>` - Add a user to the current ticket
  - **Permission Required:** Staff role
  - **Usage:** `!add_user @JohnDoe`

- `!transfer_ticket` - Move current ticket to transfer category
  - **Permission Required:** Staff role

- `!ticket_stats` - View ticket statistics
  - **Permission Required:** Staff role

## 🎯 Usage Guide

### For Users
1. Go to the designated ticket channel
2. Click the dropdown menu in the ticket system embed
3. Select your ticket type (Support or Partnership)
4. Your private ticket channel will be created automatically
5. Discuss your issue with the staff team
6. Staff will close the ticket when resolved

### For Staff
1. **Managing Tickets:**
   - View all tickets (automatic access via staff role)
   - Close tickets using the "Close Ticket" button
   - Add close reasons using "Close with Reason"
   - Add users to tickets with `!add_user @username`

2. **Organization:**
   - Transfer tickets between categories with `!transfer_ticket`
   - View server statistics with `!ticket_stats`

3. **Transcripts:**
   - Automatically generated when tickets close
   - Saved to the designated transcripts channel
   - Include complete conversation history with timestamps

## 🔧 Bot Permissions

Your bot needs the following permissions:

### Essential Permissions
- ✅ **Read Messages** - View channel content
- ✅ **Send Messages** - Send responses  
- ✅ **Manage Channels** - Create/delete ticket channels
- ✅ **Manage Roles** - Set channel permissions
- ✅ **Embed Links** - Send rich embed messages
- ✅ **Attach Files** - Send transcript files
- ✅ **Read Message History** - Generate transcripts

### Recommended Permissions
- ✅ **Manage Messages** - Clean up channels if needed
- ✅ **Use External Emojis** - Enhanced visual experience

## 📁 Project Structure

```
tickets.py/
├── main.py                 # Main bot file
├── config.json.template    # Configuration template
├── .env.template          # Environment variables template
├── requirements.txt       # Python dependencies
├── data/                  # Data storage directory
│   └── tickets.json      # Ticket persistence file
├── bot.log               # Application logs
└── README.md             # This file
```

## 🔒 Security Features

- **Rate Limiting** - Prevents spam and abuse
- **Permission Validation** - Ensures only authorized users can perform actions
- **Data Persistence** - Ticket data stored securely in JSON format
- **Comprehensive Logging** - Full audit trail of all ticket operations
- **Error Handling** - Graceful failure handling with user-friendly messages

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond to commands**
- Verify bot token is correct
- Check bot has necessary permissions
- Ensure bot is online and in your server

**Tickets not creating**
- Verify category IDs are correct
- Check bot has "Manage Channels" permission
- Ensure categories exist and bot can access them

**Transcripts not saving**
- Verify transcript channel ID is correct
- Check bot has "Attach Files" permission
- Ensure the data directory exists

**Permissions errors**
- Verify all role IDs in configuration
- Check bot's role hierarchy
- Ensure bot has "Manage Roles" permission

### Debug Mode
Enable detailed logging by modifying the logging level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

## 📋 Roadmap

- [ ] **Web Dashboard** - Browser-based ticket management
- [ ] **Ticket Templates** - Pre-defined ticket formats
- [ ] **Auto-Close** - Automatically close inactive tickets
- [ ] **Ticket Priorities** - High/Medium/Low priority system
- [ ] **Staff Notifications** - Ping staff for new tickets
- [ ] **Ticket Categories** - More granular categorization
- [ ] **Analytics Dashboard** - Advanced reporting features
- [ ] **Multi-Language** - Support for multiple languages

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

Need help? Here are your options:

- 📖 **Documentation** - Check this README and code comments
- 🐛 **Bug Reports** - Open an issue on GitHub
- 💡 **Feature Requests** - Open an issue with the "enhancement" label
- 💬 **Questions** - Open a discussion on GitHub
- 🎮 **Discord Community** - Join our [Support Server](https://discord.gg/D69gBuqs) for live help

## 👨‍💻 About the Developer

This Discord Ticket Bot is developed and maintained by **1-Tawsif-1**.

- 🐙 **GitHub:** [@1-Tawsif-1](https://github.com/1-Tawsif-1)
- 🎮 **Discord Server:** [Join Our Community](https://discord.gg/D69gBuqs)

Feel free to join our Discord server for:
- Live support and assistance
- Feature discussions and suggestions
- Community feedback and beta testing
- Direct communication with the developer
- Networking with other bot developers

## 🙏 Acknowledgments

- Built with [discord.py](https://discordpy.readthedocs.io/) - The Python Discord API wrapper
- Inspired by the Discord community's need for better ticket systems
- Thanks to all contributors and users for feedback and improvements
- Special thanks to the community members in our Discord server for continuous testing and feedback

---

<div align="center">

**Made with ❤️ for the Discord community by Tawsif**

[⭐ Star this repo](https://github.com/1-Tawsif-1/tickets.py) • [🐛 Report Bug](https://github.com/1-Tawsif-1/tickets.py/issues) • [💡 Request Feature](https://github.com/1-Tawsif-1/tickets.py/issues) • [💬 Join Discord](https://discord.gg/D69gBuqs)

</div>
