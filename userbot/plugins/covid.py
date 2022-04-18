#
# PaperplaneRemix - A modular Telegram selfbot script
# Copyright (C) 2022, Avinash Reddy and the PaperplaneRemix contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from covid import Covid

from userbot import client
from userbot.utils.events import NewMessage

plugin_category = "pandemic"
covid_str = f"""`{'Confirmed':<9}:`  **%(confirmed)s**
`{'Active':<9}:`  **%(active)s**
`{'Recovered':<9}:`  **%(recovered)s**
`{'Deaths':<9}:`  **%(deaths)s**"""
critical_str = f"\n`{'Critical':<9}:`  **%(critical)s**"


@client.onMessage(
    command=("covid", plugin_category),
    outgoing=True,
    regex=r"(?:covid|corona)(?: |$)(.*)",
)
async def covid19(event: NewMessage.Event) -> None:
    """
    Get the current COVID-19 stats for a specific country or overall.


    `{prefix}covid` or `{prefix}covid USA India` or `{prefix}covid countries`
    """
    covid = Covid(source="worldometers")
    match = event.matches[0].group(1)
    if match:
        strings = []
        failed = []
        args, _ = await client.parse_arguments(match)
        if match.lower() == "countries":
            strings = sorted(covid.list_countries())
        else:
            for c in args:
                try:
                    country = covid.get_status_by_country_name(c)
                    string = f"**COVID-19** __({country['country']})__\n"
                    string += covid_str % country
                    if country["critical"]:
                        string += critical_str % country
                    strings.append(string)
                except ValueError:
                    failed.append(c)
                    continue
        if strings:
            await event.answer("\n\n".join(strings))
        if failed:
            string = "`Couldn't find the following countries:` "
            string += ", ".join(f"`{x}`" for x in failed)
            await event.answer(string, reply=True)
    else:
        active = covid.get_total_active_cases()
        confirmed = covid.get_total_confirmed_cases()
        recovered = covid.get_total_recovered()
        deaths = covid.get_total_deaths()
        string = "**COVID-19** __(Worldwide)__\n"
        string += covid_str % {
            "active": active,
            "confirmed": confirmed,
            "recovered": recovered,
            "deaths": deaths,
        }
        await event.answer(string)
