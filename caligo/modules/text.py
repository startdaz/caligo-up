import base64
import binascii
import random
import unicodedata
from typing import ClassVar
from os import remove

from caligo import command, module


class Text(module.Module):
    name: ClassVar[str] = "Text"

    @command.desc("Unicode character from hex codepoint")
    @command.usage("[hexadecimal Unicode codepoint]")
    async def cmd_uni(self, ctx: command.Context) -> str:
        codepoint = ctx.input
        try:
            return chr(int(codepoint, 16))
        except ValueError:
            return "__Input is out of Unicode's range of__ `0x00000` __to__ `0xFFFFF` __range.__"

    @command.desc("Apply a sarcasm/mocking filter to the given text")
    @command.usage("[text to filter]", reply=True)
    async def cmd_mock(self, ctx: command.Context) -> str:
        text = ctx.input
        if not text and ctx.msg.reply_to_message:
            text = ctx.msg.reply_to_message.text
        elif not text and not ctx.msg.reply_to_message:
            return "__Give me a text or reply to a message.__"

        chars = [*text]
        for idx, ch in enumerate(chars):
            ch = ch.upper() if random.choice((True, False)) else ch.lower()
            chars[idx] = ch

        return "".join(chars)

    @command.desc("Dissect a string into named Unicode codepoints")
    @command.usage("[text to dissect]", reply=True)
    async def cmd_charinfo(self, ctx: command.Context) -> str:
        text = ctx.input
        if not text and ctx.msg.reply_to_message:
            text = ctx.msg.reply_to_message.text
        elif not text and not ctx.msg.reply_to_message:
            return "__Give me a text or reply to a message.__"

        chars = []
        for char in text:
            # Don't preview characters that mess up the output
            preview = char not in "`"

            # Attempt to get the codepoint's name
            try:
                name: str = unicodedata.name(char)
            except ValueError:
                # Control characters don't have names, so insert a placeholder
                # and prevent the character from being rendered to avoid breaking
                # the output
                name = "UNNAMED CONTROL CHARACTER"
                preview = False

            # Render the line and only show the character if safe
            line = f"`U+{ord(char):04X}` {name}"
            if preview:
                line += f" `{char}`"

            chars.append(line)

        return "\n".join(chars)

    @command.desc("Replace the spaces in a string with clap emoji")
    @command.usage("[text to filter, or reply]", reply=True)
    async def cmd_clap(self, ctx: command.Context) -> str:
        text = ctx.input
        if not text and ctx.msg.reply_to_message:
            text = ctx.msg.reply_to_message.text
        elif not text and not ctx.msg.reply_to_message:
            return "__Give me a text or reply to a message.__"

        return "\n".join("👏".join(line.split()) for line in text.split("\n"))

    @command.desc("Encode text into Base64")
    @command.alias("b64encode", "b64e")
    @command.usage("[text to encode, or reply]", reply=True)
    async def cmd_base64encode(self, ctx: command.Context) -> str:
        text = ctx.input
        if not text and ctx.msg.reply_to_message:
            text = ctx.msg.reply_to_message.text
        elif not text and not ctx.msg.reply_to_message:
            return "__Give me a text or reply to a message.__"

        return base64.b64encode(text.encode("utf-8")).decode()

    @command.desc("Decode Base64 data")
    @command.alias("b64decode", "b64d")
    @command.usage("[base64 text to decode, or reply]", reply=True)
    async def cmd_base64decode(self, ctx: command.Context) -> str:
        text = ctx.input
        if not text and ctx.msg.reply_to_message:
            text = ctx.msg.reply_to_message.text
        elif not text and not ctx.msg.reply_to_message:
            return "__Give me a text or reply to a message.__"

        try:
            return base64.b64decode(text).decode("utf-8", "replace")
        except binascii.Error as e:
            return f"⚠️ Invalid Base64 data: {e}"

"""
    @command.desc("Paste text to Spacebin")
    @command.usage("[text to paste, or reply]", reply=True)
    async def cmd_spacebin(self, ctx: command.Context) -> str:
        data = ctx.input
        if not data and ctx.msg.reply_to_message:
            data = ctx.msg.reply_to_message.text
        elif not data and not ctx.msg.reply_to_message:
            return "__Give me a text or reply to a message.__"

        msg = await ctx.respond("`Pasting to Spacebin...`")

        try:
            siteurl = "https://spaceb.in/api/"
            response = await fetch.post(siteurl, json={"content": data, "extension": "txt"})
            response = response.json()
            url = "https://spaceb.in/" + response["payload"]["id"]
        except Exception as e:
            return await msg.edit(f"ERROR: {e}")

        if not url:
            return await msg.edit("Text Too Short Or File Problems")

        uname = f"[{ctx.msg.from_user.first_name}](tg://user?id={ctx.msg.from_user.id})"
        pasted = f"**Successfully pasted your data to Spacebin: {url}\n\nPaste by {uname}**"
        await msg.edit(pasted)
"""
