import discord
import dotenv
import os
import re

dotenv.load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
COUNTING_CHANNEL_ID = int(os.getenv("COUNTING_CHANNEL_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

intents = discord.Intents().all()
bot = discord.Client(intents=intents)

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


bot.run(TOKEN)
