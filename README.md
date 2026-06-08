# Trojan War RP Bot

A Discord roleplay bot for running a Trojan War campaign where each player controls their own nation.

## Current Gameplay

This build follows the shared design doc's settlement and turn structure:

- Each Discord player can claim one nation from the Google Doc nations tab.
- Every nation starts as a blank Tier 1 Village with 2 free-choice building slots.
- Buildings are queued during the turn instead of applying instantly.
- `/turn end` runs passive generation first, then processes queued construction.
- Pending resources are reserved so players cannot double-spend them during a turn.

## How to Launch

1. Install Python 3.11 or newer.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create `.env` in this folder:

```env
DISCORD_TOKEN=your-reset-bot-token
DISCORD_GUILD_ID=your-server-id
```

4. Start the bot:

```powershell
python -m trojan_bot
```



DISCORD SERVER:
https://discord.gg/pxAZvFzzqZ

Note: This bot belongs to Average Tech-Priest on Discord.
