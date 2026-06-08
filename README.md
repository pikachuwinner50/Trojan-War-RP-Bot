# Trojan War RP Bot

A Discord roleplay bot for running a Trojan War campaign where each player controls their own nation.

## Current Gameplay

This build follows the shared design doc's settlement and turn structure:

- Each Discord player can claim one nation from the Google Doc nations tab.
- Every nation starts as a blank Tier 1 Village with 2 free-choice building slots.
- Buildings are queued during the turn instead of applying instantly.
- `/turn end` runs passive generation first, then processes queued construction.
- Pending resources are reserved so players cannot double-spend them during a turn.

## Setup

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

## Commands

Player setup:

- `/nation claim culture:Achaeans nation:Sparta`
- `/nation mine`
- `/nation list`

Settlement:

- `/settlement view`
- `/settlement view nation:Sparta`
- `/settlement buildings`

`/settlement view` opens a button UI with Overview, Settlements, Military, Resources, and Religion pages. Nations currently begin with one settlement: their capital.

The Military page shows recruitment buildings and unlocked unit types. The Religion page shows Cult Center status, favor capacity, Olympian preferred offerings, blessings, and Hubris modifiers.

Building queue:

- `/build queue building:farms`
- `/build queue building:citadel`
- `/turn queue`

GM turn resolution:

- `/turn end`

Moderator tools:

- `/admin reset_claims`
- `/admin unclaim nation:Sparta`
- `/admin missing_capitals`

Moderator-only commands require Manage Server, Manage Messages, or Administrator.
