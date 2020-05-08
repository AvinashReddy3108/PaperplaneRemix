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
import io
import PIL
from typing import Tuple, Union, BinaryIO

import asyncurban
from cowpy import cow
import random
import re
from PIL import ImageEnhance, ImageOps

from telethon.errors import rpcerrorlist
from telethon.tl import types

from userbot import client
from userbot.utils.events import NewMessage
from userbot.helper_funcs.ids import get_user_from_msg

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
    "Keep talking, someday you'll say something intelligent!\nI doubt it though.",
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

# Credits: https://git.io/JvxOa
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats 
    "]+")

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

SLAP_TEMPLATES = [
    "{hits} {victim} with a {item}.",
    "{hits} {victim} in the face with a {item}.",
    "{hits} {victim} around a bit with a {item}.",
    "{throws} a {item} at {victim}.",
    "grabs a {item} and {throws} it at {victim}'s face.",
    "{hits} a {item} at {victim}.", "{throws} a few {item} at {victim}.",
    "grabs a {item} and {throws} it in {victim}'s face.",
    "launches a {item} in {victim}'s general direction.",
    "sits on {victim}'s face while slamming a {item} {where}.",
    "starts slapping {victim} silly with a {item}.",
    "pins {victim} down and repeatedly {hits} them with a {item}.",
    "grabs up a {item} and {hits} {victim} with it.",
    "starts slapping {victim} silly with a {item}.",
    "holds {victim} down and repeatedly {hits} them with a {item}.",
    "prods {victim} with a {item}.",
    "picks up a {item} and {hits} {victim} with it.",
    "ties {victim} to a chair and {throws} a {item} at them.",
    "{hits} {victim} {where} with a {item}.",
    "ties {victim} to a pole and whips them {where} with a {item}.",
    "gave a friendly push to help {victim} learn to swim in lava.",
    "sent {victim} to /dev/null.", "sent {victim} down the memory hole.",
    "beheaded {victim}.", "threw {victim} off a building.",
    "replaced all of {victim}'s music with Nickelback.",
    "spammed {victim}'s email.", "made {victim} a knuckle sandwich.",
    "slapped {victim} with pure nothing.",
    "hit {victim} with a small, interstellar spaceship.",
    "quickscoped {victim}.", "put {victim} in check-mate.",
    "RSA-encrypted {victim} and deleted the private key.",
    "put {victim} in the friendzone.",
    "slaps {victim} with a DMCA takedown request!"
]

ITEMS = [
    "cast iron skillet",
    "large trout",
    "baseball bat",
    "cricket bat",
    "wooden cane",
    "nail",
    "printer",
    "shovel",
    "pair of trousers",
    "CRT monitor",
    "diamond sword",
    "baguette",
    "physics textbook",
    "toaster",
    "portrait of Richard Stallman",
    "television",
    "mau5head",
    "five ton truck",
    "roll of duct tape",
    "book",
    "laptop",
    "old television",
    "sack of rocks",
    "rainbow trout",
    "cobblestone block",
    "lava bucket",
    "rubber chicken",
    "spiked bat",
    "gold block",
    "fire extinguisher",
    "heavy rock",
    "chunk of dirt",
    "beehive",
    "piece of rotten meat",
    "bear",
    "ton of bricks",
]

THROW = [
    "throws",
    "flings",
    "chucks",
    "hurls",
]

HIT = [
    "hits",
    "whacks",
    "slaps",
    "smacks",
    "bashes",
]

WHERE = ["in the chest", "on the head", "on the butt", "on the crotch"]


@client.onMessage(command=("shibe", plugin_category),
                  outgoing=True,
                  regex="shibe$")
async def shibes(event: NewMessage.Event) -> None:
    """Get random pictures of shibes."""
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
                  regex=r"(cat|🐈)$")
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
                  regex=r"(bird|🐦)$")
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


@client.onMessage(command=("dog", plugin_category),
                  outgoing=True,
                  regex=r"(?:🐕|dog)(?: |$)(\w+)?(?: |$)(\w+)?")
async def dogs(event: NewMessage.Event) -> None:
    """Get random pictures of dogs."""
    breed = event.matches[0].group(1)
    subbreed = event.matches[0].group(2)
    if breed and subbreed:
        url = f"https://dog.ceo/api/breed/{breed}/{subbreed}/images/random"
    elif breed:
        url = f"https://dog.ceo/api/breed/{breed}/images/random"
    else:
        url = "https://dog.ceo/api/breeds/image/random"
    dog = await _request(url)
    if not dog:
        await event.answer("`Couldn't fetch a dog for you :(`")
        return

    _, json = dog
    try:
        await event.answer(file=json['message'],
                           reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("fox", plugin_category),
                  outgoing=True,
                  regex=r"(fox|🦊)$")
async def foxes(event: NewMessage.Event) -> None:
    """Get random pictures of foxes."""
    fox = await _request('https://some-random-api.ml/img/fox')
    if not fox:
        await event.answer("`Couldn't fetch a fox for you :(`")
        return

    _, json = fox
    try:
        await event.answer(file=json['link'], reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("panda", plugin_category),
                  outgoing=True,
                  regex=r"(panda|🐼)$")
async def pandas(event: NewMessage.Event) -> None:
    """Get random pictures of pandas."""
    panda = await _request('https://some-random-api.ml/img/panda')
    if not panda:
        await event.answer("`Couldn't fetch a panda for you :(`")
        return

    _, json = panda
    try:
        await event.answer(file=json['link'], reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("redpanda", plugin_category),
                  outgoing=True,
                  regex=r"red(panda|🐼)$")
async def redpandas(event: NewMessage.Event) -> None:
    """Get random pictures of red pandas."""
    panda = await _request('https://some-random-api.ml/img/red_panda')
    if not panda:
        await event.answer("`Couldn't fetch a red panda for you :(`")
        return

    _, json = panda
    try:
        await event.answer(file=json['link'], reply_to=event.reply_to_msg_id)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Event timed out!`")


@client.onMessage(command=("cowsay", plugin_category),
                  outgoing=True,
                  regex="(\w+)say(?: |$|\n)([\s\S]*)")
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

    await event.answer(f"<code>{cheese.milk(text)}</code>", parse_mode="html")


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
                  regex="lmg(tfy)?(?: |$|\n)(.*)")
async def lmgtfy(event: NewMessage.Event) -> None:
    """Let me Google that for you real quick."""
    query = event.matches[0].group(2) or "How to use Google?"
    query_encoded = query.replace(" ", "+")
    lmgtfy_url = f"http://letmegooglethat.com/?q={query_encoded}"
    short_url = await _request(f'http://is.gd/create.php', {
        'format': 'simple',
        'url': lmgtfy_url
    },
                               data_type="text")
    clickbait = short_url if short_url else lmgtfy_url
    await event.answer(f"__Here you go, help yourself.__\
        \n[{query}]({clickbait})")


@client.onMessage(command=("vapor", plugin_category),
                  outgoing=True,
                  regex="(vpr|vapor)(?: |$|\n)([\s\S]*)")
async def vapor(event: NewMessage.Event) -> None:
    """Vaporize everything!"""
    text = event.matches[0].group(2)
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            await event.answer("`Ｖａｐｏｒｉｚｅｄ ｔｈｅ ｖｏｉｄ．`")
            return
    reply_text = list()
    for charac in text:
        if 0x21 <= ord(charac) <= 0x7F:
            reply_text.append(chr(ord(charac) + 0xFEE0))
        elif ord(charac) == 0x20:
            reply_text.append(chr(0x3000))
        else:
            reply_text.append(charac)
    vaporized_text = "".join(reply_text)
    await event.answer(vaporized_text)


@client.onMessage(command=("zalgo", plugin_category),
                  outgoing=True,
                  regex="(zlg|zalgo)(?: |$|\n)([\s\S]*)")
async def zalgofy(event: NewMessage.Event) -> None:
    """Invoke the feeling of chaos!"""
    text = event.matches[0].group(2)
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            await event.answer(
                "`I̺͑ c̴̎a̩͘n͉͐'tͪͬ i̡͙n̺ͦṽ̘o̎͘k͇̃e̮͊ c̜̾h̩͋ä͒o̺͝s̗͟ į̶n̵ͭ t̵̙h̛ ̝e͊̀ v̗͛o̯͡i̋ͦd̙ͤ.`"
            )
            return
    reply_text = list()
    for charac in text:
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
    chaotic_text = ''.join(reply_text)
    await event.answer(f"`{chaotic_text}`")


@client.onMessage(command=("stretch", plugin_category),
                  outgoing=True,
                  regex="str(etch)?(?: |$|\n)([\s\S]*)")
async def slinky(event: NewMessage.Event) -> None:
    """Stretch it like it's rubber!"""
    text = event.matches[0].group(2)
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            await event.answer("`GiiiiiiiB sooooooomeeeeeee teeeeeeext!`")
            return
    count = random.randint(3, 10)
    reply_text = re.sub(r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵаеиоуюяыэё])", (r"\1" * count),
                        text)
    await event.answer(f"__{reply_text}__")


@client.onMessage(command=("uwu", plugin_category),
                  outgoing=True,
                  regex="(owo|uwu)(?: |$|\n)([\s\S]*)")
async def nekofy(event: NewMessage.Event) -> None:
    """Neko-fy the text, like the degenerate you are."""
    text = event.matches[0].group(2)
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            await event.answer("`I can't nyekofy the void.`")
            return
    reply_text = re.sub(r"(r|l)", "w", text)
    reply_text = re.sub(r"(R|L)", "W", reply_text)
    reply_text = re.sub(r"n([aeiou])", r"ny\1", reply_text)
    reply_text = re.sub(r"N([aeiouAEIOU])", r"Ny\1", reply_text)
    reply_text = reply_text.replace("ove", "uv")
    await event.answer(f"__{reply_text}__")


@client.onMessage(command=("pasta", plugin_category),
                  outgoing=True,
                  regex="(cp|pasta)(?: |$|\n)([\s\S]*)")
async def copypasta(event: NewMessage.Event) -> None:
    """Copypasta the famous meme."""
    text = event.matches[0].group(2)
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            await event.answer("`😂🅱️IvE👐sOME👅text👅for✌️Me👌tO👐MAkE👀iT💞funNy!💦`")
            return
    reply_text = random.choice(PASTAMOJIS)
    b_char = random.choice(text).lower()
    for owo in text:
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
    await event.answer(f"__{reply_text}__")


@client.onMessage(command=("mock", plugin_category),
                  outgoing=True,
                  regex="mock(?: |$|\n)([\s\S]*)")
async def spongemock(event: NewMessage.Event) -> None:
    """sPoNgE MoCk tHe tExT!"""
    text = event.matches[0].group(1)
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            await event.answer("`I cAnT MoCk tHe vOId!`")
            return
    reply_text = list()
    for charac in text:
        if charac.isalpha() and random.randint(0, 1):
            to_app = charac.upper() if charac.islower() else charac.lower()
            reply_text.append(to_app)
        else:
            reply_text.append(charac)
    mocked_text = "".join(reply_text)
    await event.answer(f"__{mocked_text}__")


@client.onMessage(command=("insult", plugin_category),
                  outgoing=True,
                  regex="insult$")
async def memereview(event: NewMessage.Event) -> None:
    """Insult people."""
    await event.answer(f"__{random.choice(INSULTS)}__")


@client.onMessage(command=("clap", plugin_category),
                  outgoing=True,
                  regex="clap(?: |$|\n)([\s\S]*)")
async def clapz(event: NewMessage.Event) -> None:
    """Praise people."""
    text = event.matches[0].group(1)
    if not text:
        if event.is_reply:
            text = (await event.get_reply_message()).message
        else:
            await event.answer("`Hah, I don't clap for the void!`")
            return
    clapped_text = re.sub(" ", " 👏 ", text)
    reply_text = f"👏 {clapped_text} 👏"
    await event.answer(f"__{reply_text}__")


@client.onMessage(command=("urban", plugin_category),
                  outgoing=True,
                  regex="(ud|urban)(?: |$|\n)(.*)")
async def urban_dict(event: NewMessage.Event) -> None:
    """ Looks up words in the Urban Dictionary."""
    query = event.matches[0].group(2)
    urban_dict_helper = asyncurban.UrbanDictionary()
    try:
        urban_def = await urban_dict_helper.get_word(query)
    except asyncurban.WordNotFoundError:
        await event.answer(f"`Sorry, couldn't find any results for:` {query}")
        return
    await event.answer(
        f"**Text**: `{query}`\n\n**Meaning**:\n`{urban_def.definition}`\n\n**Example**:\n__{urban_def.example}__"
    )


@client.onMessage(command=("slap", plugin_category),
                  outgoing=True,
                  regex=r"slap(?: |$)(.*)")
async def slap(event: NewMessage.Event) -> None:
    """Slap a user with random objects for fun!"""
    target = await get_user_from_msg(event)
    if not target:
        await event.answer("`I can't slap the void!`")
        return

    try:
        retard = await event.client.get_entity(target)
        slapped = f"@{retard.username}" if retard.username else f"[{retard.first_name}](tg://user?id={retard.id})"
        template = random.choice(SLAP_TEMPLATES)
        caption = "..." + template.format(victim=slapped,
                                          item=random.choice(ITEMS),
                                          hits=random.choice(HIT),
                                          throws=random.choice(THROW),
                                          where=random.choice(WHERE))
        await event.answer(f"__{caption}__")
    except:
        await event.answer("`Unfortunately, I can't slap this person.`")


@client.onMessage(command=("f", plugin_category),
                  outgoing=True,
                  regex=r"f(?: |$)(.)")
async def payf(event: NewMessage.Event) -> None:
    """Pay your respects, with custom/random emojis"""
    paytext = event.matches[0].group(1)
    if not isEmoji(paytext):
        return
    pay = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        paytext * 8, paytext * 8, paytext * 2, paytext * 2, paytext * 2,
        paytext * 6, paytext * 6, paytext * 2, paytext * 2, paytext * 2,
        paytext * 2, paytext * 2)
    await event.answer(pay)


@client.onMessage(command=("bluetext", plugin_category),
                  outgoing=True,
                  regex=r"(bt|b(lue)?text)$")
async def bt(event: NewMessage.Event) -> None:
    """ Believe me, you will find this useful. """
    if event.is_group:
        await event.answer(
            "/BLUETEXT /MUST /CLICK.\n"
            f"{random.choice(['/ARE /YOU', '/AM /I'])} /A /STUPID /ANIMAL /WHICH /IS /ATTRACTED /TO /COLOURS?"
        )


@client.onMessage(command=("deepfry", plugin_category),
                  outgoing=True,
                  regex=r"(deep)?fry(?: |$)(\d*)")
async def mamma_mia(event: NewMessage.Event) -> None:
    """Deep fry images and stickers!"""
    frycount = int(event.matches[0].group(
        2)) if event.matches[0].group(2) != '' else random.randint(1, 3)
    if event.reply_to_msg_id:
        potato = await event.get_reply_message()
        if not await _is_fryable_event(potato):
            await event.answer("`Invalid message type!`")
            return
    else:
        potato = None
        async for msg in client.iter_messages(event.chat_id,
                                              offset_id=event.message.id,
                                              limit=10):
            if await _is_fryable_event(msg):
                potato = msg
                break
        if not potato:
            await event.answer(
                "`Couldn't find any acceptable media in the recent messages.`")
            return

    # download photo as byte array.
    await event.answer("`Firing up the deep-fryer!`")
    data = potato.photo if potato.photo else potato.media.document
    image = io.BytesIO()
    await potato.download_media(file=image)
    image = PIL.Image.open(image)

    # fry the image
    for _ in range(frycount):
        image = await deepfry(image)

    fried_io = io.BytesIO()
    fried_io.name = "deepfried_image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)
    try:
        await event.answer(file=fried_io)
        await event.delete()
    except rpcerrorlist.TimeoutError:
        await event.answer("`Ran out of oil to fry this pic :P`")


@client.onMessage(outgoing=True, regex="^Ooof$", disable_prefix=True)
async def oof(event: NewMessage.Event) -> None:
    """Big Oooooof."""
    for i in range(random.randint(5, 10)):
        await event.answer("Oooo" + "o" * i + "f")


@client.onMessage(outgoing=True, regex="^-__-$", disable_prefix=True)
async def okay(event: NewMessage.Event) -> None:
    """Ok......"""
    for i in range(random.randint(5, 10)):
        await event.answer("-___" + "_" * i + "-", parse_mode='html')


@client.onMessage(outgoing=True, regex="^;__;$", disable_prefix=True)
async def crai(event: NewMessage.Event) -> None:
    """crai :("""
    for i in range(random.randint(5, 10)):
        await event.answer(";___" + "_" * i + ";", parse_mode='html')


@client.onMessage(outgoing=True, regex="^:/$", disable_prefix=True)
async def keks(event: NewMessage.Event) -> None:
    """kekz"""
    uio = ["/", "\\"]
    for i in range(1, random.randint(5, 10)):
        await asyncio.sleep(0.3)
        await event.answer(":" + uio[i % 2])


def isEmoji(inputString: str) -> bool:
    return bool(re.match(EMOJI_PATTERN, inputString))


async def _is_fryable_event(event: NewMessage.Event) -> bool:
    """Checks if the given image/sticker is worthy of the fry or not!"""
    if (event.sticker and not event.sticker.mime_type
            == 'application/x-tgsticker') or event.photo:
        return True
    if event.document and "image" in event.document.mime_type:
        return True
    return False


# Copyright (c) 2017 Ovyerus; License: MIT
async def deepfry(img: BinaryIO) -> BinaryIO:
    """Deepfry logic!"""
    colours = ((random.randint(50, 200), random.randint(40, 170),
                random.randint(40, 190)), (random.randint(190, 255),
                                           random.randint(170, 240),
                                           random.randint(180, 250)))

    # Crush image to hell and back
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize((int(width**random.uniform(
        0.8, 0.9)), int(height**random.uniform(0.8, 0.9))),
                     resample=PIL.Image.LANCZOS)
    img = img.resize((int(width**random.uniform(
        0.85, 0.95)), int(height**random.uniform(0.85, 0.95))),
                     resample=PIL.Image.BILINEAR)
    img = img.resize((int(width**random.uniform(
        0.89, 0.98)), int(height**random.uniform(0.89, 0.98))),
                     resample=PIL.Image.BICUBIC)
    img = img.resize((width, height), resample=PIL.Image.BICUBIC)
    img = ImageOps.posterize(img, random.randint(3, 7))

    # Generate colour overlay
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(random.uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(random.uniform(
        1.0, 2.0))

    overlay = ImageOps.colorize(overlay, colours[0], colours[1])

    # Overlay red and yellow onto main image and sharpen the hell out of it
    img = PIL.Image.blend(img, overlay, random.uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(random.randint(5, 300))

    return img


async def _request(
        url: str,
        params: dict = None,
        data_type: str = None
) -> Union[Union[dict, str, Tuple[str, dict]], None]:
    """Helps request data from APIs faster!"""
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
