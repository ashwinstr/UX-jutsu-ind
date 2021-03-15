""" setup sudos """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

from pyrogram.errors import PeerIdInvalid

from userge import Config, Message, get_collection, userge

SAVED_SETTINGS = get_collection("CONFIGS")
SUDO_USERS_COLLECTION = get_collection("sudo_users")
SUDO_CMDS_COLLECTION = get_collection("sudo_cmds")


async def _init() -> None:
    s_o = await SAVED_SETTINGS.find_one({"_id": "SUDO_ENABLED"})
    if s_o:
        Config.SUDO_ENABLED = s_o["data"]
    async for i in SUDO_USERS_COLLECTION.find():
        Config.SUDO_USERS.add(i["_id"])
    async for i in SUDO_CMDS_COLLECTION.find():
        Config.ALLOWED_COMMANDS.add(i["_id"])


@userge.on_cmd(
    "sudo", about={"header": "enable / disable sudo access"}, allow_channels=False
)
async def sudo_(message: Message):
    """ enable / disable sudo access """
    if Config.SUDO_ENABLED:
        Config.SUDO_ENABLED = False
        await message.edit("`sudo disabled !`", del_in=3)
    else:
        Config.SUDO_ENABLED = True
        await message.edit("`sudo enabled !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "SUDO_ENABLED"}, {"$set": {"data": Config.SUDO_ENABLED}}, upsert=True
    )


@userge.on_cmd(
    "addsudo",
    about={"header": "add sudo user", "usage": "{tr}addsudo [username | reply to msg]"},
    allow_channels=False,
)
async def add_sudo(message: Message):
    """ add sudo user """
    user_id = message.input_str
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    if not user_id:
        await message.err(f"user: `{user_id}` not found!")
        return
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    try:
        user = await message.client.get_user_dict(user_id)
    except (PeerIdInvalid, IndexError) as p_e:
        await message.err(str(p_e))
        return
    if user["id"] in Config.SUDO_USERS:
        await message.edit(f"user : `{user['id']}` already in **SUDO**!", del_in=5)
    else:
        if user["id"] in Config.OWNER_ID or user["id"] == (await userge.get_me()).id:
            await message.edit(
                f"user : `{user['id']}` is in `OWNER_ID` so no need to add in sudo",
                del_in=5,
            )
            return
        if user["id"] in Config.TG_IDS:
            await message.err("Not Permitted due to security reasons", del_in=7)
            return
        Config.SUDO_USERS.add(user["id"])
        await asyncio.gather(
            SUDO_USERS_COLLECTION.insert_one(
                {"_id": user["id"], "men": user["mention"]}
            ),
            message.edit(
                f"user : `{user['id']}` added to **SUDO**!", del_in=5, log=__name__
            ),
        )


@userge.on_cmd(
    "delsudo",
    about={
        "header": "delete sudo user",
        "flags": {"-all": "remove all sudo users"},
        "usage": "{tr}delsudo [user_id | reply to msg]\n{tr}delsudo -all",
    },
    allow_channels=False,
)
async def del_sudo(message: Message):
    """ delete sudo user """
    if "-all" in message.flags:
        Config.SUDO_USERS.clear()
        await asyncio.gather(
            SUDO_USERS_COLLECTION.drop(),
            message.edit("**SUDO** users cleared!", del_in=5),
        )
        return
    user_id = message.filtered_input_str
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    if not user_id:
        await message.err(f"user: `{user_id}` not found!")
        return
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    if not isinstance(user_id, int):
        await message.err("invalid type!")
        return
    if user_id not in Config.SUDO_USERS:
        await message.edit(f"user : `{user_id}` not in **SUDO** !", del_in=5)
    else:
        Config.SUDO_USERS.remove(user_id)
        await asyncio.gather(
            SUDO_USERS_COLLECTION.delete_one({"_id": user_id}),
            message.edit(
                f"user : `{user_id}` removed from **SUDO**!", del_in=5, log=__name__
            ),
        )


@userge.on_cmd("vsudo", about={"header": "view sudo users"}, allow_channels=False)
async def view_sudo(message: Message):
    """ view sudo users """
    if not Config.SUDO_USERS:
        await message.edit("**SUDO** users not found!", del_in=5)
        return
    out_str = "🚷 **SUDO USERS**: **[{}]**🚷\n\n"
    total = 0
    async for user in SUDO_USERS_COLLECTION.find():
        total += 1
        out_str += f" 🙋‍♂️ {user['men']} 🆔 `{user['_id']}`\n"
    await message.edit(out_str.format(total), del_in=0)


@userge.on_cmd(
    "addscmd",
    about={
        "header": "add sudo command",
        "flags": {
            "-all": "add all commands to sudo ",
            "-full": "full sudo access [i.e '-all' + term, eval, exec ...] (Dangerous !)",
        },
        "usage": "{tr}addscmd [command name]\n{tr}addscmd -all\n{tr}addscmd -full",
    },
    allow_channels=False,
)
async def add_sudo_cmd(message: Message):
    """ add sudo cmd """
    if "-all" in message.flags or "-full" in message.flags:
        await SUDO_CMDS_COLLECTION.drop()
        Config.ALLOWED_COMMANDS.clear()
        tmp_ = []
        no_go_cmd = ["addscmd", "delscmd", "addsudo", "delsudo", "eval", "term", "exec"]
        trig = Config.CMD_TRIGGER
        no_go = []
        for cmd in no_go_cmd:
            no_go.append(trig + cmd)
        for c_d in list(userge.manager.enabled_commands):
<<<<<<< HEAD
            if c_d not in no_go:
                t_c = c_d.lstrip(Config.CMD_TRIGGER)
=======
            t_c = c_d.lstrip(Config.CMD_TRIGGER)
            if "-all" in message.flags:
                mode_ = "all"
                if not (
                    t_c
                    in [
                        "exec",
                        "term",
                        "eval",
                        "addscmd",
                        "delscmd",
                        "load",
                        "unload",
                        "addsudo",
                        "delsudo",
                        "sudo",
                    ]
                ):
                    tmp_.append({"_id": t_c})
                    Config.ALLOWED_COMMANDS.add(t_c)
            else:
                mode_ = "full"
>>>>>>> 25b3158fc2fbdda9878f59c9d7c1179f8ba0457d
                tmp_.append({"_id": t_c})
                Config.ALLOWED_COMMANDS.add(t_c)
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.insert_many(tmp_),
            message.edit(
<<<<<<< HEAD
                f"**Added** all (`{len(tmp_)}`) safe commands to **SUDO**!",
=======
                f"**Added** {mode_} (`{len(tmp_)}`) commands to **SUDO** cmds!",
>>>>>>> 25b3158fc2fbdda9878f59c9d7c1179f8ba0457d
                del_in=5,
                log=__name__,
            ),
        )
        return
    cmd = message.input_str
    if not cmd:
        await message.err("input not found!")
        return
    cmd = cmd.lstrip(Config.CMD_TRIGGER)
    if cmd in Config.ALLOWED_COMMANDS:
        await message.edit(f"cmd : `{cmd}` already in **SUDO**!", del_in=5)
    elif cmd not in (
        c_d.lstrip(Config.CMD_TRIGGER) for c_d in list(userge.manager.enabled_commands)
    ):
        await message.edit(f"cmd : `{cmd}` 🤔, is that a command ?", del_in=5)
    else:
        Config.ALLOWED_COMMANDS.add(cmd)
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.insert_one({"_id": cmd}),
            message.edit(f"cmd : `{cmd}` added to **SUDO**!", del_in=5, log=__name__),
        )


@userge.on_cmd(
    "delscmd",
    about={
        "header": "delete sudo commands",
        "flags": {"-all": "remove all sudo commands"},
        "usage": "{tr}delscmd [command name]\n{tr}delscmd -all",
    },
    allow_channels=False,
)
async def del_sudo_cmd(message: Message):
    """ delete sudo cmd """
    if "-all" in message.flags:
        Config.ALLOWED_COMMANDS.clear()
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.drop(),
            message.edit("**SUDO** cmds cleared!", del_in=5),
        )
        return
    cmd = message.filtered_input_str
    if not cmd:
        await message.err("input not found!")
        return
    if cmd not in Config.ALLOWED_COMMANDS:
        await message.edit(f"cmd : `{cmd}` not in **SUDO**!", del_in=5)
    else:
        Config.ALLOWED_COMMANDS.remove(cmd)
        await asyncio.gather(
            SUDO_CMDS_COLLECTION.delete_one({"_id": cmd}),
            message.edit(
                f"cmd : `{cmd}` removed from **SUDO**!", del_in=5, log=__name__
            ),
        )


@userge.on_cmd("vscmd", about={"header": "view sudo cmds"}, allow_channels=False)
async def view_sudo_cmd(message: Message):
    """ view sudo cmds """
    if not Config.ALLOWED_COMMANDS:
        await message.edit("**SUDO** cmds not found!", del_in=5)
        return
    total = 0
    out_str = "⛔ **SUDO CMDS**: **[{}]** ⛔\n\n"
    async for cmd in SUDO_CMDS_COLLECTION.find().sort("_id"):
        total += 1
        out_str += f"`{cmd}`  "
    await message.edit_or_send_as_file(out_str.format(total), del_in=0)
