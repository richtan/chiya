import logging
import discord
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context, Greedy

from utils import embeds
from utils.record import record_usage

# Enabling logs
log = logging.getLogger(__name__)


class AdministrationCog(Cog):
    """ Administration Cog Cog """

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    @commands.before_invoke(record_usage)
    @commands.command(name="rules")
    async def rules(self, ctx: Context):
        """ Generates the #rules channel embeds. """

        # Captain Karen header image embed
        embed = embeds.make_embed(color="quotes_grey")
        embed.set_image(url="https://i.imgur.com/Yk4kwZy.gif")
        await ctx.send(embed=embed)

        # The actual rules embed
        embed = embeds.make_embed(title="📃  Discord Server Rules", color="quotes_grey", description="This list is not all-encompassing and you may be actioned for a reason outside of these rules. Use common sense when interacting in our community.")
        embed.add_field(name="Rule 1: Do not send copyright-infringing material.", inline=False, value="> Linking to copyright-infringing content via torrents, pirated stream links, direct download links, or uploading copyright-infringing material over Discord puts our community at risk of being shut down. We are a discussion community, not a file-sharing hub. ")
        embed.add_field(name="Rule 2: Be courteous and mindful of others.", inline=False, value="> Do not engage in toxic behavior such as spamming, baiting, derailing conversations, attacking or mocking other users, doxxing, or attempting to instigate drama. Bigotry and hate speech will not be tolerated. Do not use offensive or problematic profile pictures, usernames, nicknames.")
        embed.add_field(name="Rule 3: Do not post self-promotional content.", inline=False, value="> We are not a billboard and are certainly not the place to advertise your Discord server, app, website, service, etc.")
        embed.add_field(name="Rule 4: Do not post unmarked spoilers.", inline=False, value="> Use spoiler tags and include what series or episode your spoiler is in reference to outside the spoiler tag so people don't blindly click a spoiler.")
        embed.add_field(name="Rule 5: Do not backseat moderate.", inline=False, value="> If you see someone breaking the rules or have something to report, please contact staff. Do not take matters into your own hands and respect the decision of the staff.")
        embed.add_field(name="Rule 6: Do not abuse pings.", inline=False, value="> Do not ping staff outside of conversation unless necessary. Do not ping VIP users for questions or help with their service. Do not spam or ghost ping other users.")
        embed.add_field(name="Rule 7: Do not beg, buy, sell, or trade.", inline=False, value="> This includes, but is not limited to, server ranks, roles, permissions, giveaways, private community invites, or any digital or physical goods.")
        await ctx.send(embed=embed)

        # /r/animepiracy links embed
        embed = embeds.make_embed(title="🔗  Our Links", color="quotes_grey")
        embed.add_field(name="Reddit:", inline=True, value="> [/r/animepiracy](https://reddit.com/r/animepiracy)")
        embed.add_field(name="Discord:", inline=True, value="> [discord.gg/piracy](https://discord.gg/piracy)")
        embed.add_field(name="Index:", inline=True, value="> [piracy.moe](https://piracy.moe)")
        embed.add_field(name="Wiki:", inline=True, value="> [wiki.piracy.moe](https://wiki.piracy.moe)")
        embed.add_field(name="Seadex:", inline=True, value="> [seadex.piracy.moe](https://seadex.piracy.moe)")
        embed.add_field(name="GitHub:", inline=True, value="> [github.com/ranimepiracy](https://github.com/ranimepiracy)")
        embed.add_field(name="Twitter:", inline=True, value="> [@ranimepiracy](https://twitter.com/ranimepiracy)")
        embed.add_field(name="Uptime Status:", inline=True, value="> [status.piracy.moe](https://status.piracy.moe/)")
        await ctx.send(embed=embed)

        # Clean up the command invoker
        await ctx.message.delete()


def setup(bot: Bot) -> None:
    """ Load the AdministrationCog cog. """
    bot.add_cog(AdministrationCog(bot))
    log.info("Cog loaded: AdministrationCog")
