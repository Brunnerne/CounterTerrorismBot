from collections import defaultdict
import discord
import dotenv
import os
import re

dotenv.load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
COUNTING_CHANNEL_ID = int(os.getenv("COUNTING_CHANNEL_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

intents = discord.Intents().all()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

bot_deletions = []


def sanitize(msg):
    prefix = ""
    if "`" in msg:
        prefix = " (contained backticks, stripped below)"
    prefix += ":\n```"

    msg = msg.replace("`", "")
    if len(msg) > 100:
        msg = msg[:100] + "... [TRUNCATED]"

    return f"{prefix}\n{msg}\n```"


async def aenumerate(asequence):
    n = 0
    async for elem in asequence:
        yield n, elem
        n += 1


@tree.command(name="counters", description="Counting statistics", guild=discord.Object(id=GUILD_ID))
async def stats(interaction: discord.Interaction):
    # Respond immediately and send stats as normal message later
    # (Discord has 3 second response limit)
    await interaction.response.send_message("Collecting stats...")

    counting_channel = bot.get_channel(COUNTING_CHANNEL_ID)
    messages = counting_channel.history(limit=None, oldest_first=True)
    counts = defaultdict(int)
    async for i, msg in aenumerate(messages):
        # Skip rules message
        if i == 0:
            continue
        counts[msg.author] += 1

    response = "```\n"
    response += "=" * 20 + "\n     STATISTICS\n" + "=" * 20 + "\n"
    for author, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        response += f"{author.display_name}: {count}\n"
    response += "```"

    await interaction.channel.send(response)


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.channel.id != COUNTING_CHANNEL_ID:
        return

    previous = [msg async for msg in message.channel.history(limit=2)][1]

    has_error = False
    if len(message.attachments) > 0:
        error = "a message with an attachment (not re-posted here)"
        has_error = True
    elif re.fullmatch(r"\d+", message.content, flags=re.ASCII) is None:
        error = "a non-decimal message"
        has_error = True
    elif int(message.content) != int(previous.content) + 1:
        error = "the wrong next number"
        has_error = True
    elif message.author == previous.author:
        error = "two messages in a row"
        has_error = True

    if has_error:
        msg = sanitize(message.content)
        try:
            await bot.get_channel(LOG_CHANNEL_ID).send(
                f""":bell: SHAME, SHAME, SHAME :bell:
[<#{COUNTING_CHANNEL_ID}>] <@{message.author.id}> posted {error}{msg}
"""
            )
        except:
            await bot.get_channel(LOG_CHANNEL_ID).send(
                "I don't know what you just did, but you caused an exception :("
            )
        finally:
            bot_deletions.append(message.id)
            await message.delete()
        return


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.channel.id != COUNTING_CHANNEL_ID:
        return

    message = sanitize(f"{before.content} -> {after.content}")
    await bot.get_channel(LOG_CHANNEL_ID).send(
        f""":bell: SHAME, SHAME, SHAME :bell:
[<#{COUNTING_CHANNEL_ID}>] <@{before.author.id}> edited their message{message}
"""
    )


@bot.event
async def on_message_delete(message: discord.Message):
    if message.channel.id != COUNTING_CHANNEL_ID or message.id in bot_deletions:
        return

    await bot.get_channel(LOG_CHANNEL_ID).send(
        f""":bell: SHAME, SHAME, SHAME :bell:
[<#{COUNTING_CHANNEL_ID}>] A message by <@{message.author.id}> was deleted{sanitize(message.content)}"""
    )


@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Ready!")


bot.run(TOKEN)
