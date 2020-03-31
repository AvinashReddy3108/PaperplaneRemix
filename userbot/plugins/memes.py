# TG-UserBot - A modular Telegram UserBot script for Python.
# Copyright (C) 2019  Kandarp <https://github.com/kandnub>
#
# TG-UserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TG-UserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TG-UserBot.  If not, see <https://www.gnu.org/licenses/>.

import aiohttp
import asyncio
from typing import Tuple, Union

import asyncurban
from cowpy import cow
import random
import re

from telethon.errors import rpcerrorlist

from userbot import client
from userbot.utils.events import NewMessage

plugin_category = "memes"

INSULTS = [
    "Owww ... Such a stupid idiot.",
    "Don't drink and type.",
    "I think you should go home or better a mental asylum.",
    "Do you realize you are making a fool of yourself? Apparently not.",
    "You can type better than that.",
    "Sorry, we do not sell brains.",
    "Believe me you are not normal.",
    "I bet your brain feels as good as new, seeing that you never use it.",
    "If I wanted to kill myself I'd climb your ego and jump to your IQ.",
    "Zombies eat brains...\nyou're safe.",
    "You didn't evolve from apes,\n...they evolved from you.",
    "Come back and talk to me when your I.Q. exceeds your age.",
    "I'm not saying you're stupid, I'm just saying you've got bad luck when it comes to thinking.",
    "What language are you speaking? Cause it sounds like bullshit.",
    "Stupidity is not a crime so you are free to go.",
    "You are proof that evolution CAN go in reverse.",
    "I would ask you how old you are but I know you can't count that high.",
    "As an outsider, what do you think of the human race?",
    "Brains aren't everything. In your case they're nothing.",
    "Usually people live and learn. You just live.",
    "I don't know what makes you so stupid, but it really works.",
    "Keep talking, someday you'll say something intelligent!\n__(I doubt it though)__",
    "Shock me, say something intelligent.",
    "Your IQ's lower than your shoe size.",
    "Alas! Your neurotransmitters are no more working.",
    "Everyone has the right to be stupid but you are abusing the privilege.",
    "I'm sorry I hurt your feelings when I called you stupid.\nI thought you already knew that.",
    "You should try tasting cyanide.",
    "Your enzymes are meant to digest rat poison.",
    "You should try sleeping forever.",
    "You could make a world record by jumping from a plane without parachute.",
    "Stop talking BS and jump in front of a running bullet train.",
    "Try bathing with Hydrochloric Acid instead of water.",
    "You should definitely try this:\nif you hold your breath underwater for an hour, you can then hold it forever.",
    "Go Green!\nStop inhaling Oxygen.",
    "God was searching for you.\nYou should leave to meet him.",
    "give your 100%.\nNow, go donate blood.",
    "Try jumping from a hundred story building but you can do it only once.",
    "You should donate your brain seeing that you never used it.",
    "Volunteer for target in an firing range.",
    "Head shots are fun.\nGet yourself one.",
    "You should try swimming with great white sharks.",
    "You should paint yourself red and run in a bull marathon.",
    "You can stay underwater for the rest of your life without coming back up.",
    "How about you stop breathing for like 1 day?\nThat'll be great.",
    "Try provoking a tiger while you both are in a cage.",
    "Have you tried shooting yourself as high as 100m using a canon.",
    "You should try holding TNT in your mouth and igniting it.",
    "Try playing catch and throw with RDX its fun.",
    "I heard phogine is poisonous but i guess you wont mind inhaling it for fun.",
    "Launch yourself into outer space while forgetting oxygen on Earth.",
    "You should try playing snake and ladders, with real snakes and no ladders.",
    "Dance naked on a couple of HT wires.",
    "Active Volcano is the best swimming pool for you.",
    "You should try hot bath in a volcano.",
    "Try to spend one day in a coffin and it will be yours forever.",
    "Hit Uranium with a slow moving neutron in your presence. It will be a worthwhile experience.",
    "You can be the first person to step on sun. Have a try.",
]

ZALG_LIST = [[
    "̖",
    " ̗",
    " ̘",
    " ̙",
    " ̜",
    " ̝",
    " ̞",
    " ̟",
    " ̠",
    " ̤",
    " ̥",
    " ̦",
    " ̩",
    " ̪",
    " ̫",
    " ̬",
    " ̭",
    " ̮",
    " ̯",
    " ̰",
    " ̱",
    " ̲",
    " ̳",
    " ̹",
    " ̺",
    " ̻",
    " ̼",
    " ͅ",
    " ͇",
    " ͈",
    " ͉",
    " ͍",
    " ͎",
    " ͓",
    " ͔",
    " ͕",
    " ͖",
    " ͙",
    " ͚",
    " ",
],
             [
                 " ̍",
                 " ̎",
                 " ̄",
                 " ̅",
                 " ̿",
                 " ̑",
                 " ̆",
                 " ̐",
                 " ͒",
                 " ͗",
                 " ͑",
                 " ̇",
                 " ̈",
                 " ̊",
                 " ͂",
                 " ̓",
                 " ̈́",
                 " ͊",
                 " ͋",
                 " ͌",
                 " ̃",
                 " ̂",
                 " ̌",
                 " ͐",
                 " ́",
                 " ̋",
                 " ̏",
                 " ̽",
                 " ̉",
                 " ͣ",
                 " ͤ",
                 " ͥ",
                 " ͦ",
                 " ͧ",
                 " ͨ",
                 " ͩ",
                 " ͪ",
                 " ͫ",
                 " ͬ",
                 " ͭ",
                 " ͮ",
                 " ͯ",
                 " ̾",
                 " ͛",
                 " ͆",
                 " ̚",
             ],
             [
                 " ̕",
                 " ̛",
                 " ̀",
                 " ́",
                 " ͘",
                 " ̡",
                 " ̢",
                 " ̧",
                 " ̨",
                 " ̴",
                 " ̵",
                 " ̶",
                 " ͜",
                 " ͝",
                 " ͞",
                 " ͟",
                 " ͠",
                 " ͢",
                 " ̸",
                 " ̷",
                 " ͡",
             ]]

PASTAMOJIS = [
    "😂",
    "😂",
    "👌",
    "✌",
    "💞",
    "👍",
    "👌",
    "💯",
    "🎶",
    "👀",
    "😂",
    "👓",
    "👏",
    "👐",
    "🍕",
    "💥",
    "🍴",
    "💦",
    "💦",
    "🍑",
    "🍆",
    "😩",
    "😏",
    "👉👌",
    "👀",
    "👅",
    "😩",
    "🚰",
]


@client.onMessage(command=("shibe", plugin_category),
                  outgoing=True,
                  regex="shibe$")
async def shibes(event: NewMessage.Event) -> None:
    """Get random pictures of Shibes."""
    shibe = await _request('http://shibe.online/api/shibes')
    if not shibe:
        await event.answer("`Couldn't fetch a shibe for you :(`")
        return

    _, json = shibe
    try:
        await event.answer(file=json[0], reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("cat", plugin_category),
                  outgoing=True,
                  regex="cat$")
async def cats(event: NewMessage.Event) -> None:
    """Get random pictures of cats."""
    shibe = await _request('http://shibe.online/api/cats')
    if not shibe:
        await event.answer("`Couldn't fetch a cat for you :(`")
        return

    _, json = shibe
    try:
        await event.answer(file=json[0], reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("bird", plugin_category),
                  outgoing=True,
                  regex="bird$")
async def birds(event: NewMessage.Event) -> None:
    """Get random pictures of birds."""
    shibe = await _request('http://shibe.online/api/birds')
    if not shibe:
        await event.answer("`Couldn't fetch a bird for you :(`")
        return

    _, json = shibe
    try:
        await event.answer(file=json[0], reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("cowsay", plugin_category),
                  outgoing=True,
                  regex="(\w+)say(?: |$)(.*)")
async def cowsay(event: NewMessage.Event) -> None:
    """Create messages with various animals and other creatures."""
    arg = event.matches[0].group(1).lower()
    text = event.matches[0].group(2)

    if arg == "cow":
        arg = "default"
    if arg not in cow.COWACTERS:
        return
    cheese = cow.get_cow(arg)
    cheese = cheese()

    await event.answer(f"`{cheese.milk(text).replace('`', '´')}`")


@client.onMessage(command=("decide", plugin_category),
                  outgoing=True,
                  regex="(yes|no|maybe|decide)$")
async def decide(event: NewMessage.Event) -> None:
    """Helps to make a quick decision."""
    decision = event.matches[0].group(1)
    if decision.lower() != "decide":
        decide_data = await _request(f"https://yesno.wtf/api",
                                     {'force': decision})
    else:
        decide_data = await _request("https://yesno.wtf/api")

    _, json = decide_data
    try:
        await event.answer(file=json["image"], reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("lmgtfy", plugin_category),
                  outgoing=True,
                  regex="lmg(?: |$)(.*)")
async def lmgtfy(event: NewMessage.Event) -> None:
    """Let me Google that for you real quick."""
    query = event.matches[0].group(1)
    if not query:
        await event.answer("`Let me Google the void for you real quick.`")
        return
    query_encoded = query.replace(" ", "+")
    lmgtfy_url = f"http://letmegooglethat.com/?q={query_encoded}"
    short_url = await _request(f'http://is.gd/create.php', {
        'format': 'simple',
        'url': lmgtfy_url
    },
                               data_type="text")
    clickbait = short_url if short_url else lmgtfy_url
    await event.answer(f"Here you go, help yourself.\
                      \n[{query}]({clickbait})")


@client.onMessage(command=("vapor", plugin_category),
                  outgoing=True,
                  regex="vpr(?: |$)(.*)")
async def vapor(event: NewMessage.Event) -> None:
    """Vaporize everything!"""
    reply_text = list()
    textx = await event.get_reply_message()
    message = event.matches[0].group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.answer("`Ｖａｐｏｒｉｚｅｄ ｔｈｅ ｖｏｉｄ．`")
        return

    for charac in message:
        if 0x21 <= ord(charac) <= 0x7F:
            reply_text.append(chr(ord(charac) + 0xFEE0))
        elif ord(charac) == 0x20:
            reply_text.append(chr(0x3000))
        else:
            reply_text.append(charac)

    await event.answer("".join(reply_text))


@client.onMessage(command=("zalgo", plugin_category),
                  outgoing=True,
                  regex="zlg(?: |$)(.*)")
async def zalgofy(event: NewMessage.Event) -> None:
    """Invoke the feeling of chaos!"""
    reply_text = list()
    textx = await event.get_reply_message()
    message = event.matches[0].group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.answer(
            "I̺͑ c̴̎a̩͘n͉͐'tͪͬ i̡͙n̺ͦṽ̘o̎͘k͇̃e̮͊ c̜̾h̩͋ä͒o̺͝s̗͟ į̶n̵ͭ t̵̙h̛ ̝e͊̀ v̗͛o̯͡i̋ͦd̙ͤ."
        )
        return

    for charac in message:
        if not charac.isalpha():
            reply_text.append(charac)
            continue

        for _ in range(0, 3):
            zalgint = random.randint(0, 2)

            if zalgint == 0:
                charac = charac.strip() + \
                    random.choice(ZALG_LIST[0]).strip()
            elif zalgint == 1:
                charac = charac.strip() + \
                    random.choice(ZALG_LIST[1]).strip()
            else:
                charac = charac.strip() + \
                    random.choice(ZALG_LIST[2]).strip()

        reply_text.append(charac)

    await event.answer(''.join(reply_text))


@client.onMessage(command=("stretch", plugin_category),
                  outgoing=True,
                  regex="str(?: |$)(.*)")
async def slinky(event: NewMessage.Event) -> None:
    """Stretch it!"""
    textx = await event.get_reply_message()
    message = event.matches[0].group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.answer("GiiiiiiiB sooooooomeeeeeee teeeeeeext!")
        return

    count = random.randint(3, 10)
    reply_text = re.sub(r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵаеиоуюяыэё])", (r"\1" * count),
                        message)
    await event.answer(reply_text)


@client.onMessage(command=("uwu", plugin_category),
                  outgoing=True,
                  regex="uwu(?: |$)(.*)")
async def nekofy(event: NewMessage.Event) -> None:
    """Neko-fy the text, like the degenerate you are."""
    textx = await event.get_reply_message()
    message = event.matches[0].group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.answer("I can't nyekofy the void.")
        return

    reply_text = re.sub(r"(r|l)", "w", message)
    reply_text = re.sub(r"(R|L)", "W", reply_text)
    reply_text = re.sub(r"n([aeiou])", r"ny\1", reply_text)
    reply_text = re.sub(r"N([aeiouAEIOU])", r"Ny\1", reply_text)
    reply_text = reply_text.replace("ove", "uv")
    await event.answer(reply_text)


@client.onMessage(command=("copypasta", plugin_category),
                  outgoing=True,
                  regex="pasta(?: |$)(.*)")
async def copypasta(event: NewMessage.Event) -> None:
    """Copypasta the famous meme."""
    textx = await event.get_reply_message()
    message = event.matches[0].group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.answer("😂🅱️IvE👐sOME👅text👅for✌️Me👌tO👐MAkE👀iT💞funNy!💦")
        return

    reply_text = random.choice(PASTAMOJIS)
    # choose a random character in the message to be substituted with 🅱️
    b_char = random.choice(message).lower()
    for owo in message:
        if owo == " ":
            reply_text += random.choice(PASTAMOJIS)
        elif owo in PASTAMOJIS:
            reply_text += owo
            reply_text += random.choice(PASTAMOJIS)
        elif owo.lower() == b_char:
            reply_text += "🅱️"
        else:
            if bool(random.getrandbits(1)):
                reply_text += owo.upper()
            else:
                reply_text += owo.lower()
    reply_text += random.choice(PASTAMOJIS)
    await event.answer(reply_text)


@client.onMessage(command=("mock", plugin_category),
                  outgoing=True,
                  regex="mock(?: |$)(.*)")
async def spongemock(event: NewMessage.Event) -> None:
    """sPoNgE MoCk tHe tExT!"""
    reply_text = list()
    textx = await event.get_reply_message()
    message = event.matches[0].group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.answer("`I cAnT MoCk tHe vOId!`")
        return

    for charac in message:
        if charac.isalpha() and random.randint(0, 1):
            to_app = charac.upper() if charac.islower() else charac.lower()
            reply_text.append(to_app)
        else:
            reply_text.append(charac)
    mocked_text = "".join(reply_text)
    await event.answer(mocked_text)


@client.onMessage(command=("insult", plugin_category),
                  outgoing=True,
                  regex="insult$")
async def memereview(event: NewMessage.Event) -> None:
    """Insult people."""
    await event.answer(random.choice(INSULTS))


@client.onMessage(command=("clap", plugin_category),
                  outgoing=True,
                  regex="clap(?: |$)(.*)")
async def clapz(event: NewMessage.Event) -> None:
    """Praise people."""
    textx = await event.get_reply_message()
    message = event.matches[0].group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await event.answer("`Hah, I don't clap for the void!`")
        return

    clapped_text = re.sub(" ", " 👏 ", message)
    reply_text = f"👏 {clapped_text} 👏"
    await event.answer(reply_text)


@client.onMessage(command=("urbandictionary", plugin_category),
                  outgoing=True,
                  regex="ud(?: |$)(.*)")
async def urban_dict(event: NewMessage.Event) -> None:
    """ Looks up words in the Urban Dictionary. """
    await event.answer("Processing...")
    query = event.matches[0].group(1)
    urban_dict_helper = asyncurban.UrbanDictionary()
    try:
        urban_def = await urban_dict_helper.get_word(query)
    except asyncurban.WordNotFoundError:
        await event.answer(
            f"`Sorry, couldn't find any results for:` **{query}**")
        return
    await event.answer("**Text**: " + query + "\n**Meaning**: `" +
                       urban_def.definition + "`\n" + "**Example**: __" +
                       urban_def.example + "__")


@client.onMessage(outgoing=True, regex="^Oof$", disable_prefix=True)
async def oof(event: NewMessage.Event) -> None:
    """Big Oooooof."""
    for i in range(random.randint(5, 10)):
        await event.answer("Ooo" + "o" * i + "f")


@client.onMessage(outgoing=True, regex="^-_-$", disable_prefix=True)
async def okay(event: NewMessage.Event) -> None:
    """Ok......"""
    for i in range(random.randint(5, 10)):
        await event.answer("-__" + "_" * i + "-", parse_mode='html')


@client.onMessage(outgoing=True, regex="^;_;$", disable_prefix=True)
async def crai(event: NewMessage.Event) -> None:
    """crai :("""
    for i in range(random.randint(5, 10)):
        await event.answer(";__" + "_" * i + ";", parse_mode='html')


@client.onMessage(outgoing=True, regex="^:/$", disable_prefix=True)
async def keks(event: NewMessage.Event) -> None:
    """kekz"""
    uio = ["/", "\\"]
    for i in range(1, random.randint(5, 10)):
        await asyncio.sleep(0.3)
        await event.answer(":" + uio[i % 2])


async def _request(
    url: str,
    params: dict = None,
    data_type: str = None
) -> Union[Union[dict, str, Tuple[str, dict]], None]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                if data_type == "json":
                    return await response.json()
                elif data_type == "text":
                    return await response.text()
                else:
                    return await response.text(), await response.json()
            return None
