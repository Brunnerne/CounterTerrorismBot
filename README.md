# CounterTerrorismBot

Bot to counter counting-terrorism in the `#Counting` channel.

Monitors a counting channel and ensures:

1. Message is a number following regex `^[0-9]+$`
2. Number is the next in the sequence
3. No two consecutive messages are from the same authors
4. Message has no attachments

Violations and edits are logged and invalid messages deleted. Deletions are also logged but the perpetrator must be dealt with "manually".

Logs contain the violating message in triple-backticks to prevent injections and messages are sanitized before being logged (backticks removed and content truncated to at most 100 characters to avoid other reflection issues).

## Usage

Add a `.env` file with contents:

```env
BOT_TOKEN=<Discord bot token>
GUILD_ID=<Server ID>
COUNTING_CHANNEL_ID=<ID of counting channel to monitor>
LOG_CHANNEL_ID=<ID of channel to log violations in>
```

Install dependencies with `pip install -r requirements.txt` and run bot with `python main.py`.

Use the slash command `/counters` to get counting stats for each participant, sorted by most counts. This command is ignored in the counting channel.
