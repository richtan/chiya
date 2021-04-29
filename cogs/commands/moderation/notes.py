import asyncio
import datetime
import logging
import time

import dataset
import discord
from discord.embeds import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context, Greedy

import config
from utils import database
from utils import embeds
from utils.record import record_usage

# Enabling logs
log = logging.getLogger(__name__)

class NotesCog(Cog):
    """ Notes Cog """

    def __init__(self, bot):
        self.bot = bot

    @commands.has_role(config.role_staff)
    @commands.bot_has_permissions(send_messages=True)
    @commands.before_invoke(record_usage)
    @commands.command(name="addnote", aliases=['add_note', 'note'])
    async def add_note(self, ctx: Context, user: discord.User, *, note: str):
        """ Adds a moderator note to a user. """

        embed = embeds.make_embed(ctx=ctx, title=f"Noting user: {user.name}", 
            image_url=config.pencil, color=config.soft_blue)
        embed.description=f"{user.mention} was noted by {ctx.author.mention}: {note}"
        await ctx.reply(embed=embed)

        # Add the note to the mod_notes database.
        with dataset.connect(database.get_db()) as db:
            db["mod_notes"].insert(dict(
                user_id=user.id, mod_id=ctx.author.id, timestamp=int(time.time()), note=note
            ))
    
    @commands.has_role(config.role_staff)
    @commands.command(name="search")
    async def search_mod_actions(self, ctx, member: discord.Member, action_type: str = None):
        """ Searches for mod actions on a user """
        result = None
        # querying DB for the list of actions matching the filter criteria (if mentioned)
        with dataset.connect(database.get_db()) as db:
            mod_logs = db["mod_logs"]
            if action_type is not None:
                # Remove plurality from action_type to try and autocorrect for the user. 
                if action_type[-1] == "s":
                    action_type = action_type[:-1]
                result = mod_logs.find(user_id=member.id, type=action_type.lower())
            else:
                result = mod_logs.find(user_id=member.id)

        # creating a list to store actions for the paginator
        actions = []
        page_no = 0
        # number of results per page
        per_page = 4    
        # creating a temporary list to store the per_page number of actions
        page = []
        for x in result:
            # appending dict of action to the particular page
            page.append(dict(
                user_id=x['user_id'],
                mod_id=x['mod_id'],
                reason=x['reason'],
                type=x['type'],
                timestamp = x['timestamp']
            ).copy())
            
            if (page_no + 1) % per_page == 0 and page_no != 0:
                # appending the current page to the main actions list and resetting the page
                actions.append(page.copy())
                page = []
            
            # incrementing the counter variable
            page_no += 1
        
        if not (page_no + 1) % per_page == 0:
            # for the situations when some pages were left behind
            actions.append(page.copy())
        
        if len(actions[0]) == 0:
            # nothing was found, so returning an appropriate error.
            await embeds.error_message(ctx=ctx, description="No mod actions found for that user!")
            return

        page_no = 0

        def get_page(action_list, page_no: int, ctx: Context) -> Embed:
            embed = embeds.make_embed(title="Mod Actions", description=f"Page {page_no+1} of {len(action_list)}", ctx=ctx)
            action_emoji = dict(
                mute = "🤐",
                unmute = "🗣",
                warn = "⚠",
                kick = "👢",
                ban = "🔨",
                unban = "⚒"
            )
            for action in action_list[page_no]:
                action_type = action['type']
                # capitalising the first letter of the action type
                action_type = action_type[0].upper() + action_type[1:]
                # Adding fluff emoji to action_type
                action_type = f"{action_emoji[action['type']]} {action_type}"
                # Appending the other data about the action
                value = f"""
                **Timestamp:** {str(datetime.datetime.fromtimestamp(action['timestamp'], tz=datetime.timezone.utc)).replace("+00:00", " UTC")} 
                **Moderator:** <@!{action['mod_id']}>
                **Reason:** {action['reason']}
                """
                embed.add_field(name=action_type, value=value, inline=False)
                
            return embed
        
        # sending the first page. We'll edit this during pagination.
        msg = await ctx.send(embed=get_page(actions, page_no, ctx))

        FIRST_EMOJI = "\u23EE"   # [:track_previous:]
        LEFT_EMOJI = "\u2B05"    # [:arrow_left:]
        RIGHT_EMOJI = "\u27A1"   # [:arrow_right:]
        LAST_EMOJI = "\u23ED"    # [:track_next:]
        DELETE_EMOJI = "⛔"  # [:trashcan:]
        SAVE_EMOJI = "💾"  # [:floppy_disk:]

        bot = ctx.bot
        timeout = 30

        PAGINATION_EMOJI = (FIRST_EMOJI, LEFT_EMOJI, RIGHT_EMOJI,
                            LAST_EMOJI, DELETE_EMOJI, SAVE_EMOJI)

        
        for x in PAGINATION_EMOJI:
            await msg.add_reaction(x)

        def check(reaction: discord.Reaction, user: discord.Member) -> bool:
            if reaction.emoji in PAGINATION_EMOJI and user == ctx.author:
                return True
            return False

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=timeout, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                break

            if str(reaction.emoji) == DELETE_EMOJI:
                await msg.delete()
                break

            if str(reaction.emoji) == SAVE_EMOJI:
                await msg.clear_reactions()
                break

            if reaction.emoji == FIRST_EMOJI:
                await msg.remove_reaction(reaction.emoji, user)
                page_no = 0

            if reaction.emoji == LAST_EMOJI:
                await msg.remove_reaction(reaction.emoji, user)
                page_no = len(actions) - 1

            if reaction.emoji == LEFT_EMOJI:
                await msg.remove_reaction(reaction.emoji, user)

                if page_no <= 0:
                    page_no = len(actions) - 1
                else:
                    page_no -= 1

            if reaction.emoji == RIGHT_EMOJI:
                await msg.remove_reaction(reaction.emoji, user)

                if page_no >= len(actions) - 1:
                    page_no = 0
                else:
                    page_no += 1

            embed = get_page(actions, page_no, ctx)

            if embed is not None:
                await msg.edit(embed=embed)

def setup(bot: Bot) -> None:
    """ Load the Notes cog. """
    bot.add_cog(NotesCog(bot))
    log.info("Commands loaded: notes")
